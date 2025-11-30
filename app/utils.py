from datetime import datetime, timedelta, timezone
from pathlib import Path
import uuid
from fastapi import HTTPException, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
import jwt
from app.config import security_settings


APP_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = APP_DIR.joinpath("templates")


_serializer = URLSafeTimedSerializer(secret_key=security_settings.JWT_SECRET)


def generate_url_safe_token(token: str) -> dict | None:
    return _serializer.dumps(token)


def decode_url_safe_token(token: str, expiry: timedelta | None = None) -> dict | None:
    try:
        return _serializer.loads(token, max_age=expiry.total_seconds() if expiry else None)
    except (BadSignature, SignatureExpired):
        return None


def generate_access_token(data: dict, expiry: timedelta = timedelta(days=1)):
    token = jwt.encode(
              payload={
                  **data,
                  "jti": uuid.uuid4().hex,
                  "exp": datetime.now(timezone.utc) + expiry
              },
              algorithm=security_settings.JWT_ALGORITHM,  # noqa: F821
              key=security_settings.JWT_SECRET
          )
    return token


def decode_access_token(token: str):
    try:
        return jwt.decode(
            jwt=token,
            key=security_settings.JWT_SECRET,
            algorithms=[security_settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired"
        )
    except jwt.PyJWTError:
        return None
