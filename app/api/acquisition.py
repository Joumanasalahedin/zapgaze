from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from app.models.acquisition_models import AcquisitionData
from app.db import models, database

router = APIRouter()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/data")
def receive_acquisition(data: AcquisitionData, db: Session = Depends(get_db)):
    # Verify session exists and matches user
    session_entry = (
        db.query(models.Session)
          .filter_by(session_uid=data.session_uid, user_id=data.user_id)
          .first()
    )
    if not session_entry:
        raise HTTPException(
            status_code=404, detail="Session not found for this user.")
    # Persist single record
    record = models.Results(
        session_id=session_entry.id,
        data=json.dumps(data.dict())
    )
    db.add(record)
    db.commit()
    return {"status": "success"}


@router.post("/batch")
def receive_acquisition_batch(
    records: List[AcquisitionData],
    db: Session = Depends(get_db)
):
    entries = []
    for item in records:
        session_entry = (
            db.query(models.Session)
              .filter_by(session_uid=item.session_uid, user_id=item.user_id)
              .first()
        )
        if not session_entry:
            raise HTTPException(
                status_code=404,
                detail=f"Session not found for user {item.user_id} and uid {item.session_uid}"
            )
        entries.append(
            models.Results(
                session_id=session_entry.id,
                data=json.dumps(item.dict())
            )
        )
    # Bulk insert for performance
    db.bulk_save_objects(entries)
    db.commit()
    return {"status": "success", "count": len(entries)}
