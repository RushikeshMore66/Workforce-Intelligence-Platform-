from sqlalchemy.orm import Session
from app.schemas.analytics import (
    AnalyticsDataOut,
    TaskCompletionDataPoint,
    TeamWorkloadDataPoint,
    ProjectProgressDataPoint,
    WorkloadTrendPoint,
)


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_analytics_data(self) -> AnalyticsDataOut:
        return AnalyticsDataOut(
            task_completion=[
                TaskCompletionDataPoint(month="Mar", completed=18, in_progress=12, blocked=2),
                TaskCompletionDataPoint(month="Apr", completed=24, in_progress=15, blocked=3),
                TaskCompletionDataPoint(month="May", completed=29, in_progress=14, blocked=1),
                TaskCompletionDataPoint(month="Jun", completed=35, in_progress=18, blocked=4),
                TaskCompletionDataPoint(month="Jul", completed=42, in_progress=20, blocked=2),
                TaskCompletionDataPoint(month="Aug", completed=34, in_progress=18, blocked=4),
            ],
            team_workload=[
                TeamWorkloadDataPoint(team="Backend", tasks=36, completed=18, blocked=2),
                TeamWorkloadDataPoint(team="Frontend", tasks=28, completed=16, blocked=1),
                TeamWorkloadDataPoint(team="QA", tasks=20, completed=14, blocked=1),
                TeamWorkloadDataPoint(team="DevOps", tasks=14, completed=11, blocked=0),
                TeamWorkloadDataPoint(team="UI/UX", tasks=12, completed=9, blocked=0),
                TeamWorkloadDataPoint(team="Mobile", tasks=16, completed=10, blocked=0),
            ],
            project_progress=[
                ProjectProgressDataPoint(name="Hotel Billing", progress=76, target=70),
                ProjectProgressDataPoint(name="E-Commerce App", progress=62, target=75),
                ProjectProgressDataPoint(name="CRM Dev", progress=28, target=50),
                ProjectProgressDataPoint(name="Workflow Auto", progress=18, target=30),
                ProjectProgressDataPoint(name="Analytics v2", progress=88, target=85),
            ],
            workload_trend=[
                WorkloadTrendPoint(week="W1", backend=14, frontend=10, qa=6, devops=4, uiux=3),
                WorkloadTrendPoint(week="W2", backend=16, frontend=12, qa=8, devops=5, uiux=4),
                WorkloadTrendPoint(week="W3", backend=18, frontend=14, qa=10, devops=6, uiux=4),
                WorkloadTrendPoint(week="W4", backend=19, frontend=15, qa=11, devops=6, uiux=5),
                WorkloadTrendPoint(week="W5", backend=17, frontend=13, qa=9, devops=5, uiux=4),
                WorkloadTrendPoint(week="W6", backend=18, frontend=14, qa=10, devops=6, uiux=4),
                WorkloadTrendPoint(week="W7", backend=18, frontend=15, qa=12, devops=7, uiux=5),
            ],
        )
