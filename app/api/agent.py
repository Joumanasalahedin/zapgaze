"""
Agent registration and status API
Allows agents to register with the backend and frontend to check agent status
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import time
import uuid
from app.security import verify_agent_api_key, verify_frontend_api_key

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)

registered_agents: Dict[str, datetime] = {}

agent_commands: Dict[str, list] = {}

command_results: Dict[str, dict] = {}

stopped_agents: set = set()

HEARTBEAT_TIMEOUT = timedelta(seconds=30)


class AgentRegistration(BaseModel):
    session_uid: Optional[str] = None
    agent_id: Optional[str] = None


class AgentCommandResult(BaseModel):
    command_id: str
    result: Any
    success: bool
    error: Optional[str] = None


class AgentHeartbeat(BaseModel):
    session_uid: Optional[str] = None
    agent_id: Optional[str] = None
    command_result: Optional[AgentCommandResult] = None


class CalibrationPointRequest(BaseModel):
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


class StartAcquisitionRequest(BaseModel):
    session_uid: str = Field(
        ..., min_length=1, description="Session UID for acquisition"
    )
    api_url: str = Field(
        ..., pattern=r"^https?://", description="Backend API URL for data submission"
    )
    fps: float = Field(20.0, gt=0, le=120, description="Frames per second (0-120)")


@router.post("/register")
@limiter.limit("10/minute")
def register_agent(
    request: Request,
    registration: AgentRegistration,
    api_key: str = Depends(verify_agent_api_key),
) -> Dict[str, Any]:
    """Register an agent with the backend (requires API key)"""
    agent_key = registration.session_uid or registration.agent_id or "default"
    registered_agents[agent_key] = datetime.now()
    return {
        "status": "registered",
        "agent_key": agent_key,
        "timestamp": registered_agents[agent_key].isoformat(),
    }


@router.post("/heartbeat")
@limiter.limit("60/minute")
def agent_heartbeat(
    request: Request,
    heartbeat: AgentHeartbeat,
    api_key: str = Depends(verify_agent_api_key),
) -> Dict[str, Any]:
    """Update agent heartbeat and return pending commands (requires API key)"""
    session_uid = heartbeat.session_uid
    agent_id = heartbeat.agent_id
    agent_key = session_uid or agent_id or "default"

    if (
        agent_key in stopped_agents
        or (session_uid and session_uid in stopped_agents)
        or (agent_id and agent_id in stopped_agents)
    ):
        print(f"🛑 Agent {agent_key} is in stopped_agents, telling it to stop")
        return {
            "status": "stopped",
            "message": "Agent unregistered after session stop. Please stop sending heartbeats.",
        }

    registered_agents[agent_key] = datetime.now()
    if session_uid and session_uid != agent_key:
        registered_agents[session_uid] = datetime.now()
    if agent_id and agent_id != agent_key:
        registered_agents[agent_id] = datetime.now()

    if heartbeat.command_result:
        result = heartbeat.command_result
        command_id = result.command_id
        if command_id:
            command_results[command_id] = {
                "result": result.result,
                "success": result.success,
                "error": result.error,
            }

    pending_commands = []
    keys_to_check = [agent_key]
    if session_uid and session_uid != agent_key:
        keys_to_check.append(session_uid)
    if agent_id and agent_id != agent_key:
        keys_to_check.append(agent_id)

    for key in keys_to_check:
        if key in agent_commands:
            pending_commands.extend(agent_commands[key])
            agent_commands[key] = []

    return {
        "status": "ok",
        "timestamp": registered_agents[agent_key].isoformat(),
        "commands": pending_commands,
    }


@router.get("/status")
@limiter.limit("30/minute")
def get_agent_status(
    request: Request, session_uid: Optional[str] = None
) -> Dict[str, Any]:
    """Check if an agent is registered and active (public endpoint, no API key required)"""
    now = datetime.now()
    stale_keys = [
        key
        for key, last_heartbeat in registered_agents.items()
        if now - last_heartbeat > HEARTBEAT_TIMEOUT
    ]
    for key in stale_keys:
        del registered_agents[key]

    if session_uid:
        if session_uid in registered_agents:
            last_heartbeat = registered_agents[session_uid]
            if now - last_heartbeat <= HEARTBEAT_TIMEOUT:
                return {
                    "status": "connected",
                    "session_uid": session_uid,
                    "last_heartbeat": last_heartbeat.isoformat(),
                }
    else:
        active_agents = [
            key
            for key, last_heartbeat in registered_agents.items()
            if now - last_heartbeat <= HEARTBEAT_TIMEOUT
        ]
        if active_agents:
            return {
                "status": "connected",
                "active_agents": len(active_agents),
                "agent_keys": active_agents,
            }

    return {"status": "disconnected"}


@router.delete("/unregister")
@limiter.limit("10/minute")
def unregister_agent(
    request: Request,
    session_uid: Optional[str] = None,
    agent_id: Optional[str] = None,
    api_key: str = Depends(verify_agent_api_key),
) -> Dict[str, Any]:
    """Unregister an agent (requires API key)"""
    agent_key = session_uid or agent_id or "default"
    if agent_key in registered_agents:
        del registered_agents[agent_key]
        if agent_key in agent_commands:
            del agent_commands[agent_key]
        return {"status": "unregistered", "agent_key": agent_key}
    raise HTTPException(status_code=404, detail="Agent not found")


@router.post("/calibrate/start")
@limiter.limit("10/minute")
def proxy_calibrate_start(
    request: Request, api_key: str = Depends(verify_frontend_api_key)
) -> Dict[str, Any]:
    """Queue calibration start command for agent (requires API key)"""
    now = datetime.now()
    active_agents = [
        key
        for key, last_heartbeat in registered_agents.items()
        if now - last_heartbeat <= HEARTBEAT_TIMEOUT
    ]

    if not active_agents:
        raise HTTPException(
            status_code=503,
            detail=f"No active agent found. Registered agents: {list(registered_agents.keys())}",
        )

    agent_key = active_agents[0]
    command_id = str(uuid.uuid4())
    command = {
        "command_id": command_id,
        "type": "calibrate_start",
        "params": {},
    }

    if agent_key not in agent_commands:
        agent_commands[agent_key] = []
    agent_commands[agent_key].append(command)

    print(f"📤 Queued command {command_id} for agent {agent_key}")

    print(f"⏳ Waiting for command {command_id} result...")
    for i in range(100):
        time.sleep(0.1)
        if command_id in command_results:
            result = command_results.pop(command_id)
            print(f"✅ Received result for command {command_id}")
            if result["success"]:
                return result["result"]
            else:
                raise HTTPException(
                    status_code=500, detail=result.get("error", "Command failed")
                )
        if i % 10 == 0:
            print(f"⏳ Still waiting... ({i / 10:.1f}s)")

    print(f"❌ Timeout waiting for command {command_id}")
    raise HTTPException(
        status_code=504, detail="Command timeout - agent may not be responding"
    )


@router.post("/calibrate/point")
@limiter.limit("60/minute")
def proxy_calibrate_point(
    request: Request,
    data: CalibrationPointRequest,
    api_key: str = Depends(verify_frontend_api_key),
) -> Dict[str, Any]:
    """Queue calibration point command for agent (requires API key)"""
    now = datetime.now()
    active_agents = [
        key
        for key, last_heartbeat in registered_agents.items()
        if now - last_heartbeat <= HEARTBEAT_TIMEOUT
    ]

    if not active_agents:
        raise HTTPException(status_code=503, detail="No active agent found")

    agent_key = active_agents[0]
    command_id = str(uuid.uuid4())
    command = {
        "command_id": command_id,
        "type": "calibrate_point",
        "params": data.model_dump(),
    }

    if agent_key not in agent_commands:
        agent_commands[agent_key] = []
    agent_commands[agent_key].append(command)

    print(f"⏳ Waiting for command {command_id} result...")
    for i in range(150):
        time.sleep(0.1)
        if command_id in command_results:
            result = command_results.pop(command_id)
            print(f"✅ Received result for command {command_id}")
            if result["success"]:
                return result["result"]
            else:
                raise HTTPException(
                    status_code=500, detail=result.get("error", "Command failed")
                )
        if i % 10 == 0:
            print(f"⏳ Still waiting... ({i / 10:.1f}s)")

    print(f"❌ Timeout waiting for command {command_id}")
    raise HTTPException(
        status_code=504, detail="Command timeout - agent may not be responding"
    )


@router.post("/calibrate/finish")
@limiter.limit("10/minute")
def proxy_calibrate_finish(
    request: Request, api_key: str = Depends(verify_frontend_api_key)
) -> Dict[str, Any]:
    """Queue calibration finish command for agent (requires API key)"""
    now = datetime.now()
    active_agents = [
        key
        for key, last_heartbeat in registered_agents.items()
        if now - last_heartbeat <= HEARTBEAT_TIMEOUT
    ]

    if not active_agents:
        raise HTTPException(status_code=503, detail="No active agent found")

    agent_key = active_agents[0]
    command_id = str(uuid.uuid4())
    command = {
        "command_id": command_id,
        "type": "calibrate_finish",
        "params": {},
    }

    if agent_key not in agent_commands:
        agent_commands[agent_key] = []
    agent_commands[agent_key].append(command)

    for _ in range(30):
        time.sleep(0.1)
        if command_id in command_results:
            result = command_results.pop(command_id)
            if result["success"]:
                return result["result"]
            else:
                raise HTTPException(
                    status_code=500, detail=result.get("error", "Command failed")
                )

    raise HTTPException(status_code=504, detail="Command timeout")


@router.post("/start")
@limiter.limit("10/minute")
def proxy_start_acquisition(
    request: Request,
    data: StartAcquisitionRequest,
    api_key: str = Depends(verify_frontend_api_key),
) -> Dict[str, Any]:
    """Queue start acquisition command for agent (requires API key)"""
    now = datetime.now()
    active_agents = [
        key
        for key, last_heartbeat in registered_agents.items()
        if now - last_heartbeat <= HEARTBEAT_TIMEOUT
    ]

    if not active_agents:
        raise HTTPException(status_code=503, detail="No active agent found")

    agent_key = active_agents[0]
    command_id = str(uuid.uuid4())
    command = {
        "command_id": command_id,
        "type": "start_acquisition",
        "params": data.model_dump(),
    }

    if agent_key not in agent_commands:
        agent_commands[agent_key] = []
    agent_commands[agent_key].append(command)

    print(f"⏳ Waiting for command {command_id} result...")
    for i in range(50):
        time.sleep(0.1)
        if command_id in command_results:
            result = command_results.pop(command_id)
            print(f"✅ Received result for command {command_id}")
            if result["success"]:
                return result["result"]
            else:
                raise HTTPException(
                    status_code=500, detail=result.get("error", "Command failed")
                )
        if i % 10 == 0:
            print(f"⏳ Still waiting... ({i / 10:.1f}s)")

    print(f"❌ Timeout waiting for command {command_id}")
    raise HTTPException(
        status_code=504, detail="Command timeout - agent may not be responding"
    )


@router.post("/stop")
@limiter.limit("10/minute")
def proxy_stop_acquisition(
    request: Request, api_key: str = Depends(verify_frontend_api_key)
) -> Dict[str, Any]:
    """Queue stop acquisition command for agent (requires API key)"""
    now = datetime.now()
    active_agents = [
        key
        for key, last_heartbeat in registered_agents.items()
        if now - last_heartbeat <= HEARTBEAT_TIMEOUT
    ]

    if not active_agents:
        raise HTTPException(status_code=503, detail="No active agent found")

    command_id = str(uuid.uuid4())
    command = {
        "command_id": command_id,
        "type": "stop_acquisition",
        "params": {},
    }

    for agent_key in active_agents:
        if agent_key not in agent_commands:
            agent_commands[agent_key] = []
        agent_commands[agent_key].append(command)
        print(f"📤 Queued stop command {command_id} for agent key: {agent_key}")

    print(f"⏳ Waiting for command {command_id} result...")
    for i in range(50):
        time.sleep(0.1)
        if command_id in command_results:
            result = command_results.pop(command_id)
            print(f"✅ Received result for command {command_id}")
            if result["success"]:
                return result["result"]
            else:
                raise HTTPException(
                    status_code=500, detail=result.get("error", "Command failed")
                )
        if i % 10 == 0:
            print(f"⏳ Still waiting... ({i / 10:.1f}s)")

    print(f"❌ Timeout waiting for command {command_id}")
    raise HTTPException(
        status_code=504, detail="Command timeout - agent may not be responding"
    )
