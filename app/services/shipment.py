from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from app.database.models import Seller, Shipment
from app.schemas.shipment import CreateShipment, ShipmentStatus
from sqlalchemy.ext.asyncio import AsyncSession


class ShipmentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self):
        result = await self.session.execute(select(Shipment))
        return result.scalars().all()

    async def get(self, id: UUID) -> Shipment:
        return await self.session.get(Shipment, id)

    async def add(self, shipment_create: CreateShipment, seller: Seller):
        shipment = Shipment(
            **shipment_create.model_dump(),
            status=ShipmentStatus.placed,
            estimated_delivery=datetime.now()+timedelta(days=3),
            seller_id=seller.id
        )
        self.session.add(shipment)
        await self.session.commit()
        await self.session.refresh(shipment)
        return shipment

    async def update(self, id: UUID, shipment_update: dict):
        shipment = await self.get(id)
        shipment.sqlmodel_update(shipment_update)

        self.session.add(shipment)
        await self.session.commit()
        await self.session.refresh(shipment)
        return shipment

    async def delete(self, id: UUID) -> None:
        await self.session.delete(await self.get(id))
        await self.session.commit()
