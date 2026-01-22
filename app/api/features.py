from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
import json
import statistics
import numpy as np

from app.db import models, database
from app.security import verify_frontend_api_key

router = APIRouter()

# Initialize rate limiter for features endpoints
limiter = Limiter(key_func=get_remote_address)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calculate_gaze_features(samples):
    """
    Calculate eye-tracking features from gaze samples.

    Args:
        samples: List of dictionaries with gaze data

    Returns:
        Dictionary with computed features
    """
    if not samples or len(samples) < 2:
        return {
            "mean_fixation_duration": None,
            "fixation_count": None,
            "gaze_dispersion": None,
            "saccade_count": None,
            "saccade_rate": None,
        }

    # Extract gaze coordinates and timestamps
    gaze_points = []
    timestamps = []

    for sample in samples:
        # Get average gaze position from both eyes
        left_x = sample.get("left_eye", {}).get("x")
        left_y = sample.get("left_eye", {}).get("y")
        right_x = sample.get("right_eye", {}).get("x")
        right_y = sample.get("right_eye", {}).get("y")

        # Use left eye if available, otherwise right eye, otherwise skip
        if left_x is not None and left_y is not None:
            gaze_points.append((left_x, left_y))
            timestamps.append(sample["timestamp"])
        elif right_x is not None and right_y is not None:
            gaze_points.append((right_x, right_y))
            timestamps.append(sample["timestamp"])

    if len(gaze_points) < 2:
        return {
            "mean_fixation_duration": None,
            "fixation_count": None,
            "gaze_dispersion": None,
            "saccade_count": None,
            "saccade_rate": None,
        }

    gaze_points = np.array(gaze_points)
    timestamps = np.array(timestamps)

    # Calculate gaze dispersion (standard deviation of gaze positions)
    gaze_dispersion = np.std(gaze_points, axis=0)
    gaze_dispersion_magnitude = np.sqrt(np.sum(gaze_dispersion**2))

    # Fixation detection parameters
    FIXATION_THRESHOLD = 50  # pixels - threshold for considering gaze as fixation
    MIN_FIXATION_DURATION = 0.1  # seconds - minimum duration for a fixation

    # Calculate distances between consecutive gaze points
    distances = []
    for i in range(1, len(gaze_points)):
        dist = np.linalg.norm(gaze_points[i] - gaze_points[i - 1])
        distances.append(dist)

    # Detect fixations
    fixations = []
    current_fixation_start = 0
    current_fixation_center = gaze_points[0]

    for i in range(1, len(gaze_points)):
        dist = np.linalg.norm(gaze_points[i] - current_fixation_center)

        if dist > FIXATION_THRESHOLD:
            # End current fixation if it meets minimum duration
            fixation_duration = timestamps[i - 1] - timestamps[current_fixation_start]
            if fixation_duration >= MIN_FIXATION_DURATION:
                fixations.append(
                    {
                        "start": current_fixation_start,
                        "end": i - 1,
                        "duration": fixation_duration,
                        "center": current_fixation_center,
                    }
                )

            # Start new fixation
            current_fixation_start = i
            current_fixation_center = gaze_points[i]
        else:
            # Update fixation center (running average)
            current_fixation_center = (current_fixation_center + gaze_points[i]) / 2

    # Add final fixation if it meets minimum duration
    if len(gaze_points) > current_fixation_start:
        fixation_duration = timestamps[-1] - timestamps[current_fixation_start]
        if fixation_duration >= MIN_FIXATION_DURATION:
            fixations.append(
                {
                    "start": current_fixation_start,
                    "end": len(gaze_points) - 1,
                    "duration": fixation_duration,
                    "center": current_fixation_center,
                }
            )

    # Calculate fixation metrics
    fixation_count = len(fixations)
    fixation_durations = [f["duration"] for f in fixations]
    mean_fixation_duration = np.mean(fixation_durations) if fixation_durations else None

    # Detect saccades (rapid eye movements between fixations)
    SACCADE_VELOCITY_THRESHOLD = 100  # pixels/second - minimum velocity for saccade

    saccades = []
    for i in range(1, len(fixations)):
        prev_fixation = fixations[i - 1]
        curr_fixation = fixations[i]

        # Calculate distance between fixation centers
        distance = np.linalg.norm(curr_fixation["center"] - prev_fixation["center"])

        # Calculate time between fixations
        time_diff = (
            timestamps[curr_fixation["start"]] - timestamps[prev_fixation["end"]]
        )

        if time_diff > 0:
            velocity = distance / time_diff

            if velocity > SACCADE_VELOCITY_THRESHOLD:
                saccades.append(
                    {
                        "from_fixation": i - 1,
                        "to_fixation": i,
                        "distance": distance,
                        "velocity": velocity,
                    }
                )

    saccade_count = len(saccades)

    # Calculate saccade rate (saccades per minute)
    total_duration = (timestamps[-1] - timestamps[0]) / 60.0  # in minutes
    saccade_rate = saccade_count / total_duration if total_duration > 0 else None

    return {
        "mean_fixation_duration": (
            float(mean_fixation_duration)
            if mean_fixation_duration is not None
            else None
        ),
        "fixation_count": fixation_count,
        "gaze_dispersion": float(gaze_dispersion_magnitude),
        "saccade_count": saccade_count,
        "saccade_rate": float(saccade_rate) if saccade_rate is not None else None,
    }


@router.post("/compute/{session_uid}")
@limiter.limit("30/minute")  # Allow 30 feature computations per minute per IP
def compute_session_features(
    request: Request,
    session_uid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_frontend_api_key),
):
    # Validate session
    session = db.query(models.Session).filter_by(session_uid=session_uid).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Load gaze/blink samples
    raw_recs = db.query(models.Results).filter_by(session_id=session.id).all()
    samples = [json.loads(r.data) for r in raw_recs] if raw_recs else []
    timestamps = [s["timestamp"] for s in samples] if samples else []
    blinks = [s["timestamp"] for s in samples if s.get("blink")] if samples else []

    # Duration in minutes
    duration = (
        (max(timestamps) - min(timestamps)) / 60.0
        if timestamps and len(timestamps) > 1
        else 0
    )

    # Load task events
    events = (
        db.query(models.TaskEvent)
        .filter_by(session_id=session.id)
        .order_by(models.TaskEvent.timestamp)
        .all()
    )
    stimuli = [e for e in events if e.event_type == "stimulus_onset"]
    responses = [e for e in events if e.event_type == "response"]

    # Debug: Print event counts
    print(f"DEBUG: Found {len(events)} total events")
    print(f"DEBUG: Found {len(stimuli)} stimulus events")
    print(f"DEBUG: Found {len(responses)} response events")

    # Print all events for debugging
    print("DEBUG: All events:")
    for i, event in enumerate(events):
        print(
            f"  {i}: {event.event_type}, stimulus={event.stimulus}, response={event.response}, timestamp={event.timestamp}"
        )

    # Print all responses for debugging
    print("DEBUG: All responses:")
    for i, resp in enumerate(responses):
        print(
            f"  {i}: response={resp.response}, stimulus={resp.stimulus}, timestamp={resp.timestamp}"
        )

    # Compute reaction times and error counts
    rt_list = []
    omission = 0
    commission = 0

    # Group stimuli by stimulus type for better matching
    # Any letter except X is a Go trial
    go_stimuli = [s for s in stimuli if s.stimulus != "X"]
    # Only X is a No-Go trial
    nogo_stimuli = [s for s in stimuli if s.stimulus == "X"]

    print(f"DEBUG: Found {len(go_stimuli)} Go stimuli (not X)")
    print(f"DEBUG: Found {len(nogo_stimuli)} No-Go stimuli (X)")

    # Process Go trials (any letter except 'X')
    for stim in go_stimuli:
        # Find the next response after this stimulus
        matching_responses = [r for r in responses if r.timestamp >= stim.timestamp]
        if matching_responses:
            # Take the first response after stimulus
            resp = matching_responses[0]
            if resp.response:  # User responded (correct)
                rt = resp.timestamp - stim.timestamp
                rt_list.append(rt)
                print(
                    f"DEBUG: Go trial '{stim.stimulus}' - Correct response, RT={rt:.3f}s"
                )
            else:  # User didn't respond (omission)
                omission += 1
                print(f"DEBUG: Go trial '{stim.stimulus}' - Omission error")
        else:
            omission += 1
            print(f"DEBUG: Go trial '{stim.stimulus}' - No response found (omission)")

    # Process No-Go trials (stimulus = 'X')
    for stim in nogo_stimuli:
        # Find the next response after this stimulus
        matching_responses = [r for r in responses if r.timestamp >= stim.timestamp]
        if matching_responses:
            # Take the first response after stimulus
            resp = matching_responses[0]
            print(
                f"DEBUG: No-Go trial '{stim.stimulus}' at {stim.timestamp} - Response: {resp.response} at {resp.timestamp}"
            )
            if resp.response:  # User did NOT press (correct inhibition)
                print(
                    f"DEBUG: No-Go trial '{stim.stimulus}' - Correct inhibition (no commission error)"
                )
            else:  # User pressed (commission error)
                commission += 1
                print(
                    f"DEBUG: No-Go trial '{stim.stimulus}' - Commission error (user pressed)"
                )
        else:
            print(
                f"DEBUG: No-Go trial '{stim.stimulus}' - No response found (correct inhibition)"
            )

    print(f"DEBUG: Reaction times: {rt_list}")
    print(f"DEBUG: Omission errors: {omission}")
    print(f"DEBUG: Commission errors: {commission}")

    mean_rt = statistics.mean(rt_list) if rt_list else None
    sd_rt = statistics.pstdev(rt_list) if len(rt_list) > 1 else None
    total_blinks = len(blinks)
    blink_rate = total_blinks / duration if duration > 0 else None

    # Calculate eye-tracking features
    gaze_features = calculate_gaze_features(samples)

    # Prepare session_features
    sf = db.query(models.SessionFeatures).filter_by(session_id=session.id).first()
    if not sf:
        sf = models.SessionFeatures(session_id=session.id, user_id=session.user_id)

    sf.started_at = session.started_at
    sf.stopped_at = session.stopped_at
    sf.mean_fixation_duration = gaze_features["mean_fixation_duration"]
    sf.fixation_count = gaze_features["fixation_count"]
    sf.gaze_dispersion = gaze_features["gaze_dispersion"]
    sf.saccade_count = gaze_features["saccade_count"]
    sf.saccade_rate = gaze_features["saccade_rate"]
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
@limiter.limit("60/minute")  # Allow 60 requests per minute per IP
def get_session_features(
    request: Request,
    session_uid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_frontend_api_key),
):
    session = db.query(models.Session).filter_by(session_uid=session_uid).first()
    if not session or not session.features:
        raise HTTPException(
            status_code=404, detail="Features not found for this session."
        )

    # Get user information
    user = db.query(models.User).filter(models.User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Get intake information for this session
    intake = (
        db.query(models.Intake).filter(models.Intake.session_uid == session_uid).first()
    )

    sf = session.features

    # Calculate Go and No-Go trial counts from task events
    # Only count events that occurred after session start (main test trials, not practice)
    # Practice trials are not logged to the database, but this ensures we only count main test
    session_start_time = session.started_at.timestamp() if session.started_at else 0

    events = (
        db.query(models.TaskEvent)
        .filter_by(session_id=session.id)
        .filter(models.TaskEvent.event_type == "stimulus_onset")
        .filter(models.TaskEvent.timestamp >= session_start_time)
        .all()
    )
    go_trial_count = len([e for e in events if e.stimulus != "X"])
    nogo_trial_count = len([e for e in events if e.stimulus == "X"])

    # Prepare intake data
    intake_data = None
    if intake:
        intake_data = {
            "answers": json.loads(intake.answers_json),
            "total_score": intake.total_score,
            "symptom_group": intake.symptom_group,
        }

    return {
        "session_uid": session_uid,
        "user_id": session.user_id,
        "name": user.name,
        "birthdate": user.birthdate.isoformat(),
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
        "go_trial_count": go_trial_count,
        "nogo_trial_count": nogo_trial_count,
        "started_at": sf.started_at.isoformat() if sf.started_at else None,
        "stopped_at": sf.stopped_at.isoformat() if sf.stopped_at else None,
        "intake": intake_data,
    }
