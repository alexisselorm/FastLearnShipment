from fastapi import APIRouter

from .routers.seller import seller_router
from .routers.shipment import shipment_router
from .routers.delivery_partner import delivery_partner_router
all_routers = APIRouter()

all_routers.include_router(router=delivery_partner_router)
all_routers.include_router(router=seller_router)
all_routers.include_router(router=shipment_router)
