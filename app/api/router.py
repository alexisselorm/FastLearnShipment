from fastapi import APIRouter

from .routers.seller import seller_router
from .routers.shipment import shipment_router

all_routers = APIRouter()

all_routers.include_router(router=seller_router)
all_routers.include_router(router=shipment_router)
