from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from typing import List
import json

from app.models.acquisition_models import AcquisitionData
from app.db import models, database
from app.security import verify_agent_api_key

router = APIRouter()

# Initialize rate limiter for acquisition endpoints
limiter = Limiter(key_func=get_remote_address)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/data")
@limiter.limit("1000/minute")  # Allow 1000 single records per minute per IP
def receive_acquisition(
    request: Request,
    data: AcquisitionData,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_agent_api_key),
):
    """Receive single acquisition data point (requires API key)"""
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
@limiter.limit(
    "100/minute"
)  # Allow 100 batches per minute per IP (each batch can contain many records)
def receive_acquisition_batch(
    request: Request,
    records: List[AcquisitionData],
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_agent_api_key),
):
    """Receive batch acquisition data (requires API key)"""
    # Additional validation: limit batch size to prevent abuse
    if len(records) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Batch size exceeds maximum of 1000 records per batch",
        )

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
