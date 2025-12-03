from uuid import UUID
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import SellerDep, ShipmentServiceDep
from app.database.models import DeliveryPartner
from app.schemas.shipment import CreateShipment, GetShipment, ShipmentReview, UpdateShipment
from app.utils import TEMPLATES_DIR

shipment_router = APIRouter(prefix="/shipment",
                            tags=["Shipment"])

templates = Jinja2Templates(TEMPLATES_DIR)


@shipment_router.get("/", response_model=None)
async def get_all_shipments(service: ShipmentServiceDep):
    shipments = await service.get_all()
    if not shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No shipments found"
        )

    return shipments


@shipment_router.get("/{id}", response_model=GetShipment)
async def shipment(id: UUID, service: ShipmentServiceDep):

    shipment = await service.get(id)
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given id does not exist"
        )
    return shipment


# Tracking details of a shipment
@shipment_router.get("/track", response_model=None)
async def track_shipment(request: Request, id: UUID, service: ShipmentServiceDep):
    shipment = await service.get(id)
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given id does not exist"
        )

    context = shipment.model_dump()
    context["partner"] = shipment.delivery_partner.name
    context["seller"] = shipment.seller.name
    context["timeline"] = shipment.timeline
    context["status"] = shipment.status

    return HTMLResponse(
        request=request,
        name="track.html",
        context=context
    )


# Create a new shipment with
@shipment_router.post("/")
async def create_shipment(seller: SellerDep, body: CreateShipment, service: ShipmentServiceDep):

    shipment = await service.add(body, seller)

    return {"id": shipment.id}


# Update
@shipment_router.patch("/", response_model=GetShipment)
async def update_shipment(id: UUID, shipment_update: UpdateShipment, partner: DeliveryPartner, service: ShipmentServiceDep):
    update = shipment_update.model_dump(exclude_none=True)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update"
        )

    shipment = await service.update(id, shipment_update, partner)

    return shipment


@shipment_router.post("/cancel", response_model=GetShipment)
async def cancel_shipment(id: UUID, seller: SellerDep, service: ShipmentServiceDep):

    return await service.cancel(id, seller)


# Reviews
@shipment_router.post("/review")
async def review_shipment(token: str, review_data: ShipmentReview, service: ShipmentServiceDep):
    await service.rate(token, review_data)

    return {"detail": "Review added successfully."}
