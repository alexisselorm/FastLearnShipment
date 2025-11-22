from datetime import datetime
from random import randint
from uuid import UUID
from pydantic import BaseModel, Field


from app.database.models import ShipmentEvent
from app.schemas.seller import ReadSeller
from app.schemas.enums import ShipmentStatus


def random_destination():
    return randint(11000, 11999)


class BaseShipment(BaseModel):
    content: str = Field(min_length=5, max_length=30)
    weight: float = Field(
        description="Weight of the shipment in (kg)", le=25, ge=1)
    destination: int | None = Field(default_factory=random_destination)


class Shipment(BaseShipment):
    id: UUID
    status: str = Field(default="placed")


class GetShipment(BaseShipment):
    timeline: list[ShipmentEvent]
    estimated_delivery: datetime
    seller: ReadSeller


class CreateShipment(BaseShipment):
    pass


class UpdateShipment(BaseModel):
    location: int | None = Field(default=None)
    status: ShipmentStatus | None = Field(default=None)
    description: str | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)
