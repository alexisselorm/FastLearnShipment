from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import SellerDep, ShipmentServiceDep
from app.schemas.shipment import CreateShipment, GetShipment, UpdateShipment

shipment_router = APIRouter(prefix="/shipment",
                            tags=["Shipment"])


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
async def shipment(id: int, service: ShipmentServiceDep):

    shipment = await service.get(id)
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given id does not exist"
        )
    return shipment


# Create a new shipment with
@shipment_router.post("/")
async def create_shipment(_: SellerDep, body: CreateShipment, service: ShipmentServiceDep):

    shipment = await service.add(body)

    return {"id": shipment.id}


# Update
@shipment_router.patch("/", response_model=GetShipment)
async def update_shipment(id: int, body: UpdateShipment, service: ShipmentServiceDep):
    update = body.model_dump(exclude_none=True)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update"
        )

    shipment = await service.update(id, update)

    return shipment


@shipment_router.delete("/{id}")
async def delete_shipment(id: int, service: ShipmentServiceDep):

    await service.delete(id)

    return {"detail": f"Ship with id {id} has been deleted"}
