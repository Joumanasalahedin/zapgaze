import subprocess
import threading
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import os
import numpy as np
import requests
import json
import time
import sys
import uuid

app = FastAPI(title="Local Acquisition Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

task_proc = None
task_thread = None
heartbeat_thread = None
agent_id = str(uuid.uuid4())  # Unique agent identifier

app.state.cal_data = []
app.state.cal_camera = None
app.state.cal_adapter = None


def send_heartbeat():
    """Send periodic heartbeat to backend"""
    backend_url = os.getenv("BACKEND_URL", "http://20.74.82.26:8000")
    while True:
        try:
            requests.post(
                f"{backend_url}/agent/heartbeat",
                json={"agent_id": agent_id},
                timeout=2,
            )
        except requests.RequestException:
            pass  # Silently fail - backend might be down
        time.sleep(15)  # Send heartbeat every 15 seconds


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Register with backend on startup
    backend_url = os.getenv("BACKEND_URL", "http://20.74.82.26:8000")
    try:
        requests.post(
            f"{backend_url}/agent/register",
            json={"agent_id": agent_id},
            timeout=5,
        )
        print(f"✅ Registered with backend: {backend_url}")
    except requests.RequestException as e:
        print(f"⚠️  Could not register with backend: {e}")
        print("   Agent will continue running, but frontend may not detect it.")

    # Start heartbeat thread
    global heartbeat_thread
    heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
    heartbeat_thread.start()

    yield

    # Unregister on shutdown
    try:
        requests.delete(
            f"{backend_url}/agent/unregister",
            params={"agent_id": agent_id},
            timeout=2,
        )
    except requests.RequestException:
        pass


class StartRequest(BaseModel):
    session_uid: str
    api_url: str = os.getenv(
        "BACKEND_URL", "http://20.74.82.26:8000") + "/acquisition/batch"
    fps: float = 20.0


class CalPointRequest(BaseModel):
    session_uid: str
    x: float
    y: float
    duration: float = 1.0
    samples: int = 30


def run_acquisition_client(session_uid, api_url, fps):
    """Run acquisition client in a thread"""
    try:
        from agent.acquisition_client import run_acquisition

        run_acquisition(session_uid, api_url, fps)
    except Exception as e:
        import logging

        logging.error(f"Acquisition client error: {e}")
        import traceback

        traceback.print_exc()


@app.post("/start")
def start_acquisition(req: StartRequest):
    global task_proc, task_thread

    # Check if already running (either subprocess or thread)
    if task_thread and task_thread.is_alive():
        raise HTTPException(
            status_code=400, detail="Acquisition already running.")
    if task_proc and task_proc.poll() is None:
        raise HTTPException(
            status_code=400, detail="Acquisition already running.")

    # Check if we're running as a standalone executable (PyInstaller)
    if getattr(sys, "frozen", False) or not os.path.exists(
        os.path.join(os.getcwd(), "agent", "acquisition_client.py")
    ):
        # Running as executable - use thread
        task_thread = threading.Thread(
            target=run_acquisition_client,
            args=(req.session_uid, req.api_url, req.fps),
            daemon=True,
        )
        task_thread.start()
        return {"status": "acquisition_started", "mode": "thread"}
    else:
        # Running as script - use subprocess (original method)
        cmd = [
            "python",
            os.path.join(os.getcwd(), "agent", "acquisition_client.py"),
            "--session-uid",
            req.session_uid,
            "--api-url",
            req.api_url,
            "--fps",
            str(req.fps),
        ]
        env = os.environ.copy()
        current_dir = os.getcwd()
        env["PYTHONPATH"] = current_dir + ":" + env.get("PYTHONPATH", "")
        task_proc = subprocess.Popen(cmd, env=env, cwd=current_dir)
        return {
            "status": "acquisition_started",
            "pid": task_proc.pid,
            "mode": "subprocess",
        }


@app.post("/stop")
def stop_acquisition():
    global task_proc, task_thread

    # Stop thread mode
    if task_thread and task_thread.is_alive():
        # Thread will stop when acquisition_client exits (KeyboardInterrupt handling)
        # We can't directly kill a thread, but the acquisition loop should check a flag
        # For now, we'll just mark it as stopped
        task_thread = None
        return {"status": "acquisition_stopped", "mode": "thread"}

    # Stop subprocess mode
    if task_proc and task_proc.poll() is None:
        task_proc.terminate()
        try:
            task_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            if task_proc:
                task_proc.kill()
        finally:
            task_proc = None
        return {"status": "acquisition_stopped", "mode": "subprocess"}

    raise HTTPException(status_code=400, detail="No acquisition in progress.")


@app.get("/")
def root():
    """Health check endpoint - confirms agent server is running"""
    return {
        "status": "agent_server_running",
        "agent_url": "http://localhost:9000",
        "backend_url": os.getenv("BACKEND_URL", "http://20.74.82.26:8000"),
    }


@app.get("/status")
def status():
    """Status of acquisition task (not agent server)"""
    # Check thread mode
    if task_thread and task_thread.is_alive():
        return {"status": "running", "mode": "thread"}
    # Check subprocess mode
    if task_proc and task_proc.poll() is None:
        return {"status": "running", "pid": task_proc.pid, "mode": "subprocess"}
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
    backend_url = os.getenv("BACKEND_URL", "http://20.74.82.26:8000")
    try:
        requests.post(
            f"{backend_url}/session/{req.session_uid}/calibration/point",
            json=result,
            timeout=1,
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
