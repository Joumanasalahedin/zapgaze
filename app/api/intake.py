from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
import json

from app.models.intake_models import IntakeRequest
from app.db import models, database

router = APIRouter()

# Dependency


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def intake_user(data: IntakeRequest, db: Session = Depends(get_db)):

    # Validate correct number of answers
    if len(data.answers) != 18:
        raise HTTPException(
            status_code=400, detail="Exactly 18 answers are required.")

    # Calculate Part A and Part B scores
    part_a_score = sum(data.answers[:6])
    part_b_score = sum(data.answers[6:])

    # Classify symptom group
    symptom_group = "High" if part_a_score >= 4 else "Low"

    # Create User entry
    user = models.User(
        name=data.name,
        birthdate=data.birthdate,
        answers_json=json.dumps(data.answers),
        asrs_part_a_score=part_a_score,
        asrs_part_b_score=part_b_score,
        symptom_group=symptom_group
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create Session entry
    session_uid = str(uuid.uuid4())
    session = models.Session(user_id=user.id, session_uid=session_uid)
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_uid": session.session_uid,
        "part_a_score": part_a_score,
        "part_b_score": part_b_score,
        "symptom_group": symptom_group
    }
