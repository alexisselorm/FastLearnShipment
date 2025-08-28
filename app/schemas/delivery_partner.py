from uuid import UUID
from pydantic import BaseModel, EmailStr


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
    serviceable_zip_codes: list[int]
    max_handling_capacity: int


class CreateDeliveryPartner(BaseDeliveryPartner):
    password: str
