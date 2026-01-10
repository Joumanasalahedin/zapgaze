"""
Simple unit tests for the main FastAPI application.
"""

from fastapi.testclient import TestClient


def test_read_root(client: TestClient):
    """Test the root endpoint returns the expected message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "ZapGaze API is running."


def test_read_root_response_structure(client: TestClient):
    """Test the root endpoint response structure."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data
    assert isinstance(data["message"], str)
