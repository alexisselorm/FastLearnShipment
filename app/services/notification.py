from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from app.services.base import BaseService
from app.config import mail_settings
from app.utils import TEMPLATES_DIR


class NotificationService(BaseService):
    def __init__(self, tasks: BackgroundTasks):
        self.tasks = tasks
        self.fastmail = FastMail(
            ConnectionConfig(
                **mail_settings.model_dump(),
                TEMPLATE_FOLDER=TEMPLATES_DIR
            )
        )

    async def send_email(self, subject: str, recipients: list[EmailStr], body: str):
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype=MessageType.plain,
        )
        self.tasks.add_task(self.fastmail.send_message, message)

    async def send_templated_email(self, subject: str, recipients: list[EmailStr], template_name: str, context: dict):
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            template_body=context,
            template_name=template_name,
            subtype=MessageType.html,
        )
        self.tasks.add_task(
            self.fastmail.send_message,
            message,
        )
