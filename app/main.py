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
)
from app.db import models
from app.db.database import engine

app = FastAPI(title="ZapGaze Backend")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Allow CORS for frontend - read from environment variable or use defaults
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
# Clean up any whitespace
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


@app.get("/")
def read_root():
    return {"message": "ZapGaze API is running."}


models.Base.metadata.create_all(bind=engine)
