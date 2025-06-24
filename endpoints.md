**ZapGaze API Endpoints**

This document summarizes all available API endpoints, the purpose of each, required inputs, and example `curl` commands.

---

## 1. Health Check

**Endpoint:** `GET /`

**Description:** Simple test to verify the API server is running.

**Example:**
```bash
curl http://localhost:8000/
```

---

## 2. Intake (ASRS-5)

**Endpoint:** `POST /intake/`

**Description:**
- Creates a new **User** with ASRS-5 intake data (6 questions).
- Computes the **total_score** (0–24) and classifies **symptom_group** (`High`/`Low`).
- Automatically generates an initial **Session** and returns its `session_uid`.

**Request JSON:**
```json
{
  "name": "Jane Doe",
  "birthdate": "1990-01-01",
  "answers": [0,2,3,1,4,2]
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

## 3. Session Management

### a) Start Session

**Endpoint:** `POST /session/start`

**Description:**
- Begins a new or reuses an existing session for a user.
- If you provide `session_uid`, it validates and returns it; otherwise generates a new one.

**Request JSON:**
```json
{
  "user_id": <integer>,
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
  -d '{"user_id":1,"session_uid":"140d5631-7710-4adc-8575-0befddbae087"}'
```

### b) Stop Session

**Endpoint:** `POST /session/stop`

**Description:**
- Marks the most recent active session for a user as stopped, setting its `stopped_at` timestamp and `status`.

**Request JSON:**
```json
{ "user_id": <integer> }
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

## 4. Local Acquisition Agent

This lightweight microservice runs on the user’s machine (outside Docker) and controls the `acquisition_client.py` process.

Host: `http://localhost:9000`

### a) Start Acquisition

**Endpoint:** `POST /start`

**Description:** Launches the acquisition client with the provided session and user context.

**Request JSON:**
```json
{
  "session_uid": "<uuid>",
  "user_id": <integer>,
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
  -d '{"session_uid":"140d5631-7710-4adc-8575-0befddbae087","user_id":1,"api_url":"http://localhost:8000/acquisition/batch","fps":20}'
```

### b) Stop Acquisition

**Endpoint:** `POST /stop`

**Description:** Terminates the running acquisition client process.

**Response JSON:**
```json
{ "status": "acquisition_stopped" }
```

**Example:**
```bash
curl -X POST http://localhost:9000/stop
```

### c) Status

**Endpoint:** `GET /status`

**Description:** Checks whether the acquisition client is currently running.

**Response JSON:**
```json
{ "status": "running", "pid": <process_id> }  // or { "status": "stopped" }
```

**Example:**
```bash
curl http://localhost:9000/status
```

---

## 5. Task Event Logging

**Endpoint:** `POST /session/event`

**Description:** Record each CPT stimulus onset and user response.

**Request JSON:**
```json
{
  "user_id": <integer>,
  "session_uid": "<uuid>",
  "timestamp": <float_unix_time>,
  "event_type": "stimulus_onset" | "response",
  "stimulus": "O" | "X",
  "response": true | false     # only for event_type=="response"
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
  -d '{"user_id":1,"session_uid":"<uuid>","timestamp":1719020001.000,"event_type":"stimulus_onset","stimulus":"O"}'

# User response
curl -X POST http://localhost:8000/session/event \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"session_uid":"<uuid>","timestamp":1719020001.350,"event_type":"response","stimulus":"O","response":true}'
```

---

## 6. Acquisition Data

### a) Single‐Frame Ingestion

**Endpoint:** `POST /acquisition/data`

**Description:** Receives one frame’s eye-tracking & blink data.

**Request JSON:**
```json
{
  "user_id": <integer>,
  "session_uid": "<uuid>",
  "timestamp": <float_unix_time>,
  "left_eye": { "x": <float>, "y": <float> },
  "right_eye": { "x": <float>, "y": <float> },
  "ear": <float>,
  "blink": true | false
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
  -d '{"user_id":1,"session_uid":"<uuid>","timestamp":1000,"left_eye":{"x":100,"y":100},"right_eye":{"x":105,"y":100},"ear":0.3,"blink":false}'
```

### b) Batched Ingestion

**Endpoint:** `POST /acquisition/batch`

**Description:** Receives an array of multiple frame‐data objects in one request for efficiency.

**Request JSON:**
```json
[
  { /* record1 */ },
  { /* record2 */ },
  ...
]
```

**Response JSON:**
```json
{ "status": "success", "count": <number_inserted> }
```

**Example:**
```bash
curl -X POST http://localhost:8000/acquisition/batch \
  -H "Content-Type: application/json" \
  -d '[{...}, {...}]'
```

---

## 7. Raw Results Retrieval

**Endpoint:** `GET /results/{session_uid}`

**Description:** Fetch all raw acquisition records for a session (eyes, EAR, blinks).

**Response JSON:**
```json
{
  "session_uid": "<uuid>",
  "user_id": 1,
  "count": 2,
  "records": [ { /* record1 */ }, { /* record2 */ } ]
}
```

**Example:**
```bash
curl http://localhost:8000/results/<session_uid>
```

---

## 8. Feature Computation & Retrieval

### a) Compute Session Features

**Endpoint:** `POST /features/compute/{session_uid}`

**Description:** Runs the feature-extraction pipeline on raw data and stores a summary row in `session_features`.

**Response JSON:**
```json
{ "status": "session_features_computed", "session_uid": "<uuid>" }
```

**Example:**
```bash
curl -X POST http://localhost:8000/features/compute/<session_uid>
```

### b) Get Session Features

**Endpoint:** `GET /features/sessions/{session_uid}`

**Description:** Returns the aggregated metrics for a session (fixations, saccades, blinks, RT, errors).

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
  "total_blinks": 1,
  "blink_rate": 0.2,
  "go_reaction_time_mean": 0.35,
  "go_reaction_time_sd": 0.05,
  "omission_errors": 0,
  "commission_errors": 1,
  "started_at": "2025-06-20T15:00:00",
  "stopped_at": "2025-06-20T15:05:00"
}
```

**Example:**
```bash
curl http://localhost:8000/features/sessions/<session_uid>
```

---

## 9. Cleanup (Optional)

### Delete Raw Results

**Endpoint:** `DELETE /results/{session_uid}`

**Description:** Deletes all raw `results` rows for a session (useful for resetting data).

**Response JSON:**
```json
{ "deleted": <number_of_rows_deleted> }
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/results/<session_uid>
```

---

*All date/times and `<uuid>` placeholders should be replaced with actual values from your workflow.*
