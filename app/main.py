from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from app.api import (
    intake,
    acquisition,
    session,
    session_events,
    results,
    features,
    calibration,
    users,
    agent,
    gdpr,
)
from app.db import models
from app.db.database import engine

app = FastAPI(title="ZapGaze Backend")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
cors_origins = [origin.strip() for origin in cors_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User management
app.include_router(users.router, prefix="/users", tags=["users"])

# Intake and session control
app.include_router(intake.router, prefix="/intake", tags=["intake"])
app.include_router(session.router, prefix="/session", tags=["session"])
app.include_router(session_events.router, prefix="/session", tags=["session-events"])

# Calibration & Acquisition data endpoints
app.include_router(calibration.router, tags=["calibration"])
app.include_router(acquisition.router, prefix="/acquisition", tags=["acquisition"])

# Results & reporting
app.include_router(results.router, prefix="/results", tags=["results"])
app.include_router(features.router, prefix="/features", tags=["features"])

# Agent registration and status
app.include_router(agent.router, prefix="/agent", tags=["agent"])

# GDPR compliance endpoints
app.include_router(gdpr.router, prefix="/gdpr", tags=["gdpr"])


@app.on_event("startup")
async def create_tables():
    """
    Create database tables on application startup.

    This is idempotent - it only creates tables that don't exist.
    Existing tables and data are preserved. Safe to call on every startup.
    """
    try:
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        print("  Tables may already exist or database connection issue.")


@app.get("/")
def read_root():
    return {"message": "ZapGaze API is running."}
