"""
Security utilities for API authentication and rate limiting
"""

from fastapi import HTTPException, Security, Header
from fastapi.security import APIKeyHeader
from typing import Optional
import os

API_KEY_HEADER_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)

AGENT_API_KEY = os.getenv(
    "AGENT_API_KEY", "zapgaze-agent-secret-key-change-in-production"
)
FRONTEND_API_KEY = os.getenv(
    "FRONTEND_API_KEY", "zapgaze-frontend-secret-key-change-in-production"
)


def verify_agent_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Verify API key for agent endpoints.
    Raises HTTPException if key is invalid or missing.
    """
    if api_key is None:
        raise HTTPException(
            status_code=401, detail="API key required. Please provide X-API-Key header."
        )

    if api_key != AGENT_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key. Access denied.")

    return api_key


def verify_frontend_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Verify API key for frontend endpoints.
    Raises HTTPException if key is invalid or missing.
    """
    if api_key is None:
        raise HTTPException(
            status_code=401, detail="API key required. Please provide X-API-Key header."
        )

    if api_key != FRONTEND_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key. Access denied.")

    return api_key


def get_optional_api_key(
    api_key: Optional[str] = Security(api_key_header),
) -> Optional[str]:
    """
    Get API key if provided, but don't require it.
    Used for endpoints that work with or without authentication.
    """
    return api_key


def verify_agent_or_frontend_api_key(
    api_key: Optional[str] = Security(api_key_header),
) -> str:
    """
    Verify API key for endpoints that can be called by either agent or frontend.
    Accepts either AGENT_API_KEY or FRONTEND_API_KEY.
    Raises HTTPException if key is invalid or missing.
    """
    if api_key is None:
        raise HTTPException(
            status_code=401, detail="API key required. Please provide X-API-Key header."
        )

    if api_key == AGENT_API_KEY or api_key == FRONTEND_API_KEY:
        return api_key

    raise HTTPException(status_code=403, detail="Invalid API key. Access denied.")
