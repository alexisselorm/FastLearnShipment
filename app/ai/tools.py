from uuid import UUID

from langchain_core.tools import tool

from app.services.factory import ServiceFactory
# from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage


@tool
async def lookup_shipment(shipment_id: str) -> str:
    """
    Lookup a shipment by its ID and return its details.
    """
    async with ServiceFactory() as service:
        shipment_details = await service.shipment.get(UUID(shipment_id))
        if shipment_details:
            return shipment_details
        else:
            return f"Shipment with ID: {shipment_id} not found"


@tool
async def track_shipment(shipment_id: str) -> str:
    """
    Track a shipment by its ID and return its current status.
    """
    async with ServiceFactory() as service:
        s = await service.shipment.get(UUID(shipment_id))
        if s:
            # Get timeline
            lines = ["Timeline:"]
            for ev in sorted(s.timeline, key=lambda x: x.created_at):
                lines.append(
                    f"{ev.created_at}: {ev.status} - {ev.description}")
            return "\n".join(lines)
        else:
            return f"Shipment with ID: {shipment_id} not found"
