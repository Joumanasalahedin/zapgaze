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

## 2. User Management

### 2.1 Search Users

**Endpoint:** `GET /users/search`

**Purpose:** Search for existing users by name (partial match, case-insensitive).

**Parameters:**
- `name` (required): Name to search for

**Response JSON:**
```json
[
  {
    "user_id": 1,
    "name": "John Doe",
    "birthdate": "2003-11-18"
  },
  {
    "user_id": 3,
    "name": "Johnny Smith",
    "birthdate": "1995-05-20"
  }
]
```

**Example:**
```bash
curl "http://localhost:8000/users/search?name=John"
```

### 2.2 Get User Results

**Endpoint:** `GET /users/results`

**Purpose:** Get all results for a user, grouped by session. Requires birthdate verification.

**Parameters:**
- `user_id` (required): User ID
- `birthdate` (required): User birthdate for verification (YYYY-MM-DD)

**Response JSON:**
```json
{
  "user_id": 1,
  "user_name": "John Doe",
  "birthdate": "2003-11-18",
  "sessions": [
    {
      "session_uid": "abc123-def456-ghi789",
      "started_at": "2025-01-02T20:50:11",
      "stopped_at": "2025-01-02T21:15:30",
      "status": "completed",
      "features": {
        "mean_fixation_duration": 23.26,
        "fixation_count": 1,
        "gaze_dispersion": 8.53,
        "saccade_count": 0,
        "saccade_rate": 0,
        "total_blinks": 9,
        "blink_rate": 23.15,
        "go_reaction_time_mean": 0.61,
        "go_reaction_time_sd": 0.15,
        "omission_errors": 0,
        "commission_errors": 1
      },
      "intake": {
        "total_score": 12,
        "symptom_group": "Low",
        "answers": [3, 2, 1, 4, 0, 2],
        "created_at": "2025-01-02T20:50:11"
      }
    }
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/users/results?user_id=1&birthdate=2003-11-18"
```

---

## 3. Intake (ASRS-5)

### 3.1 Create Intake (New or Existing User)

**Endpoint:** `POST /intake/`

**Purpose:**
1. Create a new **User** with demographic and ASRS-5 answers, OR
2. Add a new intake for an existing user (verified by birthdate)
3. Compute **total_score** (0–24).
4. Classify **symptom_group** (`High` if ≥14, else `Low`).
5. Automatically generate a new **Session** and return its `session_uid`.

**Request JSON (New User):**
```json
{
  "name": "Jane Doe",
  "birthdate": "1990-01-01",
  "answers": [0, 2, 3, 1, 4, 2]
}
```

**Request JSON (Existing User):**
```json
{
  "user_id": 1,
  "birthdate": "1990-01-01",
  "answers": [1, 2, 3, 2, 1, 0]
}
```

**Response JSON:**
```json
{
  "id": 1,
  "user_id": 1,
  "session_uid": "abc123-def456-ghi789",
  "answers": [0, 2, 3, 1, 4, 2],
  "total_score": 12,
  "symptom_group": "Low",
  "created_at": "2025-01-02T20:50:11"
}
```

**Example (New User):**
```bash
curl -X POST http://localhost:8000/intake/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Doe","birthdate":"1990-01-01","answers":[0,2,3,1,4,2]}'
```

**Example (Existing User):**
```bash
curl -X POST http://localhost:8000/intake/ \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"birthdate":"1990-01-01","answers":[1,2,3,2,1,0]}'
```

### 3.2 Get User Intake

**Endpoint:** `GET /intake/user/{user_id}`

**Purpose:** Get the latest intake record for a specific user.

**Response JSON:**
```json
{
  "id": 1,
  "user_id": 1,
  "session_uid": "abc123-def456-ghi789",
  "answers": [0, 2, 3, 1, 4, 2],
  "total_score": 12,
  "symptom_group": "Low",
  "created_at": "2025-01-02T20:50:11"
}
```

**Example:**
```bash
curl http://localhost:8000/intake/user/1
```

### 3.3 Get User Intake History

**Endpoint:** `GET /intake/user/{user_id}/history`

**Purpose:** Get all intake records for a user (if they have multiple).

**Response JSON:**
```json
[
  {
    "id": 2,
    "user_id": 1,
    "session_uid": "newer-session-uuid",
    "answers": [1, 2, 3, 2, 1, 0],
    "total_score": 9,
    "symptom_group": "Low",
    "created_at": "2025-01-02T20:55:00"
  },
  {
    "id": 1,
    "user_id": 1,
    "session_uid": "older-session-uuid",
    "answers": [0, 2, 3, 1, 4, 2],
    "total_score": 12,
    "symptom_group": "Low",
    "created_at": "2025-01-02T20:50:11"
  }
]
```

**Example:**
```bash
curl http://localhost:8000/intake/user/1/history
```

### 3.4 Get Session Intake

**Endpoint:** `GET /intake/session/{session_uid}`

**Purpose:** Get the intake record for a specific session.

**Response JSON:**
```json
{
  "id": 1,
  "user_id": 1,
  "session_uid": "abc123-def456-ghi789",
  "answers": [0, 2, 3, 1, 4, 2],
  "total_score": 12,
  "symptom_group": "Low",
  "created_at": "2025-01-02T20:50:11"
}
```

**Example:**
```bash
curl http://localhost:8000/intake/session/abc123-def456-ghi789
```

---

## 4. Calibration (Local Acquisition Agent)

Before starting the Go/No-Go task, calibrate the eye-tracker. Run the local agent on the participant's machine:

Host: `http://localhost:9000`

### 4.1 Start Calibration

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

### 4.2 Record Calibration Point

**Endpoint:** `POST /calibrate/point`

**Purpose:** Capture multiple eye samples while the user fixates on a known screen coordinate.

**Request JSON:**
```json
{
  "session_uid": "<uuid>",
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
  -d '{"session_uid":"<uuid>","x":640,"y":360,"duration":1.0,"samples":30}'
```

### 4.3 Finish Calibration

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

## 5. Session Management (Backend API)

### 5.1 Start Session

**Endpoint:** `POST /session/start`

**Purpose:** Begin a new or validate an existing CPT session.

**Request JSON:**
```json
{
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
  -d '{}'
```

### 5.2 Stop Session

**Endpoint:** `POST /session/stop`

**Purpose:** Mark the most recent active session as stopped and record `stopped_at`.

**Request JSON:**
```json
{ "session_uid": "<uuid>" }
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
  -d '{"session_uid":"<uuid>"}'
```

---

## 6. Acquisition Data (Backend API)

### 6.1 Start Acquisition (Local Agent)

**Endpoint:** `POST /start` on Local Agent

**Host:** `http://localhost:9000`

**Purpose:** Launch `acquisition_client.py` with session context.

**Request JSON:**
```json
{
  "session_uid": "<uuid>",
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
  -d '{"session_uid":"<uuid>","api_url":"http://localhost:8000/acquisition/batch","fps":20}'
```

### 6.2 Single‐Frame Ingestion

**Endpoint:** `POST /acquisition/data`

**Purpose:** Upload one eye-tracking sample.

**Request JSON:**
```json
{
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
  -d '{"session_uid":"<uuid>","timestamp":1620000000.123,"left_eye":{"x":100,"y":100},"right_eye":{"x":105,"y":100},"ear":0.30,"blink":false}'
```

### 6.3 Batched Ingestion

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
  -d '[{"session_uid":"<uuid>",…},{…}]'
```

### 6.4 Stop Acquisition (Local Agent)

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

### 6.5 Acquisition Status (Local Agent)

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

## 7. Task Event Logging (Backend API)

**Endpoint:** `POST /session/event`

**Purpose:** Log each stimulus onset and user response (Go/No-Go).

**Request JSON:**
```json
{
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
  -d '{"session_uid":"<uuid>",…,"event_type":"stimulus_onset","stimulus":"O"}'

# Response
curl -X POST http://localhost:8000/session/event \
  -H "Content-Type: application/json" \
  -d '{"session_uid":"<uuid>",…,"event_type":"response","stimulus":"O","response":true}'
```

---

## 8. Raw Results Retrieval & Cleanup (Backend API)

### 8.1 Get Raw Results

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

### 8.2 Delete Raw Results

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

## 9. Feature Computation & Retrieval (Backend API)

### 9.1 Compute Session Features

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

### 9.2 Get Session Features

**Endpoint:** `GET /features/sessions/{session_uid}`

**Purpose:** Retrieve summary metrics (fixation, saccade, blink, RT, errors) for a session, including user and intake information.

**Response JSON:**
```json
{
  "session_uid": "<uuid>",
  "user_id": 1,
  "name": "John Doe",
  "birthdate": "2003-11-18",
  "mean_fixation_duration": 23.26,
  "fixation_count": 1,
  "gaze_dispersion": 8.53,
  "saccade_count": 0,
  "saccade_rate": 0,
  "total_blinks": 9,
  "blink_rate": 23.15,
  "go_reaction_time_mean": 0.61,
  "go_reaction_time_sd": 0.15,
  "omission_errors": 0,
  "commission_errors": 1,
  "started_at": "2025-01-02T20:50:11",
  "stopped_at": null,
  "intake": {
    "answers": [3, 2, 1, 4, 0, 2],
    "total_score": 12,
    "symptom_group": "Low"
  }
}
```

**Example:**
```bash
curl http://localhost:8000/features/sessions/<session_uid>
```

---

*Replace `<uuid>`, timestamps, and other placeholders with real values when testing.*
