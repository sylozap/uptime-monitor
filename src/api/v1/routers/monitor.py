from fastapi import APIRouter, status

from src.api.dependencies import CurrentUserDep
from src.schemas.monitor import MonitorIn, MonitorOut
from src.services.dependencies import MonitorServiceDep

router = APIRouter(prefix="/monitors", tags=["Monitors"])


@router.post("/", response_model=MonitorOut, status_code=status.HTTP_201_CREATED)
async def create_monitor(
    monitor: MonitorIn, monitor_service: MonitorServiceDep, current_user: CurrentUserDep
):
    new_monitor = await monitor_service.create_monitor(
        user_id=current_user.id, monitor=monitor
    )
    return new_monitor
