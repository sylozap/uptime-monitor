import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.models.monitor import Monitor


class Incident(Base):
    # Columns
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    monitor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("monitors.id"), nullable=False
    )
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_type: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    monitor: Mapped["Monitor"] = relationship(back_populates="incidents")
