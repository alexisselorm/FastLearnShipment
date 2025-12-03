from datetime import datetime
from random import randint
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


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
    client_contact_email: EmailStr
    client_contact_phone: str | None = Field(default=None)


class UpdateShipment(BaseModel):
    location: int | None = Field(default=None)
    status: ShipmentStatus | None = Field(default=None)
    verification_code: int | None = Field(default=None)
    description: str | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)


class ShipmentReview(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=250)
