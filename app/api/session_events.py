from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.db import models, database
from app.security import verify_frontend_api_key

router = APIRouter()

# Initialize rate limiter for session events endpoints
limiter = Limiter(key_func=get_remote_address)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TaskEventRequest(BaseModel):
    session_uid: str
    timestamp: float
    event_type: str  # e.g. "stimulus_onset", "response", "error"
    stimulus: Optional[str] = None
    response: Optional[bool] = None


@router.post("/event")
@limiter.limit(
    "1000/minute"
)  # Allow 1000 events per minute per IP (high volume during tests)
def log_event(
    request: Request,
    req: TaskEventRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_frontend_api_key),
):
    # Verify session exists using only session_uid
    sess = db.query(models.Session).filter_by(session_uid=req.session_uid).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Persist task event
    evt = models.TaskEvent(
        session_id=sess.id,
        timestamp=req.timestamp,
        event_type=req.event_type,
        stimulus=req.stimulus,
        response=req.response,
    )
    db.add(evt)
    db.commit()

    return {"status": "event_logged"}
