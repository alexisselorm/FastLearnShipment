from datetime import datetime
from enum import Enum
from random import randint
from pydantic import BaseModel, Field


def random_destination():
    return randint(11000, 11999)


class BaseShipment(BaseModel):
    content: str = Field(min_length=5, max_length=30)
    weight: float = Field(
        description="Weight of the shipment in (kg)", le=25, ge=1)
    destination: int | None = Field(default_factory=random_destination)


class ShipmentStatus(str, Enum):
    placed = "placed",
    in_transit = "in_transit",
    out_for_delivery = "out_for_delivery",
    delivered = "delivered"


class Shipment(BaseShipment):

    status: str = Field(default="placed")


class GetShipment(BaseShipment):
    status: ShipmentStatus
    estimated_delivery: datetime


class CreateShipment(BaseShipment):
    pass


class UpdateShipment(BaseModel):
    status: ShipmentStatus | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)
