from typing import Sequence
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select, any_
from app.database.models import DeliveryPartner, Shipment
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.delivery_partner import CreateDeliveryPartner
from .user import UserService


class DeliveryPartnerService(UserService):
    def __init__(self, session: AsyncSession, tasks: BackgroundTasks):
        super().__init__(DeliveryPartner, session, tasks)

    async def get_partnes_by_zipcode(self, zipcode: str) -> Sequence[DeliveryPartner]:
        result = await self.session.scalars(
            select(DeliveryPartner).where(
                any_(DeliveryPartner.serviceable_zipcodes) == zipcode)
        )
        return result.all()

    async def assign_shipment(self, shipment: Shipment):
        eligible_partners = await self.get_partnes_by_zipcode(shipment.destination)
        for partner in eligible_partners:
            if partner.current_handling_capacity > 0:
                partner.shipments.append(shipment)
                return partner
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="No delivery partner available for this shipment"
        )

    async def add(self, delivery_partner: CreateDeliveryPartner):
        return await self._add_user(delivery_partner.model_dump(), router_prefix="partner")

    async def update(self, partner: DeliveryPartner):
        return await self._update(partner)

    async def token(self, email, password) -> str:
        token = await self._generate_token(email, password)
        return token
