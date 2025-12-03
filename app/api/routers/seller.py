from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from app.api.dependencies import SellerServiceDep, get_seller_access_token
from app.database.redis import add_jti_to_blacklist
from app.schemas.seller import CreateSeller, ReadSeller


seller_router = APIRouter(prefix="/seller", tags=['Sellers'])


@seller_router.get("/me", response_model=ReadSeller)
async def read_seller(token_data: Annotated[dict, Depends(get_seller_access_token)], service: SellerServiceDep):
    # The user's ID is nested inside the 'user' dictionary in the token
    user_id = token_data['user']['id']

    # Fetch the actual seller from the database using the correct ID
    seller = await service.get(user_id)

    return seller


@seller_router.get("/verify")
async def verify_seller_email(token: str, service: SellerServiceDep):
    seller = await service.verify_email(token)
    return {"detail": "Email verified successfully", "seller_id": str(seller.id)}


@seller_router.get("/forgot_password")
async def forgot_password(email: EmailStr, service: SellerServiceDep):
    seller = await service.send_password_reset_link(email, seller_router.prefix)
    return {"detail": "Check email for password reset link", "seller_id": str(seller.id)}


@seller_router.get("/reset_password")
async def reset_password(token: str, password: str, service: SellerServiceDep):
    seller = await service.reset_password(token, password)
    return {"detail": "Password reset successful", "seller_id": str(seller.id)}


@seller_router.post("/signup", response_model=ReadSeller)
async def create_seller(create_seller: CreateSeller, service: SellerServiceDep):
    seller = await service._get_by_email(create_seller.email)
    if seller:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    res = await service.add(create_seller)
    return res


@seller_router.post("/token")
async def login_seller(request_form: Annotated[OAuth2PasswordRequestForm, Depends()], service: SellerServiceDep):
    token = await service.token(request_form.username, request_form.password)

    return {"access_token": token, "type": "jwt"}


@seller_router.get("/logout")
async def logout(token_data: Annotated[dict, Depends(get_seller_access_token)]):
    await add_jti_to_blacklist(token_data['jti'])
    return {
        "detail": "Successfully logged out"
    }
