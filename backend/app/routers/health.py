"""
Health check routes
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..database import get_db
from ..schemas import HealthCheck

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheck)
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify API and database connectivity.

    Args:
        db: Database session

    Returns:
        HealthCheck: Health status information
    """
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "timestamp": datetime.utcnow()
    }
