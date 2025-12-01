from uuid import UUID
from sqlalchemy import select
from app.database.models import User
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.notification import NotificationService
from .base import BaseService
from fastapi import BackgroundTasks, HTTPException, status
from passlib.context import CryptContext
from app.config import app_settings

from app.utils import decode_url_safe_token, generate_access_token, generate_url_safe_token

password_context = CryptContext(schemes=["bcrypt"])


class UserService(BaseService):
    def __init__(self, model: User, session: AsyncSession, tasks: BackgroundTasks):
        self.session = session
        self.model = model
        self.notification_service = NotificationService(tasks)

    async def _add_user(self, data: dict, router_prefix):
        user = self.model(
            **data,
            password_hash=password_context.hash(data['password'])
        )
        new_user = await self._add(user)
        token = generate_url_safe_token(
            {"email": user.email, "id": str(new_user.id)})

        await self.notification_service.send_templated_email(recipients=[user.email], subject="Verify your email",
                                                             context={
            "username": user.name,
            "verification_url": f"http://{app_settings.APP_DOMAIN}/{router_prefix}/verify?token={token}"
        },
            template_name="mail_email_verify.html")

        return user

    async def _get_by_email(self, email: str) -> User | None:
        return await self.session.scalar(
            select(self.model).where(self.model.email == email)
        )

    async def verify_email(self, token: str):
        payload = decode_url_safe_token(token)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        user = await self._get(UUID(payload["id"]))
        if user.email_verified:
            raise HTTPException(
                detail="Your email has already been verified",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        user.email_verified = True
        await self._update(user)
        return user

    async def _generate_token(self, email, password) -> str:
        # Validate the credentials
        user = await self._get_by_email(email)

        if user is None or not password_context.verify(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email or password is incorrect"
            )

        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email is not verified"
            )

        token = generate_access_token(data={
            "user": {
                "name": user.name,
                "id": str(user.id)
            }
        })
        return token
