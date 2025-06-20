from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import statistics
from datetime import datetime

from app.db import models, database

router = APIRouter()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/compute/{session_uid}")
def compute_session_features(session_uid: str, db: Session = Depends(get_db)):
    # Validate session
    session = db.query(models.Session).filter_by(
        session_uid=session_uid).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Load gaze/blink samples
    raw_recs = db.query(models.Results).filter_by(session_id=session.id).all()
    samples = [json.loads(r.data) for r in raw_recs]
    timestamps = [s['timestamp'] for s in samples]
    blinks = [s['timestamp'] for s in samples if s.get('blink')]

    # Duration in minutes
    duration = (max(timestamps) - min(timestamps)) / 60.0 if timestamps else 0

    # Load task events
    events = db.query(models.TaskEvent).filter_by(
        session_id=session.id).order_by(models.TaskEvent.timestamp).all()
    stimuli = [e for e in events if e.event_type == 'stimulus_onset']
    responses = [e for e in events if e.event_type == 'response']

    # Compute reaction times and error counts
    rt_list = []
    omission = 0
    commission = 0
    for stim in stimuli:
        resp = next(
            (r for r in responses if r.timestamp >= stim.timestamp), None)
        if stim.stimulus == 'O':
            if resp:
                rt_list.append(resp.timestamp - stim.timestamp)
            else:
                omission += 1
        else:
            if resp:
                commission += 1

    mean_rt = statistics.mean(rt_list) if rt_list else None
    sd_rt = statistics.pstdev(rt_list) if len(rt_list) > 1 else None
    total_blinks = len(blinks)
    blink_rate = total_blinks / duration if duration > 0 else None

    # Prepare session_features
    sf = db.query(models.SessionFeatures).filter_by(
        session_id=session.id).first()
    if not sf:
        sf = models.SessionFeatures(
            session_id=session.id, user_id=session.user_id)

    sf.started_at = session.started_at
    sf.stopped_at = session.stopped_at
    sf.mean_fixation_duration = None  # placeholder
    sf.fixation_count = None          # placeholder
    sf.gaze_dispersion = None         # placeholder
    sf.saccade_count = None           # placeholder
    sf.saccade_rate = None            # placeholder
    sf.total_blinks = total_blinks
    sf.blink_rate = blink_rate
    sf.go_reaction_time_mean = mean_rt
    sf.go_reaction_time_sd = sd_rt
    sf.omission_errors = omission
    sf.commission_errors = commission

    db.add(sf)
    db.commit()
    return {"status": "session_features_computed", "session_uid": session_uid}


@router.get("/sessions/{session_uid}")
def get_session_features(session_uid: str, db: Session = Depends(get_db)):
    session = db.query(models.Session).filter_by(
        session_uid=session_uid).first()
    if not session or not session.features:
        raise HTTPException(
            status_code=404, detail="Features not found for this session.")

    sf = session.features
    return {
        "session_uid": session_uid,
        "user_id": session.user_id,
        "mean_fixation_duration": sf.mean_fixation_duration,
        "fixation_count": sf.fixation_count,
        "gaze_dispersion": sf.gaze_dispersion,
        "saccade_count": sf.saccade_count,
        "saccade_rate": sf.saccade_rate,
        "total_blinks": sf.total_blinks,
        "blink_rate": sf.blink_rate,
        "go_reaction_time_mean": sf.go_reaction_time_mean,
        "go_reaction_time_sd": sf.go_reaction_time_sd,
        "omission_errors": sf.omission_errors,
        "commission_errors": sf.commission_errors,
        "started_at": sf.started_at.isoformat() if sf.started_at else None,
        "stopped_at": sf.stopped_at.isoformat() if sf.stopped_at else None,
    }
