from app.routers.auth import router as auth_router
from app.routers.projects import router as projects_router
from app.routers.workers import router as workers_router
from app.routers.supervisors import router as supervisors_router
from app.routers.teams import router as teams_router
from app.routers.tasks import router as tasks_router
from app.routers.blockers import router as blockers_router
from app.routers.dashboard import router as dashboard_router
from app.routers.analytics import router as analytics_router
from app.routers.notifications import router as notifications_router
from app.routers.reports import router as reports_router
from app.routers.report_schedules import router as report_schedules_router

__all__ = [
    "auth_router",
    "projects_router",
    "workers_router",
    "supervisors_router",
    "teams_router",
    "tasks_router",
    "blockers_router",
    "dashboard_router",
    "analytics_router",
    "notifications_router",
    "reports_router",
    "report_schedules_router",
]
