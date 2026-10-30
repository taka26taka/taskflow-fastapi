from datetime import UTC, date, datetime
from enum import StrEnum

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import today
from app.db.base import Base


class Priority(StrEnum):
    high = "high"
    medium = "medium"
    low = "low"


def utc_now() -> datetime:
    # SQLite stores naive datetimes; the application interprets them as UTC.
    return datetime.now(UTC).replace(tzinfo=None)


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("length(trim(title)) BETWEEN 1 AND 100"),
        CheckConstraint("length(description) <= 1000"),
        CheckConstraint("priority IN ('high', 'medium', 'low')"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, default="")
    priority: Mapped[str] = mapped_column(String(10), default=Priority.medium)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    @property
    def is_overdue(self) -> bool:
        return not self.is_completed and self.due_date is not None and self.due_date < today()
