from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import (
    intake,
    acquisition,
    session,
    session_events,
    results,
    features,
    calibration,
)
from app.db import models, database
from app.db.database import engine

app = FastAPI(title="ZapGaze Backend")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Intake and session control
app.include_router(intake.router, prefix="/intake", tags=["intake"])
app.include_router(session.router, prefix="/session", tags=["session"])
app.include_router(session_events.router, prefix="/session",
                   tags=["session-events"])

# Calibration & Acquisition data endpoints
app.include_router(calibration.router)
app.include_router(acquisition.router,
                   prefix="/acquisition", tags=["acquisition"])

# Results & reporting
app.include_router(results.router, prefix="/results", tags=["results"])
app.include_router(features.router, prefix="/features", tags=["features"])


@app.get("/")
def read_root():
    return {"message": "ZapGaze API is running."}


models.Base.metadata.create_all(bind=engine)
