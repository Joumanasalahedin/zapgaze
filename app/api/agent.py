"""
Agent registration and status API
Allows agents to register with the backend and frontend to check agent status
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import time
import uuid

router = APIRouter()

# In-memory store for registered agents
# Key: session_uid or user identifier, Value: last heartbeat timestamp
registered_agents: Dict[str, datetime] = {}

# Command queue for agents
# Key: agent_id, Value: list of pending commands
agent_commands: Dict[str, list] = {}

# Command results
# Key: command_id, Value: result
command_results: Dict[str, dict] = {}

# Agents that should stop sending heartbeats (unregistered after session stop)
stopped_agents: set = set()

# Heartbeat timeout - agent must send heartbeat within this time
HEARTBEAT_TIMEOUT = timedelta(seconds=30)


class AgentRegistration(BaseModel):
    session_uid: Optional[str] = None
    agent_id: Optional[str] = None  # Optional unique agent identifier


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
    session_uid: str = Field(..., min_length=1, description="Session UID for calibration")
    x: float = Field(..., ge=0, description="X coordinate (percentage 0-100 or normalized 0-1)")
    y: float = Field(..., ge=0, description="Y coordinate (percentage 0-100 or normalized 0-1)")
    duration: float = Field(1.0, gt=0, le=10, description="Duration in seconds (0-10)")
    samples: int = Field(30, gt=0, le=1000, description="Number of samples to collect (1-1000)")


class StartAcquisitionRequest(BaseModel):
    session_uid: str = Field(..., min_length=1, description="Session UID for acquisition")
    api_url: str = Field(..., pattern=r'^https?://', description="Backend API URL for data submission")
    fps: float = Field(20.0, gt=0, le=120, description="Frames per second (0-120)")


@router.post("/register")
def register_agent(registration: AgentRegistration) -> Dict[str, Any]:
    """Register an agent with the backend"""
    # Use session_uid or agent_id as the key
    agent_key = registration.session_uid or registration.agent_id or "default"
    registered_agents[agent_key] = datetime.now()
    return {
        "status": "registered",
        "agent_key": agent_key,
        "timestamp": registered_agents[agent_key].isoformat(),
    }


@router.post("/heartbeat")
def agent_heartbeat(heartbeat: AgentHeartbeat) -> Dict[str, Any]:
    """Update agent heartbeat and return pending commands"""
    session_uid = heartbeat.session_uid
    agent_id = heartbeat.agent_id
    agent_key = session_uid or agent_id or "default"

    # Check if agent was stopped (unregistered after session stop)
    # Check both session_uid and agent_id in case they're different
    if (
        agent_key in stopped_agents
        or (session_uid and session_uid in stopped_agents)
        or (agent_id and agent_id in stopped_agents)
    ):
        # Don't re-register, tell agent to stop
        print(f"🛑 Agent {agent_key} is in stopped_agents, telling it to stop")
        return {
            "status": "stopped",
            "message": "Agent unregistered after session stop. Please stop sending heartbeats.",
        }

    # Re-register agent (update timestamp)
    # Register with both keys if both are provided
    registered_agents[agent_key] = datetime.now()
    if session_uid and session_uid != agent_key:
        registered_agents[session_uid] = datetime.now()
    if agent_id and agent_id != agent_key:
        registered_agents[agent_id] = datetime.now()

    # Store command result if provided
    if heartbeat.command_result:
        result = heartbeat.command_result
        command_id = result.command_id
        if command_id:
            command_results[command_id] = {
                "result": result.result,
                "success": result.success,
                "error": result.error,
            }

    # Return pending commands for this agent
    # Check all possible keys (agent_key, session_uid, agent_id) to get commands
    pending_commands = []
    keys_to_check = [agent_key]
    if session_uid and session_uid != agent_key:
        keys_to_check.append(session_uid)
    if agent_id and agent_id != agent_key:
        keys_to_check.append(agent_id)

    # Collect commands from all keys and clear them
    for key in keys_to_check:
        if key in agent_commands:
            pending_commands.extend(agent_commands[key])
            agent_commands[key] = []  # Clear after returning

    return {
        "status": "ok",
        "timestamp": registered_agents[agent_key].isoformat(),
        "commands": pending_commands,
    }


@router.get("/status")
def get_agent_status(session_uid: Optional[str] = None) -> Dict[str, Any]:
    """Check if an agent is registered and active"""
    # Clean up stale agents
    now = datetime.now()
    stale_keys = [
        key
        for key, last_heartbeat in registered_agents.items()
        if now - last_heartbeat > HEARTBEAT_TIMEOUT
    ]
    for key in stale_keys:
        del registered_agents[key]

    # Check for specific session or any active agent
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
        # Check if any agent is active
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
def unregister_agent(session_uid: Optional[str] = None, agent_id: Optional[str] = None) -> Dict[str, Any]:
    """Unregister an agent"""
    agent_key = session_uid or agent_id or "default"
    if agent_key in registered_agents:
        del registered_agents[agent_key]
        # Clean up commands
        if agent_key in agent_commands:
            del agent_commands[agent_key]
        return {"status": "unregistered", "agent_key": agent_key}
    raise HTTPException(status_code=404, detail="Agent not found")


# Calibration proxy endpoints
@router.post("/calibrate/start")
def proxy_calibrate_start() -> Dict[str, Any]:
    """Queue calibration start command for agent"""
    # Get any active agent
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

    # Use the first active agent
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

    # Wait for result (polling)
    # Wait up to 10 seconds (agent polls every 1-2 seconds)
    print(f"⏳ Waiting for command {command_id} result...")
    for i in range(100):  # 100 * 0.1s = 10 seconds
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
        if i % 10 == 0:  # Log every second
            print(f"⏳ Still waiting... ({i/10:.1f}s)")

    print(f"❌ Timeout waiting for command {command_id}")
    raise HTTPException(
        status_code=504, detail="Command timeout - agent may not be responding"
    )


@router.post("/calibrate/point")
def proxy_calibrate_point(data: CalibrationPointRequest) -> Dict[str, Any]:
    """Queue calibration point command for agent"""
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

    # Wait for result (calibration point takes ~1-2 seconds to process)
    print(f"⏳ Waiting for command {command_id} result...")
    for i in range(150):  # 150 * 0.1s = 15 seconds (calibration takes time)
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
        if i % 10 == 0:  # Log every second
            print(f"⏳ Still waiting... ({i/10:.1f}s)")

    print(f"❌ Timeout waiting for command {command_id}")
    raise HTTPException(
        status_code=504, detail="Command timeout - agent may not be responding"
    )


@router.post("/calibrate/finish")
def proxy_calibrate_finish() -> Dict[str, Any]:
    """Queue calibration finish command for agent"""
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

    # Wait for result
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
def proxy_start_acquisition(data: StartAcquisitionRequest) -> Dict[str, Any]:
    """Queue start acquisition command for agent"""
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

    # Wait for result (acquisition start is quick)
    print(f"⏳ Waiting for command {command_id} result...")
    for i in range(50):  # 50 * 0.1s = 5 seconds
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
        if i % 10 == 0:  # Log every second
            print(f"⏳ Still waiting... ({i/10:.1f}s)")

    print(f"❌ Timeout waiting for command {command_id}")
    raise HTTPException(
        status_code=504, detail="Command timeout - agent may not be responding"
    )


@router.post("/stop")
def proxy_stop_acquisition() -> Dict[str, Any]:
    """Queue stop acquisition command for agent"""
    now = datetime.now()
    active_agents = [
        key
        for key, last_heartbeat in registered_agents.items()
        if now - last_heartbeat <= HEARTBEAT_TIMEOUT
    ]

    if not active_agents:
        raise HTTPException(status_code=503, detail="No active agent found")

    # Queue command for ALL active agent keys to ensure it's received
    # (agent might be registered with multiple keys: agent_id, session_uid, etc.)
    command_id = str(uuid.uuid4())
    command = {
        "command_id": command_id,
        "type": "stop_acquisition",
        "params": {},
    }

    # Queue for all active agent keys
    for agent_key in active_agents:
        if agent_key not in agent_commands:
            agent_commands[agent_key] = []
        agent_commands[agent_key].append(command)
        print(f"📤 Queued stop command {command_id} for agent key: {agent_key}")

    # Wait for result (acquisition stop is quick)
    print(f"⏳ Waiting for command {command_id} result...")
    for i in range(50):  # 50 * 0.1s = 5 seconds
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
        if i % 10 == 0:  # Log every second
            print(f"⏳ Still waiting... ({i/10:.1f}s)")

    print(f"❌ Timeout waiting for command {command_id}")
    raise HTTPException(
        status_code=504, detail="Command timeout - agent may not be responding"
    )
