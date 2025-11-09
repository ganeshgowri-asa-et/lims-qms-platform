# Analytics, KPI & Continual Improvement System

## Overview

The LIMS-QMS Analytics System provides comprehensive business intelligence, KPI tracking, and continual improvement capabilities for laboratory and quality management operations.

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Database Models](#database-models)
4. [API Endpoints](#api-endpoints)
5. [KPI Definitions](#kpi-definitions)
6. [Continual Improvement Tools](#continual-improvement-tools)
7. [AI-Powered Insights](#ai-powered-insights)
8. [Usage Examples](#usage-examples)

---

## Features

### 1. KPI Dashboard
- **Real-time KPI tracking** with customizable targets
- **Performance metrics** across all modules:
  - Document approval times
  - Task completion rates
  - Workflow cycle times
  - Equipment utilization
  - Test turnaround time
  - Nonconformance rates
  - Customer satisfaction scores
- **Customizable dashboard widgets**
- **Department/team/individual views**
- **Trend analysis and forecasting**

### 2. Business Intelligence
- **Interactive charts**: Line, Bar, Pie, Heatmaps
- **Drill-down capabilities**
- **Advanced filtering**: Date range, department, project, user
- **Export reports**: PDF, Excel, PowerPoint
- **Scheduled report generation**
- **Email distribution lists**

### 3. Continual Improvement Module
- **Kaizen suggestions** submission and tracking
- **PDCA (Plan-Do-Check-Act)** cycle tracking
- **8D problem-solving** methodology
- **5 Why analysis** for root cause investigation
- **Fishbone diagrams** (Ishikawa)
- **FMEA** (Failure Mode Effects Analysis)
- **Improvement initiative tracking**
- **Before/after metrics**
- **ROI calculation**

### 4. Nonconformance & CAPA Analytics
- NC logging and classification (minor/major/critical)
- Root cause analysis tools
- Corrective/Preventive actions tracking
- Effectiveness verification
- Recurrence analysis
- NC closure workflow analytics

### 5. Audit Analytics
- Audit findings trends
- NC by department/process
- Closure rate tracking
- Compliance score calculation
- Risk heatmaps

### 6. Quality Objectives Tracking
- Set organizational/departmental objectives
- Link to KPIs
- Quarterly/annual reviews
- Achievement percentage tracking
- Gap analysis

### 7. Benchmarking
- Internal benchmarking across departments
- Industry standard comparisons
- Best practice identification

### 8. AI-Powered Insights
- Anomaly detection in data
- Predictive analytics (failure prediction, resource planning)
- Smart recommendations for process optimization
- Natural language queries

### 9. Custom Report Builder
- Drag-and-drop report designer (API-ready)
- SQL query interface for advanced users
- Template library
- Share/save reports

---

## Architecture

### Technology Stack

- **Backend**: FastAPI + PostgreSQL
- **Analytics**: Pandas, NumPy, Scikit-learn
- **Visualization**: Plotly, Matplotlib
- **ML**: Scikit-learn for predictions
- **Caching**: Redis for performance

### Layer Structure

```
┌─────────────────────────────────────┐
│     Frontend (Streamlit)            │
├─────────────────────────────────────┤
│     API Endpoints (FastAPI)         │
├─────────────────────────────────────┤
│     Service Layer                   │
│  - KPICalculator                    │
│  - TrendAnalyzer                    │
│  - AnomalyDetector                  │
│  - BenchmarkAnalyzer                │
│  - ReportGenerator                  │
├─────────────────────────────────────┤
│     Database Models (SQLAlchemy)    │
├─────────────────────────────────────┤
│     PostgreSQL Database             │
└─────────────────────────────────────┘
```

---

## Database Models

### Core Analytics Models

#### 1. KPIDefinition
Defines what KPIs to track across the organization.

**Fields:**
- `kpi_code`: Unique identifier (e.g., KPI-DOC-001)
- `name`: KPI name
- `description`: Detailed description
- `category`: Quality, Productivity, Financial, Customer Satisfaction
- `calculation_method`: Formula or description
- `target_value`: Goal to achieve
- `unit_of_measure`: %, days, count, etc.
- `frequency`: Daily, Weekly, Monthly, Quarterly, Annually
- `is_higher_better`: True if higher values are better
- `department`: Owning department
- `show_on_dashboard`: Display on main dashboard

#### 2. KPIMeasurement
Actual KPI values recorded over time.

**Fields:**
- `kpi_definition_id`: Link to KPI definition
- `measurement_date`: Date of measurement
- `actual_value`: Measured value
- `target_value`: Target for this period
- `variance`: actual - target
- `variance_percentage`: Variance as percentage
- `trend`: Up, Down, Stable
- `meets_target`: Boolean flag
- `notes`: Contextual information

#### 3. QualityObjective
Organizational and departmental quality objectives.

**Fields:**
- `objective_number`: Unique identifier (e.g., QO-2025-001)
- `title`: Objective title
- `description`: Detailed description
- `category`: Customer Satisfaction, Process Improvement, Compliance
- `measurable_target`: Specific, measurable goal
- `kpi_definition_ids`: Linked KPIs (JSON)
- `current_achievement_percentage`: Progress tracking
- `start_date`, `target_date`: Timeline
- `status`: active, achieved, not_achieved, cancelled

### Continual Improvement Models

#### 4. KaizenSuggestion
Employee-submitted improvement suggestions.

**Fields:**
- `suggestion_number`: Unique identifier
- `title`, `description`: Suggestion details
- `current_situation`: Problem description
- `proposed_improvement`: Solution proposed
- `expected_benefits`: Anticipated outcomes
- `category`: Cost Reduction, Quality, Safety, Productivity
- `status`: Draft, Submitted, Under Review, Approved, Implemented, etc.
- `estimated_cost`, `actual_cost`: Financial tracking
- `estimated_savings`, `actual_savings`: ROI metrics
- `roi_percentage`: Return on investment
- `reward_points`: Recognition system

#### 5. ImprovementInitiative
Major improvement projects using structured methodologies.

**Fields:**
- `initiative_number`: Unique identifier
- `methodology`: 5 Why, Fishbone, 8D, PDCA, DMAIC, A3, FMEA
- `problem_statement`: Clear problem definition
- `team_leader_id`, `team_members`: Team assignment
- `status`: Draft, In Progress, Implemented, Verified, Closed
- `estimated_cost`, `actual_cost`: Budget tracking
- `estimated_benefit`, `actual_benefit`: Value tracking
- `roi_percentage`: Financial impact

#### 6. FiveWhyAnalysis
Root cause analysis using 5 Why methodology.

**Fields:**
- `problem_statement`: Initial problem
- `why_1` through `why_5`: The 5 why questions
- `answer_1` through `answer_5`: Corresponding answers
- `additional_whys`: JSON for deeper analysis
- `root_cause`: Final root cause identified
- `corrective_actions`: Actions to address root cause

#### 7. FishboneDiagram
Ishikawa/Fishbone diagram for cause analysis.

**Fields:**
- `problem_statement`: Effect being analyzed
- `man_causes`: People-related causes (JSON)
- `method_causes`: Process/procedure causes (JSON)
- `machine_causes`: Equipment causes (JSON)
- `material_causes`: Material/supply causes (JSON)
- `measurement_causes`: Measurement/inspection causes (JSON)
- `environment_causes`: Environmental causes (JSON)
- `custom_categories`: Additional categories (JSON)
- `identified_root_causes`: Prioritized causes (JSON)

#### 8. FMEARecord
Failure Mode and Effects Analysis.

**Fields:**
- `fmea_number`: Unique identifier
- `fmea_type`: Process FMEA, Design FMEA, System FMEA
- `failure_mode`: How it fails
- `potential_effects`: Impact of failure
- `severity`: 1-10 scale
- `potential_causes`: Why it fails
- `occurrence`: 1-10 scale (frequency)
- `current_detection_controls`: How failures are detected
- `detection`: 1-10 scale (detection ability)
- `rpn`: Risk Priority Number (severity × occurrence × detection)
- `recommended_actions`: Mitigation plans
- `revised_rpn`: RPN after actions

#### 9. PDCARecord
PDCA cycle tracking for continuous improvement.

**Fields:**
- `initiative_id`: Link to improvement initiative
- `cycle_number`: Support multiple PDCA cycles
- **Plan phase**: objective, actions, resources, timeline
- **Do phase**: implementation notes, challenges
- **Check phase**: results, data analysis, success criteria
- **Act phase**: standardization, next steps
- `current_phase`: Plan, Do, Check, Act

#### 10. EightDReport
8D (Eight Disciplines) problem-solving.

**Fields:**
- **D0**: Symptom description, emergency actions
- **D1**: Team formation
- **D2**: Problem description (Is/Is Not analysis)
- **D3**: Interim containment actions
- **D4**: Root cause analysis
- **D5**: Permanent corrective actions
- **D6**: Implementation and validation
- **D7**: Prevent recurrence
- **D8**: Team congratulation and lessons learned
- `overall_completion_percentage`: Progress tracking

### Analytics & Reporting Models

#### 11. BenchmarkData
Internal and external benchmarking.

**Fields:**
- `benchmark_name`: Name of benchmark
- `metric_name`: Metric being benchmarked
- `is_internal`: Internal vs external benchmark
- `benchmark_source`: Department or industry source
- `benchmark_value`: Best practice value
- `our_value`: Our current performance
- `gap`: Difference from benchmark
- `gap_percentage`: Gap as percentage
- `best_practice_description`: How to achieve benchmark

#### 12. CustomReport
User-defined report templates.

**Fields:**
- `report_code`: Unique identifier
- `report_name`: Display name
- `data_sources`: Tables/entities to query (JSON)
- `filters`: Filter conditions (JSON)
- `grouping`: Group by fields (JSON)
- `aggregations`: SUM, AVG, COUNT definitions (JSON)
- `chart_type`: line, bar, pie, table
- `is_scheduled`: Enable scheduling
- `schedule_frequency`: Daily, Weekly, Monthly
- `recipients`: Email distribution list (JSON)
- `export_format`: PDF, Excel, PowerPoint

#### 13. AnomalyDetection
AI-detected anomalies in metrics.

**Fields:**
- `metric_name`: Affected metric
- `data_source`: Where anomaly was detected
- `anomaly_type`: spike, drop, trend_break, outlier
- `severity`: low, medium, high, critical
- `expected_value`: What was expected
- `actual_value`: What was observed
- `deviation_percentage`: How far off
- `possible_causes`: AI-suggested causes (JSON)
- `recommended_actions`: AI suggestions (JSON)
- `acknowledged`: Has been reviewed
- `investigation_notes`: Human analysis

#### 14. AnalyticsCache
Pre-calculated analytics for performance.

**Fields:**
- `cache_key`: Unique cache identifier
- `cache_type`: kpi_dashboard, trend_analysis, etc.
- `cached_data`: Pre-calculated results (JSON)
- `expires_at`: Cache expiration
- `access_count`: Usage tracking

---

## API Endpoints

### KPI Dashboard Endpoints

#### GET `/api/v1/analytics/dashboard`
Get comprehensive dashboard statistics.

**Response:**
```json
{
  "projects": {"total": 45, "active": 12},
  "tasks": {"total": 230, "my_tasks": 8, "pending": 5},
  "documents": {"total": 156, "pending_approvals": 3},
  "quality": {"open_ncs": 7, "open_capas": 4},
  "equipment": {"calibration_due": 2},
  "financial": {"total_revenue": 450000, "total_expenses": 280000, "net": 170000},
  "crm": {"active_customers": 78, "pending_orders": 15}
}
```

#### GET `/api/v1/analytics/kpis/dashboard`
Get comprehensive KPI dashboard with calculated metrics.

**Parameters:**
- `start_date` (optional): Start date for KPI calculation
- `end_date` (optional): End date for KPI calculation
- `department` (optional): Filter by department

**Response:**
```json
{
  "period": {"start": "2025-10-01", "end": "2025-11-09"},
  "kpis": {
    "document_approval_time": {
      "average_days": 4.5,
      "median_days": 4.0,
      "count": 23
    },
    "task_completion_rate": {
      "total_tasks": 156,
      "completed_tasks": 142,
      "completion_rate": 91.03,
      "on_time_rate": 85.26
    },
    "equipment_utilization": {
      "total_equipment": 45,
      "active_equipment": 38,
      "utilization_rate": 84.44
    },
    "nonconformance_rate": {
      "total_ncs": 12,
      "by_severity": {"Low": 5, "Medium": 4, "High": 2, "Critical": 1},
      "closure_rate": 75.0
    }
  }
}
```

#### POST `/api/v1/analytics/kpis/definitions`
Create a new KPI definition.

**Request Body:**
```json
{
  "kpi_code": "KPI-CUSTOM-001",
  "name": "Test Accuracy Rate",
  "description": "Percentage of tests passing quality control",
  "category": "Quality",
  "target_value": 99.5,
  "unit_of_measure": "%",
  "frequency": "Monthly",
  "is_higher_better": true,
  "department": "Laboratory"
}
```

#### GET `/api/v1/analytics/kpis/definitions`
List all KPI definitions.

**Parameters:**
- `category` (optional): Filter by category
- `department` (optional): Filter by department

#### POST `/api/v1/analytics/kpis/measurements`
Record a KPI measurement.

**Request Body:**
```json
{
  "kpi_definition_id": 1,
  "measurement_date": "2025-11-01",
  "actual_value": 98.7,
  "target_value": 99.5,
  "notes": "Slight decrease due to new test method"
}
```

#### GET `/api/v1/analytics/kpis/{kpi_id}/trend`
Get trend analysis for a specific KPI.

**Parameters:**
- `months` (default: 12): Number of months to analyze

**Response:**
```json
{
  "trend": "UP",
  "slope": 0.25,
  "data_points": [
    {"date": "2025-01-01", "value": 95.2, "target": 95.0},
    {"date": "2025-02-01", "value": 96.1, "target": 95.0}
  ],
  "latest_value": 98.7,
  "change_from_first": 3.5
}
```

#### GET `/api/v1/analytics/kpis/{kpi_id}/forecast`
Get AI forecast for a KPI.

**Parameters:**
- `periods` (default: 3): Number of periods to forecast

**Response:**
```json
{
  "forecasts": [
    {"date": "2025-12-01", "forecast_value": 99.1, "is_forecast": true},
    {"date": "2026-01-01", "forecast_value": 99.4, "is_forecast": true},
    {"date": "2026-02-01", "forecast_value": 99.7, "is_forecast": true}
  ]
}
```

### Business Intelligence Endpoints

#### GET `/api/v1/analytics/bi/charts/nc-by-department`
Get NC distribution by department for charts.

**Response:**
```json
{
  "chart_type": "bar",
  "data": [
    {"department": "Laboratory", "count": 5},
    {"department": "Quality Assurance", "count": 3},
    {"department": "Production", "count": 4}
  ]
}
```

#### GET `/api/v1/analytics/bi/charts/task-completion-trend`
Get task completion trend over time.

**Parameters:**
- `months` (default: 6): Number of months

**Response:**
```json
{
  "chart_type": "line",
  "data": [
    {"month": "2025-06", "total": 45, "completed": 40, "completion_rate": 88.89},
    {"month": "2025-07", "total": 52, "completed": 48, "completion_rate": 92.31}
  ]
}
```

#### GET `/api/v1/analytics/bi/charts/revenue-vs-expenses`
Get financial trend analysis.

**Response:**
```json
{
  "chart_type": "line",
  "data": [
    {"month": "2025-01", "revenue": 45000, "expenses": 28000, "profit": 17000},
    {"month": "2025-02", "revenue": 48000, "expenses": 29000, "profit": 19000}
  ]
}
```

### Continual Improvement Endpoints

#### POST `/api/v1/analytics/kaizen/suggestions`
Submit a Kaizen suggestion.

**Request Body:**
```json
{
  "title": "Automate Sample Registration",
  "description": "Implement barcode scanning for sample registration",
  "current_situation": "Manual data entry takes 5 minutes per sample",
  "proposed_improvement": "Use barcode scanners to reduce time to 30 seconds",
  "expected_benefits": "80% time reduction, fewer data entry errors",
  "category": "Productivity",
  "area_department": "Laboratory"
}
```

#### GET `/api/v1/analytics/kaizen/suggestions`
List Kaizen suggestions.

**Parameters:**
- `status` (optional): Filter by status
- `category` (optional): Filter by category

#### POST `/api/v1/analytics/improvement/initiatives`
Create an improvement initiative.

**Request Body:**
```json
{
  "title": "Reduce Test Turnaround Time",
  "description": "Systematic approach to reduce TAT from 5 days to 3 days",
  "methodology": "8D",
  "problem_statement": "Customer complaints about slow test results"
}
```

#### POST `/api/v1/analytics/improvement/5why`
Create a 5 Why analysis.

**Request Body:**
```json
{
  "problem_statement": "Equipment calibration overdue",
  "why_1": "Why is calibration overdue?",
  "answer_1": "Calibration reminder was missed",
  "why_2": "Why was the reminder missed?",
  "answer_2": "Notification system didn't send alert",
  "why_3": "Why didn't the system send alert?",
  "answer_3": "Email server was down",
  "why_4": "Why was email server down?",
  "answer_4": "No monitoring of email server status",
  "why_5": "Why is there no monitoring?",
  "answer_5": "No IT monitoring system in place",
  "root_cause": "Lack of IT infrastructure monitoring"
}
```

#### POST `/api/v1/analytics/improvement/fishbone`
Create a Fishbone diagram.

**Request Body:**
```json
{
  "problem_statement": "Test results inconsistent",
  "man_causes": ["Inadequate training", "Operator fatigue"],
  "method_causes": ["Procedure unclear", "Method not validated"],
  "machine_causes": ["Equipment calibration drift", "Old instrument"],
  "material_causes": ["Reagent quality issues", "Expired standards"],
  "measurement_causes": ["Incorrect measurement technique"],
  "environment_causes": ["Temperature fluctuations", "Humidity variations"]
}
```

#### POST `/api/v1/analytics/improvement/fmea`
Create an FMEA record.

**Request Body:**
```json
{
  "title": "Sample Handling FMEA",
  "fmea_type": "Process FMEA",
  "process_name": "Sample Reception",
  "failure_mode": "Sample mislabeled",
  "potential_effects": "Wrong test performed, patient harm",
  "severity": 9,
  "potential_causes": "Manual labeling error",
  "occurrence": 3,
  "current_detection_controls": "Visual verification by technician",
  "detection": 6
}
```

**Response includes calculated RPN:**
```json
{
  "message": "FMEA record created",
  "fmea_number": "FMEA-2025-0001",
  "rpn": 162,
  "id": 1
}
```

### Quality Objectives Endpoints

#### POST `/api/v1/analytics/quality-objectives`
Create a quality objective.

**Request Body:**
```json
{
  "title": "Reduce Sample Rejection Rate",
  "description": "Reduce sample rejections from 5% to 2%",
  "category": "Quality",
  "department": "Laboratory",
  "measurable_target": "Sample rejection rate <= 2%"
}
```

#### GET `/api/v1/analytics/quality-objectives`
List quality objectives.

**Parameters:**
- `status` (optional): Filter by status
- `department` (optional): Filter by department

### Audit Analytics Endpoints

#### GET `/api/v1/analytics/audit-analytics`
Get comprehensive audit analytics.

**Parameters:**
- `start_date`, `end_date`: Date range

**Response:**
```json
{
  "total_audits": 12,
  "by_type": {
    "Internal": 8,
    "External": 2,
    "Surveillance": 2
  },
  "by_status": {
    "Planned": 2,
    "In Progress": 1,
    "Completed": 7,
    "Report Issued": 2
  },
  "ncs_generated": 15
}
```

### Benchmarking Endpoints

#### POST `/api/v1/analytics/benchmarks`
Create a benchmark entry.

**Request Body:**
```json
{
  "benchmark_name": "Test TAT Benchmark",
  "metric_name": "Test Turnaround Time",
  "category": "Performance",
  "is_internal": true,
  "benchmark_source": "Laboratory A",
  "benchmark_value": 2.5,
  "our_value": 3.2,
  "unit_of_measure": "days"
}
```

#### GET `/api/v1/analytics/benchmarks/compare`
Compare benchmarks.

**Parameters:**
- `metric_name`: Required - metric to compare
- `department` (optional): Specific department

### AI-Powered Insights Endpoints

#### GET `/api/v1/analytics/ai/anomalies`
Detect anomalies in KPI data.

**Parameters:**
- `kpi_id` (optional): Specific KPI to analyze

**Response:**
```json
{
  "anomalies": [
    {
      "id": 1,
      "metric_name": "Test Turnaround Time",
      "anomaly_type": "spike",
      "severity": "high",
      "actual_value": 8.5,
      "expected_value": 3.2,
      "detection_date": "2025-11-09T10:30:00"
    }
  ]
}
```

#### POST `/api/v1/analytics/ai/anomalies/{anomaly_id}/acknowledge`
Acknowledge an anomaly.

**Request Body:**
```json
{
  "notes": "Investigated - caused by equipment breakdown"
}
```

### Custom Reports Endpoints

#### POST `/api/v1/analytics/reports/custom`
Create a custom report definition.

**Request Body:**
```json
{
  "report_name": "Monthly Quality Report",
  "description": "Comprehensive quality metrics",
  "category": "Quality",
  "data_sources": ["non_conformances", "capas", "audits"],
  "filters": {"date_field": "created_at", "range": "last_30_days"},
  "chart_type": "bar"
}
```

#### GET `/api/v1/analytics/reports/custom`
List custom reports.

#### GET `/api/v1/analytics/reports/executive-dashboard`
Generate executive dashboard report.

**Response includes all key metrics across modules.**

#### GET `/api/v1/analytics/reports/quality-metrics`
Generate quality metrics report.

**Response:**
```json
{
  "period": {"start": "2025-08-01", "end": "2025-11-09"},
  "nonconformances": {
    "total": 23,
    "by_status": {"Open": 5, "Investigating": 3, "Closed": 15},
    "by_severity": {"Low": 10, "Medium": 8, "High": 4, "Critical": 1},
    "by_department": {"Laboratory": 12, "QA": 8, "Production": 3}
  },
  "capas": {
    "total": 18,
    "by_status": {"Open": 4, "In Progress": 6, "Verified": 8},
    "effectiveness_rate": 88.89
  },
  "audits": {
    "total": 6,
    "by_type": {"Internal": 4, "External": 2}
  }
}
```

### Enhanced NC & CAPA Analytics

#### GET `/api/v1/analytics/nc-analytics`
Get enhanced NC analytics with recurrence analysis.

**Response:**
```json
{
  "total_ncs": 23,
  "by_severity": {"Low": 10, "Medium": 8, "High": 4, "Critical": 1},
  "closed": 15,
  "open": 8,
  "closure_rate": 65.22,
  "recurring_processes": {
    "Sample Handling": 4,
    "Calibration": 3
  }
}
```

#### GET `/api/v1/analytics/capa-analytics`
Get CAPA effectiveness analytics.

**Response:**
```json
{
  "total_capas": 18,
  "verified": 8,
  "effective": 7,
  "effectiveness_rate": 87.5,
  "by_type": {"Corrective": 12, "Preventive": 6}
}
```

---

## Usage Examples

### Example 1: Creating and Tracking a KPI

```python
import requests

# 1. Create KPI Definition
kpi_data = {
    "kpi_code": "KPI-LAB-001",
    "name": "Sample Processing Time",
    "description": "Average time to process samples",
    "category": "Productivity",
    "target_value": 2.0,
    "unit_of_measure": "hours",
    "frequency": "Weekly",
    "is_higher_better": False
}

response = requests.post(
    "http://localhost:8000/api/v1/analytics/kpis/definitions",
    json=kpi_data,
    headers={"Authorization": f"Bearer {token}"}
)

kpi_id = response.json()["kpi_id"]

# 2. Record Measurements
measurement_data = {
    "kpi_definition_id": kpi_id,
    "measurement_date": "2025-11-01",
    "actual_value": 1.8,
    "target_value": 2.0,
    "notes": "Excellent performance this week"
}

requests.post(
    "http://localhost:8000/api/v1/analytics/kpis/measurements",
    json=measurement_data,
    headers={"Authorization": f"Bearer {token}"}
)

# 3. Get Trend Analysis
trend = requests.get(
    f"http://localhost:8000/api/v1/analytics/kpis/{kpi_id}/trend?months=6",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Trend: {trend.json()['trend']}")
```

### Example 2: Submitting a Kaizen Suggestion

```python
kaizen_data = {
    "title": "Implement LIMS Barcode Scanning",
    "description": "Use barcode scanners for sample tracking",
    "current_situation": "Manual entry of sample IDs takes 3-5 minutes",
    "proposed_improvement": "Barcode scanning reduces time to 10 seconds",
    "expected_benefits": "95% time reduction, zero transcription errors",
    "category": "Productivity",
    "area_department": "Sample Reception"
}

response = requests.post(
    "http://localhost:8000/api/v1/analytics/kaizen/suggestions",
    json=kaizen_data,
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Suggestion created: {response.json()['suggestion_number']}")
```

### Example 3: Performing 5 Why Analysis

```python
five_why_data = {
    "problem_statement": "Laboratory test results delayed",
    "why_1": "Why are results delayed?",
    "answer_1": "Samples are waiting in queue",
    "why_2": "Why are samples waiting?",
    "answer_2": "Only one technician trained on this test",
    "why_3": "Why only one technician trained?",
    "answer_3": "Training program not prioritized",
    "why_4": "Why not prioritized?",
    "answer_4": "No formal training schedule",
    "why_5": "Why no schedule?",
    "answer_5": "Training coordinator position vacant",
    "root_cause": "Lack of dedicated training resources"
}

requests.post(
    "http://localhost:8000/api/v1/analytics/improvement/5why",
    json=five_why_data,
    headers={"Authorization": f"Bearer {token}"}
)
```

### Example 4: Creating an FMEA

```python
fmea_data = {
    "title": "Sample Labeling FMEA",
    "fmea_type": "Process FMEA",
    "process_name": "Sample Registration",
    "failure_mode": "Incorrect sample labeling",
    "potential_effects": "Wrong test performed, potential patient harm",
    "severity": 9,  # Very high
    "potential_causes": "Manual transcription error",
    "occurrence": 4,  # Occasional
    "current_detection_controls": "Visual verification",
    "detection": 5  # Moderate detection
}

response = requests.post(
    "http://localhost:8000/api/v1/analytics/improvement/fmea",
    json=fmea_data,
    headers={"Authorization": f"Bearer {token}"}
)

# RPN = 9 * 4 * 5 = 180 (High risk!)
print(f"RPN: {response.json()['rpn']}")
```

### Example 5: Getting Executive Dashboard

```python
from datetime import date, timedelta

end_date = date.today()
start_date = end_date - timedelta(days=30)

dashboard = requests.get(
    f"http://localhost:8000/api/v1/analytics/reports/executive-dashboard",
    params={"start_date": start_date, "end_date": end_date},
    headers={"Authorization": f"Bearer {token}"}
)

data = dashboard.json()
print(f"Document Approval Time: {data['document_approval']['average_days']} days")
print(f"Task Completion Rate: {data['task_completion']['completion_rate']}%")
print(f"NC Closure Rate: {data['nonconformance']['closure_rate']}%")
```

---

## AI-Powered Insights

### Anomaly Detection

The system automatically detects anomalies using statistical methods:

- **Z-Score Analysis**: Identifies values that deviate significantly from the mean
- **Threshold**: Default sensitivity is 2.0 standard deviations
- **Severity Levels**:
  - **Medium**: Z-score > 2.0
  - **High**: Z-score > 2.5
  - **Critical**: Z-score > 3.0

### Predictive Analytics

- **Linear Regression Forecasting**: Simple trend-based predictions
- **Trend Detection**: Automatically identifies Up, Down, or Stable trends
- **Confidence Intervals**: (Planned) Will provide prediction confidence ranges

---

## Performance Optimization

### Caching Strategy

- **Analytics Cache Table**: Pre-calculated metrics stored with expiration
- **Redis Integration**: Fast in-memory caching for frequently accessed data
- **Cache Keys**: Unique identifiers based on query parameters

### Recommended Caching:
- Dashboard KPIs: Cache for 1 hour
- Trend Analysis: Cache for 6 hours
- Historical Reports: Cache for 24 hours

---

## Integration Points

The Analytics System integrates with all LIMS-QMS modules:

- **Documents**: Approval time tracking
- **Tasks**: Completion rate monitoring
- **Projects**: Cycle time analysis
- **Quality**: NC/CAPA analytics
- **Equipment**: Utilization tracking
- **Financial**: Revenue/expense trends
- **CRM**: Customer satisfaction metrics
- **Audit**: Compliance tracking

---

## Future Enhancements

1. **Advanced ML Models**
   - ARIMA time series forecasting
   - Neural network predictions
   - Clustering for pattern detection

2. **Natural Language Queries**
   - "Show me top 5 bottlenecks this month"
   - "What caused the spike in NCs last week?"

3. **Interactive Dashboards**
   - Real-time WebSocket updates
   - Drag-and-drop widget customization

4. **Mobile App**
   - KPI tracking on mobile devices
   - Push notifications for anomalies

5. **Export Enhancements**
   - PowerPoint report generation
   - Automated email distribution
   - Scheduled report execution

---

## Support

For questions or issues:
- **Documentation**: `/docs/ANALYTICS_SYSTEM.md`
- **API Documentation**: `http://localhost:8000/docs`
- **GitHub Issues**: Create an issue in the repository

---

**Version**: 1.0.0
**Last Updated**: November 2025
**Authors**: LIMS-QMS Development Team
