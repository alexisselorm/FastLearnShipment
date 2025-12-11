from datetime import datetime, timedelta
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from app.database.models import DeliveryPartner, Review, Seller, Shipment
from app.database.redis import get_shipment_verification_code
from app.schemas.enums import TagNames
from app.schemas.shipment import CreateShipment, ShipmentReview, ShipmentStatus, UpdateShipment
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.delivery_partner import DeliveryPartnerService
from app.services.shipment_event import ShipmentEventService
from app.utils import decode_url_safe_token

from .base import BaseService


class ShipmentService(BaseService):
    def __init__(self, session: AsyncSession, partner_service: DeliveryPartnerService, event_service: ShipmentEventService):
        super().__init__(Shipment, session)
        self.partner_service = partner_service
        self.event_service = event_service

    async def get_all(self):
        result = await self.session.execute(select(Shipment))
        return result.scalars().all()

    async def get(self, id: UUID) -> Shipment | None:
        return await self._get(id)

    async def add(self, shipment_create: CreateShipment, seller: Seller):
        shipment = Shipment(
            **shipment_create.model_dump(),
            status=ShipmentStatus.placed,
            estimated_delivery=datetime.now()+timedelta(days=3),
            seller_id=seller.id
        )

        partner = await self.partner_service.assign_shipment(shipment)
        shipment.delivery_partner_id = partner.id
        new_shipment = await self._add(shipment)

        new_event = await self.event_service.add(shipment=new_shipment.id,
                                                 location=seller.zip_code,
                                                 status=ShipmentStatus.placed,)
        shipment.timeline.append(new_event)

        return new_shipment

    async def update(self, id: UUID, shipment_update: UpdateShipment, delivery_partner: DeliveryPartner):
        shipment = await self.get(id)
        if shipment.delivery_partner_id != delivery_partner.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not authorized to update this shipment"
            )

        if shipment.status == ShipmentStatus.delivered:
            code = await get_shipment_verification_code(shipment.id)

            if not shipment_update.verification_code or str(shipment_update.verification_code) != str(code):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Client not authorized to receive the shipment without a valid verification code"
                )

        update = shipment_update.model_dump(exclude_none=True,
                                            exclude=["verification_code"])
        shipment.sqlmodel_update(shipment_update, exclude_none=True)

        if shipment_update.estimated_delivery:
            shipment.estimated_delivery = shipment_update.estimated_delivery

        if len(update) > 1 or not shipment_update.estimated_delivery:
            await self.event_service.add(shipment=shipment,
                                         **update)

        return await self._update(shipment)

    async def cancel(self, id: UUID, seller: Seller):
        shipment = await self.get(id)
        if shipment.seller_id != seller.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not authorized to cancel this shipment"
            )
        if shipment.status == ShipmentStatus.delivered:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivered shipments cannot be cancelled"
            )
        shipment.status = ShipmentStatus.cancelled
        new_event = await self.event_service.add(shipment=shipment,
                                                 status=ShipmentStatus.cancelled,
                                                 location=seller.zip_code,
                                                 description="Shipment cancelled by seller")
        shipment.timeline.append(new_event)
        return await self._update(shipment)

    async def delete(self, id: UUID) -> None:
        await self._delete(self.get(id))

    async def rate(self, token: str, review_data: ShipmentReview):
        data = decode_url_safe_token(token)
        if data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        shipment_id = UUID(data["id"])
        shipment = await self.get(shipment_id)
        if not shipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipment not found"
            )
        if shipment.status != ShipmentStatus.delivered:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only delivered shipments can be reviewed"
            )

        new_review = Review(
            **review_data.model_dump(),
        )

        self.session.add(new_review)
        await self.session.commit()

    async def add_tag(self, id: UUID, tag_name: TagNames):
        shipment = await self.get(id)

        tag = await tag_name.tag(self.session)
        if tag in shipment.tags:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag already exists for this shipment"
            )
        shipment.tags.append(tag)
        return await self._update(shipment)

    async def delete_tag(self, id: UUID, tag_name: TagNames):
        shipment = await self.get(id)

        tag = await tag_name.tag(self.session)
        if tag in shipment.tags:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag already exists for this shipment"
            )
        shipment.tags.remove(tag)
        return await self._update(shipment)
