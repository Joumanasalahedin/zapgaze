# app/api/calibration.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.db import models, database

router = APIRouter()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CalibrationPointIn(BaseModel):
    screen_x: float
    screen_y: float
    measured_x: float
    measured_y: float


@router.post("/session/{session_uid}/calibration/point", tags=["calibration"])
def add_calibration_point(
    session_uid: str, data: CalibrationPointIn, db: Session = Depends(get_db)
):
    # verify session
    sess = db.query(models.Session).filter_by(session_uid=session_uid).first()
    if not sess:
        raise HTTPException(404, "Session not found")
    # persist the point
    cp = models.CalibrationPoint(
        session_id=sess.id,
        screen_x=data.screen_x,
        screen_y=data.screen_y,
        measured_x=data.measured_x,
        measured_y=data.measured_y,
    )
    db.add(cp)
    db.commit()
    return {"status": "calibration_point_saved"}


@router.get("/session/{session_uid}/calibration", tags=["calibration"])
def get_calibration_points(session_uid: str, db: Session = Depends(get_db)):
    sess = db.query(models.Session).filter_by(session_uid=session_uid).first()
    if not sess:
        raise HTTPException(404, "Session not found")
    rows = db.query(models.CalibrationPoint).filter_by(session_id=sess.id).all()
    return [
        {
            "screen_x": r.screen_x,
            "screen_y": r.screen_y,
            "measured_x": r.measured_x,
            "measured_y": r.measured_y,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in rows
    ]
