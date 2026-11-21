from abc import ABC, abstractmethod
from threading import Lock
from typing import Dict, Iterable, List, Optional
from uuid import UUID

from .models import Task


class TaskRepository(ABC):
    @abstractmethod
    def add(self, task: Task) -> Task: ...

    @abstractmethod
    def get(self, task_id: UUID) -> Optional[Task]: ...

    @abstractmethod
    def list(self) -> List[Task]: ...

    @abstractmethod
    def save(self, task: Task) -> Task: ...

    @abstractmethod
    def delete(self, task_id: UUID) -> bool: ...


class InMemoryTaskRepository(TaskRepository):
    def __init__(self, seed: Iterable[Task] = ()):
        self._items: Dict[UUID, Task] = {t.id: t for t in seed}
        self._lock = Lock()

    def add(self, task: Task) -> Task:
        with self._lock:
            self._items[task.id] = task
        return task

    def get(self, task_id: UUID) -> Optional[Task]:
        return self._items.get(task_id)

    def list(self) -> List[Task]:
        return sorted(self._items.values(), key=lambda t: t.created_at)

    def save(self, task: Task) -> Task:
        with self._lock:
            if task.id not in self._items:
                raise KeyError(task.id)
            self._items[task.id] = task
        return task

    def delete(self, task_id: UUID) -> bool:
        with self._lock:
            return self._items.pop(task_id, None) is not None
