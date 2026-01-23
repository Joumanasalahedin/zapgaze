from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
import json

from app.db import models, database
from app.security import verify_frontend_api_key

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{session_uid}")
@limiter.limit("60/minute")
def get_results(
    request: Request,
    session_uid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_frontend_api_key),
):
    session_entry = db.query(models.Session).filter_by(session_uid=session_uid).first()
    if not session_entry:
        raise HTTPException(status_code=404, detail="Session not found.")

    records = db.query(models.Results).filter_by(session_id=session_entry.id).all()
    data = [json.loads(r.data) for r in records]

    return {
        "session_uid": session_uid,
        "user_id": session_entry.user_id,
        "count": len(data),
        "records": data,
    }


@router.delete("/{session_uid}")
@limiter.limit("30/minute")
def delete_results(
    request: Request,
    session_uid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_frontend_api_key),
):
    session_entry = db.query(models.Session).filter_by(session_uid=session_uid).first()
    if not session_entry:
        raise HTTPException(status_code=404, detail="Session not found.")
    deleted = db.query(models.Results).filter_by(session_id=session_entry.id).delete()
    db.commit()
    return {"deleted": deleted}
