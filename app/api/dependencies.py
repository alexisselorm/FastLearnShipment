

from typing import Annotated
from uuid import UUID

from fastapi import BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import oauth2scheme_seller, oauth2scheme_partner
from app.database.models import DeliveryPartner, Seller
from app.database.redis import is_jti_blacklisted
from app.database.session import get_session
from app.services.delivery_partner import DeliveryPartnerService
from app.services.seller import SellerService
from app.services.shipment import ShipmentService
from app.services.shipment_event import ShipmentEventService
from app.utils import decode_access_token

SessionDep = Annotated[AsyncSession, Depends(get_session)]


# ACCESS TOKEN DATA DEP
async def _get_access_token(token: str):
    data = decode_access_token(token)
    if data is None or await is_jti_blacklisted(data['jti']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )
    return data


async def get_seller_access_token(token: Annotated[str, Depends(oauth2scheme_seller)]):
    return await _get_access_token(token
                                   )


async def get_partner_access_token(token: Annotated[str, Depends(oauth2scheme_partner)]):
    return await _get_access_token(token
                                   )


async def get_current_seller(token_data: Annotated[dict, Depends(get_seller_access_token)], session: SessionDep):

    seller = await session.get(Seller, UUID(token_data["user"]["id"]))
    if seller is None:
        raise HTTPException(status_code=401, detail="Not authorized")
    return seller


async def get_current_partner(token_data: Annotated[dict, Depends(get_partner_access_token)], session: SessionDep):
    partner = await session.get(DeliveryPartner, UUID(token_data["user"]["id"]))
    if partner is None:
        raise HTTPException(status_code=401, detail="Not authorized")
    return partner


def get_shipment_service(session: SessionDep, tasks: BackgroundTasks):
    return ShipmentService(session, DeliveryPartnerService(session), ShipmentEventService(session, tasks))


def get_delivery_partner_service(session: SessionDep):
    return DeliveryPartnerService(session)


def get_seller_service(session: SessionDep):
    return SellerService(session)


ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]
SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]
DeliveryPartnerServiceDep = Annotated[DeliveryPartnerService, Depends(
    get_delivery_partner_service)]
SellerDep = Annotated[Seller, Depends(get_current_seller)]
DeliveryPartnerDep = Annotated[DeliveryPartner, Depends(get_current_partner)]
