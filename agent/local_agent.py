import subprocess
import signal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import numpy as np
import requests
import json
import time
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Local Acquisition Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

task_proc = None

app.state.cal_data = []
app.state.cal_camera = None
app.state.cal_adapter = None


class StartRequest(BaseModel):
    session_uid: str
    api_url: str = "http://localhost:8000/acquisition/batch"
    fps: float = 20.0


class CalPointRequest(BaseModel):
    session_uid: str
    x: float
    y: float
    duration: float = 1.0
    samples: int = 30


@app.post("/start")
def start_acquisition(req: StartRequest):
    global task_proc
    if task_proc and task_proc.poll() is None:
        raise HTTPException(
            status_code=400, detail="Acquisition already running.")

    # Build the command line
    cmd = [
        "python", os.path.join(os.getcwd(), "agent", "acquisition_client.py"),
        "--session-uid", req.session_uid,
        "--api-url", req.api_url,
        "--fps", str(req.fps)
    ]
    # Launch acquisition client with proper environment
    env = os.environ.copy()
    current_dir = os.getcwd()
    env['PYTHONPATH'] = current_dir + ':' + env.get('PYTHONPATH', '')
    task_proc = subprocess.Popen(cmd, env=env, cwd=current_dir)
    return {"status": "acquisition_started", "pid": task_proc.pid}


@app.post("/stop")
def stop_acquisition():
    global task_proc
    if not task_proc or task_proc.poll() is not None:
        raise HTTPException(
            status_code=400, detail="No acquisition in progress.")

    # Terminate the process
    task_proc.terminate()
    try:
        task_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if task_proc:  # Check if task_proc is still not None
            task_proc.kill()
    finally:
        task_proc = None
    return {"status": "acquisition_stopped"}


@app.get("/status")
def status():
    if task_proc and task_proc.poll() is None:
        return {"status": "running", "pid": task_proc.pid}
    return {"status": "stopped"}


@app.post("/calibrate/start")
def calibrate_start():
    from app.acquisition.camera_manager import CameraManager
    from app.acquisition.mediapipe_adapter import MediaPipeAdapter

    # Initialize calibration state
    app.state.cal_data = []
    # Start camera for calibration
    cam = CameraManager()
    adapter = MediaPipeAdapter()
    cam.start_camera()
    adapter.initialize()
    app.state.cal_camera = cam
    app.state.cal_adapter = adapter
    return {"status": "calibration_started"}


@app.post("/calibrate/point")
def calibrate_point(req: CalPointRequest):
    cam = app.state.cal_camera
    adapter = app.state.cal_adapter
    if cam is None or adapter is None:
        raise HTTPException(status_code=400, detail="Calibration not started.")
    pts = []
    for _ in range(req.samples):
        frame = cam.get_frame()
        res = adapter.analyze_frame(frame)
        centers = res.get("eye_centers", [])
        if centers:
            xs = [c[0] for c in centers]
            ys = [c[1] for c in centers]
            pts.append((sum(xs) / len(xs), sum(ys) / len(ys)))
        time.sleep(req.duration / req.samples)
    if not pts:
        raise HTTPException(status_code=500, detail="No eye data captured.")
    mean_x = sum([p[0] for p in pts]) / len(pts)
    mean_y = sum([p[1] for p in pts]) / len(pts)
    app.state.cal_data.append((req.x, req.y, mean_x, mean_y))
    result = {
        "screen_x": req.x,
        "screen_y": req.y,
        "measured_x": mean_x,
        "measured_y": mean_y,
    }
    try:
        requests.post(
            f"http://localhost:8000/session/{req.session_uid}/calibration/point",
            json=result,
            timeout=1
        )
    except requests.RequestException:
        pass
    return result


@app.post("/calibrate/finish")
def calibrate_finish():
    data = app.state.cal_data
    cam = app.state.cal_camera
    # Stop calibration camera
    if cam:
        cam.release_camera()
    if not data or len(data) < 3:
        raise HTTPException(
            status_code=400, detail="At least 3 calibration points required."
        )
    raw = np.array([[d[2], d[3]] for d in data])  # measured
    scr = np.array([[d[0], d[1]] for d in data])  # screen
    ones = np.ones((raw.shape[0], 1))
    X = np.hstack([raw, ones])  # Nx3
    params_x, _, _, _ = np.linalg.lstsq(X, scr[:, 0], rcond=None)
    params_y, _, _, _ = np.linalg.lstsq(X, scr[:, 1], rcond=None)
    A = [[params_x[0], params_x[1]], [params_y[0], params_y[1]]]  # 2x2
    b = [params_x[2], params_y[2]]
    transform = {"A": A, "b": b}

    with open(os.path.join(os.path.dirname(__file__), "calibration.json"), "w") as f:
        json.dump(transform, f)
    return transform
