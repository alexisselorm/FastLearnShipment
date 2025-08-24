from datetime import datetime
from uuid import UUID, uuid4
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, Column
from app.schemas.shipment import ShipmentStatus
from sqlalchemy.dialects import postgresql


class Shipment(SQLModel, table=True):
    __tablename__ = "shipments"

    id: UUID = Field(sa_column=Column(
        type_=postgresql.UUID, primary_key=True, default=uuid4))
    content: str
    weight: float = Field(le=25)
    destination: int
    status: ShipmentStatus
    estimated_delivery: datetime

    seller_id: UUID = Field(foreign_key="sellers.id")
    seller: "Seller" = Relationship(
        back_populates="shipments", sa_relationship_kwargs={"lazy": "selectin"})


class Seller(SQLModel, table=True):
    __tablename__ = "sellers"

    id: UUID = Field(sa_column=Column(
        type_=postgresql.UUID, primary_key=True, default=uuid4))
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password_hash: str

    shipments: list[Shipment] = Relationship(back_populates="seller",
                                             sa_relationship_kwargs={"lazy": "selectin"})
