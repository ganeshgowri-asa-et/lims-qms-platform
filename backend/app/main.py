"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import engine, Base
from .api.v1.endpoints import documents, equipment

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="LIMS & QMS Platform - Document Management & Equipment Calibration System",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    documents.router,
    prefix=f"{settings.API_V1_STR}/documents",
    tags=["Documents"],
)

app.include_router(
    equipment.router,
    prefix=f"{settings.API_V1_STR}/equipment",
    tags=["Equipment"],
)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "LIMS & QMS Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "features": [
            "Document Management System (QMS)",
            "Equipment Calibration & Maintenance",
            "Auto Document Numbering",
            "Version Control",
            "Approval Workflow",
            "PDF Generation with Watermarks",
            "QR Code Generation",
            "Calibration Alerts",
            "OEE Tracking",
        ],
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
