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
    # Verify session exists using only session_uid
    session_entry = (
        db.query(models.Session).filter_by(session_uid=data.session_uid).first()
    )
    if not session_entry:
        raise HTTPException(status_code=404, detail="Session not found.")
    # Persist single record
    record = models.Results(
        session_id=session_entry.id, data=json.dumps(data.model_dump())
    )
    db.add(record)
    db.commit()
    return {"status": "success"}


@router.post("/batch")
def receive_acquisition_batch(
    records: List[AcquisitionData], db: Session = Depends(get_db)
):
    entries = []
    for item in records:
        session_entry = (
            db.query(models.Session).filter_by(session_uid=item.session_uid).first()
        )
        if not session_entry:
            raise HTTPException(
                status_code=404, detail=f"Session not found for uid {item.session_uid}"
            )
        entries.append(
            models.Results(
                session_id=session_entry.id, data=json.dumps(item.model_dump())
            )
        )
    # Bulk insert for performance
    db.bulk_save_objects(entries)
    db.commit()
    return {"status": "success", "count": len(entries)}
