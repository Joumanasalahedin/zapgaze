"""
GDPR compliance endpoints - Right to Deletion (Article 17).

This module implements the GDPR right to deletion, allowing users to request
deletion of all their personal data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import datetime

from app.db import models, database
from app.security import verify_frontend_api_key

router = APIRouter()

# Initialize rate limiter for GDPR endpoints
limiter = Limiter(key_func=get_remote_address)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DeleteUserRequest(BaseModel):
    """Request model for user deletion."""

    user_id: int
    birthdate: datetime.date  # Required for verification


class DeleteUserResponse(BaseModel):
    """Response model for user deletion."""

    status: str
    message: str
    deleted_user_id: int
    deleted_sessions: int
    deleted_intakes: int
    deleted_results: int
    deleted_events: int
    deleted_calibration_points: int
    deleted_features: int


@router.delete("/delete-user", summary="Delete all user data (GDPR Right to Deletion)")
@limiter.limit("10/minute")  # Limit deletion requests to prevent abuse
def delete_user_data(
    request: Request,
    user_id: int = Query(..., description="User ID to delete"),
    birthdate: datetime.date = Query(
        ..., description="User birthdate for verification"
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_frontend_api_key),
):
    """
    Delete all data for a user (GDPR Article 17 - Right to Deletion).

    This endpoint permanently deletes:
    - User record
    - All sessions
    - All intake records
    - All results/eye-tracking data
    - All task events
    - All calibration points
    - All session features

    Requires birthdate verification for security.
    """
    # Verify user exists and birthdate matches
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Verify birthdate matches
    if user.birthdate != birthdate:
        raise HTTPException(
            status_code=403,
            detail="Birthdate does not match. Deletion request denied for security.",
        )

    # Get counts before deletion for response
    sessions = db.query(models.Session).filter(models.Session.user_id == user_id).all()
    session_ids = [s.id for s in sessions]

    intakes_count = (
        db.query(models.Intake).filter(models.Intake.user_id == user_id).count()
    )

    # Count related data
    results_count = 0
    events_count = 0
    calibration_count = 0
    features_count = 0

    if session_ids:
        results_count = (
            db.query(models.Results)
            .filter(models.Results.session_id.in_(session_ids))
            .count()
        )

        events_count = (
            db.query(models.TaskEvent)
            .filter(models.TaskEvent.session_id.in_(session_ids))
            .count()
        )

        calibration_count = (
            db.query(models.CalibrationPoint)
            .filter(models.CalibrationPoint.session_id.in_(session_ids))
            .count()
        )

        features_count = (
            db.query(models.SessionFeatures)
            .filter(models.SessionFeatures.session_id.in_(session_ids))
            .count()
        )

    # Delete in order (respecting foreign key constraints)
    try:
        # 1. Delete session features
        if session_ids:
            db.query(models.SessionFeatures).filter(
                models.SessionFeatures.session_id.in_(session_ids)
            ).delete(synchronize_session=False)

        # 2. Delete results
        if session_ids:
            db.query(models.Results).filter(
                models.Results.session_id.in_(session_ids)
            ).delete(synchronize_session=False)

        # 3. Delete task events
        if session_ids:
            db.query(models.TaskEvent).filter(
                models.TaskEvent.session_id.in_(session_ids)
            ).delete(synchronize_session=False)

        # 4. Delete calibration points
        if session_ids:
            db.query(models.CalibrationPoint).filter(
                models.CalibrationPoint.session_id.in_(session_ids)
            ).delete(synchronize_session=False)

        # 5. Delete intakes
        db.query(models.Intake).filter(models.Intake.user_id == user_id).delete(
            synchronize_session=False
        )

        # 6. Delete sessions
        if session_ids:
            db.query(models.Session).filter(models.Session.user_id == user_id).delete(
                synchronize_session=False
            )

        # 7. Delete user
        db.query(models.User).filter(models.User.id == user_id).delete(
            synchronize_session=False
        )

        # Commit all deletions
        db.commit()

        return DeleteUserResponse(
            status="success",
            message=f"All data for user {user_id} has been permanently deleted.",
            deleted_user_id=user_id,
            deleted_sessions=len(session_ids),
            deleted_intakes=intakes_count,
            deleted_results=results_count,
            deleted_events=events_count,
            deleted_calibration_points=calibration_count,
            deleted_features=features_count,
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting user data: {str(e)}"
        )
