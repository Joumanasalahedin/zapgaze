"""
Unit tests for session API endpoints.
"""

import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import models


def test_session_start_without_uid(client: TestClient, db_session: Session):
    """Test starting a session without providing session_uid."""
    response = client.post("/session/start", json={})
    assert response.status_code == 200

    data = response.json()
    assert "session_uid" in data
    assert data["session_uid"] is not None

    # Verify session was created
    session = (
        db_session.query(models.Session)
        .filter_by(session_uid=data["session_uid"])
        .first()
    )
    assert session is not None
    assert session.user_id is None  # No user_id initially
    assert session.status == "active"


def test_session_start_with_existing_uid(client: TestClient, db_session: Session):
    """Test starting a session with an existing session_uid."""
    # Create a session first
    session_uid = "existing-session-uid"
    session = models.Session(session_uid=session_uid, user_id=None)
    db_session.add(session)
    db_session.commit()

    response = client.post("/session/start", json={"session_uid": session_uid})
    assert response.status_code == 200

    data = response.json()
    assert data["session_uid"] == session_uid


def test_session_start_with_nonexistent_uid(client: TestClient):
    """Test starting a session with a non-existent session_uid."""
    response = client.post("/session/start", json={"session_uid": "non-existent-uid"})
    assert response.status_code == 404
    assert "Session UID not found" in response.json()["detail"]


def test_session_stop(client: TestClient, db_session: Session):
    """Test stopping a session."""
    # Create an active session
    session_uid = "test-session-uid"
    session = models.Session(session_uid=session_uid, user_id=None, status="active")
    db_session.add(session)
    db_session.commit()

    response = client.post("/session/stop", json={"session_uid": session_uid})
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "session_stopped"
    assert data["session_uid"] == session_uid
    assert "stopped_at" in data

    # Verify session was updated
    db_session.refresh(session)
    assert session.status == "stopped"
    assert session.stopped_at is not None


def test_session_stop_nonexistent(client: TestClient):
    """Test stopping a non-existent session."""
    response = client.post("/session/stop", json={"session_uid": "non-existent"})
    assert response.status_code == 404
    assert "No active session found" in response.json()["detail"]


def test_session_stop_already_stopped(client: TestClient, db_session: Session):
    """Test stopping an already stopped session."""
    # Create a stopped session
    session_uid = "stopped-session-uid"
    session = models.Session(
        session_uid=session_uid,
        user_id=None,
        status="stopped",
        stopped_at=datetime.utcnow(),
    )
    db_session.add(session)
    db_session.commit()

    response = client.post("/session/stop", json={"session_uid": session_uid})
    assert response.status_code == 404
    assert "No active session found" in response.json()["detail"]


def test_session_stop_requires_session_uid(client: TestClient):
    """Test that stopping a session requires session_uid."""
    response = client.post("/session/stop", json={})
    assert response.status_code == 422  # Validation error
