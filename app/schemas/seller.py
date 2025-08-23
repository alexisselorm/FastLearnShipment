from pydantic import BaseModel, EmailStr


class BaseSeller(BaseModel):
    name: str
    email: EmailStr


class ReadSeller(BaseSeller):
    pass


class LoginSeller(BaseModel):
    email: EmailStr
    password: str


class CreateSeller(BaseSeller):
    password: str
