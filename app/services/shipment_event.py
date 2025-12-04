
from random import randint

from app.database.models import Shipment, ShipmentEvent
from app.database.redis import add_shipment_verification_code
from app.schemas.shipment import ShipmentStatus
from app.services.base import BaseService
from app.config import app_settings
from app.utils import generate_url_safe_token
from app.worker.tasks import send_sms, send_templated_email


class ShipmentEventService(BaseService):
    def __init__(self, session):
        super().__init__(ShipmentEvent, session)

    async def add(self, shipment: Shipment, location: int = None, status: ShipmentStatus = None, description=None) -> ShipmentEvent:
        shipment_event = ShipmentEvent(
            shipment_id=shipment.id,
            location=location,
            status=status,
            description=description if description else await self._generate_description(status, location)
        )
        if not location or not status:
            last_event = self.get_latest_event(shipment)
            location = location if location else last_event.location
            status = status if status else last_event.status

        await self._notify(shipment, status)

        return await self._add(shipment_event)

    async def get_latest_event(self, shipment: Shipment):
        return shipment.timeline.sort(key=lambda item: item.created_at)[-1]

    async def _generate_description(self, status: ShipmentStatus, location: int):
        desc_map = {
            ShipmentStatus.PLACED: f"Shipment has been placed and is at location {location}.",
            ShipmentStatus.IN_TRANSIT: f"Shipment is in transit and currently at location {location}.",
            ShipmentStatus.OUT_FOR_DELIVERY: f"Shipment is out for delivery from location {location}.",
            ShipmentStatus.DELIVERED: f"Shipment has been delivered to the destination from location {location}.",
            ShipmentStatus.CANCELLED: f"Shipment has been cancelled at location {location}."
        }
        return desc_map.get(status, "Status update for shipment.")

    async def update(self, shipment: Shipment, location=None, status=None, description=None) -> ShipmentEvent:
        shipment_event = ShipmentEvent(
            shipment_id=shipment.id,
            location=location,
            status=status,
            description=description
        )
        return await self._add(shipment_event)

    async def _notify(self, shipment: Shipment, status: ShipmentStatus):
        match status:
            case ShipmentStatus.PLACED:
                subject = "Your shipment has been placed 📦"
                context = {
                    "shipment_id": shipment.id,
                    "seller": shipment.seller.name,
                    "delivery_partner": shipment.delivery_partner.name
                },
                template_name = "mail_placed.html"

            case ShipmentStatus.DELIVERED:
                subject = "Your shipment has been delivered 🛳"
                token = generate_url_safe_token({"id": str(shipment.id)})
                context = {
                    "shipment_id": shipment.id,
                    "seller": shipment.seller.name,
                    "delivery_partner": shipment.delivery_partner.name,
                    "review_url": f"https://{app_settings.APP_DOMAIN}/shipment/review/?token={token}"
                },
                template_name = "mail_delivered.html"
            case ShipmentStatus.CANCELLED:
                subject = "Your shipment has been cancelled ❌"
                context = {
                    "seller": shipment.seller.name,
                    "partner": shipment.delivery_partner.name
                },
                template_name = "mail_cancelled.html"

            case ShipmentStatus.OUT_FOR_DELIVERY:
                subject = "Your shipment is out for delivery 🚚"
                context = {
                    "shipment_id": shipment.id,
                    "delivery_partner": shipment.delivery_partner.name
                },
                template_name = "mail_out_for_delivery.html"
                code = randint(100_000, 999_999)

                await add_shipment_verification_code(shipment.id, code)

                if shipment.client_contact_phone:
                    send_sms.delay(
                        to_number=shipment.client_contact_phone,
                        body=f"Your verification code for delivery of shipment {shipment.id} is {code}."
                    )
                else:
                    context["verification_code"] = code
            case _:
                return  # No notification for other statuses
        send_templated_email.delay(
            subject=subject,
            recipients=[shipment.client_contact_email],
            context=context,
            template_name=template_name
        )
