from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Replaces deprecated @app.on_event("startup") pattern.
    """
    try:
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        print("  Tables may already exist or database connection issue.")

    yield

    pass


app = FastAPI(title="ZapGaze Backend", lifespan=lifespan)

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

app.include_router(users.router, prefix="/users", tags=["users"])

app.include_router(intake.router, prefix="/intake", tags=["intake"])
app.include_router(session.router, prefix="/session", tags=["session"])
app.include_router(session_events.router, prefix="/session", tags=["session-events"])

app.include_router(calibration.router, tags=["calibration"])
app.include_router(acquisition.router, prefix="/acquisition", tags=["acquisition"])

app.include_router(results.router, prefix="/results", tags=["results"])
app.include_router(features.router, prefix="/features", tags=["features"])

app.include_router(agent.router, prefix="/agent", tags=["agent"])

app.include_router(gdpr.router, prefix="/gdpr", tags=["gdpr"])


@app.get("/")
def read_root():
    return {"message": "ZapGaze API is running."}
