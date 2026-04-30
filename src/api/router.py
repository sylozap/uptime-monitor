from fastapi import APIRouter

from src.api.v1.routers.auth import router as auth_router
from src.api.v1.routers.monitor import router as monitor_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(monitor_router)
