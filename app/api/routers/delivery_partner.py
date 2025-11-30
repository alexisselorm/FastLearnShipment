from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import DeliveryPartnerDep, DeliveryPartnerServiceDep, get_partner_access_token
from app.database.redis import add_jti_to_blacklist
from app.schemas.delivery_partner import CreateDeliveryPartner, ReadDeliveryPartner, UpdateDeliveryPartner


delivery_partner_router = APIRouter(
    prefix="/delivery_partner", tags=['Delivery Partners'])


@delivery_partner_router.post("/signup", response_model=ReadDeliveryPartner)
async def create_delivery_partner(delivery_partner: CreateDeliveryPartner, service: DeliveryPartnerServiceDep):
    delivery_partner = await service.add(delivery_partner)
    return delivery_partner


@delivery_partner_router.post("/token")
async def login_delivery_partner(request_form: Annotated[OAuth2PasswordRequestForm, Depends()], service: DeliveryPartnerServiceDep):
    token = await service.token(request_form.username, request_form.password)

    return {"access_token": token, "type": "jwt"}


@delivery_partner_router.get("/verify")
async def verify_seller_email(token: str, service: DeliveryPartnerServiceDep):
    seller = await service.verify_email(token)
    return {"detail": "Email verified successfully", "seller_id": str(seller.id)}


@delivery_partner_router.post("/", response_model=ReadDeliveryPartner)
async def update_delivery_partner(
    partner_update: UpdateDeliveryPartner,
    partner: DeliveryPartnerDep,
    service: DeliveryPartnerServiceDep
):
    return await service.update(

        partner.sqlmodel_update(partner_update.model_dump(exclude_none=True))
    )


@delivery_partner_router.get("/logout")
async def logout(token_data: Annotated[dict, Depends(get_partner_access_token)]):
    await add_jti_to_blacklist(token_data['jti'])
    return {
        "detail": "Successfully logged out"
    }
