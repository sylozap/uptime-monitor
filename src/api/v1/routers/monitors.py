from fastapi import APIRouter, status

from src.schemas.monitor import MonitorIn, MonitorOut
from src.services.dependencies import MonitorServiceDep

router = APIRouter(prefix="/monitors", tags=["Monitors"])


@router.post("/", response_model=MonitorOut, status_code=status.HTTP_201_CREATED)
async def create_monitor(monitor: MonitorIn, monitor_service: MonitorServiceDep):
    pass
