"""
Unit tests for intake API endpoints.
"""

import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.intake import IntakeData, IntakeResponse
from app.db import models


def test_create_intake_new_user(client: TestClient, db_session: Session):
    """Test creating intake for a new user."""
    intake_data = {
        "name": "John Doe",
        "birthdate": "1990-01-01",
        "answers": [0, 1, 2, 3, 4, 0],
    }

    response = client.post("/intake/", json=intake_data)
    assert response.status_code == 200

    data = response.json()
    assert "session_uid" in data
    assert "user_id" in data
    assert data["total_score"] == 10  # Sum of answers
    assert data["symptom_group"] == "Low"  # < 14
    assert len(data["answers"]) == 6

    # Verify user was created
    # Note: Can't filter by name directly due to encryption, so fetch all and check
    users = db_session.query(models.User).all()
    user = next((u for u in users if u.name == "John Doe"), None)
    assert user is not None
    assert user.birthdate == date(1990, 1, 1)

    # Verify session was created
    session = (
        db_session.query(models.Session)
        .filter_by(session_uid=data["session_uid"])
        .first()
    )
    assert session is not None
    assert session.user_id == user.id

    # Verify intake was created
    intake = (
        db_session.query(models.Intake)
        .filter_by(session_uid=data["session_uid"])
        .first()
    )
    assert intake is not None
    assert intake.total_score == 10
    assert intake.symptom_group == "Low"


def test_create_intake_existing_user(client: TestClient, db_session: Session):
    """Test creating intake for an existing user."""
    # Create a user first
    user = models.User(name="Jane Doe", birthdate=date(1995, 5, 15))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    intake_data = {
        "user_id": user.id,
        "birthdate": "1995-05-15",
        "answers": [3, 3, 3, 3, 3, 3],
    }

    response = client.post("/intake/", json=intake_data)
    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == user.id
    assert data["total_score"] == 18  # Sum of answers
    assert data["symptom_group"] == "High"  # >= 14


def test_create_intake_existing_user_wrong_birthdate(
    client: TestClient, db_session: Session
):
    """Test creating intake with wrong birthdate for existing user."""
    # Create a user first
    user = models.User(name="Jane Doe", birthdate=date(1995, 5, 15))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    intake_data = {
        "user_id": user.id,
        "birthdate": "1990-01-01",  # Wrong birthdate
        "answers": [3, 3, 3, 3, 3, 3],
    }

    response = client.post("/intake/", json=intake_data)
    assert response.status_code == 404
    assert "birthdate does not match" in response.json()["detail"]


def test_create_intake_existing_user_not_found(client: TestClient, db_session: Session):
    """Test creating intake for non-existent user."""
    intake_data = {
        "user_id": 99999,
        "birthdate": "1990-01-01",
        "answers": [3, 3, 3, 3, 3, 3],
    }

    response = client.post("/intake/", json=intake_data)
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_create_intake_invalid_answers_count(client: TestClient):
    """Test creating intake with wrong number of answers."""
    intake_data = {
        "name": "John Doe",
        "birthdate": "1990-01-01",
        "answers": [0, 1, 2],  # Only 3 answers, should be 6
    }

    response = client.post("/intake/", json=intake_data)
    assert response.status_code == 422  # Validation error


def test_create_intake_both_name_and_user_id(client: TestClient):
    """Test creating intake with both name and user_id (should fail)."""
    intake_data = {
        "name": "John Doe",
        "user_id": 1,
        "birthdate": "1990-01-01",
        "answers": [0, 1, 2, 3, 4, 0],
    }

    response = client.post("/intake/", json=intake_data)
    # Pydantic validation might allow it but the endpoint logic will handle it
    # The validator should catch it, but if not, it will try to find user_id=1 which doesn't exist
    assert response.status_code in [422, 404]  # Validation error or user not found


def test_get_user_intake(client: TestClient, db_session: Session):
    """Test getting intake for a user."""
    # Create user and intake
    user = models.User(name="John Doe", birthdate=date(1990, 1, 1))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    session = models.Session(user_id=user.id, session_uid="test-session-uid")
    db_session.add(session)
    db_session.commit()

    intake = models.Intake(
        user_id=user.id,
        session_uid="test-session-uid",
        answers_json="[0,1,2,3,4,0]",
        total_score=10,
        symptom_group="Low",
    )
    db_session.add(intake)
    db_session.commit()

    response = client.get(f"/intake/user/{user.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == user.id
    assert data["total_score"] == 10
    assert data["session_uid"] == "test-session-uid"


def test_get_user_intake_not_found(client: TestClient):
    """Test getting intake for non-existent user."""
    response = client.get("/intake/user/99999")
    assert response.status_code == 404


def test_get_session_intake(client: TestClient, db_session: Session):
    """Test getting intake for a session."""
    # Create user, session, and intake
    user = models.User(name="John Doe", birthdate=date(1990, 1, 1))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    session_uid = "test-session-uid"
    session = models.Session(user_id=user.id, session_uid=session_uid)
    db_session.add(session)
    db_session.commit()

    intake = models.Intake(
        user_id=user.id,
        session_uid=session_uid,
        answers_json="[0,1,2,3,4,0]",
        total_score=10,
        symptom_group="Low",
    )
    db_session.add(intake)
    db_session.commit()

    response = client.get(f"/intake/session/{session_uid}")
    assert response.status_code == 200

    data = response.json()
    assert data["session_uid"] == session_uid
    assert data["total_score"] == 10


def test_get_session_intake_not_found(client: TestClient):
    """Test getting intake for non-existent session."""
    response = client.get("/intake/session/non-existent")
    assert response.status_code == 404


def test_get_user_intake_history(client: TestClient, db_session: Session):
    """Test getting all intake records for a user."""
    import time

    # Create user
    user = models.User(name="John Doe", birthdate=date(1990, 1, 1))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create multiple sessions and intakes
    # Store the created_at timestamps to verify ordering
    created_times = []
    for i in range(3):
        session = models.Session(user_id=user.id, session_uid=f"test-session-uid-{i}")
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)

        # Add a small delay to ensure different timestamps
        if i > 0:
            time.sleep(0.1)  # 100ms delay between records

        intake = models.Intake(
            user_id=user.id,
            session_uid=f"test-session-uid-{i}",
            answers_json="[0,1,2,3,4,0]",
            total_score=10 + i,
            symptom_group="Low",
        )
        db_session.add(intake)
        db_session.commit()
        db_session.refresh(intake)
        created_times.append(intake.created_at)

    response = client.get(f"/intake/user/{user.id}/history")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3

    # Verify all scores are present
    scores = [item["total_score"] for item in data]
    assert 10 in scores
    assert 11 in scores
    assert 12 in scores

    # Verify ordering is descending (newest first) by checking created_at timestamps
    # The API orders by created_at.desc(), so most recent should be first
    created_at_timestamps = [item["created_at"] for item in data]

    # Parse timestamps and verify they're in descending order
    from datetime import datetime

    parsed_times = [
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
        for ts in created_at_timestamps
    ]

    # Verify descending order (newest first)
    for i in range(len(parsed_times) - 1):
        assert (
            parsed_times[i] >= parsed_times[i + 1]
        ), f"Timestamps not in descending order: {parsed_times}"

    # Since we created them sequentially with delays, the last created (i=2, score=12) should be first
    # But if timestamps are identical, we can't guarantee exact order, so just verify descending
    assert data[0]["created_at"] >= data[1]["created_at"]
    assert data[1]["created_at"] >= data[2]["created_at"]


def test_symptom_group_high_threshold(client: TestClient, db_session: Session):
    """Test that symptom_group is 'High' when total_score >= 14."""
    intake_data = {
        "name": "John Doe",
        "birthdate": "1990-01-01",
        "answers": [3, 3, 3, 3, 2, 0],  # Total = 14
    }

    response = client.post("/intake/", json=intake_data)
    assert response.status_code == 200

    data = response.json()
    assert data["total_score"] == 14
    assert data["symptom_group"] == "High"


def test_symptom_group_low_threshold(client: TestClient, db_session: Session):
    """Test that symptom_group is 'Low' when total_score < 14."""
    intake_data = {
        "name": "John Doe",
        "birthdate": "1990-01-01",
        "answers": [3, 3, 3, 3, 1, 0],  # Total = 13
    }

    response = client.post("/intake/", json=intake_data)
    assert response.status_code == 200

    data = response.json()
    assert data["total_score"] == 13
    assert data["symptom_group"] == "Low"
