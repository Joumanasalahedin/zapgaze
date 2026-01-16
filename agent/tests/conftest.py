"""
Pytest configuration and shared fixtures for agent testing.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# Note: We don't use autouse=True here because CameraManager and MediaPipeAdapter
# are imported inside functions, not at module level. Tests that need these mocks
# should patch them explicitly where they're used.


@pytest.fixture
def mock_camera():
    """Mock camera manager"""
    camera = Mock()
    camera.get_frame.return_value = Mock()
    camera.start_camera.return_value = None
    camera.release_camera.return_value = None
    return camera


@pytest.fixture
def mock_adapter():
    """Mock MediaPipe adapter"""
    adapter = Mock()
    adapter.analyze_frame.return_value = {
        "eye_centers": [(100, 200), (300, 400)],
        "ear": 0.3,
        "blink": False,
        "pupil_size": 5.0,
    }
    adapter.initialize.return_value = None
    return adapter


@pytest.fixture
def mock_requests():
    """Mock requests module"""
    with patch("agent.local_agent.requests") as mock_requests:
        # Default successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok", "commands": []}
        mock_requests.post.return_value = mock_response
        mock_requests.delete.return_value = mock_response
        yield mock_requests
