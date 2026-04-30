from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.dependencies import CurrentUserDep
from src.schemas.token import RefreshTokenIn, Token
from src.schemas.user import UserIn, UserOut
from src.services.dependencies import AuthServiceDep

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserIn, auth_service: AuthServiceDep):
    new_user = await auth_service.register_user(user)
    return new_user


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
):

    return await auth_service.login_user(
        email=form_data.username,
        password=form_data.password,
    )


@router.get("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: CurrentUserDep,
):
    return current_user


@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_token(
    token_data: RefreshTokenIn,
    auth_service: AuthServiceDep,
):
    return await auth_service.refresh_token(token_data.refresh_token)
