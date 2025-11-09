"""Main FastAPI application for LIMS QMS Platform."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.api.routes import nc_routes, rca_routes, capa_routes
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="LIMS QMS Platform - Non-Conformance & CAPA Management System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(nc_routes.router)
app.include_router(rca_routes.router)
app.include_router(capa_routes.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print(f"✓ {settings.APP_NAME} - Database initialized")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": "1.0.0",
        "docs": "/docs",
        "organization": settings.ORGANIZATION_NAME
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
