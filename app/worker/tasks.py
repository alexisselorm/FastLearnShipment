from celery import Celery
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from app.config import settings, mail_settings
from asgiref.sync import async_to_sync
from twilio.rest import Client
from app.utils import TEMPLATES_DIR


fastmail = FastMail(
    ConnectionConfig(
        **mail_settings.model_dump(exclude=["TWILIO_SID", "TWILIO_AUTH_TOKEN", "TWILIO_NUMBER"]),
        TEMPLATE_FOLDER=TEMPLATES_DIR
    )
)

twilio_client = Client(
    mail_settings.TWILIO_SID,
    mail_settings.TWILIO_AUTH_TOKEN
)


send_message = async_to_sync(fastmail.send_message)

app = Celery(
    "api_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    broker_connection_retry_on_startup=True,
)


@app.task
def send_mail(subject: str, recipients: list[str], body: str):
    message = MessageSchema(
        recipients=recipients,
        subject=subject,
        body=body,
    )

    send_message(message)

    return "Message sent"


@app.task
def send_templated_email(subject: str, recipients: list[EmailStr], template_name: str, context: dict):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=context,
        subtype=MessageType.html,
    )

    send_message(
        message,
        template_name=template_name)


@app.task
def send_sms(to_number: str, body: str):
    message = twilio_client.messages.create(
        body=body,
        from_=mail_settings.TWILIO_NUMBER,
        to=to_number
    )
    return message.sid
