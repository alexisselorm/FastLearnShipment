from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import SellerServiceDep
from app.schemas.seller import CreateSeller, ReadSeller

seller_router = APIRouter(prefix="/seller", tags=['Sellers'])


@seller_router.post("/signup", response_model=ReadSeller)
async def create_seller(seller: CreateSeller, service: SellerServiceDep):
    seller = await service.add(seller)
    return seller


@seller_router.post("/token")
async def login_seller(request_form: Annotated[OAuth2PasswordRequestForm, Depends()], service: SellerServiceDep):
    token = await service.token(request_form.username, request_form.password)

    return {"access_token": token, "type": "jwt"}
