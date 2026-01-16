"""
Unit tests for agent/acquisition_client.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def test_parse_args_defaults():
    """Test parse_args with default values"""
    from agent.acquisition_client import parse_args
    import sys

    original_argv = sys.argv
    try:
        sys.argv = [
            "acquisition_client.py",
            "--session-uid",
            "test-session-123",
        ]
        args = parse_args()
        assert args.session_uid == "test-session-123"
        assert args.api_url == "http://localhost:8000/acquisition/data"
        assert args.fps == 20.0
        assert args.batch_size is None
    finally:
        sys.argv = original_argv


def test_parse_args_custom_values():
    """Test parse_args with custom values"""
    from agent.acquisition_client import parse_args
    import sys

    original_argv = sys.argv
    try:
        sys.argv = [
            "acquisition_client.py",
            "--session-uid",
            "custom-session",
            "--api-url",
            "http://example.com:9000/acquisition/data",
            "--fps",
            "30.0",
            "--batch-size",
            "15",
        ]
        args = parse_args()
        assert args.session_uid == "custom-session"
        assert args.api_url == "http://example.com:9000/acquisition/data"
        assert args.fps == 30.0
        assert args.batch_size == 15
    finally:
        sys.argv = original_argv


def test_parse_args_missing_session_uid():
    """Test parse_args requires session-uid"""
    from agent.acquisition_client import parse_args
    import sys

    original_argv = sys.argv
    try:
        sys.argv = ["acquisition_client.py"]
        with pytest.raises(SystemExit):
            parse_args()
    finally:
        sys.argv = original_argv
