import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db import models, database
from app.security import verify_frontend_api_key
import time

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SessionStartRequest(BaseModel):
    session_uid: Optional[str] = None


class SessionStopRequest(BaseModel):
    session_uid: str


@router.post("/start")
@limiter.limit("30/minute")
def session_start(
    request: Request,
    req: SessionStartRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_frontend_api_key),
):
    if req.session_uid:
        sess = db.query(models.Session).filter_by(session_uid=req.session_uid).first()
        if not sess:
            raise HTTPException(status_code=404, detail="Session UID not found.")
        return {"session_uid": sess.session_uid}

    new_uid = str(uuid.uuid4())
    sess = models.Session(session_uid=new_uid, user_id=None)
    db.add(sess)
    db.commit()
    db.refresh(sess)
    return {"session_uid": sess.session_uid}


def _stop_agent_acquisition(agent_id_to_stop: str):
    """Helper function to stop agent acquisition and unregister agent (non-blocking, fails silently)"""
    try:
        from app.api import agent as agent_module
        from datetime import datetime, timedelta

        now = datetime.now()
        timeout = timedelta(seconds=30)

        agent_key = None
        if agent_id_to_stop in agent_module.registered_agents:
            last_heartbeat = agent_module.registered_agents[agent_id_to_stop]
            if now - last_heartbeat <= timeout:
                agent_key = agent_id_to_stop

        if not agent_key:
            active_agents = [
                key
                for key, last_heartbeat in agent_module.registered_agents.items()
                if now - last_heartbeat <= timeout
            ]
            if active_agents:
                agent_key = active_agents[0]
                print(
                    f"⚠️  Agent {agent_id_to_stop} not found, using active agent {agent_key}"
                )

        if not agent_key:
            print(
                f"⚠️  No active agent found to stop acquisition (looked for: {agent_id_to_stop})"
            )
            return

        command_id = str(uuid.uuid4())
        command = {
            "command_id": command_id,
            "type": "stop_acquisition",
            "params": {},
        }

        if agent_key not in agent_module.agent_commands:
            agent_module.agent_commands[agent_key] = []
        agent_module.agent_commands[agent_key].append(command)
        print(f"📤 Queued stop acquisition command {command_id} for agent {agent_key}")

        for other_key in active_agents:
            if other_key != agent_key:
                if other_key not in agent_module.agent_commands:
                    agent_module.agent_commands[other_key] = []
                agent_module.agent_commands[other_key].append(command)
                print(f"📤 Also queued stop command {command_id} for agent {other_key}")

        import threading

        def stop_agent_after_delay():
            time.sleep(2)
            agent_module.stopped_agents.add(agent_key)
            if agent_key in agent_module.registered_agents:
                del agent_module.registered_agents[agent_key]
            print(
                f"🔌 Marked agent {agent_key} as stopped - it will stop sending heartbeats"
            )

        threading.Thread(target=stop_agent_after_delay, daemon=True).start()

    except Exception as e:
        print(f"⚠️  Failed to stop agent acquisition: {e}")
        import traceback

        traceback.print_exc()


@router.post("/stop")
@limiter.limit("30/minute")
def session_stop(
    request: Request,
    req: SessionStopRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_frontend_api_key),
):
    sess = (
        db.query(models.Session)
        .filter_by(session_uid=req.session_uid, status="active")
        .first()
    )
    if not sess:
        raise HTTPException(
            status_code=404, detail="No active session found with this session_uid."
        )

    _stop_agent_acquisition(sess.session_uid)

    sess.stopped_at = datetime.utcnow()
    sess.status = "stopped"
    db.commit()
    return {
        "status": "session_stopped",
        "session_uid": sess.session_uid,
        "stopped_at": sess.stopped_at.isoformat(),
    }
