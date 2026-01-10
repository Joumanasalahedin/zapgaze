from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import datetime
import json

from app.db import models, database

router = APIRouter()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserSearchResult(BaseModel):
    user_id: int
    name: str
    birthdate: datetime.date


class SessionResult(BaseModel):
    session_uid: str
    started_at: Optional[datetime.datetime]
    stopped_at: Optional[datetime.datetime]
    status: str
    features: Optional[dict] = None
    intake: Optional[dict] = None


class UserResultsResponse(BaseModel):
    user_id: int
    user_name: str
    birthdate: datetime.date
    sessions: List[SessionResult]


@router.get("/search", summary="Search for users by name")
def search_users(
    name: str = Query(
        ..., min_length=1, description="Name to search for (partial match)"
    ),
    db: Session = Depends(get_db),
):
    """Search for users by name (case-insensitive partial match)."""

    if not name or len(name.strip()) == 0:
        raise HTTPException(
            status_code=400, detail="Name parameter is required and cannot be empty"
        )

    # Search for users with case-insensitive partial name match
    users = (
        db.query(models.User)
        .filter(models.User.name.ilike(f"%{name.strip()}%"))
        .order_by(models.User.name)
        .all()
    )

    if not users:
        return []

    return [
        UserSearchResult(user_id=user.id, name=user.name, birthdate=user.birthdate)
        for user in users
    ]


@router.get("/results", summary="Get all results for a user grouped by session")
def get_user_results(
    user_id: int = Query(..., description="User ID"),
    birthdate: datetime.date = Query(
        ..., description="User birthdate for verification"
    ),
    db: Session = Depends(get_db),
):
    """Get all results for a user, grouped by session. Requires birthdate verification."""

    # Verify user exists and birthdate matches
    user = (
        db.query(models.User)
        .filter(models.User.id == user_id, models.User.birthdate == birthdate)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found or birthdate does not match. Please check your user ID and birthdate.",
        )

    # Get all sessions for this user
    sessions = (
        db.query(models.Session)
        .filter(models.Session.user_id == user_id)
        .order_by(models.Session.started_at.desc())
        .all()
    )

    session_results = []

    for session in sessions:
        # Get features for this session
        features = (
            db.query(models.SessionFeatures)
            .filter(models.SessionFeatures.session_id == session.id)
            .first()
        )

        # Get intake for this session
        intake = (
            db.query(models.Intake)
            .filter(models.Intake.session_uid == session.session_uid)
            .first()
        )

        # Prepare features data
        features_data = None
        if features:
            features_data = {
                "mean_fixation_duration": features.mean_fixation_duration,
                "fixation_count": features.fixation_count,
                "gaze_dispersion": features.gaze_dispersion,
                "saccade_count": features.saccade_count,
                "saccade_rate": features.saccade_rate,
                "total_blinks": features.total_blinks,
                "blink_rate": features.blink_rate,
                "go_reaction_time_mean": features.go_reaction_time_mean,
                "go_reaction_time_sd": features.go_reaction_time_sd,
                "omission_errors": features.omission_errors,
                "commission_errors": features.commission_errors,
            }

        # Prepare intake data
        intake_data = None
        if intake:
            intake_data = {
                "total_score": intake.total_score,
                "symptom_group": intake.symptom_group,
                "answers": json.loads(intake.answers_json),
                "created_at": intake.created_at,
            }

        session_results.append(
            SessionResult(
                session_uid=session.session_uid,
                started_at=session.started_at,
                stopped_at=session.stopped_at,
                status=session.status,
                features=features_data,
                intake=intake_data,
            )
        )

    return UserResultsResponse(
        user_id=user.id,
        user_name=user.name,
        birthdate=user.birthdate,
        sessions=session_results,
    )
