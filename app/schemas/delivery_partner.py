from uuid import UUID
from pydantic import BaseModel, EmailStr
from sqlmodel import Field


class BaseDeliveryPartner(BaseModel):

    name: str
    email: EmailStr
    serviceable_zip_codes: list[int]
    max_handling_capacity: int


class ReadDeliveryPartner(BaseDeliveryPartner):
    id: UUID


class LoginDeliveryPartner(BaseModel):
    email: EmailStr
    password: str


class UpdateDeliveryPartner(BaseModel):
    serviceable_zip_codes: list[int] | None = Field(default=None)
    max_handling_capacity: int | None = Field(default=None)


class CreateDeliveryPartner(BaseDeliveryPartner):
    password: str
