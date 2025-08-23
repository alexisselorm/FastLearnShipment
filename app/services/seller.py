from datetime import datetime, timedelta
from fastapi import HTTPException, status
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Seller
from app.schemas.seller import CreateSeller

from app.config import security_settings

from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"])


class SellerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, credentials: CreateSeller):
        seller = Seller(
            **credentials.model_dump(),
            password_hash=password_context.hash(credentials.password)
        )

        self.session.add(seller)
        await self.session.commit()
        await self.session.refresh(seller)
        return seller

    async def token(self, email, password) -> str:
        # Validate the credentials
        result = await self.session.execute(select(Seller).where(Seller.email == email))
        seller = result.scalar()

        if seller is None or password_context.verify(password, seller.password_hash):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email or password is incorrect"
            )

        token = jwt.encode(
            payload={
                "user": {
                    "name": seller.name,
                    "email": seller.email
                },
                "exp": datetime.now()+timedelta(days=1)
            },
            algorithm=security_settings.JWT_ALGORITHM,
            key=security_settings.JWT_SECRET
        )
        return token
