from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from fastapi import HTTPException, status

from app.utils import decode_access_token

oauth2scheme = OAuth2PasswordBearer(tokenUrl="/seller/token")


class AccesstokenBearer(HTTPBearer):
    async def __call__(self, request):
        auth_credentials = await super().__call__(request)
        token = auth_credentials.credentials

        token_data = decode_access_token(token)

        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )

        return token


access_token_bearer = AccesstokenBearer()
