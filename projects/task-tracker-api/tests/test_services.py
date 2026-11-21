from datetime import date, timedelta

import pytest

from app.models import Priority, Status, TaskCreate, TaskUpdate
from app.repository import InMemoryTaskRepository
from app.services import TaskNotFound, TaskService


@pytest.fixture
def service():
    return TaskService(InMemoryTaskRepository())


def test_create_and_get(service):
    task = service.create(TaskCreate(title="Write docs", project="api"))
    assert service.get(task.id).title == "Write docs"
    assert task.status == Status.TODO


def test_complete_sets_timestamp(service):
    task = service.create(TaskCreate(title="Ship release"))
    done = service.complete(task.id)
    assert done.status == Status.DONE
    assert done.completed_at is not None


def test_update_partial_fields(service):
    task = service.create(TaskCreate(title="Old title", priority=Priority.LOW))
    updated = service.update(task.id, TaskUpdate(title="New title"))
    assert updated.title == "New title"
    assert updated.priority == Priority.LOW


def test_search_orders_by_priority(service):
    service.create(TaskCreate(title="low", priority=Priority.LOW))
    service.create(TaskCreate(title="urgent", priority=Priority.URGENT))
    service.create(TaskCreate(title="medium"))
    titles = [t.title for t in service.search()]
    assert titles == ["urgent", "medium", "low"]


def test_overdue_filter(service):
    yesterday = date.today() - timedelta(days=1)
    service.create(TaskCreate(title="late", due_date=yesterday))
    service.create(TaskCreate(title="fine"))
    overdue = service.search(overdue_only=True)
    assert [t.title for t in overdue] == ["late"]


def test_missing_task_raises(service):
    task = service.create(TaskCreate(title="temp"))
    service.delete(task.id)
    with pytest.raises(TaskNotFound):
        service.get(task.id)
