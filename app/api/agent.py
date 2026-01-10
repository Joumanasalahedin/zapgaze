"""
Agent registration and status API
Allows agents to register with the backend and frontend to check agent status
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Dict, Optional
import time

router = APIRouter()

# In-memory store for registered agents
# Key: session_uid or user identifier, Value: last heartbeat timestamp
registered_agents: Dict[str, datetime] = {}

# Heartbeat timeout - agent must send heartbeat within this time
HEARTBEAT_TIMEOUT = timedelta(seconds=30)


class AgentRegistration(BaseModel):
    session_uid: Optional[str] = None
    agent_id: Optional[str] = None  # Optional unique agent identifier


class AgentHeartbeat(BaseModel):
    session_uid: Optional[str] = None
    agent_id: Optional[str] = None


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
def agent_heartbeat(heartbeat: AgentHeartbeat):
    """Update agent heartbeat - agent should call this every 10-15 seconds"""
    agent_key = heartbeat.session_uid or heartbeat.agent_id or "default"
    registered_agents[agent_key] = datetime.now()
    return {"status": "ok", "timestamp": registered_agents[agent_key].isoformat()}


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
        return {"status": "unregistered", "agent_key": agent_key}
    raise HTTPException(status_code=404, detail="Agent not found")
