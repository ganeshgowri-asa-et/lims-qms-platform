"""AI/ML Models Package - SESSION 10

This package contains all AI/ML models for the LIMS-QMS Platform:
1. Predictive Maintenance (Equipment Failure Forecasting)
2. NC Root Cause Auto-Suggestion (NLP on Historical Data)
3. Test Duration Estimation (ML Regression)
4. Document Classification & Auto-Tagging
"""

from .predictive_maintenance import PredictiveMaintenanceModel
from .nc_root_cause import NCRootCauseSuggestionModel
from .test_duration import TestDurationEstimator
from .doc_classification import DocumentClassifier

__all__ = [
    "PredictiveMaintenanceModel",
    "NCRootCauseSuggestionModel",
    "TestDurationEstimator",
    "DocumentClassifier"
]
