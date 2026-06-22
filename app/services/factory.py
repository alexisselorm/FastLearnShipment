from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database.session import engine
from app.services.delivery_partner import DeliveryPartnerService
from app.services.seller import SellerService
from app.services.shipment import ShipmentService
from app.services.shipment_event import ShipmentEventService


class ServiceFactory:
    def __init__(self):
        self.session: AsyncSession | None = None
        self.shipment: ShipmentService | None = None
        self.seller: SellerService | None = None
        self.delivery_partner: DeliveryPartnerService | None = None
        self.shipment_event: ShipmentEventService | None = None

    async def __aenter__(self):
        maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=True)
        self.session = maker()
        event_svc = ShipmentEventService(self.session)
        partner_svc = DeliveryPartnerService(self.session)
        self.shipment = ShipmentService(self.session, partner_svc, event_svc)
        self.seller = SellerService(self.session)
        self.delivery_partner = partner_svc
        self.shipment_event = event_svc
        return self

    async def __aexit__(self, *args):
        await self.session.close()
