"""
Analytics, KPI, and Continual Improvement models
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, DateTime, Enum, JSON, Boolean, Float, Numeric
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class KPIFrequencyEnum(str, enum.Enum):
    """KPI measurement frequency"""
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    ANNUALLY = "Annually"


class KPITrendEnum(str, enum.Enum):
    """KPI trend direction"""
    UP = "Up"
    DOWN = "Down"
    STABLE = "Stable"


class ReportFormatEnum(str, enum.Enum):
    """Report export format"""
    PDF = "PDF"
    EXCEL = "Excel"
    POWERPOINT = "PowerPoint"
    CSV = "CSV"
    JSON = "JSON"


class ImprovementStatusEnum(str, enum.Enum):
    """Improvement initiative status"""
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    IN_PROGRESS = "In Progress"
    IMPLEMENTED = "Implemented"
    VERIFIED = "Verified"
    CLOSED = "Closed"
    REJECTED = "Rejected"


class PDCAPhaseEnum(str, enum.Enum):
    """PDCA cycle phases"""
    PLAN = "Plan"
    DO = "Do"
    CHECK = "Check"
    ACT = "Act"


class ProblemSolvingMethodEnum(str, enum.Enum):
    """Problem solving methodologies"""
    FIVE_WHY = "5 Why"
    FISHBONE = "Fishbone/Ishikawa"
    EIGHT_D = "8D"
    PDCA = "PDCA"
    DMAIC = "DMAIC"
    A3 = "A3"
    FMEA = "FMEA"


class KPIDefinition(BaseModel):
    """KPI Definition model - defines what KPIs to track"""
    __tablename__ = 'kpi_definitions'

    kpi_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # Quality, Productivity, Financial, Customer Satisfaction

    # Calculation
    calculation_method = Column(Text, nullable=True)  # Formula or description
    data_source = Column(String(200), nullable=True)  # Which table/module to pull data from
    aggregation_function = Column(String(50), nullable=True)  # SUM, AVG, COUNT, RATIO

    # Target and thresholds
    target_value = Column(Numeric(15, 2), nullable=True)
    unit_of_measure = Column(String(50), nullable=True)  # %, hours, days, count
    lower_threshold = Column(Numeric(15, 2), nullable=True)  # Red zone
    upper_threshold = Column(Numeric(15, 2), nullable=True)  # Green zone

    # Tracking
    frequency = Column(Enum(KPIFrequencyEnum), default=KPIFrequencyEnum.MONTHLY)
    is_higher_better = Column(Boolean, default=True)  # True if higher values are better

    # Ownership
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    department = Column(String(100), nullable=True)

    # Display settings
    display_order = Column(Integer, default=0)
    show_on_dashboard = Column(Boolean, default=True)
    chart_type = Column(String(50), nullable=True)  # line, bar, gauge, pie

    # Relationships
    measurements = relationship('KPIMeasurement', back_populates='kpi_definition')


class KPIMeasurement(BaseModel):
    """KPI Measurement model - actual KPI values over time"""
    __tablename__ = 'kpi_measurements'

    kpi_definition_id = Column(Integer, ForeignKey('kpi_definitions.id'), nullable=False)
    measurement_date = Column(Date, nullable=False)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)

    # Values
    actual_value = Column(Numeric(15, 2), nullable=False)
    target_value = Column(Numeric(15, 2), nullable=True)
    previous_value = Column(Numeric(15, 2), nullable=True)

    # Analysis
    variance = Column(Numeric(15, 2), nullable=True)  # actual - target
    variance_percentage = Column(Numeric(15, 2), nullable=True)
    trend = Column(Enum(KPITrendEnum), nullable=True)

    # Status
    meets_target = Column(Boolean, nullable=True)
    color_status = Column(String(20), nullable=True)  # red, yellow, green

    # Context
    notes = Column(Text, nullable=True)
    measured_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Relationships
    kpi_definition = relationship('KPIDefinition', back_populates='measurements')


class QualityObjective(BaseModel):
    """Quality Objectives tracking"""
    __tablename__ = 'quality_objectives'

    objective_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)

    # Scope
    category = Column(String(100), nullable=True)  # Customer Satisfaction, Process Improvement, Compliance
    department = Column(String(100), nullable=True)
    is_organizational = Column(Boolean, default=False)  # Organization-wide vs department-specific

    # Measurement
    measurable_target = Column(Text, nullable=False)
    success_criteria = Column(Text, nullable=True)
    kpi_definition_ids = Column(JSON, nullable=True)  # Linked KPIs

    # Timeline
    start_date = Column(Date, nullable=True)
    target_date = Column(Date, nullable=True)
    review_frequency = Column(String(50), nullable=True)  # Quarterly, Annual

    # Progress
    current_achievement_percentage = Column(Numeric(5, 2), nullable=True)
    status = Column(String(50), default='active')  # active, achieved, not_achieved, cancelled

    # Ownership
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Review
    last_review_date = Column(Date, nullable=True)
    next_review_date = Column(Date, nullable=True)
    review_notes = Column(Text, nullable=True)

    # Gap analysis
    gap_analysis = Column(Text, nullable=True)
    action_plan = Column(Text, nullable=True)


class KaizenSuggestion(BaseModel):
    """Kaizen (Continuous Improvement) Suggestions"""
    __tablename__ = 'kaizen_suggestions'

    suggestion_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)

    # Problem & Solution
    current_situation = Column(Text, nullable=True)
    proposed_improvement = Column(Text, nullable=False)
    expected_benefits = Column(Text, nullable=True)

    # Category
    category = Column(String(100), nullable=True)  # Cost Reduction, Quality, Safety, Productivity
    area_department = Column(String(100), nullable=True)
    process_affected = Column(String(200), nullable=True)

    # Submission
    submitted_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    submission_date = Column(Date, nullable=False)

    # Review
    status = Column(Enum(ImprovementStatusEnum), default=ImprovementStatusEnum.SUBMITTED)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    review_date = Column(Date, nullable=True)
    review_notes = Column(Text, nullable=True)

    # Implementation
    implementation_plan = Column(Text, nullable=True)
    assigned_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    estimated_cost = Column(Numeric(15, 2), nullable=True)
    estimated_savings = Column(Numeric(15, 2), nullable=True)
    implementation_date = Column(Date, nullable=True)

    # Verification
    actual_cost = Column(Numeric(15, 2), nullable=True)
    actual_savings = Column(Numeric(15, 2), nullable=True)
    roi_percentage = Column(Numeric(15, 2), nullable=True)
    before_metrics = Column(JSON, nullable=True)
    after_metrics = Column(JSON, nullable=True)

    # Recognition
    reward_points = Column(Integer, nullable=True)
    reward_notes = Column(Text, nullable=True)

    # Attachments
    attachments = Column(JSON, nullable=True)


class ImprovementInitiative(BaseModel):
    """Major Improvement Initiatives (PDCA, 8D, etc.)"""
    __tablename__ = 'improvement_initiatives'

    initiative_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    methodology = Column(Enum(ProblemSolvingMethodEnum), nullable=False)

    # Source
    source_type = Column(String(100), nullable=True)  # NC, Audit, Kaizen, Management Review
    related_nc_id = Column(Integer, ForeignKey('non_conformances.id'), nullable=True)
    related_audit_id = Column(Integer, ForeignKey('audits.id'), nullable=True)

    # Problem definition
    problem_statement = Column(Text, nullable=False)
    impact = Column(Text, nullable=True)
    urgency = Column(String(50), nullable=True)  # Low, Medium, High, Critical

    # Team
    team_leader_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    team_members = Column(JSON, nullable=True)  # List of user IDs

    # Status
    status = Column(Enum(ImprovementStatusEnum), default=ImprovementStatusEnum.IN_PROGRESS)
    current_phase = Column(String(100), nullable=True)

    # Timeline
    start_date = Column(Date, nullable=True)
    target_completion_date = Column(Date, nullable=True)
    actual_completion_date = Column(Date, nullable=True)

    # Financial impact
    estimated_cost = Column(Numeric(15, 2), nullable=True)
    actual_cost = Column(Numeric(15, 2), nullable=True)
    estimated_benefit = Column(Numeric(15, 2), nullable=True)
    actual_benefit = Column(Numeric(15, 2), nullable=True)
    roi_percentage = Column(Numeric(15, 2), nullable=True)


class PDCARecord(BaseModel):
    """PDCA (Plan-Do-Check-Act) cycle tracking"""
    __tablename__ = 'pdca_records'

    initiative_id = Column(Integer, ForeignKey('improvement_initiatives.id'), nullable=False)
    cycle_number = Column(Integer, default=1)  # Support multiple PDCA cycles

    # Plan phase
    plan_objective = Column(Text, nullable=True)
    plan_actions = Column(JSON, nullable=True)  # List of planned actions
    plan_resources = Column(Text, nullable=True)
    plan_timeline = Column(Text, nullable=True)
    plan_completed_date = Column(Date, nullable=True)

    # Do phase
    do_implementation_notes = Column(Text, nullable=True)
    do_challenges_encountered = Column(Text, nullable=True)
    do_completed_date = Column(Date, nullable=True)

    # Check phase
    check_results = Column(Text, nullable=True)
    check_data_analysis = Column(JSON, nullable=True)
    check_success_criteria_met = Column(Boolean, nullable=True)
    check_lessons_learned = Column(Text, nullable=True)
    check_completed_date = Column(Date, nullable=True)

    # Act phase
    act_standardize = Column(Text, nullable=True)
    act_next_steps = Column(Text, nullable=True)
    act_start_new_cycle = Column(Boolean, default=False)
    act_completed_date = Column(Date, nullable=True)

    current_phase = Column(Enum(PDCAPhaseEnum), default=PDCAPhaseEnum.PLAN)


class EightDReport(BaseModel):
    """8D Problem Solving Methodology"""
    __tablename__ = 'eight_d_reports'

    initiative_id = Column(Integer, ForeignKey('improvement_initiatives.id'), nullable=False)

    # D0: Prepare
    d0_symptom_description = Column(Text, nullable=True)
    d0_emergency_actions = Column(Text, nullable=True)
    d0_completed = Column(Boolean, default=False)

    # D1: Team
    d1_team_members = Column(JSON, nullable=True)
    d1_team_leader_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    d1_completed = Column(Boolean, default=False)

    # D2: Problem Description
    d2_problem_description = Column(Text, nullable=True)
    d2_is_is_not_analysis = Column(JSON, nullable=True)
    d2_completed = Column(Boolean, default=False)

    # D3: Interim Containment Actions
    d3_containment_actions = Column(Text, nullable=True)
    d3_verification = Column(Text, nullable=True)
    d3_completed = Column(Boolean, default=False)

    # D4: Root Cause Analysis
    d4_root_cause = Column(Text, nullable=True)
    d4_analysis_method = Column(String(100), nullable=True)  # 5 Why, Fishbone
    d4_verification = Column(Text, nullable=True)
    d4_completed = Column(Boolean, default=False)

    # D5: Permanent Corrective Actions
    d5_corrective_actions = Column(Text, nullable=True)
    d5_verification_plan = Column(Text, nullable=True)
    d5_completed = Column(Boolean, default=False)

    # D6: Implement and Validate
    d6_implementation_details = Column(Text, nullable=True)
    d6_validation_results = Column(Text, nullable=True)
    d6_completed = Column(Boolean, default=False)

    # D7: Prevent Recurrence
    d7_preventive_actions = Column(Text, nullable=True)
    d7_system_changes = Column(Text, nullable=True)
    d7_completed = Column(Boolean, default=False)

    # D8: Congratulate Team
    d8_recognition = Column(Text, nullable=True)
    d8_lessons_learned = Column(Text, nullable=True)
    d8_completed = Column(Boolean, default=False)

    overall_completion_percentage = Column(Numeric(5, 2), nullable=True)


class FiveWhyAnalysis(BaseModel):
    """5 Why Root Cause Analysis"""
    __tablename__ = 'five_why_analysis'

    initiative_id = Column(Integer, ForeignKey('improvement_initiatives.id'), nullable=True)
    related_nc_id = Column(Integer, ForeignKey('non_conformances.id'), nullable=True)
    related_capa_id = Column(Integer, ForeignKey('capas.id'), nullable=True)

    problem_statement = Column(Text, nullable=False)

    # The 5 Whys
    why_1 = Column(Text, nullable=True)
    answer_1 = Column(Text, nullable=True)

    why_2 = Column(Text, nullable=True)
    answer_2 = Column(Text, nullable=True)

    why_3 = Column(Text, nullable=True)
    answer_3 = Column(Text, nullable=True)

    why_4 = Column(Text, nullable=True)
    answer_4 = Column(Text, nullable=True)

    why_5 = Column(Text, nullable=True)
    answer_5 = Column(Text, nullable=True)

    # Can go deeper if needed
    additional_whys = Column(JSON, nullable=True)

    # Root cause conclusion
    root_cause = Column(Text, nullable=True)
    corrective_actions = Column(Text, nullable=True)

    conducted_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    conducted_date = Column(Date, nullable=True)


class FishboneDiagram(BaseModel):
    """Fishbone/Ishikawa Diagram for root cause analysis"""
    __tablename__ = 'fishbone_diagrams'

    initiative_id = Column(Integer, ForeignKey('improvement_initiatives.id'), nullable=True)
    related_nc_id = Column(Integer, ForeignKey('non_conformances.id'), nullable=True)

    problem_statement = Column(Text, nullable=False)

    # 6M Categories
    man_causes = Column(JSON, nullable=True)  # People-related causes
    method_causes = Column(JSON, nullable=True)  # Process/procedure causes
    machine_causes = Column(JSON, nullable=True)  # Equipment causes
    material_causes = Column(JSON, nullable=True)  # Material/supply causes
    measurement_causes = Column(JSON, nullable=True)  # Measurement/inspection causes
    environment_causes = Column(JSON, nullable=True)  # Environmental causes

    # Additional custom categories
    custom_categories = Column(JSON, nullable=True)

    # Root cause conclusion
    identified_root_causes = Column(JSON, nullable=True)
    priority_root_cause = Column(Text, nullable=True)

    conducted_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    conducted_date = Column(Date, nullable=True)


class FMEARecord(BaseModel):
    """FMEA (Failure Mode and Effects Analysis)"""
    __tablename__ = 'fmea_records'

    fmea_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    fmea_type = Column(String(50), nullable=True)  # Process FMEA, Design FMEA, System FMEA

    # Scope
    process_name = Column(String(200), nullable=True)
    process_step = Column(String(200), nullable=True)
    product_name = Column(String(200), nullable=True)

    # Failure mode
    failure_mode = Column(Text, nullable=False)
    potential_effects = Column(Text, nullable=True)
    severity = Column(Integer, nullable=True)  # 1-10 scale

    # Causes
    potential_causes = Column(Text, nullable=True)
    occurrence = Column(Integer, nullable=True)  # 1-10 scale

    # Current controls
    current_detection_controls = Column(Text, nullable=True)
    detection = Column(Integer, nullable=True)  # 1-10 scale

    # Risk Priority Number
    rpn = Column(Integer, nullable=True)  # severity * occurrence * detection

    # Actions
    recommended_actions = Column(Text, nullable=True)
    responsibility = Column(Integer, ForeignKey('users.id'), nullable=True)
    target_completion_date = Column(Date, nullable=True)

    # After actions
    actions_taken = Column(Text, nullable=True)
    revised_severity = Column(Integer, nullable=True)
    revised_occurrence = Column(Integer, nullable=True)
    revised_detection = Column(Integer, nullable=True)
    revised_rpn = Column(Integer, nullable=True)

    status = Column(String(50), default='open')  # open, in_progress, completed


class BenchmarkData(BaseModel):
    """Benchmarking data (internal and external)"""
    __tablename__ = 'benchmark_data'

    benchmark_name = Column(String(200), nullable=False)
    metric_name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True)

    # Benchmark type
    is_internal = Column(Boolean, default=True)
    benchmark_source = Column(String(200), nullable=True)  # Department name or industry source

    # Value
    benchmark_value = Column(Numeric(15, 2), nullable=False)
    unit_of_measure = Column(String(50), nullable=True)

    # Our performance
    our_value = Column(Numeric(15, 2), nullable=True)
    gap = Column(Numeric(15, 2), nullable=True)
    gap_percentage = Column(Numeric(15, 2), nullable=True)

    # Period
    measurement_date = Column(Date, nullable=False)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)

    # Best practice
    best_practice_description = Column(Text, nullable=True)
    action_plan = Column(Text, nullable=True)

    notes = Column(Text, nullable=True)


class CustomReport(BaseModel):
    """Custom Report Definitions"""
    __tablename__ = 'custom_reports'

    report_code = Column(String(100), unique=True, nullable=False, index=True)
    report_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)

    # Report definition
    data_sources = Column(JSON, nullable=False)  # Tables/entities to query
    filters = Column(JSON, nullable=True)  # Filter conditions
    grouping = Column(JSON, nullable=True)  # Group by fields
    aggregations = Column(JSON, nullable=True)  # SUM, AVG, COUNT definitions
    sorting = Column(JSON, nullable=True)

    # Visualization
    chart_type = Column(String(50), nullable=True)  # line, bar, pie, table
    chart_config = Column(JSON, nullable=True)  # Chart-specific configuration

    # Scheduling
    is_scheduled = Column(Boolean, default=False)
    schedule_frequency = Column(String(50), nullable=True)  # Daily, Weekly, Monthly
    schedule_day = Column(Integer, nullable=True)
    schedule_time = Column(String(10), nullable=True)

    # Distribution
    recipients = Column(JSON, nullable=True)  # Email addresses or user IDs
    export_format = Column(Enum(ReportFormatEnum), default=ReportFormatEnum.PDF)

    # Owner
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    is_public = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)


class ReportExecution(BaseModel):
    """Report Execution History"""
    __tablename__ = 'report_executions'

    report_id = Column(Integer, ForeignKey('custom_reports.id'), nullable=False)
    execution_date = Column(DateTime, nullable=False)
    executed_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Parameters
    parameters = Column(JSON, nullable=True)  # Date ranges, filters applied

    # Output
    export_format = Column(Enum(ReportFormatEnum), nullable=False)
    file_path = Column(String(500), nullable=True)
    file_size_kb = Column(Integer, nullable=True)

    # Status
    status = Column(String(50), default='completed')  # running, completed, failed
    error_message = Column(Text, nullable=True)
    execution_time_seconds = Column(Numeric(10, 2), nullable=True)

    # Distribution
    emailed_to = Column(JSON, nullable=True)
    email_sent = Column(Boolean, default=False)


class AnalyticsCache(BaseModel):
    """Cache for pre-calculated analytics"""
    __tablename__ = 'analytics_cache'

    cache_key = Column(String(200), unique=True, nullable=False, index=True)
    cache_type = Column(String(100), nullable=False)  # kpi_dashboard, trend_analysis, etc.

    # Cached data
    cached_data = Column(JSON, nullable=False)

    # Metadata
    department = Column(String(100), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Cache management
    expires_at = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0)


class AnomalyDetection(BaseModel):
    """AI-detected anomalies in data"""
    __tablename__ = 'anomaly_detections'

    detection_date = Column(DateTime, nullable=False)
    metric_name = Column(String(200), nullable=False)
    data_source = Column(String(200), nullable=False)

    # Anomaly details
    anomaly_type = Column(String(100), nullable=True)  # spike, drop, trend_break, outlier
    severity = Column(String(50), nullable=True)  # low, medium, high, critical

    # Values
    expected_value = Column(Numeric(15, 2), nullable=True)
    actual_value = Column(Numeric(15, 2), nullable=False)
    deviation_percentage = Column(Numeric(15, 2), nullable=True)

    # Context
    description = Column(Text, nullable=True)
    possible_causes = Column(JSON, nullable=True)
    recommended_actions = Column(JSON, nullable=True)

    # Status
    acknowledged = Column(Boolean, default=False)
    acknowledged_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)

    investigation_notes = Column(Text, nullable=True)
    resolution = Column(Text, nullable=True)
