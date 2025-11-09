"""
Main FastAPI Application for LIMS-QMS Platform
Session 8: Audit & Risk Management System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.api.audit_risk import router as audit_risk_router

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-Powered LIMS & QMS Platform for Solar PV Testing & R&D Laboratories"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(audit_risk_router, prefix=settings.API_PREFIX)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "LIMS-QMS Platform API",
        "version": settings.API_VERSION,
        "session": "Session 8: Audit & Risk Management System",
        "features": [
            "Audit Program Management (QSF1701)",
            "Audit Scheduling & Tracking",
            "Audit Findings with NC Linkage",
            "Risk Register with 5x5 Matrix",
            "Compliance Tracking (ISO 17025, ISO 9001)"
        ]
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
