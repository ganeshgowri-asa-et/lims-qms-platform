"""
Analytics Service Layer for KPI calculations and metric aggregations
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, extract, distinct
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
import pandas as pd
import numpy as np
from backend.models import *


class KPICalculator:
    """KPI calculation engine"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_document_approval_time(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Calculate average document approval time"""
        documents = self.db.query(Document).filter(
            and_(
                Document.status == 'Approved',
                Document.approved_at != None,
                Document.created_at >= str(start_date),
                Document.created_at <= str(end_date),
                Document.is_deleted == False
            )
        ).all()

        if not documents:
            return {"average_days": 0, "count": 0, "median_days": 0}

        approval_times = []
        for doc in documents:
            if doc.approved_at and doc.created_at:
                # Convert string to datetime if needed
                approved = datetime.fromisoformat(doc.approved_at.replace('Z', '+00:00')) if isinstance(doc.approved_at, str) else doc.approved_at
                created = doc.created_at
                delta = (approved - created).days
                approval_times.append(delta)

        return {
            "average_days": round(np.mean(approval_times), 2) if approval_times else 0,
            "median_days": round(np.median(approval_times), 2) if approval_times else 0,
            "min_days": min(approval_times) if approval_times else 0,
            "max_days": max(approval_times) if approval_times else 0,
            "count": len(approval_times)
        }

    def calculate_task_completion_rate(self, start_date: date, end_date: date,
                                      department: Optional[str] = None,
                                      user_id: Optional[int] = None) -> Dict[str, Any]:
        """Calculate task completion rate"""
        query = self.db.query(Task).filter(
            and_(
                Task.created_at >= str(start_date),
                Task.created_at <= str(end_date),
                Task.is_deleted == False
            )
        )

        if department:
            query = query.filter(Task.department == department)
        if user_id:
            query = query.filter(Task.assigned_to_id == user_id)

        total_tasks = query.count()
        completed_tasks = query.filter(Task.status == 'Completed').count()
        on_time_tasks = query.filter(
            and_(
                Task.status == 'Completed',
                Task.completed_at <= Task.due_date
            )
        ).count()

        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        on_time_rate = (on_time_tasks / total_tasks * 100) if total_tasks > 0 else 0

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round(completion_rate, 2),
            "on_time_tasks": on_time_tasks,
            "on_time_rate": round(on_time_rate, 2)
        }

    def calculate_workflow_cycle_time(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Calculate average workflow cycle time"""
        projects = self.db.query(Project).filter(
            and_(
                Project.status == 'Completed',
                Project.actual_end_date != None,
                Project.start_date != None,
                Project.start_date >= start_date,
                Project.actual_end_date <= end_date,
                Project.is_deleted == False
            )
        ).all()

        if not projects:
            return {"average_days": 0, "count": 0}

        cycle_times = []
        for project in projects:
            delta = (project.actual_end_date - project.start_date).days
            cycle_times.append(delta)

        return {
            "average_days": round(np.mean(cycle_times), 2),
            "median_days": round(np.median(cycle_times), 2),
            "count": len(cycle_times)
        }

    def calculate_equipment_utilization(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Calculate equipment utilization rate"""
        total_equipment = self.db.query(Equipment).filter(
            Equipment.is_deleted == False
        ).count()

        # Equipment with recent calibration (considered active)
        active_equipment = self.db.query(Equipment).filter(
            and_(
                Equipment.calibration_required == True,
                Equipment.last_calibration_date >= start_date,
                Equipment.is_deleted == False
            )
        ).count()

        # Equipment due for calibration (may indicate lack of use)
        overdue_calibration = self.db.query(Equipment).filter(
            and_(
                Equipment.calibration_required == True,
                Equipment.next_calibration_date < date.today(),
                Equipment.is_deleted == False
            )
        ).count()

        utilization_rate = (active_equipment / total_equipment * 100) if total_equipment > 0 else 0

        return {
            "total_equipment": total_equipment,
            "active_equipment": active_equipment,
            "utilization_rate": round(utilization_rate, 2),
            "overdue_calibration": overdue_calibration
        }

    def calculate_test_turnaround_time(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Calculate test/order turnaround time (from CRM orders)"""
        orders = self.db.query(Order).filter(
            and_(
                Order.status == 'Delivered',
                Order.order_date >= start_date,
                Order.delivery_date <= end_date,
                Order.is_deleted == False
            )
        ).all()

        if not orders:
            return {"average_days": 0, "count": 0}

        turnaround_times = []
        for order in orders:
            if order.delivery_date and order.order_date:
                delta = (order.delivery_date - order.order_date).days
                turnaround_times.append(delta)

        return {
            "average_days": round(np.mean(turnaround_times), 2) if turnaround_times else 0,
            "median_days": round(np.median(turnaround_times), 2) if turnaround_times else 0,
            "count": len(turnaround_times)
        }

    def calculate_nonconformance_rate(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Calculate nonconformance rates by severity"""
        ncs = self.db.query(NonConformance).filter(
            and_(
                NonConformance.detected_date >= start_date,
                NonConformance.detected_date <= end_date,
                NonConformance.is_deleted == False
            )
        ).all()

        total_ncs = len(ncs)

        by_severity = {
            "Low": 0,
            "Medium": 0,
            "High": 0,
            "Critical": 0
        }

        closed_count = 0
        open_count = 0

        for nc in ncs:
            if nc.severity:
                severity_str = nc.severity.value if hasattr(nc.severity, 'value') else str(nc.severity)
                if severity_str in by_severity:
                    by_severity[severity_str] += 1

            if nc.status == NCStatusEnum.CLOSED:
                closed_count += 1
            elif nc.status in [NCStatusEnum.OPEN, NCStatusEnum.INVESTIGATING]:
                open_count += 1

        closure_rate = (closed_count / total_ncs * 100) if total_ncs > 0 else 0

        return {
            "total_ncs": total_ncs,
            "by_severity": by_severity,
            "closed": closed_count,
            "open": open_count,
            "closure_rate": round(closure_rate, 2)
        }

    def calculate_customer_satisfaction(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Calculate customer satisfaction metrics"""
        # From support tickets - measure resolution time and quality
        tickets = self.db.query(SupportTicket).filter(
            and_(
                SupportTicket.created_date >= start_date,
                SupportTicket.created_date <= end_date,
                SupportTicket.is_deleted == False
            )
        ).all()

        total_tickets = len(tickets)
        resolved_tickets = len([t for t in tickets if t.status == 'Closed'])
        resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0

        # Calculate average resolution time
        resolution_times = []
        for ticket in tickets:
            if ticket.status == 'Closed' and ticket.resolved_at and ticket.created_date:
                resolved = datetime.fromisoformat(ticket.resolved_at.replace('Z', '+00:00')) if isinstance(ticket.resolved_at, str) else ticket.resolved_at
                delta = (resolved - datetime.combine(ticket.created_date, datetime.min.time())).days
                resolution_times.append(delta)

        avg_resolution_days = round(np.mean(resolution_times), 2) if resolution_times else 0

        return {
            "total_tickets": total_tickets,
            "resolved_tickets": resolved_tickets,
            "resolution_rate": round(resolution_rate, 2),
            "average_resolution_days": avg_resolution_days
        }


class TrendAnalyzer:
    """Analyze trends in KPI data"""

    def __init__(self, db: Session):
        self.db = db

    def get_kpi_trend(self, kpi_definition_id: int, months: int = 12) -> Dict[str, Any]:
        """Get trend for a specific KPI over time"""
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)

        measurements = self.db.query(KPIMeasurement).filter(
            and_(
                KPIMeasurement.kpi_definition_id == kpi_definition_id,
                KPIMeasurement.measurement_date >= start_date,
                KPIMeasurement.measurement_date <= end_date
            )
        ).order_by(KPIMeasurement.measurement_date).all()

        if not measurements:
            return {"trend": "STABLE", "data_points": []}

        data_points = [
            {
                "date": m.measurement_date.isoformat(),
                "value": float(m.actual_value),
                "target": float(m.target_value) if m.target_value else None
            }
            for m in measurements
        ]

        # Calculate trend using linear regression
        values = [float(m.actual_value) for m in measurements]
        if len(values) >= 2:
            x = np.arange(len(values))
            slope = np.polyfit(x, values, 1)[0]

            # Determine trend direction
            if abs(slope) < 0.1:
                trend = "STABLE"
            elif slope > 0:
                trend = "UP"
            else:
                trend = "DOWN"
        else:
            trend = "STABLE"

        return {
            "trend": trend,
            "slope": float(slope) if len(values) >= 2 else 0,
            "data_points": data_points,
            "latest_value": float(measurements[-1].actual_value),
            "change_from_first": float(measurements[-1].actual_value) - float(measurements[0].actual_value)
        }

    def forecast_kpi(self, kpi_definition_id: int, periods_ahead: int = 3) -> List[Dict[str, Any]]:
        """Simple linear forecast for KPI"""
        measurements = self.db.query(KPIMeasurement).filter(
            KPIMeasurement.kpi_definition_id == kpi_definition_id
        ).order_by(KPIMeasurement.measurement_date.desc()).limit(12).all()

        if len(measurements) < 3:
            return []

        measurements.reverse()  # Order chronologically
        values = [float(m.actual_value) for m in measurements]
        x = np.arange(len(values))

        # Fit linear model
        coefficients = np.polyfit(x, values, 1)
        poly = np.poly1d(coefficients)

        # Generate forecasts
        forecasts = []
        last_date = measurements[-1].measurement_date

        for i in range(1, periods_ahead + 1):
            forecast_value = poly(len(values) + i - 1)
            forecast_date = last_date + timedelta(days=30 * i)  # Assuming monthly

            forecasts.append({
                "date": forecast_date.isoformat(),
                "forecast_value": round(float(forecast_value), 2),
                "is_forecast": True
            })

        return forecasts


class AnomalyDetector:
    """Detect anomalies in metrics"""

    def __init__(self, db: Session):
        self.db = db

    def detect_anomalies(self, kpi_definition_id: int, sensitivity: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalies using standard deviation method"""
        measurements = self.db.query(KPIMeasurement).filter(
            KPIMeasurement.kpi_definition_id == kpi_definition_id
        ).order_by(KPIMeasurement.measurement_date).limit(100).all()

        if len(measurements) < 10:
            return []

        values = [float(m.actual_value) for m in measurements]
        mean = np.mean(values)
        std = np.std(values)

        anomalies = []
        for measurement in measurements:
            value = float(measurement.actual_value)
            z_score = abs((value - mean) / std) if std > 0 else 0

            if z_score > sensitivity:
                anomaly_type = "spike" if value > mean else "drop"
                severity = "critical" if z_score > 3 else "high" if z_score > 2.5 else "medium"

                anomalies.append({
                    "date": measurement.measurement_date.isoformat(),
                    "value": value,
                    "expected_value": round(mean, 2),
                    "deviation": round(value - mean, 2),
                    "z_score": round(z_score, 2),
                    "anomaly_type": anomaly_type,
                    "severity": severity
                })

        return anomalies

    def detect_metric_anomalies(self, metric_name: str, data_source: str,
                                values: List[float], dates: List[date]) -> List[Dict[str, Any]]:
        """Generic anomaly detection for any metric"""
        if len(values) < 10:
            return []

        mean = np.mean(values)
        std = np.std(values)

        anomalies = []
        for i, (value, dt) in enumerate(zip(values, dates)):
            z_score = abs((value - mean) / std) if std > 0 else 0

            if z_score > 2.0:
                anomaly_type = "spike" if value > mean else "drop"
                severity = "critical" if z_score > 3 else "high" if z_score > 2.5 else "medium"

                # Create anomaly detection record
                anomaly = AnomalyDetection(
                    detection_date=datetime.now(),
                    metric_name=metric_name,
                    data_source=data_source,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    expected_value=Decimal(str(round(mean, 2))),
                    actual_value=Decimal(str(round(value, 2))),
                    deviation_percentage=Decimal(str(round((value - mean) / mean * 100, 2))) if mean != 0 else Decimal('0'),
                    description=f"{anomaly_type.capitalize()} detected in {metric_name}",
                    acknowledged=False
                )

                self.db.add(anomaly)
                anomalies.append({
                    "date": dt.isoformat() if isinstance(dt, date) else dt,
                    "value": value,
                    "expected": round(mean, 2),
                    "severity": severity
                })

        if anomalies:
            self.db.commit()

        return anomalies


class BenchmarkAnalyzer:
    """Benchmark analysis"""

    def __init__(self, db: Session):
        self.db = db

    def compare_internal_benchmarks(self, metric_name: str, department: str) -> Dict[str, Any]:
        """Compare department performance to internal benchmarks"""
        benchmarks = self.db.query(BenchmarkData).filter(
            and_(
                BenchmarkData.metric_name == metric_name,
                BenchmarkData.is_internal == True
            )
        ).all()

        if not benchmarks:
            return {}

        dept_benchmark = next((b for b in benchmarks if b.benchmark_source == department), None)

        if not dept_benchmark:
            return {}

        other_benchmarks = [b for b in benchmarks if b.benchmark_source != department]

        if not other_benchmarks:
            return {"position": "only_department"}

        values = [float(b.benchmark_value) for b in other_benchmarks]
        avg = np.mean(values)
        best = max(values)
        worst = min(values)

        dept_value = float(dept_benchmark.benchmark_value)

        # Calculate percentile
        all_values = values + [dept_value]
        percentile = (sum(1 for v in all_values if v <= dept_value) / len(all_values)) * 100

        return {
            "department_value": dept_value,
            "company_average": round(avg, 2),
            "best_performer": round(best, 2),
            "worst_performer": round(worst, 2),
            "percentile": round(percentile, 2),
            "gap_from_average": round(dept_value - avg, 2),
            "gap_from_best": round(dept_value - best, 2)
        }


class ReportGenerator:
    """Generate analytical reports"""

    def __init__(self, db: Session):
        self.db = db
        self.kpi_calc = KPICalculator(db)

    def generate_executive_dashboard(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate executive dashboard data"""
        return {
            "document_approval": self.kpi_calc.calculate_document_approval_time(start_date, end_date),
            "task_completion": self.kpi_calc.calculate_task_completion_rate(start_date, end_date),
            "equipment_utilization": self.kpi_calc.calculate_equipment_utilization(start_date, end_date),
            "nonconformance": self.kpi_calc.calculate_nonconformance_rate(start_date, end_date),
            "customer_satisfaction": self.kpi_calc.calculate_customer_satisfaction(start_date, end_date),
            "test_turnaround": self.kpi_calc.calculate_test_turnaround_time(start_date, end_date)
        }

    def generate_quality_metrics_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate comprehensive quality metrics report"""
        # NC statistics
        ncs = self.db.query(NonConformance).filter(
            and_(
                NonConformance.detected_date >= start_date,
                NonConformance.detected_date <= end_date,
                NonConformance.is_deleted == False
            )
        ).all()

        # CAPA statistics
        capas = self.db.query(CAPA).filter(
            and_(
                CAPA.created_at >= str(start_date),
                CAPA.created_at <= str(end_date),
                CAPA.is_deleted == False
            )
        ).all()

        # Audit statistics
        audits = self.db.query(Audit).filter(
            and_(
                Audit.planned_date >= start_date,
                Audit.planned_date <= end_date,
                Audit.is_deleted == False
            )
        ).all()

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "nonconformances": {
                "total": len(ncs),
                "by_status": self._group_by_attribute(ncs, 'status'),
                "by_severity": self._group_by_attribute(ncs, 'severity'),
                "by_department": self._group_by_attribute(ncs, 'area_department')
            },
            "capas": {
                "total": len(capas),
                "by_status": self._group_by_attribute(capas, 'status'),
                "effectiveness_rate": self._calculate_capa_effectiveness(capas)
            },
            "audits": {
                "total": len(audits),
                "by_type": self._group_by_attribute(audits, 'audit_type'),
                "by_status": self._group_by_attribute(audits, 'status')
            }
        }

    def _group_by_attribute(self, items: List, attribute: str) -> Dict[str, int]:
        """Helper to group items by attribute"""
        grouped = {}
        for item in items:
            value = getattr(item, attribute, None)
            if value:
                key = value.value if hasattr(value, 'value') else str(value)
                grouped[key] = grouped.get(key, 0) + 1
        return grouped

    def _calculate_capa_effectiveness(self, capas: List[CAPA]) -> float:
        """Calculate CAPA effectiveness rate"""
        verified = len([c for c in capas if c.status == CAPAStatusEnum.VERIFIED and c.is_effective == True])
        total_completed = len([c for c in capas if c.status in [CAPAStatusEnum.VERIFIED, CAPAStatusEnum.CLOSED]])
        return round((verified / total_completed * 100), 2) if total_completed > 0 else 0
