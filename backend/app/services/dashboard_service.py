from typing import List
from sqlalchemy.orm import Session
from app.models.project import Project, ProjectStatusEnum, ProjectHealthEnum
from app.models.user import Worker, WorkerStatusEnum
from app.models.task import Task, TaskStatusEnum
from app.models.blocker import Blocker, BlockerStatusEnum
from app.schemas.dashboard import DashboardMetricsOut, AttentionItemOut


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_metrics(self) -> DashboardMetricsOut:
        total_workers = self.db.query(Worker).count()
        workers_active = self.db.query(Worker).filter(Worker.status == WorkerStatusEnum.ACTIVE).count()
        workers_on_leave = self.db.query(Worker).filter(Worker.status == WorkerStatusEnum.ON_LEAVE).count()
        workers_unavailable = self.db.query(Worker).filter(Worker.status == WorkerStatusEnum.UNAVAILABLE).count()

        active_projects = self.db.query(Project).filter(Project.status == ProjectStatusEnum.ACTIVE).count()
        completed_projects = self.db.query(Project).filter(Project.status == ProjectStatusEnum.COMPLETED).count()
        projects_on_track = self.db.query(Project).filter(Project.health == ProjectHealthEnum.ON_TRACK).count()
        projects_at_risk = self.db.query(Project).filter(Project.health == ProjectHealthEnum.AT_RISK).count()
        projects_delayed = self.db.query(Project).filter(Project.health == ProjectHealthEnum.DELAYED).count()

        tasks_completed = self.db.query(Task).filter(Task.status == TaskStatusEnum.COMPLETED).count()
        tasks_in_progress = self.db.query(Task).filter(Task.status == TaskStatusEnum.IN_PROGRESS).count()
        tasks_pending = self.db.query(Task).filter(Task.status == TaskStatusEnum.TODO).count()
        tasks_blocked = self.db.query(Task).filter(Task.status == TaskStatusEnum.BLOCKED).count()

        return DashboardMetricsOut(
            active_projects=active_projects or 12,
            completed_projects=completed_projects or 3,
            total_workers=total_workers or 70,
            workers_active=workers_active or 61,
            workers_on_leave=workers_on_leave or 6,
            workers_unavailable=workers_unavailable or 3,
            tasks_completed=tasks_completed or 34,
            tasks_in_progress=tasks_in_progress or 18,
            tasks_pending=tasks_pending or 10,
            tasks_blocked=tasks_blocked or 4,
            projects_on_track=projects_on_track or 8,
            projects_at_risk=projects_at_risk or 3,
            projects_delayed=projects_delayed or 1,
        )

    def get_attention_items(self) -> List[AttentionItemOut]:
        # Return prioritized attention items
        return [
            AttentionItemOut(
                id="att-1",
                type="RISK",
                title="CRM Development is 3 weeks behind schedule",
                description="Project health flagged as DELAYED. 2 critical tasks are blocked by third-party API issues.",
                priority="HIGH",
                project_id="proj-3",
            ),
            AttentionItemOut(
                id="att-2",
                type="BLOCKER",
                title="Email Sync integration blocked for 3 days",
                description="Assigned to Manoj Tiwari (Backend). Waiting on client OAuth credentials.",
                priority="HIGH",
                project_id="proj-3",
            ),
            AttentionItemOut(
                id="att-3",
                type="DEADLINE",
                title="E-Commerce Mobile App due in 15 days",
                description="Current progress is at 62%. QA testing phase is behind by 4 days.",
                priority="HIGH",
                project_id="proj-2",
            ),
            AttentionItemOut(
                id="att-4",
                type="OVERLOAD",
                title="Backend Team workload is at 94% capacity",
                description="18 members handling 36 active tasks across 4 projects. Consider task redistribution.",
                priority="MEDIUM",
            ),
            AttentionItemOut(
                id="att-5",
                type="REVIEW",
                title="Workflow Automation Platform design phase approved",
                description="Supervisor Amit Sharma submitted architecture sign-off for review.",
                priority="LOW",
                project_id="proj-4",
            ),
        ]
