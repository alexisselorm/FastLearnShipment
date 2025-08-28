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
    delivery_partner_id: UUID | None = Field(
        foreign_key="delivery_partners.id")
    delivery_partner: "DeliveryPartner" = Relationship(
        back_populates="shipments", sa_relationship_kwargs={"lazy": "selectin"})
    created_at: datetime = Field(sa_column=Column(
        postgresql.TIMESTAMP(), default=datetime.now
    ))


class User(SQLModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password_hash: str


class Seller(User, table=True):
    __tablename__ = "sellers"

    id: UUID = Field(sa_column=Column(
        type_=postgresql.UUID, primary_key=True, default=uuid4))

    shipments: list[Shipment] = Relationship(back_populates="seller",
                                             sa_relationship_kwargs={"lazy": "selectin"})
    created_at: datetime = Field(sa_column=Column(
        postgresql.TIMESTAMP(), default=datetime.now
    ))


class DeliveryPartner(User, table=True):
    __tablename__ = "delivery_partners"

    id: UUID = Field(sa_column=Column(
        type_=postgresql.UUID, primary_key=True, default=uuid4))
    serviceable_zipcodes: list[int] = Field(
        sa_column=Column(postgresql.ARRAY(postgresql.INTEGER)))
    shipments: list[Shipment] = Relationship(back_populates="delivery_partner",
                                             sa_relationship_kwargs={"lazy": "selectin"})
    created_at: datetime = Field(sa_column=Column(
        postgresql.TIMESTAMP(), default=datetime.now
    ))
