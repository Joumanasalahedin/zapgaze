"""
Unit tests for agent API endpoints.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.api.agent import (
    registered_agents,
    agent_commands,
    command_results,
    stopped_agents,
    HEARTBEAT_TIMEOUT,
)


@pytest.fixture(autouse=True)
def clear_agent_state():
    """Clear agent state before each test."""
    registered_agents.clear()
    agent_commands.clear()
    command_results.clear()
    stopped_agents.clear()
    yield
    # Cleanup after test
    registered_agents.clear()
    agent_commands.clear()
    command_results.clear()
    stopped_agents.clear()


def test_register_agent(client: TestClient):
    """Test registering an agent."""

    registration = {"session_uid": "test-session-uid"}
    response = client.post("/agent/register", json=registration)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "registered"
    assert data["agent_key"] == "test-session-uid"
    assert "timestamp" in data

    # Verify agent is registered
    assert "test-session-uid" in registered_agents


def test_register_agent_with_agent_id(client: TestClient):
    """Test registering an agent with agent_id."""

    registration = {"agent_id": "test-agent-id"}
    response = client.post("/agent/register", json=registration)
    assert response.status_code == 200

    data = response.json()
    assert data["agent_key"] == "test-agent-id"
    assert "test-agent-id" in registered_agents


def test_agent_heartbeat(client: TestClient):
    """Test agent heartbeat."""

    # Register agent first
    registration = {"session_uid": "test-session-uid"}
    client.post("/agent/register", json=registration)

    # Send heartbeat
    heartbeat = {"session_uid": "test-session-uid"}
    response = client.post("/agent/heartbeat", json=heartbeat)
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "commands" in data
    assert isinstance(data["commands"], list)

    # Verify timestamp was updated
    assert "test-session-uid" in registered_agents


def test_agent_heartbeat_stopped_agent(client: TestClient):
    """Test that stopped agents receive stop signal."""

    # Register and then stop agent
    registration = {"session_uid": "test-session-uid"}
    client.post("/agent/register", json=registration)
    stopped_agents.add("test-session-uid")

    # Send heartbeat
    heartbeat = {"session_uid": "test-session-uid"}
    response = client.post("/agent/heartbeat", json=heartbeat)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "stopped"
    assert "stop sending heartbeats" in data["message"]


def test_agent_heartbeat_with_commands(client: TestClient):
    """Test agent heartbeat returns pending commands."""

    # Register agent
    registration = {"session_uid": "test-session-uid"}
    client.post("/agent/register", json=registration)

    # Queue a command
    command = {
        "command_id": "test-command-id",
        "type": "calibrate_start",
        "params": {},
    }
    agent_commands["test-session-uid"] = [command]

    # Send heartbeat
    heartbeat = {"session_uid": "test-session-uid"}
    response = client.post("/agent/heartbeat", json=heartbeat)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"  # Not stopped
    assert len(data["commands"]) == 1
    assert data["commands"][0]["command_id"] == "test-command-id"
    assert data["commands"][0]["type"] == "calibrate_start"

    # Command should be removed after being returned
    assert len(agent_commands["test-session-uid"]) == 0


def test_agent_heartbeat_with_command_result(client: TestClient):
    """Test agent heartbeat with command result."""

    # Register agent
    registration = {"session_uid": "test-session-uid"}
    client.post("/agent/register", json=registration)

    # Send heartbeat with command result
    heartbeat = {
        "session_uid": "test-session-uid",
        "command_result": {
            "command_id": "test-command-id",
            "result": {"status": "success"},
            "success": True,
        },
    }
    response = client.post("/agent/heartbeat", json=heartbeat)
    assert response.status_code == 200

    # Verify result was stored
    assert "test-command-id" in command_results
    assert command_results["test-command-id"]["success"] is True


def test_agent_status(client: TestClient):
    """Test checking agent status."""

    # No agents registered
    response = client.get("/agent/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "disconnected"

    # Register agent
    registration = {"session_uid": "test-session-uid"}
    client.post("/agent/register", json=registration)

    # Check status
    response = client.get("/agent/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "connected"
    # Response has either "session_uid" or "agent_keys" depending on whether session_uid is provided
    assert "session_uid" in data or "agent_keys" in data


def test_agent_status_with_session_uid(client: TestClient):
    """Test checking agent status for specific session."""

    # Register agent with session_uid
    registration = {"session_uid": "test-session-uid"}
    client.post("/agent/register", json=registration)

    # Check status for specific session
    response = client.get("/agent/status?session_uid=test-session-uid")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "connected"

    # Check status for non-existent session
    response = client.get("/agent/status?session_uid=non-existent")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "disconnected"


def test_agent_unregister(client: TestClient):
    """Test unregistering an agent."""

    # Register agent
    registration = {"session_uid": "test-session-uid"}
    client.post("/agent/register", json=registration)
    assert "test-session-uid" in registered_agents

    # Unregister agent (DELETE method, not POST)
    response = client.delete("/agent/unregister?session_uid=test-session-uid")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "unregistered"

    # Verify agent is removed
    assert "test-session-uid" not in registered_agents


def test_agent_heartbeat_timeout(client: TestClient):
    """Test that agents timeout after HEARTBEAT_TIMEOUT."""

    # Register agent with old timestamp
    old_time = datetime.now() - HEARTBEAT_TIMEOUT - timedelta(seconds=1)
    registered_agents["test-session-uid"] = old_time

    # Check status - should be disconnected due to timeout
    response = client.get("/agent/status?session_uid=test-session-uid")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "disconnected"
