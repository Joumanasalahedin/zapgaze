"""
Unit tests for users API endpoints.
"""

import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import json

from app.db import models


def test_search_users(client: TestClient, db_session: Session):
    """Test searching for users by name."""
    # Create some users
    users = [
        models.User(name="John Doe", birthdate=date(1990, 1, 1)),
        models.User(name="Jane Smith", birthdate=date(1995, 5, 15)),
        models.User(name="Johnny Appleseed", birthdate=date(1985, 3, 20)),
    ]
    for user in users:
        db_session.add(user)
    db_session.commit()

    # Search for "John"
    response = client.get("/users/search?name=John")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2  # John Doe and Johnny Appleseed
    assert all("John" in user["name"] for user in data)


def test_search_users_case_insensitive(client: TestClient, db_session: Session):
    """Test that user search is case-insensitive."""
    user = models.User(name="John Doe", birthdate=date(1990, 1, 1))
    db_session.add(user)
    db_session.commit()

    # Search with lowercase
    response = client.get("/users/search?name=john")
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Search with uppercase
    response = client.get("/users/search?name=JOHN")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_users_partial_match(client: TestClient, db_session: Session):
    """Test that user search supports partial matching."""
    user = models.User(name="John Doe", birthdate=date(1990, 1, 1))
    db_session.add(user)
    db_session.commit()

    # Search with partial name
    response = client.get("/users/search?name=oh")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_users_no_results(client: TestClient):
    """Test searching for users that don't exist."""
    response = client.get("/users/search?name=Nonexistent")
    assert response.status_code == 200
    assert response.json() == []


def test_search_users_empty_name(client: TestClient):
    """Test searching with empty name."""
    response = client.get("/users/search?name=")
    # FastAPI returns 422 for validation errors (empty query param)
    assert response.status_code in [400, 422]
    # The endpoint might handle empty strings differently
    if response.status_code == 422:
        # Validation error from FastAPI
        assert "detail" in response.json()
    else:
        # Custom validation error from endpoint
        assert "cannot be empty" in response.json()["detail"]


def test_get_user_results(client: TestClient, db_session: Session):
    """Test getting all results for a user."""
    # Create user
    user = models.User(name="John Doe", birthdate=date(1990, 1, 1))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create sessions
    session1 = models.Session(
        user_id=user.id, session_uid="session-1", status="stopped"
    )
    session2 = models.Session(
        user_id=user.id, session_uid="session-2", status="stopped"
    )
    db_session.add(session1)
    db_session.add(session2)
    db_session.commit()
    db_session.refresh(session1)
    db_session.refresh(session2)

    # Create intake for session1
    intake1 = models.Intake(
        user_id=user.id,
        session_uid="session-1",
        answers_json="[0,1,2,3,4,0]",
        total_score=10,
        symptom_group="Low",
    )
    db_session.add(intake1)
    db_session.commit()

    # Create features for session1
    features1 = models.SessionFeatures(
        session_id=session1.id,
        user_id=user.id,
        mean_fixation_duration=200.0,
        fixation_count=50,
        gaze_dispersion=45.0,
    )
    db_session.add(features1)
    db_session.commit()

    response = client.get(f"/users/results?user_id={user.id}&birthdate=1990-01-01")
    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == user.id
    assert data["user_name"] == "John Doe"
    assert len(data["sessions"]) == 2

    # Check that session1 has features and intake
    session1_data = next(s for s in data["sessions"] if s["session_uid"] == "session-1")
    assert session1_data["features"] is not None
    assert session1_data["intake"] is not None
    assert session1_data["features"]["mean_fixation_duration"] == 200.0
    assert session1_data["intake"]["total_score"] == 10


def test_get_user_results_wrong_birthdate(client: TestClient, db_session: Session):
    """Test getting user results with wrong birthdate."""
    user = models.User(name="John Doe", birthdate=date(1990, 1, 1))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    response = client.get(f"/users/results?user_id={user.id}&birthdate=1995-01-01")
    assert response.status_code == 404
    assert "birthdate does not match" in response.json()["detail"]


def test_get_user_results_user_not_found(client: TestClient):
    """Test getting results for non-existent user."""
    response = client.get("/users/results?user_id=99999&birthdate=1990-01-01")
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_get_user_results_no_sessions(client: TestClient, db_session: Session):
    """Test getting results for user with no sessions."""
    user = models.User(name="John Doe", birthdate=date(1990, 1, 1))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    response = client.get(f"/users/results?user_id={user.id}&birthdate=1990-01-01")
    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == user.id
    assert len(data["sessions"]) == 0
