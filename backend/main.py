"""
Main FastAPI application for LIMS-QMS Platform
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.core.config import settings
from backend.core.database import init_db
from backend.api.endpoints import (
    auth,
    users,
    documents,
    forms,
    projects,
    tasks,
    hr,
    procurement,
    financial,
    crm,
    quality,
    analytics,
    workflow,
    milestones,
    risks,
    quotations,
    equipment_lifecycle,
    time_tracking
)
import os

# Create uploads directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Complete Organization Operating System - Unified LIMS-QMS Platform",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["Documents"])
app.include_router(forms.router, prefix=f"{settings.API_V1_STR}/forms", tags=["Forms"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["Projects"])
app.include_router(tasks.router, prefix=f"{settings.API_V1_STR}/tasks", tags=["Tasks"])
app.include_router(hr.router, prefix=f"{settings.API_V1_STR}/hr", tags=["HR"])
app.include_router(procurement.router, prefix=f"{settings.API_V1_STR}/procurement", tags=["Procurement"])
app.include_router(financial.router, prefix=f"{settings.API_V1_STR}/financial", tags=["Financial"])
app.include_router(crm.router, prefix=f"{settings.API_V1_STR}/crm", tags=["CRM"])
app.include_router(quality.router, prefix=f"{settings.API_V1_STR}/quality", tags=["Quality"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Analytics"])

# Workflow Automation Engine - Session 3
app.include_router(workflow.router, prefix=f"{settings.API_V1_STR}/workflows", tags=["Workflows"])
app.include_router(milestones.router, prefix=f"{settings.API_V1_STR}/milestones", tags=["Milestones"])
app.include_router(risks.router, prefix=f"{settings.API_V1_STR}/risks", tags=["Risks"])
app.include_router(quotations.router, prefix=f"{settings.API_V1_STR}/quotations", tags=["Quotations"])
app.include_router(equipment_lifecycle.router, prefix=f"{settings.API_V1_STR}/equipment-lifecycle", tags=["Equipment Lifecycle"])
app.include_router(time_tracking.router, prefix=f"{settings.API_V1_STR}/time-tracking", tags=["Time Tracking"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print(f"🚀 {settings.APP_NAME} started successfully!")
    print(f"📚 API Documentation: http://localhost:8000/api/docs")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
