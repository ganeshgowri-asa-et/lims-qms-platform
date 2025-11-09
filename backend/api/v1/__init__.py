"""
API v1 Router
"""

from fastapi import APIRouter
from backend.api.v1.endpoints import (
    documents,
    equipment,
    training,
    lims,
    iec_reports,
    nonconformance,
    audit_risk,
    ai_models,
    analytics
)

api_router = APIRouter()

# Include all module routers
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(equipment.router, prefix="/equipment", tags=["equipment"])
api_router.include_router(training.router, prefix="/training", tags=["training"])
api_router.include_router(lims.router, prefix="/lims", tags=["lims"])
api_router.include_router(iec_reports.router, prefix="/iec-reports", tags=["iec-reports"])
api_router.include_router(nonconformance.router, prefix="/nonconformance", tags=["nonconformance"])
api_router.include_router(audit_risk.router, prefix="/audit-risk", tags=["audit-risk"])
api_router.include_router(ai_models.router, prefix="/ai", tags=["ai-models"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
