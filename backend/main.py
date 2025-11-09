"""
Main FastAPI application for LIMS-QMS Platform
Integration Layer & AI Orchestration - SESSION 7
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
    integrations
)
from backend.integrations.middleware import (
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    APIVersioningMiddleware,
    CORSSecurityMiddleware,
    RequestThrottlingMiddleware
)
from backend.integrations.events import event_bus
import os
import asyncio

# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("exports", exist_ok=True)
os.makedirs("backups", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Complete Organization Operating System - Unified LIMS-QMS Platform with AI Orchestration",
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

# Integration Layer Middleware (in order)
# 1. Security headers
app.add_middleware(CORSSecurityMiddleware)

# 2. Request logging
app.add_middleware(RequestLoggingMiddleware)

# 3. API versioning
app.add_middleware(APIVersioningMiddleware, default_version="v1")

# 4. Rate limiting (100 requests per 60 seconds)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# 5. Request throttling (max 10 concurrent requests per client)
app.add_middleware(RequestThrottlingMiddleware, max_concurrent=10)

# Mount static files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# Include routers - Core Modules
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

# Include routers - Integration Layer (SESSION 7)
app.include_router(integrations.router, prefix=f"{settings.API_V1_STR}/integrations", tags=["Integrations"])


@app.on_event("startup")
async def startup_event():
    """Initialize database and integration layer on startup"""
    init_db()

    # Connect event bus
    await event_bus.connect()

    # Start event bus listener in background
    asyncio.create_task(event_bus.listen())

    print(f"🚀 {settings.APP_NAME} started successfully!")
    print(f"📚 API Documentation: http://localhost:8000/api/docs")
    print(f"🔄 Integration Layer: ACTIVE")
    print(f"🤖 AI Orchestration: {'ENABLED' if settings.ANTHROPIC_API_KEY else 'DISABLED'}")
    print(f"📊 Event Bus: CONNECTED")
    print(f"⚡ Celery Workers: Use 'celery -A backend.integrations.celery_app worker' to start")
    print(f"🕐 Celery Beat: Use 'celery -A backend.integrations.celery_app beat' to start scheduler")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await event_bus.disconnect()
    print("👋 Application shutdown complete")


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
