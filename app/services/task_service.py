from sqlalchemy.orm import Session

from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskNotFound(Exception):
    pass


class TaskService:
    """Writes commit here; failures rollback here. Repositories never commit."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = TaskRepository(session)

    def get(self, task_id: int) -> Task:
        task = self.repository.get(task_id)
        if task is None:
            raise TaskNotFound
        return task

    def save(self, task: Task) -> Task:
        try:
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)
        except Exception:
            self.session.rollback()
            raise
        return task

    def create(self, data: TaskCreate) -> Task:
        return self.save(Task(**data.model_dump()))

    def update(self, task_id: int, data: TaskUpdate) -> Task:
        task = self.get(task_id)
        for name, value in data.model_dump(exclude_unset=True).items():
            setattr(task, name, value)
        return self.save(task)

    def delete(self, task_id: int) -> None:
        task = self.get(task_id)
        try:
            self.session.delete(task)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
