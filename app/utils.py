from datetime import datetime, timedelta, timezone
from pathlib import Path
import uuid
from fastapi import HTTPException, status
import jwt
from app.config import security_settings


APP_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = APP_DIR.joinpath("templates")


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
