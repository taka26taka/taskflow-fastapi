from fastapi import APIRouter, Response

from app.api.dependencies import Service
from app.repositories.task_repository import TaskSort, TaskStatus
from app.schemas.task import TaskCreate, TaskRead, TaskStats, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
def list_tasks(
    service: Service, status: TaskStatus = "all", sort: TaskSort = "created_at"
) -> object:
    return service.repository.list(status, sort)


@router.get("/stats", response_model=TaskStats)
def stats(service: Service) -> TaskStats:
    return service.repository.stats()


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, service: Service) -> object:
    return service.get(task_id)


@router.post("", response_model=TaskRead, status_code=201)
def create_task(data: TaskCreate, service: Service) -> object:
    return service.create(data)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, data: TaskUpdate, service: Service) -> object:
    return service.update(task_id, data)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, service: Service) -> Response:
    service.delete(task_id)
    return Response(status_code=204)
