from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List
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
    name: str
    birthdate: datetime.date
    # ASRS-5 has 6 items (0=Never to 4=Very Often)
    answers: List[int] = Field(..., min_items=6, max_items=6)


@router.post("/", summary="Create user intake and compute ASRS-5 total score")
def intake(data: IntakeData, db: Session = Depends(get_db)):
    # Compute total ASRS-5 score (0-24)
    total_score = sum(data.answers)

    # Classify symptom group: >=14 = High, else Low
    symptom_group = "High" if total_score >= 14 else "Low"

    # Persist new User (store total_score)
    user = models.User(
        name=data.name,
        birthdate=data.birthdate,
        answers_json=json.dumps(data.answers),
        total_score=total_score,
        symptom_group=symptom_group
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create initial session for user
    session_uid = str(uuid.uuid4())
    session_entry = models.Session(user_id=user.id, session_uid=session_uid)
    db.add(session_entry)
    db.commit()

    return {
        "session_uid": session_uid,
        "total_score": total_score,
        "symptom_group": symptom_group
    }
