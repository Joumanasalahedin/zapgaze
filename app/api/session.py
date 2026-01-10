import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db import models, database

router = APIRouter()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SessionStartRequest(BaseModel):
    session_uid: Optional[str] = None


class SessionStopRequest(BaseModel):
    session_uid: str


@router.post("/start")
def session_start(req: SessionStartRequest, db: Session = Depends(get_db)):
    if req.session_uid:
        sess = db.query(models.Session).filter_by(session_uid=req.session_uid).first()
        if not sess:
            raise HTTPException(status_code=404, detail="Session UID not found.")
        return {"session_uid": sess.session_uid}

    # Create new session without user_id (will be set during intake)
    new_uid = str(uuid.uuid4())
    sess = models.Session(session_uid=new_uid, user_id=None)
    db.add(sess)
    db.commit()
    db.refresh(sess)
    return {"session_uid": sess.session_uid}


@router.post("/stop")
def session_stop(req: SessionStopRequest, db: Session = Depends(get_db)):
    sess = (
        db.query(models.Session)
        .filter_by(session_uid=req.session_uid, status="active")
        .first()
    )
    if not sess:
        raise HTTPException(
            status_code=404, detail="No active session found with this session_uid."
        )

    sess.stopped_at = datetime.utcnow()
    sess.status = "stopped"
    db.commit()
    return {
        "status": "session_stopped",
        "session_uid": sess.session_uid,
        "stopped_at": sess.stopped_at.isoformat(),
    }
