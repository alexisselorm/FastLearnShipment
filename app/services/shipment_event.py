
from app.database.models import Shipment, ShipmentEvent
from app.schemas.shipment import ShipmentStatus
from app.services.base import BaseService
from app.services.notification import NotificationService


class ShipmentEventService(BaseService):
    def __init__(self, session, tasks):
        super().__init__(ShipmentEvent, session)
        self.notification_service = NotificationService(tasks)

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
                context = {
                    "shipment_id": shipment.id,
                    "seller": shipment.seller.name,
                    "delivery_partner": shipment.delivery_partner.name
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
            case _:
                return  # No notification for other statuses
        await self.notification_service.send_templated_email(
            subject=subject,
            recipients=[shipment.client_contact_email],
            context=context,
            template_name=template_name
        )
