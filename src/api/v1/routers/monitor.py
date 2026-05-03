import uuid
from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from src.api.dependencies import CurrentUserDep
from src.schemas.monitor import (
    MonitorFilterParams,
    MonitorIn,
    MonitorOut,
    MonitorUpdate,
)
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


@router.get("/", response_model=list[MonitorOut], status_code=status.HTTP_200_OK)
async def get_monitors(
    filter_query: Annotated[MonitorFilterParams, Query()],
    monitor_service: MonitorServiceDep,
    current_user: CurrentUserDep,
):
    monitors = await monitor_service.get_monitors(
        user_id=current_user.id, filter_query=filter_query
    )

    return monitors


@router.get("/{id}", response_model=MonitorOut, status_code=status.HTTP_200_OK)
async def get_monitor_by_id(
    id: Annotated[uuid.UUID, Path()],
    current_user: CurrentUserDep,
    monitor_service: MonitorServiceDep,
):
    monitor = await monitor_service.get_monitor_by_id(id=id, user_id=current_user.id)

    return monitor


@router.patch("/{id}", response_model=MonitorOut, status_code=status.HTTP_200_OK)
async def update_monitor(
    id: Annotated[uuid.UUID, Path()],
    current_user: CurrentUserDep,
    monitor_service: MonitorServiceDep,
    fields_to_update: MonitorUpdate,
):
    updated_monitor = await monitor_service.update_monitor(
        id=id, user_id=current_user.id, fields_to_update=fields_to_update
    )

    return updated_monitor


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monitor(
    id: Annotated[uuid.UUID, Path()],
    current_user: CurrentUserDep,
    monitor_service: MonitorServiceDep,
) -> None:
    await monitor_service.delete_monitor(id=id, user_id=current_user.id)
