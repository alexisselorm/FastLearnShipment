from datetime import datetime
from uuid import UUID, uuid4
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, Column
from app.schemas.enums import ShipmentStatus, TagNames
from sqlalchemy.dialects import postgresql


class ShipmentEvent(SQLModel, table=True):
    __tablename__ = "shipment_events"
    id: UUID = Field(sa_column=Column(
        type_=postgresql.UUID, primary_key=True, default=uuid4))
    created_at: datetime = Field(sa_column=Column(
        postgresql.TIMESTAMP(), default=datetime.now))
    location: int
    status: ShipmentStatus
    description: str | None = Field(default=None)
    shipment_id: UUID = Field(foreign_key="shipments.id")

    shipment: "Shipment" = Relationship(back_populates="timeline",
                                        sa_relationship_kwargs={"lazy": "selectin"})


class Shipment(SQLModel, table=True):
    __tablename__ = "shipments"

    id: UUID = Field(sa_column=Column(
        type_=postgresql.UUID, primary_key=True, default=uuid4))
    content: str
    weight: float = Field(le=25)
    destination: int
    estimated_delivery: datetime
    client_contact_email: EmailStr
    client_contact_phone: str | None

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

    timeline: list["ShipmentEvent"] = Relationship(back_populates="shipment",
                                                   sa_relationship_kwargs={"lazy": "selectin"})

    review: "Review" = Relationship(
        back_populates="shipment", sa_relationship_kwargs={"lazy": "selectin"})

    tags: list["Tag"] = Relationship(
        back_populates="shipments",
        link_model="ShipmentTag",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    @property
    def status(self):
        return self.timeline[-1].status if len(self.timeline) > 0 else None


class ShipmentTag(SQLModel, table=True):
    __tablename__ = "shipment_tag"

    shipment_id: UUID = Field(foreign_key="shipments.id", primary_key=True)
    tag_id: UUID = Field(foreign_key="tags.id", primary_key=True)


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: UUID = Field(sa_column=Column(
        type_=postgresql.UUID, primary_key=True, default=uuid4))
    name: TagNames = Field(min_length=2, max_length=30,
                           unique=True, default=TagNames.STANDARD)
    instruction: str

    shipments: list["Shipment"] = Relationship(
        back_populates="tags",
        link_model="ShipmentTag",
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class User(SQLModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(unique=True)
    email_verified: bool = Field(default=False)
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

    address: str | None = Field(default=None)
    zip_code: int | None = Field(default=None)


class DeliveryPartner(User, table=True):
    __tablename__ = "delivery_partners"

    id: UUID = Field(sa_column=Column(
        type_=postgresql.UUID, primary_key=True, default=uuid4))
    serviceable_zipcodes: list[int] = Field(
        sa_column=Column(postgresql.ARRAY(postgresql.INTEGER)))
    max_handling_capacity: int

    shipments: list[Shipment] = Relationship(back_populates="delivery_partner",
                                             sa_relationship_kwargs={"lazy": "selectin"})
    created_at: datetime = Field(sa_column=Column(
        postgresql.TIMESTAMP(), default=datetime.now
    ))

    @property
    def active_shipments(self):
        return [shipment for shipment in self.shipments if shipment.status != ShipmentStatus.delivered or shipment.status != ShipmentStatus.cancelled]

    @property
    def current_handling_capacity(self):
        return self.max_handling_capacity - len(self.active_shipments())


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id: UUID = Field(sa_column=Column(
        type_=postgresql.UUID, primary_key=True, default=uuid4))
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None)
    created_at: datetime = Field(sa_column=Column(
        postgresql.TIMESTAMP(), default=datetime.now
    ))

    shipment_id: UUID = Field(foreign_key="shipments.id")
    shipment: Shipment = Relationship(
        back_populates="review",
        sa_relationship_kwargs={"lazy": "selectin"})
