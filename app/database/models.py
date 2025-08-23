from datetime import datetime
from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from app.schemas.shipment import ShipmentStatus


class Shipment(SQLModel, table=True):
    __tablename__ = "shipments"

    id: int = Field(primary_key=True)
    content: str
    weight: float = Field(le=25)
    destination: int
    status: ShipmentStatus
    estimated_delivery: datetime


class Seller(SQLModel, table=True):
    __tablename__ = "sellers"

    id: int = Field(primary_key=True)
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password_hash: str
