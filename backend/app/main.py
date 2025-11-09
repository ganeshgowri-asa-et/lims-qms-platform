"""
Main FastAPI application for LIMS/QMS Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routes import health, customers, test_requests, samples

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="LIMS/QMS Platform API for Test Request and Sample Management",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down...")


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(customers.router, prefix="/api/v1", tags=["Customers"])
app.include_router(test_requests.router, prefix="/api/v1", tags=["Test Requests"])
app.include_router(samples.router, prefix="/api/v1", tags=["Samples"])


# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to LIMS/QMS Platform API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
