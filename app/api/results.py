from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from app.db import models, database

router = APIRouter()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{session_uid}")
def get_results(session_uid: str, db: Session = Depends(get_db)):
    session_entry = db.query(models.Session).filter_by(
        session_uid=session_uid).first()
    if not session_entry:
        raise HTTPException(status_code=404, detail="Session not found.")

    records = db.query(models.Results).filter_by(
        session_id=session_entry.id).all()
    data = [json.loads(r.data) for r in records]

    return {
        "session_uid": session_uid,
        "user_id": session_entry.user_id,
        "count": len(data),
        "records": data
    }


@router.delete("/{session_uid}")
def delete_results(session_uid: str, db: Session = Depends(get_db)):
    session_entry = db.query(models.Session).filter_by(
        session_uid=session_uid).first()
    if not session_entry:
        raise HTTPException(status_code=404, detail="Session not found.")
    deleted = db.query(models.Results).filter_by(
        session_id=session_entry.id).delete()
    db.commit()
    return {"deleted": deleted}
