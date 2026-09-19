"""
Idempotent seed script for the Workforce Intelligence Platform.

Run with: python seed.py

Creates realistic demo data covering all roles and workflows.
Safe to run multiple times — checks before inserting.
"""

import sys
import os
from datetime import date, datetime, timedelta

# Ensure the app package is importable
sys.path.insert(0, os.path.dirname(__file__))

import bcrypt
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models.user import User, UserRoleEnum, Supervisor, TeamLeader, Worker, WorkerStatusEnum
from app.models.team import Team
from app.models.project import Project, ProjectStatusEnum, ProjectHealthEnum, ProjectPriorityEnum
from app.models.task import Task, TaskStatusEnum, WorkUpdate, TaskTransition
from app.models.blocker import Blocker, BlockerStatusEnum
from app.models.activity import ProjectActivity, ActivityTypeEnum
from app.models.notification import Notification


PASSWORD = "WipDev2024!"
HASHED_PW = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt()).decode()

TODAY = date.today()
NOW = datetime.utcnow()


def h(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def exists(db: Session, model, **kwargs) -> bool:
    return db.query(model).filter_by(**kwargs).first() is not None


def seed(db: Session):
    print("Seeding users...")

    # ─────────────────────────────────────────────
    # USERS
    # ─────────────────────────────────────────────

    owner_user = None
    if not exists(db, User, email="owner@wip.dev"):
        owner_user = User(
            id="u-owner-1",
            email="owner@wip.dev",
            name="Rajesh Mehta",
            hashed_password=HASHED_PW,
            role=UserRoleEnum.OWNER,
            avatar_initials="RM",
            company="Apex Software Solutions",
        )
        db.add(owner_user)
    else:
        owner_user = db.query(User).filter_by(email="owner@wip.dev").first()

    sup1_user = None
    if not exists(db, User, email="supervisor1@wip.dev"):
        sup1_user = User(
            id="u-sup-1",
            email="supervisor1@wip.dev",
            name="Amit Sharma",
            hashed_password=HASHED_PW,
            role=UserRoleEnum.SUPERVISOR,
            avatar_initials="AS",
            company="Apex Software Solutions",
        )
        db.add(sup1_user)
    else:
        sup1_user = db.query(User).filter_by(email="supervisor1@wip.dev").first()

    sup2_user = None
    if not exists(db, User, email="supervisor2@wip.dev"):
        sup2_user = User(
            id="u-sup-2",
            email="supervisor2@wip.dev",
            name="Priya Deshmukh",
            hashed_password=HASHED_PW,
            role=UserRoleEnum.SUPERVISOR,
            avatar_initials="PD",
            company="Apex Software Solutions",
        )
        db.add(sup2_user)
    else:
        sup2_user = db.query(User).filter_by(email="supervisor2@wip.dev").first()

    tl1_user = None
    if not exists(db, User, email="teamleader1@wip.dev"):
        tl1_user = User(
            id="u-tl-1",
            email="teamleader1@wip.dev",
            name="Kiran Joshi",
            hashed_password=HASHED_PW,
            role=UserRoleEnum.TEAM_LEADER,
            avatar_initials="KJ",
            company="Apex Software Solutions",
        )
        db.add(tl1_user)
    else:
        tl1_user = db.query(User).filter_by(email="teamleader1@wip.dev").first()

    tl2_user = None
    if not exists(db, User, email="teamleader2@wip.dev"):
        tl2_user = User(
            id="u-tl-2",
            email="teamleader2@wip.dev",
            name="Sneha Patil",
            hashed_password=HASHED_PW,
            role=UserRoleEnum.TEAM_LEADER,
            avatar_initials="SP",
            company="Apex Software Solutions",
        )
        db.add(tl2_user)
    else:
        tl2_user = db.query(User).filter_by(email="teamleader2@wip.dev").first()

    w1_user = None
    if not exists(db, User, email="worker1@wip.dev"):
        w1_user = User(
            id="u-w-1",
            email="worker1@wip.dev",
            name="Rohan Verma",
            hashed_password=HASHED_PW,
            role=UserRoleEnum.WORKER,
            avatar_initials="RV",
            company="Apex Software Solutions",
        )
        db.add(w1_user)
    else:
        w1_user = db.query(User).filter_by(email="worker1@wip.dev").first()

    w2_user = None
    if not exists(db, User, email="worker2@wip.dev"):
        w2_user = User(
            id="u-w-2",
            email="worker2@wip.dev",
            name="Kavitha Nair",
            hashed_password=HASHED_PW,
            role=UserRoleEnum.WORKER,
            avatar_initials="KN",
            company="Apex Software Solutions",
        )
        db.add(w2_user)
    else:
        w2_user = db.query(User).filter_by(email="worker2@wip.dev").first()

    w3_user = None
    if not exists(db, User, email="worker3@wip.dev"):
        w3_user = User(
            id="u-w-3",
            email="worker3@wip.dev",
            name="Sunil Gupta",
            hashed_password=HASHED_PW,
            role=UserRoleEnum.WORKER,
            avatar_initials="SG",
            company="Apex Software Solutions",
        )
        db.add(w3_user)
    else:
        w3_user = db.query(User).filter_by(email="worker3@wip.dev").first()

    w4_user = None
    if not exists(db, User, email="worker4@wip.dev"):
        w4_user = User(
            id="u-w-4",
            email="worker4@wip.dev",
            name="Deepak Tiwari",
            hashed_password=HASHED_PW,
            role=UserRoleEnum.WORKER,
            avatar_initials="DT",
            company="Apex Software Solutions",
        )
        db.add(w4_user)
    else:
        w4_user = db.query(User).filter_by(email="worker4@wip.dev").first()

    db.flush()

    # ─────────────────────────────────────────────
    # SUPERVISOR PROFILES
    # ─────────────────────────────────────────────
    print("Seeding supervisor profiles...")

    sup1 = None
    if not exists(db, Supervisor, id="sup-1"):
        sup1 = Supervisor(id="sup-1", user_id=sup1_user.id)
        db.add(sup1)
    else:
        sup1 = db.query(Supervisor).filter_by(id="sup-1").first()

    sup2 = None
    if not exists(db, Supervisor, id="sup-2"):
        sup2 = Supervisor(id="sup-2", user_id=sup2_user.id)
        db.add(sup2)
    else:
        sup2 = db.query(Supervisor).filter_by(id="sup-2").first()

    db.flush()

    # ─────────────────────────────────────────────
    # TEAMS
    # ─────────────────────────────────────────────
    print("Seeding teams...")

    team1 = None
    if not exists(db, Team, id="team-1"):
        team1 = Team(id="team-1", name="Backend Engineering", supervisor_id="sup-1")
        db.add(team1)
    else:
        team1 = db.query(Team).filter_by(id="team-1").first()

    team2 = None
    if not exists(db, Team, id="team-2"):
        team2 = Team(id="team-2", name="Frontend Engineering", supervisor_id="sup-2")
        db.add(team2)
    else:
        team2 = db.query(Team).filter_by(id="team-2").first()

    db.flush()

    # ─────────────────────────────────────────────
    # TEAM LEADER PROFILES
    # ─────────────────────────────────────────────
    print("Seeding team leader profiles...")

    tl1 = None
    if not exists(db, TeamLeader, id="tl-1"):
        tl1 = TeamLeader(id="tl-1", user_id=tl1_user.id, team_id="team-1")
        db.add(tl1)
    else:
        tl1 = db.query(TeamLeader).filter_by(id="tl-1").first()

    tl2 = None
    if not exists(db, TeamLeader, id="tl-2"):
        tl2 = TeamLeader(id="tl-2", user_id=tl2_user.id, team_id="team-2")
        db.add(tl2)
    else:
        tl2 = db.query(TeamLeader).filter_by(id="tl-2").first()

    db.flush()

    # ─────────────────────────────────────────────
    # PROJECTS
    # ─────────────────────────────────────────────
    print("Seeding projects...")

    proj1 = None
    if not exists(db, Project, id="proj-1"):
        proj1 = Project(
            id="proj-1",
            name="Hotel Billing System",
            client="Grand Hospitality Group",
            description="A full-featured billing and invoicing system for hotel chains. Covers room billing, restaurant charges, conference room bookings, and multi-currency invoicing.",
            start_date=TODAY - timedelta(days=90),
            deadline=TODAY + timedelta(days=45),
            priority=ProjectPriorityEnum.HIGH,
            supervisor_id="sup-1",
            status=ProjectStatusEnum.ACTIVE,
            health=ProjectHealthEnum.ON_TRACK,
            progress=72,
        )
        db.add(proj1)
    else:
        proj1 = db.query(Project).filter_by(id="proj-1").first()

    proj2 = None
    if not exists(db, Project, id="proj-2"):
        proj2 = Project(
            id="proj-2",
            name="E-Commerce Mobile App",
            client="ShopEasy India",
            description="A React Native mobile app for iOS and Android enabling product browsing, cart management, payment integration, and real-time order tracking.",
            start_date=TODAY - timedelta(days=60),
            deadline=TODAY + timedelta(days=15),
            priority=ProjectPriorityEnum.CRITICAL,
            supervisor_id="sup-2",
            status=ProjectStatusEnum.ACTIVE,
            health=ProjectHealthEnum.AT_RISK,
            progress=62,
        )
        db.add(proj2)
    else:
        proj2 = db.query(Project).filter_by(id="proj-2").first()

    proj3 = None
    if not exists(db, Project, id="proj-3"):
        proj3 = Project(
            id="proj-3",
            name="CRM Development",
            client="TechCorp Solutions",
            description="Custom CRM system with lead management, pipeline tracking, email integration, automated follow-up sequences, and sales analytics dashboard.",
            start_date=TODAY - timedelta(days=120),
            deadline=TODAY + timedelta(days=30),
            priority=ProjectPriorityEnum.HIGH,
            supervisor_id="sup-1",
            status=ProjectStatusEnum.ACTIVE,
            health=ProjectHealthEnum.DELAYED,
            progress=28,
        )
        db.add(proj3)
    else:
        proj3 = db.query(Project).filter_by(id="proj-3").first()

    proj4 = None
    if not exists(db, Project, id="proj-4"):
        proj4 = Project(
            id="proj-4",
            name="Internal Analytics Dashboard",
            client="Apex Software Solutions (Internal)",
            description="Internal BI dashboard for tracking engineering team performance, project health, and delivery metrics.",
            start_date=TODAY - timedelta(days=30),
            deadline=TODAY + timedelta(days=120),
            priority=ProjectPriorityEnum.MEDIUM,
            supervisor_id="sup-1",
            status=ProjectStatusEnum.ACTIVE,
            health=ProjectHealthEnum.ON_TRACK,
            progress=20,
        )
        db.add(proj4)
    else:
        proj4 = db.query(Project).filter_by(id="proj-4").first()

    db.flush()

    # ─────────────────────────────────────────────
    # TEAM → PROJECT associations
    # ─────────────────────────────────────────────
    print("Seeding team-project links...")

    team1_obj = db.query(Team).filter_by(id="team-1").first()
    proj1_obj = db.query(Project).filter_by(id="proj-1").first()
    proj3_obj = db.query(Project).filter_by(id="proj-3").first()
    proj4_obj = db.query(Project).filter_by(id="proj-4").first()

    if proj1_obj and proj1_obj not in (team1_obj.projects or []):
        team1_obj.projects.append(proj1_obj)
    if proj3_obj and proj3_obj not in (team1_obj.projects or []):
        team1_obj.projects.append(proj3_obj)
    if proj4_obj and proj4_obj not in (team1_obj.projects or []):
        team1_obj.projects.append(proj4_obj)

    team2_obj = db.query(Team).filter_by(id="team-2").first()
    proj2_obj = db.query(Project).filter_by(id="proj-2").first()

    if proj2_obj and proj2_obj not in (team2_obj.projects or []):
        team2_obj.projects.append(proj2_obj)

    db.flush()

    # ─────────────────────────────────────────────
    # WORKER PROFILES
    # ─────────────────────────────────────────────
    print("Seeding worker profiles...")

    worker1 = None
    if not exists(db, Worker, id="w-1"):
        worker1 = Worker(
            id="w-1",
            user_id=w1_user.id,
            role="Senior Backend Developer",
            team_id="team-1",
            team_leader_id="tl-1",
            supervisor_id="sup-1",
            status=WorkerStatusEnum.ACTIVE,
            active_project_id="proj-1",
        )
        db.add(worker1)
    else:
        worker1 = db.query(Worker).filter_by(id="w-1").first()

    worker2 = None
    if not exists(db, Worker, id="w-2"):
        worker2 = Worker(
            id="w-2",
            user_id=w2_user.id,
            role="Backend Developer",
            team_id="team-1",
            team_leader_id="tl-1",
            supervisor_id="sup-1",
            status=WorkerStatusEnum.ACTIVE,
            active_project_id="proj-3",
        )
        db.add(worker2)
    else:
        worker2 = db.query(Worker).filter_by(id="w-2").first()

    worker3 = None
    if not exists(db, Worker, id="w-3"):
        worker3 = Worker(
            id="w-3",
            user_id=w3_user.id,
            role="Backend Developer",
            team_id="team-1",
            team_leader_id="tl-1",
            supervisor_id="sup-1",
            status=WorkerStatusEnum.ON_LEAVE,
            active_project_id=None,
        )
        db.add(worker3)
    else:
        worker3 = db.query(Worker).filter_by(id="w-3").first()

    worker4 = None
    if not exists(db, Worker, id="w-4"):
        worker4 = Worker(
            id="w-4",
            user_id=w4_user.id,
            role="Senior Frontend Developer",
            team_id="team-2",
            team_leader_id="tl-2",
            supervisor_id="sup-2",
            status=WorkerStatusEnum.ACTIVE,
            active_project_id="proj-2",
        )
        db.add(worker4)
    else:
        worker4 = db.query(Worker).filter_by(id="w-4").first()

    db.flush()

    # ─────────────────────────────────────────────
    # TASKS
    # ─────────────────────────────────────────────
    print("Seeding tasks...")

    tasks = [
        # proj-1: Hotel Billing (ON_TRACK, 72%)
        ("task-1", "proj-1", "Implement multi-currency invoice generation", "w-1", "team-1", TaskStatusEnum.COMPLETED, ProjectPriorityEnum.HIGH, TODAY - timedelta(days=10)),
        ("task-2", "proj-1", "Build room billing engine", "w-1", "team-1", TaskStatusEnum.COMPLETED, ProjectPriorityEnum.HIGH, TODAY - timedelta(days=20)),
        ("task-3", "proj-1", "Restaurant charge aggregation module", "w-2", "team-1", TaskStatusEnum.COMPLETED, ProjectPriorityEnum.MEDIUM, TODAY - timedelta(days=15)),
        ("task-4", "proj-1", "Conference room booking integration", "w-1", "team-1", TaskStatusEnum.IN_PROGRESS, ProjectPriorityEnum.MEDIUM, TODAY + timedelta(days=10)),
        ("task-5", "proj-1", "Payment gateway webhook handlers", "w-2", "team-1", TaskStatusEnum.TODO, ProjectPriorityEnum.HIGH, TODAY + timedelta(days=20)),
        ("task-6", "proj-1", "Performance load testing", "w-1", "team-1", TaskStatusEnum.TODO, ProjectPriorityEnum.LOW, TODAY + timedelta(days=30)),

        # proj-2: E-Commerce Mobile (AT_RISK, 62%, deadline in 15 days)
        ("task-7", "proj-2", "Product listing screen with filters", "w-4", "team-2", TaskStatusEnum.COMPLETED, ProjectPriorityEnum.HIGH, TODAY - timedelta(days=5)),
        ("task-8", "proj-2", "Shopping cart with persistent state", "w-4", "team-2", TaskStatusEnum.COMPLETED, ProjectPriorityEnum.HIGH, TODAY - timedelta(days=10)),
        ("task-9", "proj-2", "Razorpay payment integration", "w-4", "team-2", TaskStatusEnum.IN_PROGRESS, ProjectPriorityEnum.CRITICAL, TODAY + timedelta(days=5)),
        ("task-10", "proj-2", "Push notification setup", "w-4", "team-2", TaskStatusEnum.BLOCKED, ProjectPriorityEnum.HIGH, TODAY + timedelta(days=8)),
        ("task-11", "proj-2", "Order tracking real-time feed", "w-4", "team-2", TaskStatusEnum.TODO, ProjectPriorityEnum.MEDIUM, TODAY + timedelta(days=12)),

        # proj-3: CRM (DELAYED, 28%, 30 days deadline)
        ("task-12", "proj-3", "Lead management CRUD", "w-2", "team-1", TaskStatusEnum.COMPLETED, ProjectPriorityEnum.HIGH, TODAY - timedelta(days=30)),
        ("task-13", "proj-3", "Email sync integration", "w-2", "team-1", TaskStatusEnum.BLOCKED, ProjectPriorityEnum.CRITICAL, TODAY - timedelta(days=3)),
        ("task-14", "proj-3", "Sales pipeline Kanban board", "w-1", "team-1", TaskStatusEnum.IN_PROGRESS, ProjectPriorityEnum.HIGH, TODAY + timedelta(days=15)),
        ("task-15", "proj-3", "Automated follow-up scheduler", None, "team-1", TaskStatusEnum.TODO, ProjectPriorityEnum.MEDIUM, TODAY + timedelta(days=25)),

        # proj-4: Internal Dashboard (ON_TRACK, 20%)
        ("task-16", "proj-4", "Design metrics schema", "w-1", "team-1", TaskStatusEnum.COMPLETED, ProjectPriorityEnum.MEDIUM, TODAY - timedelta(days=5)),
        ("task-17", "proj-4", "Build aggregation service", "w-2", "team-1", TaskStatusEnum.IN_PROGRESS, ProjectPriorityEnum.MEDIUM, TODAY + timedelta(days=30)),
        ("task-18", "proj-4", "React dashboard components", None, "team-1", TaskStatusEnum.TODO, ProjectPriorityEnum.LOW, TODAY + timedelta(days=60)),
    ]

    for (tid, pid, title, assignee_id, team_id, status, priority, due) in tasks:
        if not exists(db, Task, id=tid):
            db.add(Task(
                id=tid,
                project_id=pid,
                title=title,
                assignee_id=assignee_id,
                team_id=team_id,
                status=status,
                priority=priority,
                due_date=due,
                created_at=NOW - timedelta(days=60),
                updated_at=NOW,
            ))

    db.flush()

    # ─────────────────────────────────────────────
    # BLOCKERS
    # ─────────────────────────────────────────────
    print("Seeding blockers...")

    if not exists(db, Blocker, id="blk-1"):
        db.add(Blocker(
            id="blk-1",
            project_id="proj-3",
            task_id="task-13",
            title="Client OAuth credentials not provided",
            description="Email sync integration (task-13) is blocked waiting for TechCorp Solutions to provide their Google Workspace OAuth 2.0 credentials. Escalated to account manager on " + (TODAY - timedelta(days=3)).strftime('%d %b %Y') + ".",
            reported_by_id=owner_user.id,
            team_id="team-1",
            created_date=TODAY - timedelta(days=3),
            status=BlockerStatusEnum.OPEN,
        ))

    if not exists(db, Blocker, id="blk-2"):
        db.add(Blocker(
            id="blk-2",
            project_id="proj-2",
            task_id="task-10",
            title="Firebase FCM project credentials missing",
            description="Push notification setup blocked — ShopEasy India has not yet shared Firebase project credentials. Cannot configure FCM sender ID or server key without client action.",
            reported_by_id=sup2_user.id,
            team_id="team-2",
            created_date=TODAY - timedelta(days=5),
            status=BlockerStatusEnum.OPEN,
        ))

    if not exists(db, Blocker, id="blk-3"):
        db.add(Blocker(
            id="blk-3",
            project_id="proj-1",
            task_id=None,
            title="Test database connection pool exhaustion in staging",
            description="Hotel Billing staging environment hit connection pool exhaustion during load testing. Root cause identified as missing connection timeout config. Fixed and resolved.",
            reported_by_id=sup1_user.id,
            team_id="team-1",
            created_date=TODAY - timedelta(days=20),
            resolved_date=TODAY - timedelta(days=18),
            status=BlockerStatusEnum.RESOLVED,
        ))

    db.flush()

    # ─────────────────────────────────────────────
    # WORK UPDATES
    # ─────────────────────────────────────────────
    print("Seeding work updates...")

    if not exists(db, WorkUpdate, id="wu-1"):
        db.add(WorkUpdate(
            id="wu-1",
            task_id="task-4",
            worker_id="w-1",
            created_by_user_id=w1_user.id,
            description="Conference room booking integration 70% complete. API contracts finalized with Grand Hospitality Group. Implementing SOAP to REST adapter layer today.",
            timestamp=NOW - timedelta(hours=4),
        ))

    if not exists(db, WorkUpdate, id="wu-2"):
        db.add(WorkUpdate(
            id="wu-2",
            task_id="task-9",
            worker_id="w-4",
            created_by_user_id=w4_user.id,
            description="Razorpay test environment configured. Payment flow working for cards. UPI integration in progress. Webhook signature verification implemented.",
            timestamp=NOW - timedelta(hours=8),
        ))

    if not exists(db, WorkUpdate, id="wu-3"):
        db.add(WorkUpdate(
            id="wu-3",
            task_id="task-14",
            worker_id="w-1",
            created_by_user_id=w1_user.id,
            description="Sales pipeline Kanban board backend APIs done. Frontend drag-and-drop integration starting Monday. On track to deliver by end of sprint.",
            timestamp=NOW - timedelta(days=1),
        ))

    db.flush()

    # ─────────────────────────────────────────────
    # TASK TRANSITIONS (for analytics)
    # ─────────────────────────────────────────────
    print("Seeding task transitions...")

    transitions = [
        ("tr-1", "task-1", None, TaskStatusEnum.TODO, owner_user.id, NOW - timedelta(days=60)),
        ("tr-2", "task-1", TaskStatusEnum.TODO, TaskStatusEnum.IN_PROGRESS, w1_user.id, NOW - timedelta(days=30)),
        ("tr-3", "task-1", TaskStatusEnum.IN_PROGRESS, TaskStatusEnum.COMPLETED, w1_user.id, NOW - timedelta(days=10)),
        ("tr-4", "task-2", None, TaskStatusEnum.TODO, owner_user.id, NOW - timedelta(days=60)),
        ("tr-5", "task-2", TaskStatusEnum.TODO, TaskStatusEnum.IN_PROGRESS, w1_user.id, NOW - timedelta(days=25)),
        ("tr-6", "task-2", TaskStatusEnum.IN_PROGRESS, TaskStatusEnum.COMPLETED, w1_user.id, NOW - timedelta(days=20)),
        ("tr-7", "task-12", None, TaskStatusEnum.TODO, owner_user.id, NOW - timedelta(days=60)),
        ("tr-8", "task-12", TaskStatusEnum.TODO, TaskStatusEnum.IN_PROGRESS, w2_user.id, NOW - timedelta(days=40)),
        ("tr-9", "task-12", TaskStatusEnum.IN_PROGRESS, TaskStatusEnum.COMPLETED, w2_user.id, NOW - timedelta(days=30)),
    ]

    for (tid, task_id, from_s, to_s, user_id, ts) in transitions:
        if not exists(db, TaskTransition, id=tid):
            db.add(TaskTransition(
                id=tid,
                task_id=task_id,
                from_status=from_s,
                to_status=to_s,
                changed_by_user_id=user_id,
                timestamp=ts,
            ))

    db.flush()

    # ─────────────────────────────────────────────
    # PROJECT ACTIVITIES
    # ─────────────────────────────────────────────
    print("Seeding project activities...")

    activities = [
        ("act-1", "proj-1", "Project Hotel Billing System created", owner_user.id, "Rajesh Mehta", ActivityTypeEnum.PROJECT_CREATED, NOW - timedelta(days=90)),
        ("act-2", "proj-1", "Assigned supervisor Amit Sharma to Hotel Billing System", owner_user.id, "Rajesh Mehta", ActivityTypeEnum.PROJECT_ASSIGNED, NOW - timedelta(days=89)),
        ("act-3", "proj-1", "Task 'Implement multi-currency invoice generation' marked COMPLETED", w1_user.id, "Rohan Verma", ActivityTypeEnum.TASK_COMPLETED, NOW - timedelta(days=10)),
        ("act-4", "proj-3", "Project CRM Development created", owner_user.id, "Rajesh Mehta", ActivityTypeEnum.PROJECT_CREATED, NOW - timedelta(days=120)),
        ("act-5", "proj-3", "Health status changed to DELAYED — progress at 28%", sup1_user.id, "Amit Sharma", ActivityTypeEnum.PROJECT_UPDATED, NOW - timedelta(days=5)),
        ("act-6", "proj-3", "Blocker reported: Client OAuth credentials not provided", owner_user.id, "Rajesh Mehta", ActivityTypeEnum.BLOCKER_REPORTED, NOW - timedelta(days=3)),
        ("act-7", "proj-2", "Project E-Commerce Mobile App created", owner_user.id, "Rajesh Mehta", ActivityTypeEnum.PROJECT_CREATED, NOW - timedelta(days=60)),
        ("act-8", "proj-2", "Health status changed to AT_RISK — deadline in 15 days", sup2_user.id, "Priya Deshmukh", ActivityTypeEnum.PROJECT_UPDATED, NOW - timedelta(days=2)),
        ("act-9", "proj-2", "Blocker reported: Firebase FCM credentials missing", sup2_user.id, "Priya Deshmukh", ActivityTypeEnum.BLOCKER_REPORTED, NOW - timedelta(days=5)),
        ("act-10", "proj-4", "Project Internal Analytics Dashboard created", owner_user.id, "Rajesh Mehta", ActivityTypeEnum.PROJECT_CREATED, NOW - timedelta(days=30)),
    ]

    for (aid, pid, desc, uid, uname, atype, ts) in activities:
        if not exists(db, ProjectActivity, id=aid):
            db.add(ProjectActivity(
                id=aid,
                project_id=pid,
                description=desc,
                user_id=uid,
                user_name=uname,
                timestamp=ts,
                type=atype,
            ))

    db.flush()

    # ─────────────────────────────────────────────
    # NOTIFICATIONS
    # ─────────────────────────────────────────────
    print("Seeding notifications...")

    from app.models.notification import Notification, NotificationTypeEnum, NotificationPriorityEnum

    notifs = [
        ("notif-1", owner_user.id, NotificationTypeEnum.BLOCKER, "New blocker on CRM Development", "Client OAuth credentials not provided is blocking email sync integration on CRM Development.", "proj-3", NotificationPriorityEnum.HIGH),
        ("notif-2", owner_user.id, NotificationTypeEnum.PROJECT_ALERT, "E-Commerce Mobile App is at risk", "The E-Commerce Mobile App deadline is in 15 days with 2 open blockers.", "proj-2", NotificationPriorityEnum.HIGH),
        ("notif-3", sup1_user.id, NotificationTypeEnum.PROJECT_ALERT, "CRM Development is DELAYED", "CRM Development project health is now DELAYED. Progress: 28%. Deadline in 30 days.", "proj-3", NotificationPriorityEnum.HIGH),
        ("notif-4", sup2_user.id, NotificationTypeEnum.BLOCKER, "New blocker on E-Commerce Mobile App", "Firebase FCM project credentials are missing, blocking push notification setup.", "proj-2", NotificationPriorityEnum.HIGH),
        ("notif-5", tl1_user.id, NotificationTypeEnum.TASK, "Task blocked: Email sync integration", "Email sync integration has been blocked for 3 days. Update required.", "proj-3", NotificationPriorityEnum.MEDIUM),
    ]

    for (nid, uid, ntype, title, description, pid, priority) in notifs:
        if not exists(db, Notification, id=nid):
            db.add(Notification(
                id=nid,
                user_id=uid,
                type=ntype,
                title=title,
                description=description,
                project_id=pid,
                read=False,
                timestamp=NOW - timedelta(hours=2),
                priority=priority,
            ))

    db.commit()
    print("\nSeed complete.")
    print(f"\nDemo accounts (password: {PASSWORD}):")
    print("  owner@wip.dev        → OWNER")
    print("  supervisor1@wip.dev  → SUPERVISOR (Backend team)")
    print("  supervisor2@wip.dev  → SUPERVISOR (Frontend team)")
    print("  teamleader1@wip.dev  → TEAM_LEADER (Backend Engineering)")
    print("  teamleader2@wip.dev  → TEAM_LEADER (Frontend Engineering)")
    print("  worker1@wip.dev      → WORKER (Rohan Verma)")
    print("  worker2@wip.dev      → WORKER (Kavitha Nair)")
    print("  worker3@wip.dev      → WORKER (Sunil Gupta, ON_LEAVE)")
    print("  worker4@wip.dev      → WORKER (Deepak Tiwari)")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    except Exception as e:
        db.rollback()
        print(f"\nSeed FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()
