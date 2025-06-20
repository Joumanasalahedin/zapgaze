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
    user_id: int
    session_uid: Optional[str] = None


class SessionStopRequest(BaseModel):
    user_id: int


@router.post("/start")
def session_start(req: SessionStartRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if req.session_uid:
        sess = (
            db.query(models.Session)
              .filter_by(user_id=req.user_id, session_uid=req.session_uid)
              .first()
        )
        if not sess:
            raise HTTPException(
                status_code=404, detail="Session UID not found for this user.")
        return {"session_uid": sess.session_uid}

    new_uid = str(uuid.uuid4())
    sess = models.Session(user_id=req.user_id, session_uid=new_uid)
    db.add(sess)
    db.commit()
    db.refresh(sess)
    return {"session_uid": sess.session_uid}


@router.post("/stop")
def session_stop(req: SessionStopRequest, db: Session = Depends(get_db)):
    sess = (
        db.query(models.Session)
          .filter_by(user_id=req.user_id, status="active")
          .order_by(models.Session.started_at.desc())
          .first()
    )
    if not sess:
        raise HTTPException(
            status_code=404, detail="No active session found for this user.")

    sess.stopped_at = datetime.utcnow()
    sess.status = "stopped"
    db.commit()
    return {
        "status": "session_stopped",
        "session_uid": sess.session_uid,
        "stopped_at": sess.stopped_at.isoformat()
    }
