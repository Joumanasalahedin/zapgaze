"""
Unit tests for agent/task_manager.py
"""
import pytest
from agent.task_manager import parse_args


def test_parse_args_required_session_uid():
    """Test that parse_args requires session-uid argument."""
    # Test with missing required argument - should raise SystemExit
    with pytest.raises(SystemExit):
        parse_args()


def test_parse_args_with_session_uid():
    """Test parse_args with required session-uid argument."""
    import sys

    # Mock sys.argv to include required argument
    original_argv = sys.argv
    try:
        sys.argv = ["task_manager.py", "--session-uid", "test-session-123"]
        args = parse_args()
        assert args.session_uid == "test-session-123"
        # Check defaults
        assert args.api_base == "http://localhost:8000"
        assert args.trials == 100
        assert args.go_prob == 0.8
        assert args.stim_duration == 0.5
        assert args.isi == 1.0
    finally:
        sys.argv = original_argv


def test_parse_args_with_custom_values():
    """Test parse_args with custom argument values."""
    import sys

    original_argv = sys.argv
    try:
        sys.argv = [
            "task_manager.py",
            "--session-uid",
            "custom-session",
            "--api-base",
            "http://example.com:9000",
            "--trials",
            "50",
            "--go-prob",
            "0.7",
            "--stim-duration",
            "0.3",
            "--isi",
            "0.5",
        ]
        args = parse_args()
        assert args.session_uid == "custom-session"
        assert args.api_base == "http://example.com:9000"
        assert args.trials == 50
        assert args.go_prob == 0.7
        assert args.stim_duration == 0.3
        assert args.isi == 0.5
    finally:
        sys.argv = original_argv
