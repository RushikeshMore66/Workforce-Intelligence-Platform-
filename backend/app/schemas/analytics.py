from typing import List
from app.schemas.common import BaseSchema


class TaskCompletionDataPoint(BaseSchema):
    month: str
    completed: int
    in_progress: int
    blocked: int


class TeamWorkloadDataPoint(BaseSchema):
    team: str
    tasks: int
    completed: int
    blocked: int


class ProjectProgressDataPoint(BaseSchema):
    name: str
    progress: int
    target: int


class WorkloadTrendPoint(BaseSchema):
    week: str
    backend: int
    frontend: int
    qa: int
    devops: int
    uiux: int


class AnalyticsDataOut(BaseSchema):
    task_completion: List[TaskCompletionDataPoint]
    team_workload: List[TeamWorkloadDataPoint]
    project_progress: List[ProjectProgressDataPoint]
    workload_trend: List[WorkloadTrendPoint]
