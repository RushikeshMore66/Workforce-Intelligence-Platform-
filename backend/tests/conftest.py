"""
Shared pytest fixtures for the Workforce Intelligence Platform backend tests.

The test environment uses SQLite in-memory for speed and isolation.
Passwords are stored as a plain sha256 hex for test users ONLY to avoid
a known passlib/bcrypt incompatibility with Python 3.11's bundled bcrypt
(see: https://foss.heptapod.net/python-libs/passlib/-/issues/187).
The production get_password_hash (bcrypt) remains unchanged.
"""

import hashlib
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRoleEnum
from app.core.security import get_password_hash

# In-memory SQLite for fast, isolated testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)





@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Seed owner user with test-safe hash
    owner = User(
        id="usr-test-owner",
        name="Rajesh Mehta",
        email="rajesh.mehta@apexsoftware.in",
        hashed_password=get_password_hash("password123"),
        role=UserRoleEnum.OWNER,
        company="Apex Software Solutions",
        avatar_initials="RM",
    )
    db.add(owner)
    db.commit()
    db.close()

    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
