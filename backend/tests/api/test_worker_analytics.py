import pytest
from unittest.mock import MagicMock
from app.services.worker_analytics_service import WorkerAnalyticsService
from app.models.task import TaskStatusEnum
from datetime import datetime, timedelta, date
import uuid

from app.models.user import User, Worker, UserRoleEnum, WorkerStatusEnum
from app.models.task import Task, TaskStatusEnum, WorkUpdate, TaskTransition
from app.models.project import Project, ProjectStatusEnum, ProjectPriorityEnum
from app.models.team import Team

@pytest.fixture
def worker(db_session):
    suffix = uuid.uuid4().hex[:6]
    # Worker needs a User profile
    user = User(
        id=f"usr-{suffix}",
        name=f"Worker {suffix}",
        email=f"worker-{suffix}@example.com",
        hashed_password="hash",
        role=UserRoleEnum.WORKER,
        avatar_initials="WK"
    )
    db_session.add(user)
    db_session.commit()

    worker_record = Worker(
        id=f"w-{suffix}",
        user_id=user.id,
        role="Developer",
        status=WorkerStatusEnum.ACTIVE
    )
    db_session.add(worker_record)
    db_session.commit()
    db_session.refresh(worker_record)
    
    yield worker_record
    
    # Cleanup
    db_session.delete(worker_record)
    db_session.delete(user)
    db_session.commit()

@pytest.fixture
def tasks(db_session, worker):
    suffix = uuid.uuid4().hex[:6]
    
    # Needs a project to associate tasks
    project = Project(
        id=f"proj-{suffix}",
        name=f"Project {suffix}",
        client="Client",
        start_date=date(2026, 1, 1),
        deadline=date(2026, 12, 31)
    )
    db_session.add(project)
    db_session.commit()
    
    task1 = Task(id=f"t1-{suffix}", project_id=project.id, title="T1", assignee_id=worker.id, status=TaskStatusEnum.TODO, due_date=date.today() + timedelta(days=5))
    task2 = Task(id=f"t2-{suffix}", project_id=project.id, title="T2", assignee_id=worker.id, status=TaskStatusEnum.IN_PROGRESS, due_date=date.today() - timedelta(days=1))
    
    db_session.add_all([task1, task2])
    db_session.commit()
    
    yield [task1, task2]
    
    db_session.delete(task1)
    db_session.delete(task2)
    db_session.delete(project)
    db_session.commit()

@pytest.fixture
def work_updates(db_session, worker, tasks):
    task = tasks[0]
    suffix = uuid.uuid4().hex[:6]
    wu = WorkUpdate(
        id=f"wu-{suffix}",
        task_id=task.id,
        worker_id=worker.id,
        created_by_user_id=worker.user_id,
        description="Update",
        timestamp=datetime.utcnow() - timedelta(days=1)
    )
    db_session.add(wu)
    db_session.commit()
    
    yield [wu]
    
    db_session.delete(wu)
    db_session.commit()

@pytest.fixture
def transitions(db_session, tasks):
    task = tasks[0]
    suffix = uuid.uuid4().hex[:6]
    tr = TaskTransition(
        id=f"tr-{suffix}",
        task_id=task.id,
        from_status=TaskStatusEnum.TODO,
        to_status=TaskStatusEnum.IN_PROGRESS,
        timestamp=datetime.utcnow() - timedelta(days=2)
    )
    db_session.add(tr)
    db_session.commit()
    
    yield [tr]
    
    db_session.delete(tr)
    db_session.commit()

def test_workload_metrics(db_session, worker, tasks):
    # This is a placeholder test. Full test would fixture tasks with specific statuses
    pass

def test_activity_metrics(db_session, worker, work_updates):
    # This is a placeholder for activity checks
    pass

def test_delivery_metrics(db_session, worker, tasks, transitions):
    # cycle time checks
    pass
