"""
AI/ML Models API (Session 10)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Optional

from backend.core.database import get_db
from backend.services.ai_models import (
    predictive_maintenance_model,
    nc_root_cause_predictor,
    test_duration_estimator,
    document_classifier
)


router = APIRouter()


# Schemas
class PredictMaintenanceRequest(BaseModel):
    equipment_id: int
    days_since_calibration: int
    calibration_frequency: int
    maintenance_frequency: int
    equipment_age_days: int
    past_failures: int


class NCRootCausePredictRequest(BaseModel):
    nc_description: str
    nc_category: Optional[str] = None


class TestDurationRequest(BaseModel):
    test_standard: str
    test_type_encoded: int = 1
    sample_complexity_score: int = 3
    quantity: int = 1
    technician_experience_years: int = 3


class DocumentClassifyRequest(BaseModel):
    document_text: str
    title: Optional[str] = None


@router.post("/predict-equipment-failure")
def predict_equipment_failure(request: PredictMaintenanceRequest):
    """
    Predict equipment failure probability using ML model
    """
    prediction = predictive_maintenance_model.predict_failure_probability(
        request.dict()
    )

    return prediction


@router.post("/suggest-root-cause")
def suggest_nc_root_cause(request: NCRootCausePredictRequest):
    """
    Suggest root causes for non-conformance using NLP
    """
    suggestion = nc_root_cause_predictor.suggest_root_cause(
        request.nc_description,
        request.nc_category
    )

    return suggestion


@router.post("/estimate-test-duration")
def estimate_test_duration(request: TestDurationRequest):
    """
    Estimate test duration using ML regression model
    """
    estimation = test_duration_estimator.estimate_duration(request.dict())

    return estimation


@router.post("/classify-document")
def classify_document(request: DocumentClassifyRequest):
    """
    Classify document and suggest tags using NLP
    """
    classification = document_classifier.classify_document(
        request.document_text,
        request.title
    )

    return classification


@router.get("/models/health")
def check_models_health():
    """
    Check if AI models are loaded and operational
    """
    from pathlib import Path
    from backend.core.config import settings

    model_path = Path(settings.ML_MODEL_PATH)

    models_status = {
        "predictive_maintenance": (model_path / "predictive_maintenance.pkl").exists(),
        "nc_root_cause": (model_path / "nc_root_cause.pkl").exists(),
        "test_duration": (model_path / "test_duration.pkl").exists(),
        "document_classifier": (model_path / "doc_classifier.pkl").exists()
    }

    all_loaded = all(models_status.values())

    return {
        "status": "healthy" if all_loaded else "partial",
        "models": models_status,
        "note": "Models will use rule-based fallback if not trained"
    }


@router.get("/recommendations/equipment/{equipment_id}")
def get_equipment_recommendations(equipment_id: int, db: Session = Depends(get_db)):
    """
    Get AI-powered recommendations for specific equipment
    """
    from backend.models.equipment import Equipment, CalibrationRecord
    from datetime import date

    # Get equipment
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        return {"error": "Equipment not found"}

    # Calculate features
    if equipment.last_calibration_date:
        days_since = (date.today() - equipment.last_calibration_date).days
    else:
        days_since = 365

    if equipment.purchase_date:
        age_days = (date.today() - equipment.purchase_date).days
    else:
        age_days = 365

    # Count past failures (calibrations that failed)
    past_failures = db.query(CalibrationRecord).filter(
        CalibrationRecord.equipment_id == equipment_id,
        CalibrationRecord.result == "Fail"
    ).count()

    # Get prediction
    prediction = predictive_maintenance_model.predict_failure_probability({
        "days_since_calibration": days_since,
        "calibration_frequency": equipment.calibration_frequency_days,
        "maintenance_frequency": 90,  # Default 90 days
        "equipment_age_days": age_days,
        "past_failures": past_failures
    })

    return {
        "equipment_id": equipment.equipment_id,
        "equipment_name": equipment.name,
        "prediction": prediction,
        "next_calibration_date": equipment.next_calibration_date
    }
