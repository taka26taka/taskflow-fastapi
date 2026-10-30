from datetime import UTC, date, datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    StringConstraints,
    field_validator,
    model_validator,
)

from app.models.task import Priority

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Description = Annotated[str, StringConstraints(max_length=1000)]


class TaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    @field_validator("priority", mode="before", check_fields=False)
    @classmethod
    def parse_priority(cls, value: object) -> Priority:
        if not isinstance(value, str):
            raise ValueError("優先順位が不正です")
        return Priority(value)

    @field_validator("due_date", mode="before", check_fields=False)
    @classmethod
    def parse_date(cls, value: object) -> date | None:
        if value is None or isinstance(value, date):
            return value
        if isinstance(value, str):
            return date.fromisoformat(value)
        raise ValueError("期限は YYYY-MM-DD で指定してください")


class TaskCreate(TaskInput):
    title: Title
    description: Description = ""
    priority: Priority = Priority.medium
    due_date: date | None = None


class TaskUpdate(TaskInput):
    title: Title | None = None
    description: Description | None = None
    priority: Priority | None = None
    due_date: date | None = None
    is_completed: bool | None = None

    @model_validator(mode="after")
    def reject_null(self) -> "TaskUpdate":
        for name in self.model_fields_set - {"due_date"}:
            if getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")
        return self


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    priority: Priority
    is_completed: bool
    due_date: date | None
    created_at: datetime
    updated_at: datetime
    is_overdue: bool

    @field_validator("created_at", "updated_at")
    @classmethod
    def utc_timestamp(cls, value: datetime) -> datetime:
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


class TaskStats(BaseModel):
    total: int
    completed: int
    pending: int
    overdue: int
