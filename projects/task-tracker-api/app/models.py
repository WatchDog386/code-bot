from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Status(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Priority(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    project: str = Field(default="general", max_length=50)
    priority: Priority = Priority.MEDIUM
    due_date: Optional[date] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    project: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    due_date: Optional[date] = None


class Task(TaskBase):
    id: UUID = Field(default_factory=uuid4)
    status: Status = Status.TODO
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    @property
    def is_overdue(self) -> bool:
        if self.due_date is None or self.status == Status.DONE:
            return False
        return self.due_date < date.today()
