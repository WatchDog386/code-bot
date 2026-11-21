from datetime import datetime
from typing import List, Optional
from uuid import UUID

from .models import Priority, Status, Task, TaskCreate, TaskUpdate
from .repository import TaskRepository


class TaskNotFound(Exception):
    def __init__(self, task_id: UUID):
        super().__init__(f"Task {task_id} not found")
        self.task_id = task_id


class TaskService:
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def create(self, data: TaskCreate) -> Task:
        task = Task(**data.model_dump())
        return self.repo.add(task)

    def get(self, task_id: UUID) -> Task:
        task = self.repo.get(task_id)
        if task is None:
            raise TaskNotFound(task_id)
        return task

    def update(self, task_id: UUID, data: TaskUpdate) -> Task:
        task = self.get(task_id)
        changes = data.model_dump(exclude_unset=True)
        updated = task.model_copy(update=changes)
        if changes.get("status") == Status.DONE and task.status != Status.DONE:
            updated.completed_at = datetime.utcnow()
        return self.repo.save(updated)

    def complete(self, task_id: UUID) -> Task:
        return self.update(task_id, TaskUpdate(status=Status.DONE))

    def delete(self, task_id: UUID) -> None:
        if not self.repo.delete(task_id):
            raise TaskNotFound(task_id)

    def search(
        self,
        project: Optional[str] = None,
        status: Optional[Status] = None,
        min_priority: Optional[Priority] = None,
        overdue_only: bool = False,
    ) -> List[Task]:
        tasks = self.repo.list()
        if project:
            tasks = [t for t in tasks if t.project == project]
        if status:
            tasks = [t for t in tasks if t.status == status]
        if min_priority:
            tasks = [t for t in tasks if t.priority >= min_priority]
        if overdue_only:
            tasks = [t for t in tasks if t.is_overdue]
        return sorted(tasks, key=lambda t: (-t.priority, t.created_at))

    def summary(self) -> dict:
        tasks = self.repo.list()
        by_status = {s.value: 0 for s in Status}
        for task in tasks:
            by_status[task.status.value] += 1
        return {
            "total": len(tasks),
            "by_status": by_status,
            "overdue": sum(1 for t in tasks if t.is_overdue),
        }
