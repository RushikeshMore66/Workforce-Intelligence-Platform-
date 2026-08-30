from sqlalchemy import Column, String, ForeignKey, Table, Integer
from sqlalchemy.orm import relationship
from app.database import Base

# Association table for Team <-> Project many-to-many relationship
team_projects = Table(
    "team_projects",
    Base.metadata,
    Column("team_id", String, ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True),
    Column("project_id", String, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
)


class Team(Base):
    __tablename__ = "teams"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    supervisor_id = Column(String, ForeignKey("supervisors.id", ondelete="SET NULL"), nullable=True)
    team_leader_id = Column(String, ForeignKey("team_leaders.id", ondelete="SET NULL"), nullable=True)
    member_count = Column(Integer, default=0)

    supervisor = relationship("Supervisor", back_populates="teams")
    leader = relationship("TeamLeader", back_populates="team", foreign_keys=[team_leader_id])
    workers = relationship("Worker", back_populates="team", foreign_keys="Worker.team_id")
    projects = relationship("Project", secondary=team_projects, back_populates="teams")
