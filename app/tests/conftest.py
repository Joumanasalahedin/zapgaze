"""
Pytest configuration and shared fixtures for backend testing.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Set test database URL and encryption key before importing app modules
# Use PostgreSQL test database
# Default: Try to use Docker Compose postgres if available, otherwise localhost
# You can override with TEST_DATABASE_URL environment variable
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    # Try Docker Compose postgres first (if running), fallback to localhost
    os.getenv(
        "DATABASE_URL",  # Use same as main app if available
        "postgresql://zapgaze_user:zapgaze_password@localhost:5432/zapgaze_test",
    ),
)

# Set DATABASE_URL for the app to use during tests
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

# Set encryption key for tests (required for User model encryption)
# Generate a valid Fernet key for testing if not already set
if "ENCRYPTION_KEY" not in os.environ:
    try:
        # Try to generate a valid Fernet key (cryptography should be installed)
        from cryptography.fernet import Fernet

        test_key = Fernet.generate_key().decode()
        os.environ["ENCRYPTION_KEY"] = test_key
    except (ImportError, Exception) as e:
        # If cryptography is not available or generation fails, raise a clear error
        raise RuntimeError(
            f"Failed to generate test encryption key: {e}\n"
            "Please ensure 'cryptography' is installed (pip install cryptography)\n"
            "Or set ENCRYPTION_KEY environment variable with a valid Fernet key:\n"
            '  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        )

from app.main import app
from app.db.database import Base, SessionLocal

# Create test engine
# For PostgreSQL, use NullPool (no connection pooling) to avoid transaction issues
# StaticPool doesn't work well with PostgreSQL's transaction handling
engine = create_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,  # No pooling for tests - each connection is fresh
    echo=False,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()  # Commit any pending changes
    except Exception:
        db.rollback()  # Rollback on error
        raise
    finally:
        db.close()
        # Drop all tables to clean up (in a separate connection)
        # This ensures clean state for each test
        with engine.connect() as conn:
            Base.metadata.drop_all(bind=conn)
            conn.commit()


def override_get_db():
    """Override get_db dependency to use test database."""
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()  # Commit any pending changes
    except Exception:
        db.rollback()  # Rollback on error
        raise
    finally:
        db.close()


def verify_api_key_always_pass(api_key=None):
    """Mock API key verification that always passes for tests."""
    return api_key or "test-api-key"


@pytest.fixture
def client(db_session):
    """Create a test client for API testing with database dependency override."""
    # Override get_db dependency in all routers
    from app.api import intake, session, users, acquisition, features, calibration
    from app.security import verify_frontend_api_key, verify_agent_api_key

    # Patch get_db for all routers
    app.dependency_overrides[intake.get_db] = override_get_db
    app.dependency_overrides[session.get_db] = override_get_db
    app.dependency_overrides[users.get_db] = override_get_db
    app.dependency_overrides[acquisition.get_db] = override_get_db
    app.dependency_overrides[features.get_db] = override_get_db
    if hasattr(calibration, "get_db"):
        app.dependency_overrides[calibration.get_db] = override_get_db

    # Override API key verification to always pass in tests
    app.dependency_overrides[verify_frontend_api_key] = verify_api_key_always_pass
    app.dependency_overrides[verify_agent_api_key] = verify_api_key_always_pass

    # Create test client
    test_client = TestClient(app)

    yield test_client

    # Clean up overrides after test
    app.dependency_overrides.clear()
