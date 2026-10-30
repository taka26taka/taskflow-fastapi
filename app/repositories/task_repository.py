from typing import Literal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.core.config import today
from app.models.task import Task
from app.schemas.task import TaskStats

TaskStatus = Literal["all", "pending", "completed"]
TaskSort = Literal["created_at", "priority", "due_date"]


class TaskRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, task_id: int) -> Task | None:
        return self.session.get(Task, task_id)

    def list(self, status: TaskStatus, sort: TaskSort) -> list[Task]:
        query = select(Task)
        if status != "all":
            query = query.where(Task.is_completed == (status == "completed"))
        if sort == "priority":
            query = query.order_by(case({"high": 0, "medium": 1, "low": 2}, value=Task.priority))
        elif sort == "due_date":
            query = query.order_by(Task.due_date.is_(None), Task.due_date)
        return list(self.session.scalars(query.order_by(Task.created_at.desc(), Task.id.desc())))

    def stats(self) -> TaskStats:
        total = self.session.scalar(select(func.count()).select_from(Task)) or 0
        completed = (
            self.session.scalar(
                select(func.count()).select_from(Task).where(Task.is_completed.is_(True))
            )
            or 0
        )
        overdue = (
            self.session.scalar(
                select(func.count())
                .select_from(Task)
                .where(Task.is_completed.is_(False), Task.due_date < today())
            )
            or 0
        )
        return TaskStats(
            total=total, completed=completed, pending=total - completed, overdue=overdue
        )
