"""
Health check endpoint
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()


@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "LIMS/QMS Platform API",
        "version": "1.0.0"
    }


@router.get("/health/db")
def database_health_check(db: Session = Depends(get_db)):
    """Database health check"""
    try:
        # Try to execute a simple query
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
