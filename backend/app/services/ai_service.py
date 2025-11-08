"""
AI service for predictive maintenance, failure detection, and calibration optimization
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import pickle
import os
import logging

from app.models.equipment import EquipmentMaster, EquipmentUtilization
from app.models.calibration import CalibrationRecord
from app.models.maintenance import (
    MaintenanceRecord,
    EquipmentFailureLog,
    MaintenanceType,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered predictive analytics"""

    @staticmethod
    async def prepare_equipment_data(
        db: AsyncSession, equipment_id: int, lookback_days: int = 365
    ) -> pd.DataFrame:
        """Prepare equipment data for ML analysis"""
        cutoff_date = date.today() - timedelta(days=lookback_days)

        # Get maintenance records
        maintenance_result = await db.execute(
            select(MaintenanceRecord).where(
                and_(
                    MaintenanceRecord.equipment_id == equipment_id,
                    MaintenanceRecord.scheduled_date >= cutoff_date,
                )
            )
        )
        maintenance_records = maintenance_result.scalars().all()

        # Get calibration records
        calibration_result = await db.execute(
            select(CalibrationRecord).where(
                and_(
                    CalibrationRecord.equipment_id == equipment_id,
                    CalibrationRecord.calibration_date >= cutoff_date,
                )
            )
        )
        calibration_records = calibration_result.scalars().all()

        # Get failure logs
        failure_result = await db.execute(
            select(EquipmentFailureLog).where(
                and_(
                    EquipmentFailureLog.equipment_id == equipment_id,
                    EquipmentFailureLog.failure_date
                    >= datetime.combine(cutoff_date, datetime.min.time()),
                )
            )
        )
        failure_logs = failure_result.scalars().all()

        # Get utilization data
        utilization_result = await db.execute(
            select(EquipmentUtilization).where(
                and_(
                    EquipmentUtilization.equipment_id == equipment_id,
                    EquipmentUtilization.date >= cutoff_date,
                )
            )
        )
        utilization_records = utilization_result.scalars().all()

        # Convert to DataFrame
        data = []

        for util in utilization_records:
            # Find failures on this date
            failures_on_date = [
                f for f in failure_logs if f.failure_date.date() == util.date
            ]

            data.append(
                {
                    "date": util.date,
                    "usage_hours": float(util.actual_production_time or 0),
                    "downtime": float(util.downtime or 0),
                    "availability": float(util.availability or 0),
                    "performance": float(util.performance or 0),
                    "quality": float(util.quality or 0),
                    "oee": float(util.oee or 0),
                    "failure_occurred": 1 if failures_on_date else 0,
                    "failure_count": len(failures_on_date),
                }
            )

        df = pd.DataFrame(data)

        if len(df) > 0:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")

            # Add derived features
            df["days_since_start"] = (df["date"] - df["date"].min()).dt.days
            df["cumulative_usage"] = df["usage_hours"].cumsum()
            df["rolling_avg_oee"] = df["oee"].rolling(window=7, min_periods=1).mean()
            df["rolling_avg_downtime"] = (
                df["downtime"].rolling(window=7, min_periods=1).mean()
            )

        return df

    @staticmethod
    async def predict_failure_probability(
        db: AsyncSession, equipment_id: int
    ) -> Dict[str, Any]:
        """
        Predict probability of equipment failure in the next 30 days
        """
        try:
            df = await AIService.prepare_equipment_data(db, equipment_id)

            if len(df) < 30:  # Need minimum data
                return {
                    "equipment_id": equipment_id,
                    "failure_probability": 0.0,
                    "confidence": "low",
                    "message": "Insufficient historical data",
                    "recommendations": ["Collect more operational data"],
                }

            # Feature engineering
            features = [
                "usage_hours",
                "downtime",
                "availability",
                "performance",
                "quality",
                "oee",
                "cumulative_usage",
                "rolling_avg_oee",
                "rolling_avg_downtime",
            ]

            X = df[features].fillna(0)
            y = df["failure_occurred"]

            if y.sum() < 3:  # Need minimum failures for training
                return {
                    "equipment_id": equipment_id,
                    "failure_probability": 0.0,
                    "confidence": "low",
                    "message": "Insufficient failure history",
                    "recommendations": ["Continue monitoring equipment"],
                }

            # Train Random Forest model
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            model = RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42
            )
            model.fit(X_scaled, y)

            # Predict on last 7 days average
            latest_data = df[features].tail(7).mean()
            latest_scaled = scaler.transform([latest_data.values])

            failure_prob = model.predict_proba(latest_scaled)[0][1]

            # Determine confidence based on amount of data
            confidence = "high" if len(df) > 180 else "medium" if len(df) > 90 else "low"

            # Generate recommendations
            recommendations = []
            if failure_prob > 0.7:
                recommendations.append("Schedule immediate preventive maintenance")
                recommendations.append("Inspect critical components")
            elif failure_prob > 0.5:
                recommendations.append("Plan maintenance within next 2 weeks")
                recommendations.append("Monitor closely for signs of degradation")
            elif failure_prob > 0.3:
                recommendations.append("Continue regular monitoring")
            else:
                recommendations.append("Equipment operating normally")

            # Feature importance
            feature_importance = dict(
                zip(features, model.feature_importances_.tolist())
            )

            return {
                "equipment_id": equipment_id,
                "failure_probability": round(float(failure_prob) * 100, 2),
                "confidence": confidence,
                "risk_level": (
                    "high"
                    if failure_prob > 0.7
                    else "medium" if failure_prob > 0.4 else "low"
                ),
                "recommendations": recommendations,
                "feature_importance": feature_importance,
                "data_points_analyzed": len(df),
            }

        except Exception as e:
            logger.error(f"Failure prediction error: {str(e)}")
            return {
                "equipment_id": equipment_id,
                "error": str(e),
                "message": "Failed to generate prediction",
            }

    @staticmethod
    async def detect_failure_patterns(
        db: AsyncSession, equipment_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect patterns in equipment failures using clustering
        """
        try:
            # Get failure logs
            query = select(EquipmentFailureLog)
            if equipment_id:
                query = query.where(EquipmentFailureLog.equipment_id == equipment_id)

            result = await db.execute(query)
            failures = result.scalars().all()

            if len(failures) < 5:
                return []

            # Prepare data
            data = []
            for failure in failures:
                data.append(
                    {
                        "equipment_id": failure.equipment_id,
                        "failure_type": failure.failure_type,
                        "severity": failure.severity,
                        "usage_hours": float(failure.usage_hours_at_failure or 0),
                        "days_since_cal": failure.days_since_last_calibration or 0,
                        "days_since_maint": failure.days_since_last_maintenance or 0,
                        "downtime_hours": float(failure.downtime_hours or 0),
                    }
                )

            df = pd.DataFrame(data)

            # Use Isolation Forest for anomaly detection
            features = [
                "usage_hours",
                "days_since_cal",
                "days_since_maint",
                "downtime_hours",
            ]
            X = df[features].fillna(0)

            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            df["anomaly"] = iso_forest.fit_predict(X)

            # Identify patterns
            patterns = []

            # Pattern 1: Failures related to overdue calibration
            overdue_cal_failures = df[df["days_since_cal"] > 180]
            if len(overdue_cal_failures) > 0:
                patterns.append(
                    {
                        "pattern_type": "overdue_calibration",
                        "description": f"{len(overdue_cal_failures)} failures occurred when calibration was overdue",
                        "severity": "high",
                        "recommendation": "Ensure calibrations are performed on time",
                        "affected_equipment_count": overdue_cal_failures[
                            "equipment_id"
                        ].nunique(),
                    }
                )

            # Pattern 2: Failures related to overdue maintenance
            overdue_maint_failures = df[df["days_since_maint"] > 90]
            if len(overdue_maint_failures) > 0:
                patterns.append(
                    {
                        "pattern_type": "overdue_maintenance",
                        "description": f"{len(overdue_maint_failures)} failures occurred when maintenance was overdue",
                        "severity": "high",
                        "recommendation": "Adhere to preventive maintenance schedule",
                        "affected_equipment_count": overdue_maint_failures[
                            "equipment_id"
                        ].nunique(),
                    }
                )

            # Pattern 3: High usage failures
            high_usage_failures = df[df["usage_hours"] > df["usage_hours"].quantile(0.75)]
            if len(high_usage_failures) > 0:
                patterns.append(
                    {
                        "pattern_type": "high_usage",
                        "description": f"{len(high_usage_failures)} failures occurred during high usage periods",
                        "severity": "medium",
                        "recommendation": "Consider more frequent inspections during high usage",
                        "affected_equipment_count": high_usage_failures[
                            "equipment_id"
                        ].nunique(),
                    }
                )

            # Pattern 4: Anomalous failures
            anomalies = df[df["anomaly"] == -1]
            if len(anomalies) > 0:
                patterns.append(
                    {
                        "pattern_type": "anomalous_failures",
                        "description": f"{len(anomalies)} failures show unusual patterns",
                        "severity": "medium",
                        "recommendation": "Investigate root causes of anomalous failures",
                        "affected_equipment_count": anomalies["equipment_id"].nunique(),
                    }
                )

            return patterns

        except Exception as e:
            logger.error(f"Pattern detection error: {str(e)}")
            return []

    @staticmethod
    async def recommend_calibration_frequency(
        db: AsyncSession, equipment_id: int
    ) -> Dict[str, Any]:
        """
        Recommend optimal calibration frequency based on historical data
        """
        try:
            # Get calibration history
            cal_result = await db.execute(
                select(CalibrationRecord)
                .where(CalibrationRecord.equipment_id == equipment_id)
                .order_by(CalibrationRecord.calibration_date.desc())
            )
            calibrations = cal_result.scalars().all()

            if len(calibrations) < 3:
                return {
                    "equipment_id": equipment_id,
                    "current_frequency": "unknown",
                    "recommended_frequency": "yearly",
                    "confidence": "low",
                    "message": "Insufficient calibration history",
                }

            # Analyze drift trends
            drift_data = []
            for cal in calibrations:
                if cal.as_found_data and cal.as_left_data:
                    # Calculate drift (simplified)
                    drift_data.append(
                        {
                            "date": cal.calibration_date,
                            "result": cal.result.value,
                        }
                    )

            df = pd.DataFrame(drift_data)

            # Count failures/out of tolerance
            failures = df[df["result"] == "fail"].shape[0]
            total = len(df)
            failure_rate = failures / total if total > 0 else 0

            # Recommend frequency based on failure rate
            if failure_rate > 0.3:
                recommended_freq = "quarterly"
                reason = "High out-of-tolerance rate detected"
            elif failure_rate > 0.15:
                recommended_freq = "half_yearly"
                reason = "Moderate drift detected"
            else:
                recommended_freq = "yearly"
                reason = "Equipment shows good stability"

            # Get equipment current frequency
            equipment_result = await db.execute(
                select(EquipmentMaster).where(EquipmentMaster.id == equipment_id)
            )
            equipment = equipment_result.scalar_one_or_none()

            current_freq = (
                equipment.calibration_frequency.value
                if equipment and equipment.calibration_frequency
                else "unknown"
            )

            return {
                "equipment_id": equipment_id,
                "current_frequency": current_freq,
                "recommended_frequency": recommended_freq,
                "confidence": "high" if total > 5 else "medium",
                "reason": reason,
                "failure_rate": round(failure_rate * 100, 2),
                "data_points_analyzed": total,
                "change_required": recommended_freq != current_freq,
            }

        except Exception as e:
            logger.error(f"Calibration frequency recommendation error: {str(e)}")
            return {
                "equipment_id": equipment_id,
                "error": str(e),
                "message": "Failed to generate recommendation",
            }

    @staticmethod
    async def generate_predictive_maintenance_schedule(
        db: AsyncSession, equipment_id: int, days_ahead: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Generate predictive maintenance schedule based on AI analysis
        """
        try:
            # Get failure probability
            failure_pred = await AIService.predict_failure_probability(db, equipment_id)

            # Get equipment info
            equipment_result = await db.execute(
                select(EquipmentMaster).where(EquipmentMaster.id == equipment_id)
            )
            equipment = equipment_result.scalar_one_or_none()

            if not equipment:
                return []

            schedule = []
            today = date.today()

            # Recommend maintenance based on failure probability
            if failure_pred.get("failure_probability", 0) > 70:
                schedule.append(
                    {
                        "equipment_id": equipment_id,
                        "equipment_name": equipment.equipment_name,
                        "maintenance_type": "predictive",
                        "recommended_date": today + timedelta(days=7),
                        "priority": "urgent",
                        "reason": "High failure probability detected",
                        "failure_risk": failure_pred.get("failure_probability"),
                    }
                )
            elif failure_pred.get("failure_probability", 0) > 50:
                schedule.append(
                    {
                        "equipment_id": equipment_id,
                        "equipment_name": equipment.equipment_name,
                        "maintenance_type": "predictive",
                        "recommended_date": today + timedelta(days=21),
                        "priority": "high",
                        "reason": "Elevated failure probability",
                        "failure_risk": failure_pred.get("failure_probability"),
                    }
                )

            # Add regular preventive maintenance if scheduled
            if equipment.next_maintenance_date:
                schedule.append(
                    {
                        "equipment_id": equipment_id,
                        "equipment_name": equipment.equipment_name,
                        "maintenance_type": "preventive",
                        "recommended_date": equipment.next_maintenance_date,
                        "priority": "normal",
                        "reason": "Scheduled preventive maintenance",
                        "failure_risk": failure_pred.get("failure_probability", 0),
                    }
                )

            return sorted(schedule, key=lambda x: x["recommended_date"])

        except Exception as e:
            logger.error(f"Predictive schedule generation error: {str(e)}")
            return []
