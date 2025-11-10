from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from app.database.models import Seller, Shipment
from app.schemas.shipment import CreateShipment, ShipmentStatus
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.delivery_partner import DeliveryPartnerService

from .base import BaseService


class ShipmentService(BaseService):
    def __init__(self, session: AsyncSession, partner_service: DeliveryPartnerService):
        super().__init__(Shipment, session)
        self.partner_service = partner_service

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
        return await self._add(shipment)

    async def update(self, id: UUID, shipment_update: dict):
        shipment = await self.get(id)
        shipment.sqlmodel_update(shipment_update)

        return await self._update(shipment)

    async def delete(self, id: UUID) -> None:
        await self._delete(self.get(id))
