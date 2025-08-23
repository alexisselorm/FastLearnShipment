from fastapi.security import OAuth2PasswordBearer


oauth2scheme = OAuth2PasswordBearer(tokenUrl="/seller/token")
