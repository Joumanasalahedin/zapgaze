import subprocess
import signal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI(title="Local Acquisition Agent")

task_proc = None


class StartRequest(BaseModel):
    session_uid: str
    user_id: int
    api_url: str = "http://localhost:8000/acquisition/batch"
    fps: float = 20.0


@app.post("/start")
def start_acquisition(req: StartRequest):
    global task_proc
    if task_proc and task_proc.poll() is None:
        raise HTTPException(
            status_code=400, detail="Acquisition already running.")

    # Build the command line
    cmd = [
        "python", os.path.join(os.getcwd(), "acquisition_client.py"),
        "--user-id", str(req.user_id),
        "--session-uid", req.session_uid,
        "--api-url", req.api_url,
        "--fps", str(req.fps)
    ]
    # Launch acquisition client
    task_proc = subprocess.Popen(cmd)
    return {"status": "acquisition_started", "pid": task_proc.pid}


@app.post("/stop")
def stop_acquisition():
    global task_proc
    if not task_proc or task_proc.poll() is not None:
        raise HTTPException(
            status_code=400, detail="No acquisition in progress.")
    # Terminate the process\    task_proc.terminate()
    try:
        task_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        task_proc.kill()
    finally:
        task_proc = None
    return {"status": "acquisition_stopped"}


@app.get("/status")
def status():
    if task_proc and task_proc.poll() is None:
        return {"status": "running", "pid": task_proc.pid}
    return {"status": "stopped"}
