"""
AI/ML Models for LIMS-QMS Platform
Session 10: AI Integration
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session

# ML libraries
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path

from backend.core.config import settings


class PredictiveMaintenanceModel:
    """
    Equipment Failure Forecasting Model
    Predicts when equipment might fail based on historical calibration and maintenance data
    """

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.model_path = Path(settings.ML_MODEL_PATH) / "predictive_maintenance.pkl"
        self.scaler_path = Path(settings.ML_MODEL_PATH) / "pm_scaler.pkl"

    def train(self, training_data: pd.DataFrame):
        """
        Train the model on historical equipment data
        Features: days_since_calibration, calibration_frequency, maintenance_frequency,
                  equipment_age, failure_history
        """
        features = ['days_since_calibration', 'calibration_frequency',
                    'maintenance_frequency', 'equipment_age_days', 'past_failures']

        X = training_data[features]
        y = training_data['failed']  # Binary: 1 if equipment failed, 0 otherwise

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

        # Save model
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)

        return {"message": "Model trained successfully", "accuracy": self.model.score(X_scaled, y)}

    def predict_failure_probability(self, equipment_data: Dict) -> Dict:
        """
        Predict probability of equipment failure
        Returns: probability score and risk level
        """
        try:
            # Load model if exists
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)

            features = np.array([[
                equipment_data['days_since_calibration'],
                equipment_data['calibration_frequency'],
                equipment_data['maintenance_frequency'],
                equipment_data['equipment_age_days'],
                equipment_data['past_failures']
            ]])

            features_scaled = self.scaler.transform(features)
            probability = self.model.predict_proba(features_scaled)[0][1]

            # Determine risk level
            if probability < 0.3:
                risk_level = "low"
            elif probability < 0.6:
                risk_level = "medium"
            elif probability < 0.8:
                risk_level = "high"
            else:
                risk_level = "critical"

            return {
                "failure_probability": round(probability * 100, 2),
                "risk_level": risk_level,
                "recommendation": self._get_recommendation(risk_level)
            }

        except Exception as e:
            return {
                "error": str(e),
                "failure_probability": 0,
                "risk_level": "unknown"
            }

    def _get_recommendation(self, risk_level: str) -> str:
        recommendations = {
            "low": "Continue normal maintenance schedule",
            "medium": "Schedule preventive maintenance within 2 weeks",
            "high": "Schedule immediate inspection and maintenance",
            "critical": "Stop using equipment and perform emergency maintenance"
        }
        return recommendations.get(risk_level, "Monitor equipment closely")


class NCRootCausePredictor:
    """
    Non-Conformance Root Cause Auto-Suggestion
    Uses NLP on historical NC data to suggest root causes
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model_path = Path(settings.ML_MODEL_PATH) / "nc_root_cause.pkl"
        self.vectorizer_path = Path(settings.ML_MODEL_PATH) / "nc_vectorizer.pkl"

        # Common root cause categories
        self.root_cause_categories = [
            "Human Error - Training Gap",
            "Human Error - Procedure Not Followed",
            "Equipment Malfunction",
            "Calibration Issue",
            "Environmental Conditions",
            "Material/Sample Issue",
            "Documentation Error",
            "Communication Gap",
            "Process Design Flaw",
            "System/Software Issue"
        ]

    def train(self, training_data: pd.DataFrame):
        """
        Train on historical NC descriptions and their root causes
        """
        X = self.vectorizer.fit_transform(training_data['description'])
        y = training_data['root_cause_category']

        self.model.fit(X, y)

        joblib.dump(self.model, self.model_path)
        joblib.dump(self.vectorizer, self.vectorizer_path)

        return {"message": "NC Root Cause model trained successfully"}

    def suggest_root_cause(self, nc_description: str, nc_category: str = None) -> Dict:
        """
        Suggest probable root causes based on NC description
        """
        try:
            # Load model if exists
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)

            # Vectorize description
            X = self.vectorizer.transform([nc_description])

            # Get prediction probabilities
            probabilities = self.model.predict_proba(X)[0]
            top_indices = np.argsort(probabilities)[-3:][::-1]  # Top 3

            suggestions = []
            for idx in top_indices:
                suggestions.append({
                    "root_cause": self.model.classes_[idx],
                    "confidence": round(probabilities[idx] * 100, 2)
                })

            return {
                "suggested_root_causes": suggestions,
                "primary_suggestion": suggestions[0] if suggestions else None
            }

        except Exception as e:
            # Fallback to rule-based suggestions
            return self._rule_based_suggestion(nc_description, nc_category)

    def _rule_based_suggestion(self, description: str, category: str = None) -> Dict:
        """Fallback rule-based root cause suggestion"""
        description_lower = description.lower()

        if any(word in description_lower for word in ['calibration', 'measurement', 'accuracy']):
            primary = "Calibration Issue"
        elif any(word in description_lower for word in ['training', 'knowledge', 'skill']):
            primary = "Human Error - Training Gap"
        elif any(word in description_lower for word in ['equipment', 'machine', 'instrument']):
            primary = "Equipment Malfunction"
        elif any(word in description_lower for word in ['procedure', 'protocol', 'followed']):
            primary = "Human Error - Procedure Not Followed"
        elif any(word in description_lower for word in ['document', 'record', 'paperwork']):
            primary = "Documentation Error"
        else:
            primary = "Process Design Flaw"

        return {
            "suggested_root_causes": [
                {"root_cause": primary, "confidence": 75.0}
            ],
            "primary_suggestion": {"root_cause": primary, "confidence": 75.0}
        }


class TestDurationEstimator:
    """
    Test Duration Estimation Model
    Predicts how long a test will take based on test type and sample characteristics
    """

    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.model_path = Path(settings.ML_MODEL_PATH) / "test_duration.pkl"
        self.scaler_path = Path(settings.ML_MODEL_PATH) / "td_scaler.pkl"

    def train(self, training_data: pd.DataFrame):
        """
        Train on historical test execution data
        Features: test_type_encoded, sample_complexity, quantity, technician_experience
        Target: actual_duration_hours
        """
        features = ['test_type_encoded', 'sample_complexity_score',
                    'quantity', 'technician_experience_years']

        X = training_data[features]
        y = training_data['actual_duration_hours']

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)

        return {"message": "Test duration model trained successfully"}

    def estimate_duration(self, test_info: Dict) -> Dict:
        """
        Estimate test duration
        """
        try:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)

            features = np.array([[
                test_info['test_type_encoded'],
                test_info['sample_complexity_score'],
                test_info['quantity'],
                test_info.get('technician_experience_years', 3)
            ]])

            features_scaled = self.scaler.transform(features)
            estimated_hours = self.model.predict(features_scaled)[0]

            # Add buffer
            estimated_hours_with_buffer = estimated_hours * 1.2

            return {
                "estimated_hours": round(estimated_hours, 2),
                "estimated_hours_with_buffer": round(estimated_hours_with_buffer, 2),
                "estimated_days": round(estimated_hours_with_buffer / 8, 1),
                "confidence_interval": f"±{round(estimated_hours * 0.15, 2)} hours"
            }

        except Exception as e:
            # Fallback to rule-based estimation
            return self._rule_based_estimation(test_info)

    def _rule_based_estimation(self, test_info: Dict) -> Dict:
        """Fallback rule-based duration estimation"""

        # Base durations for common IEC tests (in hours)
        base_durations = {
            "IEC61215": 160,  # ~3 weeks
            "IEC61730": 120,  # ~2.5 weeks
            "IEC61701": 80,   # ~1.5 weeks
        }

        test_standard = test_info.get('test_standard', 'IEC61215')
        quantity = test_info.get('quantity', 1)

        base = base_durations.get(test_standard, 100)
        estimated = base * (0.7 + (quantity * 0.1))  # Economies of scale

        return {
            "estimated_hours": round(estimated, 2),
            "estimated_hours_with_buffer": round(estimated * 1.2, 2),
            "estimated_days": round(estimated * 1.2 / 8, 1),
            "confidence_interval": "±20%"
        }


class DocumentClassifier:
    """
    Document Classification & Auto-Tagging
    Classifies documents into categories and suggests tags
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=300, stop_words='english')
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model_path = Path(settings.ML_MODEL_PATH) / "doc_classifier.pkl"
        self.vectorizer_path = Path(settings.ML_MODEL_PATH) / "doc_vectorizer.pkl"

        self.document_categories = [
            "Quality Manual",
            "Procedure",
            "Work Instruction",
            "Form",
            "Test Report",
            "Calibration Certificate",
            "Training Material",
            "Audit Report"
        ]

    def train(self, training_data: pd.DataFrame):
        """Train document classifier"""
        X = self.vectorizer.fit_transform(training_data['document_text'])
        y = training_data['category']

        self.classifier.fit(X, y)

        joblib.dump(self.classifier, self.model_path)
        joblib.dump(self.vectorizer, self.vectorizer_path)

        return {"message": "Document classifier trained successfully"}

    def classify_document(self, document_text: str, title: str = None) -> Dict:
        """
        Classify document and suggest tags
        """
        try:
            if self.model_path.exists():
                self.classifier = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)

            X = self.vectorizer.transform([document_text])
            probabilities = self.classifier.predict_proba(X)[0]
            predicted_category = self.classifier.predict(X)[0]

            # Extract keywords for tags
            tags = self._extract_tags(document_text, title)

            return {
                "predicted_category": predicted_category,
                "confidence": round(max(probabilities) * 100, 2),
                "suggested_tags": tags
            }

        except Exception as e:
            return self._rule_based_classification(document_text, title)

    def _extract_tags(self, text: str, title: str = None) -> List[str]:
        """Extract relevant tags from document"""
        tags = []

        # Common QMS keywords
        keywords = {
            'calibration': 'calibration',
            'audit': 'audit',
            'training': 'training',
            'procedure': 'procedure',
            'quality': 'quality',
            'test': 'testing',
            'equipment': 'equipment',
            'nonconformance': 'nc',
            'capa': 'capa',
            'risk': 'risk-management'
        }

        text_lower = (text + " " + (title or "")).lower()

        for keyword, tag in keywords.items():
            if keyword in text_lower:
                tags.append(tag)

        return list(set(tags))[:5]  # Max 5 tags

    def _rule_based_classification(self, text: str, title: str = None) -> Dict:
        """Fallback rule-based classification"""
        text_lower = (text + " " + (title or "")).lower()

        if 'test report' in text_lower or 'iec' in text_lower:
            category = "Test Report"
        elif 'calibration' in text_lower and 'certificate' in text_lower:
            category = "Calibration Certificate"
        elif 'procedure' in text_lower or 'sop' in text_lower:
            category = "Procedure"
        elif 'audit' in text_lower:
            category = "Audit Report"
        elif 'form' in text_lower or 'qsf' in text_lower:
            category = "Form"
        else:
            category = "Work Instruction"

        tags = self._extract_tags(text, title)

        return {
            "predicted_category": category,
            "confidence": 80.0,
            "suggested_tags": tags
        }


# Singleton instances
predictive_maintenance_model = PredictiveMaintenanceModel()
nc_root_cause_predictor = NCRootCausePredictor()
test_duration_estimator = TestDurationEstimator()
document_classifier = DocumentClassifier()
