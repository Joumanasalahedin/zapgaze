from fastapi import FastAPI
from app.api import intake, acquisition, session, session_events, results

app = FastAPI(title="ZapGaze Backend")

# Intake and session control
app.include_router(intake.router, prefix="/intake", tags=["intake"])
app.include_router(session.router, prefix="/session", tags=["session"])
app.include_router(session_events.router, prefix="/session", tags=["session-events"])

# Acquisition data endpoints
app.include_router(acquisition.router, prefix="/acquisition", tags=["acquisition"])

# Results & reporting
app.include_router(results.router, prefix="/results", tags=["results"])

@app.get("/")
def read_root():
    return {"message": "ZapGaze API is running."}
