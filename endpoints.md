**ZapGaze API & Local Agent Endpoints (Process Order)**

A step-by-step guide to all endpoints, organized by the typical user flow: from health check, intake, calibration, session lifecycle, acquisition, event logging, through feature computation and cleanup.

---

## 1. Health Check

**Endpoint:** `GET /`

**Description:** Verify the backend API is up and running.

**Example:**
```bash
curl http://localhost:8000/
```

---

## 2. Intake (ASRS-5)

**Endpoint:** `POST /intake/`

**Purpose:**
1. Create a new **User** with demographic and ASRS-5 answers.
2. Compute **total_score** (0–24).
3. Classify **symptom_group** (`High` if ≥14, else `Low`).
4. Automatically generate an initial **Session** and return its `session_uid`.

**Request JSON:**
```json
{
  "name": "Jane Doe",
  "birthdate": "1990-01-01",
  "answers": [0, 2, 3, 1, 4, 2]
}
```

**Response JSON:**
```json
{
  "session_uid": "<uuid>",
  "total_score": 12,
  "symptom_group": "Low"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/intake/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Doe","birthdate":"1990-01-01","answers":[0,2,3,1,4,2]}'
```

---

## 3. Calibration (Local Acquisition Agent)

Before starting the Go/No-Go task, calibrate the eye-tracker. Run the local agent on the participant’s machine:

Host: `http://localhost:9000`

### 3.1 Start Calibration

**Endpoint:** `POST /calibrate/start`

**Purpose:** Initialize the camera and adapter, clear previous calibration data.

**Response JSON:**
```json
{ "status": "calibration_started" }
```

**Example:**
```bash
curl -X POST http://localhost:9000/calibrate/start
```

### 3.2 Record Calibration Point

**Endpoint:** `POST /calibrate/point`

**Purpose:** Capture multiple eye samples while the user fixates on a known screen coordinate.

**Request JSON:**
```json
{
  "x": <screen_x>,        # horizontal pixel coordinate
  "y": <screen_y>,        # vertical pixel coordinate
  "duration": 1.0,        # seconds to sample
  "samples": 30           # number of frames to record
}
```

**Response JSON:**
```json
{
  "screen_x": <screen_x>,
  "screen_y": <screen_y>,
  "measured_x": <avg_eye_x>,
  "measured_y": <avg_eye_y>
}
```

**Example:**
```bash
curl -X POST http://localhost:9000/calibrate/point \
  -H "Content-Type: application/json" \
  -d '{"x":640,"y":360,"duration":1.0,"samples":30}'
```

### 3.3 Finish Calibration

**Endpoint:** `POST /calibrate/finish`

**Purpose:** Compute and store the affine transform (raw eye → screen coords) in `calibration.json`.

**Response JSON:**
```json
{
  "A": [[a11, a12], [a21, a22]],
  "b": [b1, b2]
}
```

**Example:**
```bash
curl -X POST http://localhost:9000/calibrate/finish
```

---

## 4. Session Management (Backend API)

### 4.1 Start Session

**Endpoint:** `POST /session/start`

**Purpose:** Begin a new or validate an existing CPT session.

**Request JSON:**
```json
{
  "user_id": 1,
  "session_uid": "<optional-existing-uuid>"
}
```

**Response JSON:**
```json
{ "session_uid": "<uuid>" }
```

**Example:**
```bash
curl -X POST http://localhost:8000/session/start \
  -H "Content-Type: application/json" \
  -d '{"user_id":1}'
```

### 4.2 Stop Session

**Endpoint:** `POST /session/stop`

**Purpose:** Mark the most recent active session as stopped and record `stopped_at`.

**Request JSON:**
```json
{ "user_id": 1 }
```

**Response JSON:**
```json
{
  "status": "session_stopped",
  "session_uid": "<uuid>",
  "stopped_at": "2025-06-20T17:40:00.123456"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/session/stop \
  -H "Content-Type: application/json" \
  -d '{"user_id":1}'
```

---

## 5. Acquisition Data (Backend API)

### 5.1 Start Acquisition (Local Agent)

**Endpoint:** `POST /start` on Local Agent

**Host:** `http://localhost:9000`

**Purpose:** Launch `acquisition_client.py` with session context.

**Request JSON:**
```json
{
  "session_uid": "<uuid>",
  "user_id": 1,
  "api_url": "http://localhost:8000/acquisition/batch",
  "fps": 20.0
}
```

**Response JSON:**
```json
{ "status": "acquisition_started", "pid": <process_id> }
```

**Example:**
```bash
curl -X POST http://localhost:9000/start \
  -H "Content-Type: application/json" \
  -d '{"session_uid":"<uuid>","user_id":1,"api_url":"http://localhost:8000/acquisition/batch","fps":20}'
```

### 5.2 Single‐Frame Ingestion

**Endpoint:** `POST /acquisition/data`

**Purpose:** Upload one eye-tracking sample.

**Request JSON:**
```json
{
  "user_id": 1,
  "session_uid": "<uuid>",
  "timestamp": 1620000000.123,
  "left_eye": { "x": 100, "y": 100 },
  "right_eye": { "x": 105, "y": 100 },
  "ear": 0.30,
  "blink": false
}
```

**Response JSON:**
```json
{ "status": "success" }
```

**Example:**
```bash
curl -X POST http://localhost:8000/acquisition/data \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"session_uid":"<uuid>","timestamp":1620000000.123,"left_eye":{"x":100,"y":100},"right_eye":{"x":105,"y":100},"ear":0.30,"blink":false}'
```

### 5.3 Batched Ingestion

**Endpoint:** `POST /acquisition/batch`

**Purpose:** Upload multiple samples in one request for efficiency.

**Request JSON:**
```json
[
  { /* sample 1 */ },
  { /* sample 2 */ }
]
```

**Response JSON:**
```json
{ "status": "success", "count": 2 }
```

**Example:**
```bash
curl -X POST http://localhost:8000/acquisition/batch \
  -H "Content-Type: application/json" \
  -d '[{"user_id":1,…},{…}]'
```

### 5.4 Stop Acquisition (Local Agent)

**Endpoint:** `POST /stop` on Local Agent

**Host:** `http://localhost:9000`

**Purpose:** Terminate the running acquisition client process.

**Response JSON:**
```json
{ "status": "acquisition_stopped" }
```

**Example:**
```bash
curl -X POST http://localhost:9000/stop
```

### 5.5 Acquisition Status (Local Agent)

**Endpoint:** `GET /status`

**Host:** `http://localhost:9000`

**Purpose:** Check if the acquisition client is active.

**Response JSON:**
```json
{ "status": "running", "pid": <process_id> }
```
or
```json
{ "status": "stopped" }
```

**Example:**
```bash
curl http://localhost:9000/status
```

---

## 6. Task Event Logging (Backend API)

**Endpoint:** `POST /session/event`

**Purpose:** Log each stimulus onset and user response (Go/No-Go).

**Request JSON:**
```json
{
  "user_id": 1,
  "session_uid": "<uuid>",
  "timestamp": 1620000001.500,
  "event_type": "stimulus_onset" | "response",
  "stimulus": "O" | "X",
  "response": true | false
}
```

**Response JSON:**
```json
{ "status": "event_logged" }
```

**Example:**
```bash
# Stimulus onset
curl -X POST http://localhost:8000/session/event \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,…,"event_type":"stimulus_onset","stimulus":"O"}'

# Response
curl -X POST http://localhost:8000/session/event \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,…,"event_type":"response","stimulus":"O","response":true}'
```

---

## 7. Raw Results Retrieval & Cleanup (Backend API)

### 7.1 Get Raw Results

**Endpoint:** `GET /results/{session_uid}`

**Purpose:** Retrieve all raw eye-tracking samples for a session.

**Response JSON:**
```json
{
  "session_uid": "<uuid>",
  "user_id": 1,
  "count": 10,
  "records": [ { /* sample1 */ }, … ]
}
```

**Example:**
```bash
curl http://localhost:8000/results/<session_uid>
```

### 7.2 Delete Raw Results

**Endpoint:** `DELETE /results/{session_uid}`

**Purpose:** Remove all raw samples (for resetting or cleanup).

**Response JSON:**
```json
{ "deleted": 10 }
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/results/<session_uid>
```

---

## 8. Feature Computation & Retrieval (Backend API)

### 8.1 Compute Session Features

**Endpoint:** `POST /features/compute/{session_uid}`

**Purpose:** Run the feature-extraction pipeline on stored raw data and events, then save summary metrics.

**Response JSON:**
```json
{ "status": "session_features_computed", "session_uid": "<uuid>" }
```

**Example:**
```bash
curl -X POST http://localhost:8000/features/compute/<session_uid>
```

### 8.2 Get Session Features

**Endpoint:** `GET /features/sessions/{session_uid}`

**Purpose:** Retrieve summary metrics (fixation, saccade, blink, RT, errors) for a session.

**Response JSON:**
```json
{
  "session_uid": "<uuid>",
  "user_id": 1,
  "mean_fixation_duration": null,
  "fixation_count": null,
  "gaze_dispersion": null,
  "saccade_count": null,
  "saccade_rate": null,
  "total_blinks": 2,
  "blink_rate": 0.5,
  "go_reaction_time_mean": 0.35,
  "go_reaction_time_sd": 0.05,
  "omission_errors": 1,
  "commission_errors": 0,
  "started_at": "2025-06-20T15:00:00",
  "stopped_at": "2025-06-20T15:05:00"
}
```

**Example:**
```bash
curl http://localhost:8000/features/sessions/<session_uid>
```

---

*Replace `<uuid>`, timestamps, and other placeholders with real values when testing.*
