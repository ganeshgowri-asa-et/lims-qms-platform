"""
Test Duration Estimation Model
ML regression model for predicting test completion time

Uses XGBoost regression to predict test duration based on:
- Test standard type (IEC 61215, 61730, 61701)
- Number of samples
- Test parameters count
- Historical test execution times
- Equipment availability
- Lab workload
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import joblib
from pathlib import Path

try:
    import xgboost as xgb
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
except ImportError:
    pass


class TestDurationEstimator:
    """Test duration estimation model using ML regression."""

    def __init__(self, model_path: Optional[Path] = None):
        """Initialize the model.

        Args:
            model_path: Path to saved model files
        """
        self.model_path = model_path
        self.regressor = None
        self.encoders = {}
        self.feature_names = []

        if model_path and model_path.exists():
            self.load_model()

    def extract_features(self, test_request_data: Dict) -> np.ndarray:
        """Extract features from test request data.

        Features:
        1. Test standard type (encoded)
        2. Number of samples
        3. Number of test parameters
        4. Product type (encoded)
        5. Urgency level (encoded)
        6. Day of week (test start)
        7. Month of year
        8. Historical average for similar tests
        9. Current lab workload (pending tests)
        10. Equipment availability score

        Args:
            test_request_data: Dictionary with test request information

        Returns:
            Feature vector as numpy array
        """
        features = []

        # Test standard (categorical)
        test_standard = test_request_data.get('test_standard', 'IEC 61215')
        if 'test_standard' in self.encoders:
            std_encoded = self.encoders['test_standard'].transform([test_standard])[0]
        else:
            std_encoded = hash(test_standard) % 10
        features.append(std_encoded)

        # Sample and parameter counts
        features.append(test_request_data.get('sample_count', 1))
        features.append(test_request_data.get('test_parameter_count', 10))

        # Product type (categorical)
        product_type = test_request_data.get('product_type', 'Solar Module')
        if 'product_type' in self.encoders:
            prod_encoded = self.encoders['product_type'].transform([product_type])[0]
        else:
            prod_encoded = hash(product_type) % 5
        features.append(prod_encoded)

        # Urgency (categorical)
        urgency_map = {'Normal': 0, 'Urgent': 1, 'Rush': 2}
        urgency = test_request_data.get('urgency', 'Normal')
        features.append(urgency_map.get(urgency, 0))

        # Time features
        request_date = test_request_data.get('request_date', datetime.now())
        if isinstance(request_date, str):
            request_date = datetime.strptime(request_date, '%Y-%m-%d')

        features.append(request_date.weekday())  # Day of week (0-6)
        features.append(request_date.month)  # Month (1-12)

        # Historical average
        features.append(test_request_data.get('historical_avg_duration', 30))

        # Current workload
        features.append(test_request_data.get('current_lab_workload', 5))

        # Equipment availability (0-100)
        features.append(test_request_data.get('equipment_availability_score', 80))

        return np.array(features).reshape(1, -1)

    def train(self, training_data: pd.DataFrame):
        """Train the test duration estimation model.

        Args:
            training_data: DataFrame with test request data and actual durations
                Required columns:
                - test_standard
                - sample_count
                - test_parameter_count
                - product_type
                - urgency
                - request_date
                - actual_duration_days (target)
        """
        print("Training Test Duration Estimation Model...")

        # Encode categorical features
        self.encoders['test_standard'] = LabelEncoder()
        self.encoders['product_type'] = LabelEncoder()

        training_data['test_standard_encoded'] = self.encoders['test_standard'].fit_transform(
            training_data['test_standard']
        )
        training_data['product_type_encoded'] = self.encoders['product_type'].fit_transform(
            training_data['product_type']
        )

        # Extract features
        X = np.vstack([
            self.extract_features(row.to_dict())
            for _, row in training_data.iterrows()
        ])

        # Target
        y = training_data['actual_duration_days'].values

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train XGBoost regressor
        print("Training XGBoost regressor...")
        self.regressor = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            objective='reg:squarederror',
            random_state=42
        )

        self.regressor.fit(X_train, y_train)

        # Evaluate
        train_pred = self.regressor.predict(X_train)
        test_pred = self.regressor.predict(X_test)

        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
        test_r2 = r2_score(y_test, test_pred)

        print(f"Train MAE: {train_mae:.2f} days")
        print(f"Test MAE: {test_mae:.2f} days")
        print(f"Test RMSE: {test_rmse:.2f} days")
        print(f"Test R²: {test_r2:.3f}")
        print("Model training complete!")

    def predict(self, test_request_data: Dict) -> Dict:
        """Predict test duration for a test request.

        Args:
            test_request_data: Dictionary with test request information

        Returns:
            Dictionary with:
            - predicted_duration_days: Predicted duration
            - confidence_interval: {lower_bound, upper_bound}
            - factors_considered: Key factors affecting duration
        """
        if self.regressor is None:
            return self._mock_prediction(test_request_data)

        # Extract features
        features = self.extract_features(test_request_data)

        # Predict
        predicted_days = max(1, int(self.regressor.predict(features)[0]))

        # Confidence interval (±20% for demonstration)
        lower_bound = max(1, int(predicted_days * 0.8))
        upper_bound = int(predicted_days * 1.2)

        # Analyze factors
        factors = self._analyze_factors(test_request_data, features[0])

        return {
            "predicted_duration_days": predicted_days,
            "confidence_interval": {
                "lower_bound": lower_bound,
                "upper_bound": upper_bound
            },
            "factors_considered": factors,
            "prediction_date": datetime.now()
        }

    def _analyze_factors(self, test_data: Dict, features: np.ndarray) -> Dict:
        """Analyze factors affecting test duration."""
        factors = {}

        # Sample count impact
        sample_count = test_data.get('sample_count', 1)
        factors['sample_count'] = {
            'value': sample_count,
            'impact': 'high' if sample_count > 5 else 'medium' if sample_count > 2 else 'low'
        }

        # Test parameters impact
        param_count = test_data.get('test_parameter_count', 10)
        factors['test_complexity'] = {
            'value': param_count,
            'impact': 'high' if param_count > 20 else 'medium' if param_count > 10 else 'low'
        }

        # Test standard
        factors['test_standard'] = {
            'value': test_data.get('test_standard', 'IEC 61215'),
            'impact': 'high'
        }

        # Urgency
        urgency = test_data.get('urgency', 'Normal')
        factors['urgency_level'] = {
            'value': urgency,
            'impact': 'high' if urgency == 'Rush' else 'medium' if urgency == 'Urgent' else 'low'
        }

        # Current workload
        workload = test_data.get('current_lab_workload', 5)
        factors['lab_workload'] = {
            'value': workload,
            'impact': 'high' if workload > 10 else 'medium' if workload > 5 else 'low'
        }

        return factors

    def _mock_prediction(self, test_request_data: Dict) -> Dict:
        """Generate mock prediction when model is not trained."""
        # Simple heuristic-based estimation
        sample_count = test_request_data.get('sample_count', 1)
        param_count = test_request_data.get('test_parameter_count', 10)
        test_standard = test_request_data.get('test_standard', 'IEC 61215')

        # Base duration by standard
        base_duration = {
            'IEC 61215': 45,
            'IEC 61730': 30,
            'IEC 61701': 60
        }.get(test_standard, 40)

        # Adjust for samples and parameters
        duration = base_duration + (sample_count - 1) * 5 + (param_count - 10) * 0.5

        # Urgency adjustment
        urgency = test_request_data.get('urgency', 'Normal')
        if urgency == 'Rush':
            duration *= 0.7  # Faster turnaround
        elif urgency == 'Urgent':
            duration *= 0.85

        predicted_days = max(5, int(duration))

        return {
            "predicted_duration_days": predicted_days,
            "confidence_interval": {
                "lower_bound": max(5, int(predicted_days * 0.8)),
                "upper_bound": int(predicted_days * 1.2)
            },
            "factors_considered": self._analyze_factors(test_request_data, np.array([])),
            "prediction_date": datetime.now()
        }

    def save_model(self, path: Path):
        """Save model to disk."""
        path.mkdir(parents=True, exist_ok=True)

        if self.regressor:
            joblib.dump(self.regressor, path / "duration_regressor.pkl")

        joblib.dump(self.encoders, path / "encoders.pkl")
        print(f"Model saved to {path}")

    def load_model(self):
        """Load model from disk."""
        if self.model_path:
            self.regressor = joblib.load(self.model_path / "duration_regressor.pkl")
            self.encoders = joblib.load(self.model_path / "encoders.pkl")
            print(f"Model loaded from {self.model_path}")
