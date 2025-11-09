"""
LIMS-QMS Platform - Main Application
AI-Powered Laboratory Information Management System & Quality Management System
For Solar PV Testing & R&D Laboratories (ISO 17025/9001 Compliance)
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import time
from typing import Callable

from backend.config import settings
from backend.database import connect_db, disconnect_db

# Import routers
from backend.api import (
    documents,
    equipment,
    training,
    lims,
    test_reports,
    nonconformance,
    audit,
    analytics,
    ai_models
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await connect_db()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🤖 AI Models: {'Enabled' if settings.AI_MODELS_ENABLED else 'Disabled'}")

    yield

    # Shutdown
    await disconnect_db()
    print("👋 Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## AI-Powered LIMS & QMS Platform for Solar PV Testing Laboratories

    ### Key Features:
    - 📄 **Document Management System** - ISO-compliant version control & digital signatures
    - 🔧 **Equipment & Calibration** - Lifecycle management with predictive maintenance AI
    - 👨‍🎓 **Training & Competency** - Gap analysis and auto-certification
    - 🧪 **LIMS Core** - Test request, sample tracking, and quote automation
    - 📊 **IEC Test Reports** - Automated report generation (IEC 61215/61730/61701)
    - ⚠️ **Non-Conformance & CAPA** - AI root cause suggestions with 5-Why/Fishbone
    - 🔍 **Audit & Risk Management** - QSF1701 compliance with 5x5 risk matrix
    - 📈 **Analytics Dashboard** - Executive/Operational/Quality KPIs with real-time tracking
    - 🤖 **AI Integration** - Predictive maintenance, NLP root cause analysis, test duration forecasting

    ### Standards Compliance:
    - ISO/IEC 17025:2017 - Testing and Calibration Laboratories
    - ISO 9001:2015 - Quality Management Systems
    - IEC 61215 - PV Module Design Qualification
    - IEC 61730 - PV Module Safety
    - IEC 61701 - Salt Mist Corrosion Testing
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Middleware for response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable):
    """Add response time header to all requests."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "ai_models_enabled": settings.AI_MODELS_ENABLED
    }


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI-Powered LIMS & QMS Platform for Solar PV Testing Laboratories",
        "documentation": "/docs",
        "health_check": "/health",
        "api_prefix": settings.API_PREFIX
    }


# Include all module routers with unified API gateway
app.include_router(
    documents.router,
    prefix=f"{settings.API_PREFIX}/documents",
    tags=["📄 Document Management"]
)

app.include_router(
    equipment.router,
    prefix=f"{settings.API_PREFIX}/equipment",
    tags=["🔧 Equipment & Calibration"]
)

app.include_router(
    training.router,
    prefix=f"{settings.API_PREFIX}/training",
    tags=["👨‍🎓 Training & Competency"]
)

app.include_router(
    lims.router,
    prefix=f"{settings.API_PREFIX}/lims",
    tags=["🧪 LIMS - Test Requests & Samples"]
)

app.include_router(
    test_reports.router,
    prefix=f"{settings.API_PREFIX}/test-reports",
    tags=["📊 IEC Test Reports"]
)

app.include_router(
    nonconformance.router,
    prefix=f"{settings.API_PREFIX}/nc-capa",
    tags=["⚠️ Non-Conformance & CAPA"]
)

app.include_router(
    audit.router,
    prefix=f"{settings.API_PREFIX}/audit",
    tags=["🔍 Audit & Risk Management"]
)

app.include_router(
    analytics.router,
    prefix=f"{settings.API_PREFIX}/analytics",
    tags=["📈 Analytics & Dashboards"]
)

app.include_router(
    ai_models.router,
    prefix=f"{settings.API_PREFIX}/ai",
    tags=["🤖 AI/ML Models & Predictions"]
)


# Custom OpenAPI schema
def custom_openapi():
    """Customize OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=app.description,
        routes=app.routes,
    )

    # Add custom tags
    openapi_schema["tags"] = [
        {
            "name": "System",
            "description": "System health and information endpoints"
        },
        {
            "name": "📄 Document Management",
            "description": "QMS document control with version management and digital signatures (SESSION 2)"
        },
        {
            "name": "🔧 Equipment & Calibration",
            "description": "Equipment lifecycle, calibration scheduling, and OEE tracking (SESSION 3)"
        },
        {
            "name": "👨‍🎓 Training & Competency",
            "description": "Training matrix, competency gap analysis, and certifications (SESSION 4)"
        },
        {
            "name": "🧪 LIMS - Test Requests & Samples",
            "description": "Test request management, sample tracking, and barcode generation (SESSION 5)"
        },
        {
            "name": "📊 IEC Test Reports",
            "description": "Automated IEC test report generation with digital certificates (SESSION 6)"
        },
        {
            "name": "⚠️ Non-Conformance & CAPA",
            "description": "NC tracking, root cause analysis, and CAPA management (SESSION 7)"
        },
        {
            "name": "🔍 Audit & Risk Management",
            "description": "Audit scheduling, findings tracking, and risk register (SESSION 8)"
        },
        {
            "name": "📈 Analytics & Dashboards",
            "description": "KPI dashboards, trend analysis, and customer portal (SESSION 9)"
        },
        {
            "name": "🤖 AI/ML Models & Predictions",
            "description": "Predictive maintenance, root cause suggestions, duration estimation (SESSION 10)"
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
