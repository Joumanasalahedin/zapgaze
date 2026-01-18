import json
import os
import subprocess
import sys
import threading
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict

import numpy as np
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Global variables
task_proc = None
task_thread = None
heartbeat_thread = None
agent_id = str(uuid.uuid4())  # Unique agent identifier
current_session_uid = None  # Track the current session UID for heartbeats
acquisition_stop_flag = threading.Event()  # Flag to signal acquisition to stop
acquisition_camera = None

try:
    from agent.agent_config import AGENT_API_KEY as EMBEDDED_API_KEY

    # Use embedded key, but allow override via environment variable for testing
    AGENT_API_KEY = os.getenv("AGENT_API_KEY", EMBEDDED_API_KEY)
except ImportError:
    # agent_config.py doesn't exist (development mode)
    # Use environment variable or default development key
    AGENT_API_KEY = os.getenv(
        "AGENT_API_KEY", "zapgaze-agent-secret-key-change-in-production"
    )


def send_heartbeat():
    """Send periodic heartbeat to backend and execute any pending commands"""
    backend_url = os.getenv("BACKEND_URL", "http://20.74.82.26:8000")
    while True:
        try:
            # Send both agent_id and session_uid (if available) so backend can match by either
            heartbeat_data = {"agent_id": agent_id}
            if current_session_uid:
                heartbeat_data["session_uid"] = current_session_uid

            response = requests.post(
                f"{backend_url}/agent/heartbeat",
                json=heartbeat_data,
                headers={"X-API-Key": AGENT_API_KEY},
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()

                # Check if backend told us to stop
                if data.get("status") == "stopped":
                    print(
                        f"🛑 Backend requested agent to stop: {data.get('message', 'Session stopped')}"
                    )
                    print("   Stopping heartbeat loop...")
                    break  # Exit the heartbeat loop

                # Check for pending commands
                commands = data.get("commands", [])
                if commands:
                    print(f"📥 Received {len(commands)} command(s) from backend")
                for command in commands:
                    print(f"⚙️  Executing command: {command.get('type')}")
                    # Execute commands in a separate thread so they don't block heartbeat
                    command_thread = threading.Thread(
                        target=execute_command,
                        args=(command, backend_url),
                        daemon=True,
                    )
                    command_thread.start()
        except requests.RequestException as e:
            # Log error for debugging
            print(f"⚠️  Heartbeat error: {e}")
            pass  # Silently fail - backend might be down
        time.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Register with backend on startup
    backend_url = os.getenv("BACKEND_URL", "http://20.74.82.26:8000")
    try:
        requests.post(
            f"{backend_url}/agent/register",
            json={"agent_id": agent_id},
            headers={"X-API-Key": AGENT_API_KEY},
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
            headers={"X-API-Key": AGENT_API_KEY},
            timeout=2,
        )
    except requests.RequestException:
        pass


def execute_command(command: dict, backend_url: str):
    """Execute a command from the backend"""
    global task_proc, task_thread, acquisition_stop_flag, current_session_uid, acquisition_camera  # Declare all globals at the top

    command_id = command.get("command_id")
    command_type = command.get("type")
    params = command.get("params", {})

    try:
        if command_type == "calibrate_start":
            from app.acquisition.camera_manager import CameraManager
            from app.acquisition.mediapipe_adapter import MediaPipeAdapter

            app.state.cal_data = []
            cam = CameraManager()
            adapter = MediaPipeAdapter()
            cam.start_camera()
            adapter.initialize()
            app.state.cal_camera = cam
            app.state.cal_adapter = adapter

            result = {"status": "calibration_started"}

        elif command_type == "calibrate_point":
            cam = app.state.cal_camera
            adapter = app.state.cal_adapter
            if cam is None or adapter is None:
                raise Exception("Calibration not started")

            pts = []
            samples = params.get("samples", 30)
            duration = params.get("duration", 1.0)
            max_attempts = samples * 2  # Allow up to 2x samples in case of failures
            attempt = 0
            successful_samples = 0

            print(
                f"📸 Starting calibration point capture: {samples} samples over {duration}s"
            )

            start_time = time.time()
            timeout = duration + 5  # Add 5 second buffer for processing

            while successful_samples < samples and attempt < max_attempts:
                # Check for timeout
                if time.time() - start_time > timeout:
                    print(f"⏱️  Calibration point timeout after {timeout}s")
                    break

                try:
                    # Try to get frame with a timeout check
                    frame = cam.get_frame()
                    if frame is None:
                        print(f"⚠️  Failed to get frame (attempt {attempt + 1})")
                        attempt += 1
                        time.sleep(0.05)  # Short delay before retry
                        continue

                    res = adapter.analyze_frame(frame)
                    centers = res.get("eye_centers", [])
                    if centers and len(centers) >= 2:
                        xs = [c[0] for c in centers]
                        ys = [c[1] for c in centers]
                        pts.append((sum(xs) / len(xs), sum(ys) / len(ys)))
                        successful_samples += 1
                        if successful_samples % 10 == 0:
                            print(
                                f"📊 Collected {successful_samples}/{samples} samples"
                            )
                    else:
                        # No eyes detected, but continue
                        pass

                    # Sleep to maintain timing
                    time.sleep(duration / samples)
                    attempt += 1

                except Exception as e:
                    print(f"⚠️  Error during calibration sample {attempt + 1}: {e}")
                    attempt += 1
                    time.sleep(0.05)  # Short delay before retry
                    # Continue trying - don't fail on individual frame errors

            if not pts:
                raise Exception(f"No eye data captured after {attempt} attempts")

            mean_x = sum([p[0] for p in pts]) / len(pts)
            mean_y = sum([p[1] for p in pts]) / len(pts)
            app.state.cal_data.append((params["x"], params["y"], mean_x, mean_y))

            result = {
                "screen_x": params["x"],
                "screen_y": params["y"],
                "measured_x": mean_x,
                "measured_y": mean_y,
            }

            print(
                f"✅ Calibration point completed: ({params['x']}, {params['y']}) -> ({mean_x:.2f}, {mean_y:.2f})"
            )

            # Also send to backend
            try:
                requests.post(
                    f"{backend_url}/session/{params.get('session_uid')}/calibration/point",
                    json=result,
                    timeout=1,
                )
            except:
                pass

        elif command_type == "calibrate_finish":
            data = app.state.cal_data
            cam = app.state.cal_camera
            if cam:
                cam.release_camera()
            if not data or len(data) < 3:
                raise Exception("At least 3 calibration points required")

            raw = np.array([[d[2], d[3]] for d in data])
            scr = np.array([[d[0], d[1]] for d in data])
            ones = np.ones((raw.shape[0], 1))
            X = np.hstack([raw, ones])
            params_x, _, _, _ = np.linalg.lstsq(X, scr[:, 0], rcond=None)
            params_y, _, _, _ = np.linalg.lstsq(X, scr[:, 1], rcond=None)
            A = [[params_x[0], params_x[1]], [params_y[0], params_y[1]]]
            b = [params_x[2], params_y[2]]
            transform = {"A": A, "b": b}

            with open(
                os.path.join(os.path.dirname(__file__), "calibration.json"), "w"
            ) as f:
                json.dump(transform, f)

            result = transform

        elif command_type == "start_acquisition":
            # Start acquisition using the same logic as the /start endpoint
            # Check if already running
            if task_thread and task_thread.is_alive():
                raise Exception("Acquisition already running")
            if task_proc and task_proc.poll() is None:
                raise Exception("Acquisition already running")

            session_uid = params.get("session_uid")
            api_url = params.get("api_url", f"{backend_url}/acquisition/batch")
            fps = params.get("fps", 20.0)

            # Track the current session UID for heartbeats
            current_session_uid = session_uid

            # Check if we're running as a standalone executable (PyInstaller)
            if getattr(sys, "frozen", False) or not os.path.exists(
                os.path.join(os.getcwd(), "agent", "acquisition_client.py")
            ):
                # Running as executable - use thread
                # Reset stop flag before starting new acquisition
                acquisition_stop_flag.clear()

                task_thread = threading.Thread(
                    target=run_acquisition_client,
                    args=(session_uid, api_url, fps),
                    daemon=True,
                )
                task_thread.start()
                result = {"status": "acquisition_started", "mode": "thread"}
            else:
                # Running as script - use subprocess
                cmd = [
                    "python",
                    os.path.join(os.getcwd(), "agent", "acquisition_client.py"),
                    "--session-uid",
                    session_uid,
                    "--api-url",
                    api_url,
                    "--fps",
                    str(fps),
                ]
                env = os.environ.copy()
                current_dir = os.getcwd()
                env["PYTHONPATH"] = current_dir + ":" + env.get("PYTHONPATH", "")
                task_proc = subprocess.Popen(cmd, env=env, cwd=current_dir)
                result = {
                    "status": "acquisition_started",
                    "pid": task_proc.pid,
                    "mode": "subprocess",
                }

        elif command_type == "stop_acquisition":
            # Stop acquisition using the same method as calibration_finish - directly release camera
            print(
                f"🛑 Stop command received. task_thread: {task_thread}, is_alive: {task_thread.is_alive() if task_thread else 'N/A'}"
            )
            print(f"🛑 app.state.acquisition_camera: {app.state.acquisition_camera}")
            # Stop thread mode - use same approach as calibration: directly release camera
            if task_thread and task_thread.is_alive():
                # Directly release camera (like calibration_finish does)
                # This will cause camera.get_frame() to fail, breaking the loop immediately
                # Set stop flag first (as backup)
                acquisition_stop_flag.set()
                print("🛑 Set stop flag")

                # Directly release camera (like calibration_finish does)
                # This will cause camera.get_frame() to fail, breaking the loop immediately
                cam = app.state.acquisition_camera
                if cam:
                    print(
                        "🛑 Directly releasing acquisition camera (like calibration_finish)"
                    )
                    try:
                        cam.release_camera()
                        app.state.acquisition_camera = None
                        print(
                            "✅ Camera released directly - loop should exit on next get_frame()"
                        )
                    except Exception as e:
                        print(f"⚠️  Error releasing camera: {e}")
                        import traceback

                        traceback.print_exc()
                        # Stop flag already set, so loop will exit on next check
                else:
                    print("⚠️  No acquisition_camera in app.state, using stop flag only")

                result = {"status": "acquisition_stopped", "mode": "thread"}

                # Note: We don't set task_thread = None here because the thread might still be
                # finishing up (flushing buffer, releasing camera). The thread will exit on its own.
            # Stop subprocess mode
            elif task_proc and task_proc.poll() is None:
                task_proc.terminate()
                try:
                    task_proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    if task_proc:
                        task_proc.kill()
                finally:
                    task_proc = None
                result = {"status": "acquisition_stopped", "mode": "subprocess"}
            else:
                # Acquisition already stopped or never started - this is fine, just return success
                print(
                    "ℹ️  Stop command received but no acquisition is running (already stopped)"
                )
                result = {"status": "acquisition_stopped", "mode": "already_stopped"}

            # Clear session UID when acquisition stops
            current_session_uid = None
        else:
            raise Exception(f"Unknown command type: {command_type}")

        # Report success
        print(f"✅ Command {command_id} executed successfully")
        try:
            requests.post(
                f"{backend_url}/agent/heartbeat",
                json={
                    "agent_id": agent_id,
                    "command_result": {
                        "command_id": command_id,
                        "result": result,
                        "success": True,
                    },
                },
                headers={"X-API-Key": AGENT_API_KEY},
                timeout=2,
            )
            print(f"📤 Reported success for command {command_id}")
        except Exception as e:
            print(f"❌ Failed to report command result: {e}")
    except Exception as e:
        # Report error
        try:
            requests.post(
                f"{backend_url}/agent/heartbeat",
                json={
                    "agent_id": agent_id,
                    "command_result": {
                        "command_id": command_id,
                        "result": None,
                        "success": False,
                        "error": str(e),
                    },
                },
                headers={"X-API-Key": AGENT_API_KEY},
                timeout=2,
            )
        except:
            pass


app = FastAPI(title="Local Acquisition Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.state.cal_data = []
app.state.cal_camera = None
app.state.cal_adapter = None
app.state.acquisition_camera = None


class StartRequest(BaseModel):
    session_uid: str = Field(
        ..., min_length=1, description="Session UID for acquisition"
    )
    api_url: str = Field(
        default_factory=lambda: os.getenv("BACKEND_URL", "http://20.74.82.26:8000")
        + "/acquisition/batch",
        pattern=r"^https?://",
        description="Backend API URL for data submission",
    )
    fps: float = Field(20.0, gt=0, le=120, description="Frames per second (0-120)")


class CalPointRequest(BaseModel):
    session_uid: str = Field(
        ..., min_length=1, description="Session UID for calibration"
    )
    x: float = Field(
        ..., ge=0, description="X coordinate (percentage 0-100 or normalized 0-1)"
    )
    y: float = Field(
        ..., ge=0, description="Y coordinate (percentage 0-100 or normalized 0-1)"
    )
    duration: float = Field(1.0, gt=0, le=10, description="Duration in seconds (0-10)")
    samples: int = Field(
        30, gt=0, le=1000, description="Number of samples to collect (1-1000)"
    )


def run_acquisition_client(session_uid, api_url, fps):
    """Run acquisition client in a thread"""
    global acquisition_stop_flag, acquisition_camera

    try:
        from agent.acquisition_client import run_acquisition

        # Reset stop flag before starting
        acquisition_stop_flag.clear()
        acquisition_camera = None  # Clear any previous reference

        # Pass stop flag to acquisition function, and get camera reference back
        # We'll modify run_acquisition to store the camera instance globally
        # List to hold camera reference (mutable, for backup)
        camera_ref_holder = [None]
        run_acquisition(
            session_uid,
            api_url,
            fps,
            stop_event=acquisition_stop_flag,
            camera_ref_holder=camera_ref_holder,
        )

        # Note: acquisition_camera should be set inside run_acquisition before the loop starts
        # If it wasn't set, try to get it from camera_ref_holder (though this won't work
        # since run_acquisition blocks, but it's here for completeness)
    except Exception as e:
        import logging

        logging.error(f"Acquisition client error: {e}")
        import traceback

        traceback.print_exc()


@app.post("/start")
def start_acquisition(req: StartRequest) -> Dict[str, Any]:
    """Start acquisition for a session"""
    global task_proc, task_thread, acquisition_stop_flag, current_session_uid

    # Check if already running (either subprocess or thread)
    if task_thread and task_thread.is_alive():
        raise HTTPException(status_code=400, detail="Acquisition already running.")
    if task_proc and task_proc.poll() is None:
        raise HTTPException(status_code=400, detail="Acquisition already running.")

    # Track the current session UID for heartbeats
    current_session_uid = req.session_uid

    # Check if we're running as a standalone executable (PyInstaller)
    if getattr(sys, "frozen", False) or not os.path.exists(
        os.path.join(os.getcwd(), "agent", "acquisition_client.py")
    ):
        # Running as executable - use thread
        # Reset stop flag before starting new acquisition
        acquisition_stop_flag.clear()

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
def stop_acquisition() -> Dict[str, Any]:
    """Stop acquisition"""
    global task_proc, task_thread, acquisition_stop_flag, current_session_uid

    # Stop thread mode
    if task_thread and task_thread.is_alive():
        # Set stop flag to signal the acquisition loop to exit
        acquisition_stop_flag.set()
        print("🛑 Set stop flag for acquisition thread")
        # Wait a moment for the thread to see the flag
        time.sleep(0.5)
        task_thread = None
        current_session_uid = None  # Clear session UID when stopped
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
            current_session_uid = None  # Clear session UID when stopped
        return {"status": "acquisition_stopped", "mode": "subprocess"}

    raise HTTPException(status_code=400, detail="No acquisition in progress.")


@app.get("/")
def root() -> Dict[str, Any]:
    """Health check endpoint - confirms agent server is running"""
    return {
        "status": "agent_server_running",
        "agent_url": "http://localhost:9000",
        "backend_url": os.getenv("BACKEND_URL", "http://20.74.82.26:8000"),
    }


@app.get("/status")
def status() -> Dict[str, Any]:
    """Status of acquisition task (not agent server)"""
    # Check thread mode
    if task_thread and task_thread.is_alive():
        return {"status": "running", "mode": "thread"}
    # Check subprocess mode
    if task_proc and task_proc.poll() is None:
        return {"status": "running", "pid": task_proc.pid, "mode": "subprocess"}
    return {"status": "stopped"}


@app.post("/calibrate/start")
def calibrate_start() -> Dict[str, Any]:
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
def calibrate_point(req: CalPointRequest) -> Dict[str, Any]:
    """Record a calibration point"""
    cam = app.state.cal_camera
    adapter = app.state.cal_adapter
    if cam is None or adapter is None:
        raise HTTPException(
            status_code=400,
            detail="Calibration not started. Call /calibrate/start first.",
        )
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
            headers={"X-API-Key": AGENT_API_KEY},
            timeout=1,
        )
    except requests.RequestException:
        pass
    return result


@app.post("/calibrate/finish")
def calibrate_finish() -> Dict[str, Any]:
    """Finish calibration and compute transformation matrix"""
    data = app.state.cal_data
    cam = app.state.cal_camera
    if cam:
        cam.release_camera()
        app.state.cal_camera = None
        app.state.cal_adapter = None
    if not data or len(data) < 3:
        raise HTTPException(
            status_code=400,
            detail="At least 3 calibration points required. Current points: "
            + str(len(data) if data else 0),
        )
    raw = np.array([[d[2], d[3]] for d in data])
    scr = np.array([[d[0], d[1]] for d in data])
    ones = np.ones((raw.shape[0], 1))
    X = np.hstack([raw, ones])
    params_x, _, _, _ = np.linalg.lstsq(X, scr[:, 0], rcond=None)
    params_y, _, _, _ = np.linalg.lstsq(X, scr[:, 1], rcond=None)
    A = [[params_x[0], params_x[1]], [params_y[0], params_y[1]]]
    b = [params_x[2], params_y[2]]
    transform = {"A": A, "b": b}

    with open(os.path.join(os.path.dirname(__file__), "calibration.json"), "w") as f:
        json.dump(transform, f)
    return transform
