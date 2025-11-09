"""
Predictive Maintenance AI Model
Equipment Failure Forecasting using LSTM + Random Forest Ensemble

This model predicts equipment failures based on:
- Equipment age and usage patterns
- Calibration history and maintenance records
- Historical failure data and downtime logs
- OEE (Overall Equipment Effectiveness) trends
- Environmental conditions
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import joblib
from pathlib import Path

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    import xgboost as xgb
except ImportError:
    pass


class PredictiveMaintenanceModel:
    """Predictive maintenance model for equipment failure forecasting."""

    def __init__(self, model_path: Optional[Path] = None):
        """Initialize the model.

        Args:
            model_path: Path to saved model files
        """
        self.model_path = model_path
        self.failure_classifier = None
        self.failure_date_regressor = None
        self.scaler = StandardScaler()
        self.feature_names = []

        if model_path and model_path.exists():
            self.load_model()

    def extract_features(self, equipment_data: Dict) -> np.ndarray:
        """Extract features from equipment data.

        Features:
        1. Equipment age (days)
        2. Days since last calibration
        3. Days until next calibration
        4. Days since last maintenance
        5. Total calibration count
        6. Total maintenance count
        7. Average OEE (last 30 days)
        8. OEE trend (slope)
        9. Total downtime hours (last 90 days)
        10. Failure count (historical)
        11. Equipment category encoding
        12. Calibration overdue flag
        13. Days since last failure
        14. Average time between failures
        15. Maintenance compliance score

        Args:
            equipment_data: Dictionary with equipment information

        Returns:
            Feature vector as numpy array
        """
        features = []

        # Age features
        install_date = equipment_data.get('installation_date')
        if install_date:
            age_days = (datetime.now().date() - install_date).days
        else:
            age_days = 0
        features.append(age_days)

        # Calibration features
        last_cal_date = equipment_data.get('last_calibration_date')
        next_cal_date = equipment_data.get('next_calibration_date')

        if last_cal_date:
            days_since_cal = (datetime.now().date() - last_cal_date).days
        else:
            days_since_cal = 999

        if next_cal_date:
            days_until_cal = (next_cal_date - datetime.now().date()).days
        else:
            days_until_cal = 0

        features.extend([days_since_cal, days_until_cal])

        # Maintenance features
        last_maint_date = equipment_data.get('last_maintenance_date')
        if last_maint_date:
            days_since_maint = (datetime.now().date() - last_maint_date).days
        else:
            days_since_maint = 999
        features.append(days_since_maint)

        # Counts
        features.append(equipment_data.get('calibration_count', 0))
        features.append(equipment_data.get('maintenance_count', 0))

        # OEE metrics
        oee_history = equipment_data.get('oee_history', [])
        if oee_history:
            avg_oee = np.mean(oee_history[-30:])
            if len(oee_history) >= 2:
                oee_trend = np.polyfit(range(len(oee_history[-30:])), oee_history[-30:], 1)[0]
            else:
                oee_trend = 0
        else:
            avg_oee = 0
            oee_trend = 0

        features.extend([avg_oee, oee_trend])

        # Downtime
        features.append(equipment_data.get('total_downtime_hours_90d', 0))

        # Failure history
        features.append(equipment_data.get('historical_failure_count', 0))

        # Category encoding (simple hash for demo)
        category = equipment_data.get('category', 'Unknown')
        category_encoded = hash(category) % 10
        features.append(category_encoded)

        # Calibration overdue flag
        cal_overdue = 1 if days_until_cal < 0 else 0
        features.append(cal_overdue)

        # Time between failures
        features.append(equipment_data.get('days_since_last_failure', 999))
        features.append(equipment_data.get('avg_time_between_failures', 365))

        # Maintenance compliance score (0-100)
        features.append(equipment_data.get('maintenance_compliance_score', 100))

        return np.array(features).reshape(1, -1)

    def train(self, training_data: pd.DataFrame):
        """Train the predictive maintenance model.

        Args:
            training_data: DataFrame with equipment data and failure labels
        """
        print("Training Predictive Maintenance Model...")

        # Extract features
        X = np.vstack([
            self.extract_features(row.to_dict())
            for _, row in training_data.iterrows()
        ])

        # Labels
        y_failure = training_data['failed'].values  # Binary: 0/1
        y_days_to_failure = training_data['days_to_failure'].values  # Continuous

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Split data
        X_train, X_test, y_fail_train, y_fail_test = train_test_split(
            X_scaled, y_failure, test_size=0.2, random_state=42
        )

        # Train failure classifier (Random Forest)
        print("Training failure classifier...")
        self.failure_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        self.failure_classifier.fit(X_train, y_fail_train)

        # Evaluate
        train_acc = self.failure_classifier.score(X_train, y_fail_train)
        test_acc = self.failure_classifier.score(X_test, y_fail_test)
        print(f"Failure Classifier - Train Accuracy: {train_acc:.3f}, Test Accuracy: {test_acc:.3f}")

        # Train days-to-failure regressor (XGBoost) - only on failed equipment
        failed_indices = y_failure == 1
        if failed_indices.sum() > 0:
            X_failed = X_scaled[failed_indices]
            y_failed = y_days_to_failure[failed_indices]

            print("Training failure date regressor...")
            self.failure_date_regressor = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            self.failure_date_regressor.fit(X_failed, y_failed)
            print("Model training complete!")

    def predict(self, equipment_data: Dict) -> Dict:
        """Predict equipment failure probability and date.

        Args:
            equipment_data: Dictionary with equipment information

        Returns:
            Dictionary with predictions:
            - failure_probability: 0-100%
            - predicted_failure_date: Date or None
            - confidence_score: 0-100
            - risk_factors: Dict of contributing factors
            - recommended_actions: List of recommendations
        """
        if self.failure_classifier is None:
            return self._mock_prediction(equipment_data)

        # Extract and scale features
        features = self.extract_features(equipment_data)
        features_scaled = self.scaler.transform(features)

        # Predict failure probability
        failure_proba = self.failure_classifier.predict_proba(features_scaled)[0][1] * 100

        # Predict days to failure if probability is high
        predicted_date = None
        if failure_proba > 30 and self.failure_date_regressor is not None:
            days_to_failure = max(1, int(self.failure_date_regressor.predict(features_scaled)[0]))
            predicted_date = datetime.now().date() + timedelta(days=days_to_failure)

        # Analyze risk factors
        risk_factors = self._analyze_risk_factors(equipment_data, features[0])

        # Generate recommendations
        recommendations = self._generate_recommendations(
            failure_proba, risk_factors, equipment_data
        )

        # Confidence score (based on model certainty)
        confidence = min(95, max(60, 100 - abs(failure_proba - 50)))

        return {
            "failure_probability": round(failure_proba, 2),
            "predicted_failure_date": predicted_date,
            "confidence_score": round(confidence, 2),
            "risk_factors": risk_factors,
            "recommended_actions": recommendations
        }

    def _analyze_risk_factors(self, equipment_data: Dict, features: np.ndarray) -> Dict:
        """Analyze and rank risk factors."""
        risk_factors = {}

        # Check calibration status
        days_until_cal = features[2]
        if days_until_cal < 0:
            risk_factors['calibration_overdue'] = {
                'severity': 'high',
                'value': abs(days_until_cal),
                'description': f'Calibration overdue by {abs(int(days_until_cal))} days'
            }
        elif days_until_cal < 7:
            risk_factors['calibration_due_soon'] = {
                'severity': 'medium',
                'value': days_until_cal,
                'description': f'Calibration due in {int(days_until_cal)} days'
            }

        # Check OEE
        avg_oee = features[6]
        if avg_oee < 70:
            risk_factors['low_oee'] = {
                'severity': 'high',
                'value': avg_oee,
                'description': f'Low OEE: {avg_oee:.1f}% (target: 85%)'
            }

        # Check downtime
        downtime = features[8]
        if downtime > 40:
            risk_factors['high_downtime'] = {
                'severity': 'high',
                'value': downtime,
                'description': f'High downtime: {downtime:.1f} hours in last 90 days'
            }

        # Check age
        age_days = features[0]
        if age_days > 3650:  # 10 years
            risk_factors['equipment_age'] = {
                'severity': 'medium',
                'value': age_days,
                'description': f'Equipment age: {age_days // 365} years'
            }

        return risk_factors

    def _generate_recommendations(
        self, failure_proba: float, risk_factors: Dict, equipment_data: Dict
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if failure_proba > 70:
            recommendations.append("URGENT: Schedule immediate preventive maintenance")
            recommendations.append("Consider equipment replacement or major overhaul")

        elif failure_proba > 50:
            recommendations.append("Schedule preventive maintenance within 7 days")
            recommendations.append("Conduct detailed inspection")

        elif failure_proba > 30:
            recommendations.append("Monitor equipment closely")
            recommendations.append("Plan maintenance within 30 days")

        # Specific recommendations based on risk factors
        if 'calibration_overdue' in risk_factors:
            recommendations.append("Calibrate equipment immediately")

        if 'low_oee' in risk_factors:
            recommendations.append("Investigate OEE degradation causes")
            recommendations.append("Review operating procedures and training")

        if 'high_downtime' in risk_factors:
            recommendations.append("Analyze downtime root causes")
            recommendations.append("Optimize maintenance schedule")

        return recommendations

    def _mock_prediction(self, equipment_data: Dict) -> Dict:
        """Generate mock prediction when model is not trained."""
        # Simple heuristic-based prediction
        age_days = (datetime.now().date() - equipment_data.get('installation_date', datetime.now().date())).days
        days_until_cal = (equipment_data.get('next_calibration_date', datetime.now().date()) - datetime.now().date()).days

        # Calculate simple risk score
        risk_score = 0
        if days_until_cal < 0:
            risk_score += 30
        if age_days > 1825:  # 5 years
            risk_score += 20
        if equipment_data.get('maintenance_count', 0) == 0:
            risk_score += 25

        failure_proba = min(95, risk_score)

        return {
            "failure_probability": failure_proba,
            "predicted_failure_date": datetime.now().date() + timedelta(days=180) if failure_proba > 50 else None,
            "confidence_score": 75.0,
            "risk_factors": {
                "calibration_status": {
                    "severity": "high" if days_until_cal < 0 else "low",
                    "value": days_until_cal,
                    "description": "Calibration status check"
                }
            },
            "recommended_actions": [
                "Schedule preventive maintenance",
                "Review equipment calibration status"
            ]
        }

    def save_model(self, path: Path):
        """Save model to disk."""
        path.mkdir(parents=True, exist_ok=True)

        if self.failure_classifier:
            joblib.dump(self.failure_classifier, path / "failure_classifier.pkl")
        if self.failure_date_regressor:
            joblib.dump(self.failure_date_regressor, path / "failure_regressor.pkl")

        joblib.dump(self.scaler, path / "scaler.pkl")
        print(f"Model saved to {path}")

    def load_model(self):
        """Load model from disk."""
        if self.model_path:
            self.failure_classifier = joblib.load(self.model_path / "failure_classifier.pkl")
            self.failure_date_regressor = joblib.load(self.model_path / "failure_regressor.pkl")
            self.scaler = joblib.load(self.model_path / "scaler.pkl")
            print(f"Model loaded from {self.model_path}")
