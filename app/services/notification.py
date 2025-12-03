from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from app.services.base import BaseService
from app.config import mail_settings
from app.utils import TEMPLATES_DIR
from twilio.rest import Client


class NotificationService(BaseService):
    def __init__(self, tasks: BackgroundTasks):
        self.tasks = tasks
        self.fastmail = FastMail(
            ConnectionConfig(
                **mail_settings.model_dump(exclude=["TWILIO_SID", "TWILIO_AUTH_TOKEN", "TWILIO_NUMBER"]),
                TEMPLATE_FOLDER=TEMPLATES_DIR
                # TEMPLATE_FOLDER="/home/rm_rf_master/Documents/Learning/FastLearn/app/templates",
            )
        )

        self.twilio_client = Client(
            mail_settings.TWILIO_SID,
            mail_settings.TWILIO_AUTH_TOKEN
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
        print("Sending templated email to:")
        print(recipients)
        print(TEMPLATES_DIR)
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            template_body=context,
            subtype=MessageType.html,
        )

        self.tasks.add_task(
            self.fastmail.send_message,
            message,
            template_name=template_name
        )

    async def send_sms(self, to_number: str, body: str):
        message = await self.twilio_client.messages.create_async(
            body=body,
            from_=mail_settings.TWILIO_NUMBER,
            to=to_number
        )
        return message.sid
