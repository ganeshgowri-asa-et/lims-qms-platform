"""
Unit tests for AI/ML models
"""

import pytest
from datetime import datetime, date, timedelta
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_models.predictive_maintenance.model import PredictiveMaintenanceModel
from ai_models.nc_root_cause.model import NCRootCauseSuggestionModel
from ai_models.test_duration.model import TestDurationEstimator
from ai_models.doc_classification.model import DocumentClassifier


class TestPredictiveMaintenanceModel:
    """Test predictive maintenance model."""

    def test_model_initialization(self):
        """Test model can be initialized."""
        model = PredictiveMaintenanceModel()
        assert model is not None

    def test_feature_extraction(self):
        """Test feature extraction from equipment data."""
        model = PredictiveMaintenanceModel()

        equipment_data = {
            'installation_date': date(2020, 1, 1),
            'last_calibration_date': date(2024, 6, 1),
            'next_calibration_date': date(2025, 6, 1),
            'last_maintenance_date': date(2024, 9, 1),
            'calibration_count': 5,
            'maintenance_count': 10,
            'oee_history': [85, 87, 86, 88, 85],
            'total_downtime_hours_90d': 12.5,
            'historical_failure_count': 0,
            'category': 'Testing Equipment'
        }

        features = model.extract_features(equipment_data)
        assert features is not None
        assert features.shape[0] == 1  # One sample
        assert features.shape[1] > 0  # Has features

    def test_mock_prediction(self):
        """Test mock prediction (when model is not trained)."""
        model = PredictiveMaintenanceModel()

        equipment_data = {
            'installation_date': date(2020, 1, 1),
            'next_calibration_date': date.today() + timedelta(days=30),
            'maintenance_count': 5
        }

        prediction = model.predict(equipment_data)

        assert 'failure_probability' in prediction
        assert 'confidence_score' in prediction
        assert 'risk_factors' in prediction
        assert 'recommended_actions' in prediction
        assert 0 <= prediction['failure_probability'] <= 100


class TestNCRootCauseSuggestionModel:
    """Test NC root cause suggestion model."""

    def test_model_initialization(self):
        """Test model can be initialized."""
        model = NCRootCauseSuggestionModel()
        assert model is not None

    def test_text_preprocessing(self):
        """Test text preprocessing."""
        model = NCRootCauseSuggestionModel()

        text = "Equipment Calibration Failed - URGENT!"
        processed = model.preprocess_text(text)

        assert processed is not None
        assert processed.islower()
        assert "equipment" in processed

    def test_mock_suggestion(self):
        """Test mock root cause suggestion."""
        model = NCRootCauseSuggestionModel()

        nc_description = "Equipment calibration certificate expired"
        result = model.suggest_root_causes(nc_description)

        assert 'suggested_root_causes' in result
        assert 'similar_cases' in result
        assert 'confidence_score' in result
        assert len(result['suggested_root_causes']) > 0


class TestTestDurationEstimator:
    """Test test duration estimation model."""

    def test_model_initialization(self):
        """Test model can be initialized."""
        model = TestDurationEstimator()
        assert model is not None

    def test_feature_extraction(self):
        """Test feature extraction."""
        model = TestDurationEstimator()

        test_data = {
            'test_standard': 'IEC 61215',
            'sample_count': 3,
            'test_parameter_count': 15,
            'product_type': 'Solar Module',
            'urgency': 'Normal',
            'request_date': datetime.now(),
            'historical_avg_duration': 40,
            'current_lab_workload': 5,
            'equipment_availability_score': 85
        }

        features = model.extract_features(test_data)
        assert features is not None
        assert features.shape[0] == 1

    def test_mock_prediction(self):
        """Test mock duration prediction."""
        model = TestDurationEstimator()

        test_data = {
            'test_standard': 'IEC 61215',
            'sample_count': 3,
            'test_parameter_count': 15,
            'urgency': 'Normal'
        }

        prediction = model.predict(test_data)

        assert 'predicted_duration_days' in prediction
        assert 'confidence_interval' in prediction
        assert prediction['predicted_duration_days'] > 0


class TestDocumentClassifier:
    """Test document classification model."""

    def test_model_initialization(self):
        """Test model can be initialized."""
        model = DocumentClassifier()
        assert model is not None

    def test_text_preprocessing(self):
        """Test text preprocessing."""
        model = DocumentClassifier()

        text = "Standard Operating Procedure for Equipment Calibration"
        processed = model.preprocess_text(text)

        assert processed is not None
        assert "procedure" in processed
        assert "equipment" in processed

    def test_tag_generation(self):
        """Test automatic tag generation."""
        model = DocumentClassifier()

        text = "This document describes the calibration procedure for testing equipment in the solar PV laboratory."
        tags = model.generate_tags(text)

        assert len(tags) > 0
        assert 'calibration' in tags
        assert 'testing' in tags or 'equipment' in tags

    def test_entity_extraction(self):
        """Test entity extraction."""
        model = DocumentClassifier()

        text = "Refer to QSF-2024-001 for equipment EQP-2024-005 calibration using IEC 61215 standard. Contact admin@lims.com"
        entities = model.extract_entities(text)

        assert 'document_numbers' in entities
        assert 'equipment_ids' in entities
        assert 'standards' in entities
        assert 'email_addresses' in entities

    def test_mock_classification(self):
        """Test mock document classification."""
        model = DocumentClassifier()

        doc_text = "Standard Operating Procedure for Equipment Calibration and Maintenance"
        doc_title = "SOP-CAL-001"

        result = model.classify(doc_text, doc_title)

        assert 'predicted_category' in result
        assert 'confidence_score' in result
        assert 'suggested_tags' in result
        assert 'extracted_entities' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
