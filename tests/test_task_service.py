from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService


def test_save_update_delete(session: Session) -> None:
    service = TaskService(session)
    task = service.create(TaskCreate(title="first"))
    task_id = task.id
    before = task.updated_at
    session.expire_all()
    assert service.get(task_id).title == "first"
    updated = service.update(task_id, TaskUpdate(title="second"))
    assert updated.updated_at > before
    session.expire_all()
    assert service.get(task_id).title == "second"
    service.delete(task_id)
    assert session.get(Task, task_id) is None


def test_save_rollback(session: Session) -> None:
    service = TaskService(session)
    with pytest.raises(IntegrityError):
        service.save(Task(title="", description="", priority="medium"))
    assert list(session.scalars(select(Task))) == []
    assert service.create(TaskCreate(title="after rollback")).id is not None


def test_delete_rollback(session: Session) -> None:
    service = TaskService(session)
    task = service.create(TaskCreate(title="keep"))
    with patch.object(session, "commit", side_effect=RuntimeError("failure")):
        with pytest.raises(RuntimeError):
            service.delete(task.id)
    assert service.get(task.id).title == "keep"


def test_isolated_database(session: Session) -> None:
    assert list(session.scalars(select(Task))) == []
