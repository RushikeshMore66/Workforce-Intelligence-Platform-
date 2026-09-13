import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.user import User, UserRoleEnum, TeamLeader
from app.models.team import Team
from app.models.task import Task
from app.models.report_schedule import ReportSchedule, ReportTypeEnum, ReportFormatEnum, ReportFrequencyEnum
from app.models.report_run import ReportRun, ReportRunStatusEnum, TriggerTypeEnum


class TestDatabaseReliability:
    def test_duplicate_email_rejection(self, db_session):
        """Verify that attempting to insert a duplicate email raises IntegrityError and can be rolled back."""
        # Insert first user
        user1 = User(
            id=f"usr-{uuid.uuid4().hex[:6]}",
            name="Alice",
            email="duplicate@example.com",
            hashed_password="hash",
            role=UserRoleEnum.WORKER,
            avatar_initials="AB",
        )
        db_session.add(user1)
        db_session.commit()

        # Attempt to insert second user with same email
        user2 = User(
            id=f"usr-{uuid.uuid4().hex[:6]}",
            name="Bob",
            email="duplicate@example.com",
            hashed_password="hash",
            role=UserRoleEnum.WORKER,
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
            
        # Rollback the failed transaction so the session is usable again
        db_session.rollback()
        
        # Verify session is still usable by querying
        users = db_session.query(User).filter(User.email == "duplicate@example.com").all()
        assert len(users) == 1
        assert users[0].name == "Alice"

    def test_foreign_key_violation_handling(self, db_session):
        """Verify that foreign key constraints prevent invalid relations."""
        # Attempt to create a task pointing to a non-existent project
        task = Task(
            id=f"task-{uuid.uuid4().hex[:6]}",
            project_id="proj-does-not-exist",
            title="Invalid Task",
            description="Testing FK constraints",
        )
        db_session.add(task)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
            
        db_session.rollback()

    def test_duplicate_team_leader_assignment(self, db_session):
        """Verify the unique constraint on (user_id, team_id) for team leaders."""
        # Create team
        team = Team(id=f"team-{uuid.uuid4().hex[:6]}", name=f"Team {uuid.uuid4().hex[:6]}")
        db_session.add(team)
        
        # Create user
        leader_user = User(
            id=f"usr-{uuid.uuid4().hex[:6]}",
            name="Leader",
            email=f"leader-{uuid.uuid4().hex[:6]}@example.com",
            hashed_password="hash",
            role=UserRoleEnum.TEAM_LEADER,
            avatar_initials="LD",
        )
        db_session.add(leader_user)
        db_session.commit()

        # Assign leader to team
        leader_assignment1 = TeamLeader(
            id=f"tl-{uuid.uuid4().hex[:6]}",
            user_id=leader_user.id,
            team_id=team.id,
        )
        db_session.add(leader_assignment1)
        db_session.commit()

        # Attempt duplicate assignment
        leader_assignment2 = TeamLeader(
            id=f"tl-{uuid.uuid4().hex[:6]}",
            user_id=leader_user.id,
            team_id=team.id,
        )
        db_session.add(leader_assignment2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
            
        db_session.rollback()

    def test_duplicate_report_run_execution_key(self, db_session):
        """Verify that duplicate report runs are prevented by execution_key."""
        # Create schedule
        schedule = ReportSchedule(
            id=f"rs-{uuid.uuid4().hex[:6]}",
            name="Test Schedule",
            report_type=ReportTypeEnum.ORGANIZATION,
            export_format=ReportFormatEnum.CSV,
            frequency=ReportFrequencyEnum.DAILY,
            timezone="UTC",
            next_run_at=datetime.now(timezone.utc),
        )
        db_session.add(schedule)
        db_session.commit()

        run1 = ReportRun(
            id=f"rr-{uuid.uuid4().hex[:6]}",
            schedule_id=schedule.id,
            execution_key="unique-execution-key-123",
            status=ReportRunStatusEnum.RUNNING,
            trigger_type=TriggerTypeEnum.MANUAL,
        )
        db_session.add(run1)
        db_session.commit()

        run2 = ReportRun(
            id=f"rr-{uuid.uuid4().hex[:6]}",
            schedule_id=schedule.id,
            execution_key="unique-execution-key-123",
            status=ReportRunStatusEnum.RUNNING,
            trigger_type=TriggerTypeEnum.MANUAL,
        )
        db_session.add(run2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
            
        db_session.rollback()
