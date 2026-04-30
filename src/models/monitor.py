import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.models.check_log import CheckLog
    from src.models.incident import Incident
    from src.models.user import User


class Monitor(Base):
    # Columns
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    check_interval: Mapped[int] = mapped_column(server_default=text("60"))
    timeout: Mapped[int] = mapped_column(server_default=text("10"))
    is_active: Mapped[bool] = mapped_column(server_default=text("true"))
    expected_status: Mapped[int] = mapped_column(server_default=text("200"))
    last_status: Mapped[bool | None] = mapped_column(nullable=True)
    last_status_code: Mapped[int | None] = mapped_column(nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="monitors")
    check_logs: Mapped[list["CheckLog"]] = relationship(
        back_populates="monitor", cascade="all, delete-orphan"
    )
    incidents: Mapped[list["Incident"]] = relationship(
        back_populates="monitor", cascade="all, delete-orphan"
    )
