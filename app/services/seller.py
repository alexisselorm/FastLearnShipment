from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Seller
from app.schemas.seller import CreateSeller


from passlib.context import CryptContext

from .user import UserService

password_context = CryptContext(schemes=["bcrypt"])


class SellerService(UserService):
    def __init__(self, session: AsyncSession, tasks: BackgroundTasks):
        super().__init__(Seller, session, tasks)

    async def get(self, user_id: str):
        result = await self.session.execute(select(Seller).where(Seller.id == user_id))
        seller = result.scalar()
        if seller is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seller not found"
            )
        return seller

    async def add(self, credentials: CreateSeller):
        return await self._add_user(credentials.model_dump(), router_prefix="seller")

    async def token(self, email, password) -> str:
        # Validate the credentials
        token = await self._generate_token(email, password)
        return token
