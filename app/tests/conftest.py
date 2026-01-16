"""
Pytest configuration and shared fixtures for backend testing.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from app.main import app
from app.db.database import Base, SessionLocal

# Use in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def override_get_db():
    """Override get_db dependency to use test database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    """Create a test client for API testing with database dependency override."""
    # Override get_db dependency in all routers
    from app.api import intake, session, users, acquisition, features, calibration

    # Patch get_db for all routers
    app.dependency_overrides[intake.get_db] = override_get_db
    app.dependency_overrides[session.get_db] = override_get_db
    app.dependency_overrides[users.get_db] = override_get_db
    app.dependency_overrides[acquisition.get_db] = override_get_db
    app.dependency_overrides[features.get_db] = override_get_db
    if hasattr(calibration, "get_db"):
        app.dependency_overrides[calibration.get_db] = override_get_db

    yield TestClient(app)

    # Clean up overrides after test
    app.dependency_overrides.clear()
