from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"


class TagNames(str, Enum):
    FRAGILE = "fragile"
    PERISHABLE = "perishable"
    HEAVY = "heavy"
    GIFT = "gift"
    ELECTRONICS = "electronics"
    DOCUMENTS = "documents"
    RETURN = "return"
    EXPRESS = "express"
    INTERNATIONAL = "international"
    TEMPERATURE_CONTROLLED = "temperature_controlled"
    STANDARD = "standard"

    async def tag(self, session: AsyncSession):
        from app.database.models import Tag
        tag = await session.scalar(select(Tag).where(Tag.name == self.value))
        return tag
