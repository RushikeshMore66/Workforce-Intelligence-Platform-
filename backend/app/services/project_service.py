import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.project import Project, ProjectStatusEnum, ProjectHealthEnum, ProjectPriorityEnum
from app.models.activity import ProjectActivity, ActivityTypeEnum
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.repositories.project_repo import ProjectRepository
from app.core.exceptions import EntityNotFoundException


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProjectRepository(db)

    def get_projects(
        self,
        search: Optional[str] = None,
        status: Optional[ProjectStatusEnum] = None,
        health: Optional[ProjectHealthEnum] = None,
        priority: Optional[ProjectPriorityEnum] = None,
    ) -> List[Project]:
        return self.repo.filter_projects(
            search=search, status=status, health=health, priority=priority
        )

    def get_project(self, project_id: str) -> Project:
        proj = self.repo.get_by_id(project_id)
        if not proj:
            raise EntityNotFoundException("Project", project_id)
        return proj

    def create_project(self, project_in: ProjectCreate, current_user_name: str = "System") -> Project:
        project_dict = project_in.model_dump()
        project_id = f"proj-{uuid.uuid4().hex[:6]}"
        project_dict["id"] = project_id
        project_dict["status"] = ProjectStatusEnum.ACTIVE
        project_dict["health"] = ProjectHealthEnum.ON_TRACK
        project_dict["progress"] = 0

        project = self.repo.create(project_dict)

        # Log creation activity
        activity = ProjectActivity(
            id=f"act-{uuid.uuid4().hex[:6]}",
            project_id=project_id,
            description=f"Project '{project.name}' was created.",
            user_name=current_user_name,
            type=ActivityTypeEnum.PROJECT_UPDATED,
        )
        self.db.add(activity)
        self.db.commit()

        return project

    def update_project(self, project_id: str, update_in: ProjectUpdate) -> Project:
        proj = self.get_project(project_id)
        return self.repo.update(proj, update_in.model_dump(exclude_unset=True))
