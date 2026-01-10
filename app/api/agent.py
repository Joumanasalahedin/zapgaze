"""
Agent registration and status API
Allows agents to register with the backend and frontend to check agent status
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
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

# Heartbeat timeout - agent must send heartbeat within this time
HEARTBEAT_TIMEOUT = timedelta(seconds=30)


class AgentRegistration(BaseModel):
    session_uid: Optional[str] = None
    agent_id: Optional[str] = None  # Optional unique agent identifier


class AgentHeartbeat(BaseModel):
    session_uid: Optional[str] = None
    agent_id: Optional[str] = None


class AgentCommandResult(BaseModel):
    command_id: str
    result: Any
    success: bool
    error: Optional[str] = None


@router.post("/register")
def register_agent(registration: AgentRegistration):
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
def agent_heartbeat(heartbeat: dict):
    """Update agent heartbeat and return pending commands"""
    agent_key = heartbeat.get("session_uid") or heartbeat.get("agent_id") or "default"
    registered_agents[agent_key] = datetime.now()
    
    # Store command result if provided
    if "command_result" in heartbeat:
        result = heartbeat["command_result"]
        command_id = result.get("command_id")
        if command_id:
            command_results[command_id] = {
                "result": result.get("result"),
                "success": result.get("success", False),
                "error": result.get("error"),
            }
    
    # Return pending commands for this agent
    pending_commands = agent_commands.get(agent_key, [])
    # Clear commands after returning them
    if agent_key in agent_commands:
        agent_commands[agent_key] = []
    
    return {
        "status": "ok",
        "timestamp": registered_agents[agent_key].isoformat(),
        "commands": pending_commands,
    }


@router.get("/status")
def get_agent_status(session_uid: Optional[str] = None):
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
def unregister_agent(session_uid: Optional[str] = None, agent_id: Optional[str] = None):
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
def proxy_calibrate_start():
    """Queue calibration start command for agent"""
    # Get any active agent
    now = datetime.now()
    active_agents = [
        key
        for key, last_heartbeat in registered_agents.items()
        if now - last_heartbeat <= HEARTBEAT_TIMEOUT
    ]
    
    if not active_agents:
        raise HTTPException(status_code=503, detail="No active agent found")
    
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
    
    # Wait for result (polling)
    for _ in range(30):  # Wait up to 3 seconds
        time.sleep(0.1)
        if command_id in command_results:
            result = command_results.pop(command_id)
            if result["success"]:
                return result["result"]
            else:
                raise HTTPException(status_code=500, detail=result.get("error", "Command failed"))
    
    raise HTTPException(status_code=504, detail="Command timeout")


@router.post("/calibrate/point")
def proxy_calibrate_point(data: dict):
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
        "params": data,
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
                raise HTTPException(status_code=500, detail=result.get("error", "Command failed"))
    
    raise HTTPException(status_code=504, detail="Command timeout")


@router.post("/calibrate/finish")
def proxy_calibrate_finish():
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
                raise HTTPException(status_code=500, detail=result.get("error", "Command failed"))
    
    raise HTTPException(status_code=504, detail="Command timeout")
