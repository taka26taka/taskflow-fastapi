from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.task_service import TaskService


def get_session() -> Generator[Session]:
    with SessionLocal() as session:
        yield session


def get_service(session: Annotated[Session, Depends(get_session)]) -> TaskService:
    return TaskService(session)


Service = Annotated[TaskService, Depends(get_service)]
