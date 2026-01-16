"""
Unit tests for acquisition API endpoints.
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import json

from app.db import models


def test_receive_acquisition_data(client: TestClient, db_session: Session):
    """Test receiving single acquisition data."""
    # Create session
    session = models.Session(session_uid="test-session-uid", user_id=None)
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)

    # Send acquisition data
    data = {
        "session_uid": "test-session-uid",
        "timestamp": 1234567890.0,
        "left_eye": {"x": 100.0, "y": 200.0},
        "right_eye": {"x": 105.0, "y": 205.0},
    }

    response = client.post("/acquisition/data", json=data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify data was stored
    result = db_session.query(models.Results).filter_by(session_id=session.id).first()
    assert result is not None
    stored_data = json.loads(result.data)
    assert stored_data["session_uid"] == "test-session-uid"
    assert stored_data["timestamp"] == 1234567890.0


def test_receive_acquisition_data_session_not_found(client: TestClient):
    """Test receiving acquisition data for non-existent session."""
    data = {
        "session_uid": "non-existent",
        "timestamp": 1234567890.0,
        "left_eye": {"x": 100.0, "y": 200.0},
        "right_eye": {"x": 105.0, "y": 205.0},
    }

    response = client.post("/acquisition/data", json=data)
    assert response.status_code == 404
    assert "Session not found" in response.json()["detail"]


def test_receive_acquisition_batch(client: TestClient, db_session: Session):
    """Test receiving batch acquisition data."""
    # Create session
    session = models.Session(session_uid="test-session-uid", user_id=None)
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)

    # Send batch data
    batch = [
        {
            "session_uid": "test-session-uid",
            "timestamp": 1234567890.0 + i,
            "left_eye": {"x": 100.0 + i, "y": 200.0 + i},
            "right_eye": {"x": 105.0 + i, "y": 205.0 + i},
        }
        for i in range(5)
    ]

    response = client.post("/acquisition/batch", json=batch)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["count"] == 5

    # Verify all records were stored
    results = (
        db_session.query(models.Results).filter_by(session_id=session.id).all()
    )
    assert len(results) == 5


def test_receive_acquisition_batch_mixed_sessions(client: TestClient, db_session: Session):
    """Test receiving batch with mixed sessions."""
    # Create two sessions
    session1 = models.Session(session_uid="session-1", user_id=None)
    session2 = models.Session(session_uid="session-2", user_id=None)
    db_session.add(session1)
    db_session.add(session2)
    db_session.commit()
    db_session.refresh(session1)
    db_session.refresh(session2)

    # Send batch with mixed sessions
    batch = [
        {
            "session_uid": "session-1",
            "timestamp": 1234567890.0,
            "left_eye": {"x": 100.0, "y": 200.0},
            "right_eye": {"x": 105.0, "y": 205.0},
        },
        {
            "session_uid": "session-2",
            "timestamp": 1234567891.0,
            "left_eye": {"x": 110.0, "y": 210.0},
            "right_eye": {"x": 115.0, "y": 215.0},
        },
    ]

    response = client.post("/acquisition/batch", json=batch)
    assert response.status_code == 200
    assert response.json()["count"] == 2

    # Verify records were stored for both sessions
    results1 = (
        db_session.query(models.Results).filter_by(session_id=session1.id).all()
    )
    results2 = (
        db_session.query(models.Results).filter_by(session_id=session2.id).all()
    )
    assert len(results1) == 1
    assert len(results2) == 1


def test_receive_acquisition_batch_invalid_session(client: TestClient, db_session: Session):
    """Test receiving batch with invalid session."""
    # Create one session
    session = models.Session(session_uid="session-1", user_id=None)
    db_session.add(session)
    db_session.commit()

    # Send batch with one invalid session
    batch = [
        {
            "session_uid": "session-1",
            "timestamp": 1234567890.0,
            "left_eye": {"x": 100.0, "y": 200.0},
            "right_eye": {"x": 105.0, "y": 205.0},
        },
        {
            "session_uid": "non-existent",
            "timestamp": 1234567891.0,
            "left_eye": {"x": 110.0, "y": 210.0},
            "right_eye": {"x": 115.0, "y": 215.0},
        },
    ]

    response = client.post("/acquisition/batch", json=batch)
    assert response.status_code == 404
    assert "Session not found" in response.json()["detail"]
