from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.db import models, database

router = APIRouter()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TaskEventRequest(BaseModel):
    session_uid: str
    timestamp: float
    event_type: str             # e.g. "stimulus_onset", "response", "error"
    stimulus: Optional[str] = None
    response: Optional[bool] = None


@router.post("/event")
def log_event(req: TaskEventRequest, db: Session = Depends(get_db)):
    # Verify session exists using only session_uid
    sess = (
        db.query(models.Session)
          .filter_by(session_uid=req.session_uid)
          .first()
    )
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Persist task event
    evt = models.TaskEvent(
        session_id=sess.id,
        timestamp=req.timestamp,
        event_type=req.event_type,
        stimulus=req.stimulus,
        response=req.response
    )
    db.add(evt)
    db.commit()

    return {"status": "event_logged"}
