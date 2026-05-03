import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.models.monitor import Monitor


class CheckLog(Base):
    # Columns
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    monitor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("monitors.id", ondelete="CASCADE"), nullable=False
    )
    response_time: Mapped[int] = mapped_column(nullable=False)
    status_code: Mapped[int] = mapped_column()
    is_available: Mapped[bool] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    monitor: Mapped["Monitor"] = relationship(back_populates="check_logs")
