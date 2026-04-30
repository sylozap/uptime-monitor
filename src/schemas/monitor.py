import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class BaseMonitor(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    name: str = Field(min_length=1, max_length=255)


class MonitorIn(BaseMonitor):
    url: HttpUrl = Field(max_length=2048)
    check_interval: int = Field(default=60, ge=1, le=86400)
    timeout: int = Field(default=10, ge=1, le=60)
    expected_status: int = Field(default=200, ge=100, le=599)
    is_active: bool = True


class MonitorUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(None, min_length=1, max_length=255)
    url: HttpUrl | None = Field(None, max_length=2048)
    check_interval: int | None = Field(None, ge=1, le=86400)
    timeout: int | None = Field(None, ge=1, le=60)
    expected_status: int | None = Field(None, ge=100, le=599)
    is_active: bool | None = None


class MonitorOut(BaseMonitor):
    id: uuid.UUID
    user_id: uuid.UUID
    url: HttpUrl
    check_interval: int
    timeout: int
    is_active: bool
    expected_status: int

    last_status: bool | None
    last_status_code: int | None
    last_checked_at: datetime | None

    created_at: datetime
    updated_at: datetime
