import uuid
from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from src.api.dependencies import CurrentUserDep
from src.schemas.monitor import (
    MonitorCreate,
    MonitorFilterParams,
    MonitorResponse,
    MonitorUpdate,
)
from src.services.dependencies import MonitorServiceDep

router = APIRouter(prefix="/monitors", tags=["Monitors"])


@router.post("/", response_model=MonitorResponse, status_code=status.HTTP_201_CREATED)
async def create_monitor(
    monitor: MonitorCreate,
    monitor_service: MonitorServiceDep,
    current_user: CurrentUserDep,
):
    new_monitor = await monitor_service.create_monitor(
        user_id=current_user.id, monitor=monitor
    )
    return new_monitor


@router.get("/", response_model=list[MonitorResponse], status_code=status.HTTP_200_OK)
async def get_monitors(
    filters: Annotated[MonitorFilterParams, Query()],
    monitor_service: MonitorServiceDep,
    current_user: CurrentUserDep,
):
    monitors = await monitor_service.get_monitors(
        user_id=current_user.id, filters=filters
    )

    return monitors


@router.get(
    "/{monitor_id}", response_model=MonitorResponse, status_code=status.HTTP_200_OK
)
async def get_monitor_by_id(
    monitor_id: Annotated[uuid.UUID, Path()],
    current_user: CurrentUserDep,
    monitor_service: MonitorServiceDep,
):
    monitor = await monitor_service.get_monitor_by_id(
        id=monitor_id, user_id=current_user.id
    )

    return monitor


@router.patch(
    "/{monitor_id}", response_model=MonitorResponse, status_code=status.HTTP_200_OK
)
async def update_monitor(
    monitor_id: Annotated[uuid.UUID, Path()],
    current_user: CurrentUserDep,
    monitor_service: MonitorServiceDep,
    fields_to_update: MonitorUpdate,
):
    updated_monitor = await monitor_service.update_monitor(
        id=monitor_id, user_id=current_user.id, fields_to_update=fields_to_update
    )

    return updated_monitor


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monitor(
    monitor_id: Annotated[uuid.UUID, Path()],
    current_user: CurrentUserDep,
    monitor_service: MonitorServiceDep,
) -> None:
    await monitor_service.delete_monitor(id=monitor_id, user_id=current_user.id)
