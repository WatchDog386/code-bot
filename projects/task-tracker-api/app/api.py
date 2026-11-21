from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from .config import settings
from .models import Priority, Status, Task, TaskCreate, TaskUpdate
from .repository import InMemoryTaskRepository
from .services import TaskNotFound, TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])

_service = TaskService(InMemoryTaskRepository())


def get_service() -> TaskService:
    return _service


@router.get("", response_model=List[Task])
def list_tasks(
    project: Optional[str] = None,
    status_filter: Optional[Status] = Query(default=None, alias="status"),
    min_priority: Optional[Priority] = None,
    overdue: bool = False,
    limit: int = Query(default=settings.default_page_size, le=settings.max_page_size),
    offset: int = Query(default=0, ge=0),
    service: TaskService = Depends(get_service),
):
    tasks = service.search(project, status_filter, min_priority, overdue)
    return tasks[offset : offset + limit]


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, service: TaskService = Depends(get_service)):
    return service.create(data)


@router.get("/summary")
def task_summary(service: TaskService = Depends(get_service)):
    return service.summary()


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: UUID, service: TaskService = Depends(get_service)):
    try:
        return service.get(task_id)
    except TaskNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/{task_id}", response_model=Task)
def update_task(
    task_id: UUID, data: TaskUpdate, service: TaskService = Depends(get_service)
):
    try:
        return service.update(task_id, data)
    except TaskNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{task_id}/complete", response_model=Task)
def complete_task(task_id: UUID, service: TaskService = Depends(get_service)):
    try:
        return service.complete(task_id)
    except TaskNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID, service: TaskService = Depends(get_service)):
    try:
        service.delete(task_id)
    except TaskNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc))
