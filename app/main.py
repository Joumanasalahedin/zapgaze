from fastapi import FastAPI
from app.api import intake
# , session, results

app = FastAPI(title="ADHD Eye-Tracking Backend")

# Include API routers
app.include_router(intake.router, prefix="/intake")
# app.include_router(session.router, prefix="/session")
# app.include_router(results.router, prefix="/results")


@app.get("/")
def read_root():
    return {"message": "ADHD Eye-Tracking API is running."}
