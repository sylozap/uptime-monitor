from fastapi import APIRouter, status

from src.schemas.user import UserIn, UserOut
from src.services.dependencies import AuthServiceDep

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserIn, auth_service: AuthServiceDep):
    new_user = await auth_service.register_user(user)
    return new_user
