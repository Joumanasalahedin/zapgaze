from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional
import uuid
import json
import datetime

from app.db import models, database

router = APIRouter()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


class IntakeData(BaseModel):
    # For new users
    name: Optional[str] = None
    # For existing users
    user_id: Optional[int] = None
    # Required for both
    birthdate: datetime.date
    # ASRS-5 has 6 items (0=Never to 4=Very Often)
    answers: List[int] = Field(..., min_length=6, max_length=6)

    @model_validator(mode="after")
    def validate_user_identification(self):
        """Ensure either name (new user) or user_id (existing user) is provided, but not both."""
        if self.name is not None and self.user_id is not None:
            raise ValueError(
                "Cannot provide both name and user_id. Use name for new users, user_id for existing users."
            )
        if self.name is None and self.user_id is None:
            raise ValueError("Either name (for new users) or user_id (for existing users) must be provided.")
        return self


class IntakeResponse(BaseModel):
    id: int
    user_id: int
    session_uid: str
    answers: List[int]
    total_score: int
    symptom_group: str
    created_at: datetime.datetime


@router.post("/", summary="Create user intake and compute ASRS-5 total score")
def intake(data: IntakeData, db: Session = Depends(get_db)):
    # Compute total ASRS-5 score (0-24)
    total_score = sum(data.answers)

    # Classify symptom group: >=14 = High, else Low
    symptom_group = "High" if total_score >= 14 else "Low"

    user = None

    # Handle existing user case
    if data.user_id is not None:
        # Verify existing user exists and birthdate matches
        user = (
            db.query(models.User)
            .filter(
                models.User.id == data.user_id, models.User.birthdate == data.birthdate
            )
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found or birthdate does not match. Please check your user ID and birthdate.",
            )

        print(f"Using existing user: {user.name} (ID: {user.id})")

    # Handle new user case
    elif data.name is not None:
        # Create new User (basic info only)
        user = models.User(name=data.name, birthdate=data.birthdate)
        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"Created new user: {user.name} (ID: {user.id})")

    # Create new session for the user
    session_uid = str(uuid.uuid4())
    session_entry = models.Session(user_id=user.id, session_uid=session_uid)
    db.add(session_entry)
    db.commit()

    # Create Intake record linked to the user and session
    intake_record = models.Intake(
        user_id=user.id,
        session_uid=session_uid,
        answers_json=json.dumps(data.answers),
        total_score=total_score,
        symptom_group=symptom_group,
    )
    db.add(intake_record)
    db.commit()
    db.refresh(intake_record)

    return IntakeResponse(
        id=intake_record.id,
        user_id=intake_record.user_id,
        session_uid=intake_record.session_uid,
        answers=json.loads(intake_record.answers_json),
        total_score=intake_record.total_score,
        symptom_group=intake_record.symptom_group,
        created_at=intake_record.created_at,
    )


@router.get("/user/{user_id}", summary="Get intake data for a specific user")
def get_user_intake(user_id: int, db: Session = Depends(get_db)):
    """Get the latest intake record for a user."""

    # Check if user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the latest intake record for this user
    intake_record = (
        db.query(models.Intake)
        .filter(models.Intake.user_id == user_id)
        .order_by(models.Intake.created_at.desc())
        .first()
    )

    if not intake_record:
        raise HTTPException(
            status_code=404, detail="No intake data found for this user"
        )

    return IntakeResponse(
        id=intake_record.id,
        user_id=intake_record.user_id,
        session_uid=intake_record.session_uid,
        answers=json.loads(intake_record.answers_json),
        total_score=intake_record.total_score,
        symptom_group=intake_record.symptom_group,
        created_at=intake_record.created_at,
    )


@router.get("/session/{session_uid}", summary="Get intake data for a specific session")
def get_session_intake(session_uid: str, db: Session = Depends(get_db)):
    """Get the intake record for a specific session."""

    # Check if session exists
    session = (
        db.query(models.Session)
        .filter(models.Session.session_uid == session_uid)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get the intake record for this session
    intake_record = (
        db.query(models.Intake).filter(models.Intake.session_uid == session_uid).first()
    )

    if not intake_record:
        raise HTTPException(
            status_code=404, detail="No intake data found for this session"
        )

    return IntakeResponse(
        id=intake_record.id,
        user_id=intake_record.user_id,
        session_uid=intake_record.session_uid,
        answers=json.loads(intake_record.answers_json),
        total_score=intake_record.total_score,
        symptom_group=intake_record.symptom_group,
        created_at=intake_record.created_at,
    )


@router.get("/user/{user_id}/history", summary="Get all intake records for a user")
def get_user_intake_history(user_id: int, db: Session = Depends(get_db)):
    """Get all intake records for a user (if they have multiple)."""

    # Check if user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all intake records for this user
    intake_records = (
        db.query(models.Intake)
        .filter(models.Intake.user_id == user_id)
        .order_by(models.Intake.created_at.desc())
        .all()
    )

    if not intake_records:
        raise HTTPException(
            status_code=404, detail="No intake data found for this user"
        )

    return [
        IntakeResponse(
            id=record.id,
            user_id=record.user_id,
            session_uid=record.session_uid,
            answers=json.loads(record.answers_json),
            total_score=record.total_score,
            symptom_group=record.symptom_group,
            created_at=record.created_at,
        )
        for record in intake_records
    ]
