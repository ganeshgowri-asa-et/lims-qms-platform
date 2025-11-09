-- LIMS-QMS Platform Complete Database Schema
-- AI-Powered Laboratory Information Management System & Quality Management System
-- For Solar PV Testing & R&D Laboratories (ISO 17025/9001 Compliance)

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- SESSION 2: Document Management System
-- ============================================================================

CREATE TABLE qms_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_number VARCHAR(50) UNIQUE NOT NULL, -- QSF-YYYY-XXX format
    title VARCHAR(255) NOT NULL,
    doc_type VARCHAR(50) NOT NULL, -- Procedure, Form, Work Instruction, Policy, etc.
    category VARCHAR(100),
    revision VARCHAR(20) NOT NULL DEFAULT '1.0',
    owner_id UUID,
    department VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'Draft', -- Draft, Under Review, Approved, Obsolete
    effective_date DATE,
    review_date DATE,
    next_review_date DATE,
    file_path TEXT,
    file_hash VARCHAR(64),
    tags TEXT[], -- AI auto-tags
    classification VARCHAR(50), -- AI document classification
    is_controlled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    approved_by UUID
);

CREATE TABLE document_revisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES qms_documents(id) ON DELETE CASCADE,
    revision VARCHAR(20) NOT NULL,
    change_description TEXT,
    revised_by UUID,
    revised_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path TEXT,
    previous_revision VARCHAR(20)
);

CREATE TABLE document_distribution (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES qms_documents(id) ON DELETE CASCADE,
    copy_number VARCHAR(20),
    distributed_to VARCHAR(255),
    department VARCHAR(100),
    distributed_date DATE,
    acknowledgment_status VARCHAR(50) DEFAULT 'Pending',
    acknowledged_at TIMESTAMP
);

CREATE TABLE document_approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES qms_documents(id) ON DELETE CASCADE,
    revision VARCHAR(20),
    approver_role VARCHAR(50), -- Doer, Checker, Approver
    approver_id UUID,
    status VARCHAR(50) DEFAULT 'Pending', -- Pending, Approved, Rejected
    comments TEXT,
    digital_signature TEXT,
    approved_at TIMESTAMP
);

-- ============================================================================
-- SESSION 3: Equipment Calibration & Maintenance
-- ============================================================================

CREATE TABLE equipment_master (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    equipment_id VARCHAR(50) UNIQUE NOT NULL, -- EQP-YYYY-XXX format
    equipment_name VARCHAR(255) NOT NULL,
    category VARCHAR(100), -- Measurement, Testing, Environmental Chamber, etc.
    manufacturer VARCHAR(255),
    model_number VARCHAR(100),
    serial_number VARCHAR(100),
    location VARCHAR(255),
    department VARCHAR(100),
    purchase_date DATE,
    installation_date DATE,
    warranty_expiry DATE,
    calibration_frequency_days INTEGER DEFAULT 365,
    last_calibration_date DATE,
    next_calibration_date DATE,
    calibration_status VARCHAR(50) DEFAULT 'Valid', -- Valid, Due, Overdue, Not Required
    maintenance_frequency_days INTEGER DEFAULT 180,
    last_maintenance_date DATE,
    next_maintenance_date DATE,
    status VARCHAR(50) DEFAULT 'Active', -- Active, Under Maintenance, Calibration Due, Decommissioned
    qr_code_path TEXT,
    oee_target DECIMAL(5,2) DEFAULT 85.00, -- Overall Equipment Effectiveness target
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    failure_risk_score DECIMAL(5,2), -- AI predicted failure risk (0-100)
    predicted_failure_date DATE -- AI predicted next failure
);

CREATE TABLE calibration_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    equipment_id UUID REFERENCES equipment_master(id) ON DELETE CASCADE,
    calibration_date DATE NOT NULL,
    next_calibration_date DATE NOT NULL,
    calibrated_by VARCHAR(255),
    calibration_agency VARCHAR(255),
    certificate_number VARCHAR(100),
    certificate_path TEXT,
    calibration_standard VARCHAR(255),
    traceability VARCHAR(255), -- NABL, NIST, etc.
    result VARCHAR(50), -- Pass, Fail, Conditional
    deviation_recorded TEXT,
    corrective_action TEXT,
    cost DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'Completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE preventive_maintenance_schedule (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    equipment_id UUID REFERENCES equipment_master(id) ON DELETE CASCADE,
    maintenance_type VARCHAR(100), -- Preventive, Corrective, Breakdown
    scheduled_date DATE NOT NULL,
    completed_date DATE,
    performed_by VARCHAR(255),
    duration_hours DECIMAL(5,2),
    description TEXT,
    checklist_items JSONB, -- Dynamic checklist
    parts_replaced TEXT,
    cost DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'Scheduled', -- Scheduled, In Progress, Completed, Cancelled
    downtime_hours DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE equipment_usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    equipment_id UUID REFERENCES equipment_master(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    planned_hours DECIMAL(5,2) DEFAULT 8.0,
    operating_hours DECIMAL(5,2),
    downtime_hours DECIMAL(5,2) DEFAULT 0,
    downtime_reason TEXT,
    quality_output_hours DECIMAL(5,2), -- Hours producing quality output
    availability DECIMAL(5,2), -- (Operating Hours / Planned Hours) * 100
    performance DECIMAL(5,2), -- Actual vs Ideal performance
    quality DECIMAL(5,2), -- Good output / Total output
    oee DECIMAL(5,2), -- Availability * Performance * Quality
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SESSION 4: Training & Competency Management
-- ============================================================================

CREATE TABLE training_master (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    training_code VARCHAR(50) UNIQUE NOT NULL,
    training_name VARCHAR(255) NOT NULL,
    training_type VARCHAR(100), -- Technical, Quality, Safety, Soft Skills
    category VARCHAR(100),
    description TEXT,
    duration_hours DECIMAL(5,2),
    validity_months INTEGER, -- NULL for one-time trainings
    trainer_name VARCHAR(255),
    competency_criteria TEXT,
    evaluation_method VARCHAR(100), -- Written Test, Practical, Both
    pass_percentage DECIMAL(5,2) DEFAULT 70.0,
    is_mandatory BOOLEAN DEFAULT false,
    applicable_roles TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employee_training_matrix (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL,
    employee_name VARCHAR(255) NOT NULL,
    employee_code VARCHAR(50),
    department VARCHAR(100),
    designation VARCHAR(100),
    training_id UUID REFERENCES training_master(id) ON DELETE CASCADE,
    required BOOLEAN DEFAULT false,
    completed BOOLEAN DEFAULT false,
    completion_date DATE,
    expiry_date DATE,
    score DECIMAL(5,2),
    competency_status VARCHAR(50), -- Competent, Not Competent, Expired, Pending
    certificate_number VARCHAR(100),
    certificate_path TEXT,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE training_attendance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    training_id UUID REFERENCES training_master(id) ON DELETE CASCADE,
    training_date DATE NOT NULL,
    venue VARCHAR(255),
    trainer_name VARCHAR(255),
    attendees JSONB, -- Array of {employee_id, name, signature, score}
    duration_hours DECIMAL(5,2),
    topics_covered TEXT,
    materials_used TEXT,
    assessment_conducted BOOLEAN DEFAULT false,
    effectiveness_rating DECIMAL(3,2), -- 1-5 scale
    feedback TEXT,
    form_reference VARCHAR(50), -- QSF0203, QSF0205, QSF0206
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SESSION 5: LIMS Core - Test Request & Sample Management
-- ============================================================================

CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_code VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_type VARCHAR(50), -- Corporate, Individual, Government
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    pincode VARCHAR(20),
    gst_number VARCHAR(50),
    pan_number VARCHAR(50),
    credit_limit DECIMAL(12,2),
    payment_terms VARCHAR(100),
    status VARCHAR(50) DEFAULT 'Active',
    portal_access BOOLEAN DEFAULT false, -- Customer portal access
    portal_username VARCHAR(100),
    portal_password_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trq_number VARCHAR(50) UNIQUE NOT NULL, -- TRQ-YYYY-XXXX format
    customer_id UUID REFERENCES customers(id),
    request_date DATE NOT NULL DEFAULT CURRENT_DATE,
    customer_po_number VARCHAR(100),
    customer_po_date DATE,
    project_name VARCHAR(255),
    product_type VARCHAR(100), -- Solar Module, Junction Box, Cable, etc.
    test_standard VARCHAR(100), -- IEC 61215, IEC 61730, IEC 61701, etc.
    urgency VARCHAR(50) DEFAULT 'Normal', -- Normal, Urgent, Rush
    expected_completion_date DATE,
    estimated_duration_days INTEGER, -- AI predicted duration
    quotation_number VARCHAR(50),
    quotation_amount DECIMAL(12,2),
    quotation_status VARCHAR(50), -- Draft, Sent, Approved, Rejected
    status VARCHAR(50) DEFAULT 'New', -- New, Quotation Sent, Approved, In Progress, Completed, Cancelled
    assigned_to UUID,
    sample_count INTEGER DEFAULT 0,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID
);

CREATE TABLE samples (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sample_id VARCHAR(50) UNIQUE NOT NULL, -- Auto-generated barcode
    trq_id UUID REFERENCES test_requests(id) ON DELETE CASCADE,
    sample_number INTEGER, -- Sequential number within TRQ
    sample_description TEXT,
    manufacturer VARCHAR(255),
    model_number VARCHAR(100),
    serial_number VARCHAR(100),
    batch_number VARCHAR(100),
    received_date DATE DEFAULT CURRENT_DATE,
    received_condition VARCHAR(100), -- Good, Damaged, Incomplete
    quantity INTEGER DEFAULT 1,
    storage_location VARCHAR(100),
    sample_status VARCHAR(50) DEFAULT 'Received', -- Received, In Testing, Testing Complete, Dispatched
    barcode_path TEXT,
    qr_code_path TEXT,
    disposal_date DATE,
    disposal_method VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test_parameters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trq_id UUID REFERENCES test_requests(id) ON DELETE CASCADE,
    sample_id UUID REFERENCES samples(id),
    test_name VARCHAR(255) NOT NULL,
    test_code VARCHAR(50),
    test_standard VARCHAR(100),
    parameter_name VARCHAR(255),
    specification TEXT,
    method VARCHAR(255),
    equipment_required TEXT[],
    estimated_duration_hours DECIMAL(5,2),
    assigned_to UUID,
    scheduled_date DATE,
    start_date TIMESTAMP,
    completion_date TIMESTAMP,
    result_value TEXT,
    result_status VARCHAR(50), -- Pass, Fail, Conditional, In Progress, Pending
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SESSION 6: IEC Test Report Generation
-- ============================================================================

CREATE TABLE test_standards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    standard_code VARCHAR(50) UNIQUE NOT NULL, -- IEC 61215, IEC 61730, IEC 61701
    standard_name VARCHAR(255) NOT NULL,
    version VARCHAR(50),
    category VARCHAR(100),
    description TEXT,
    active BOOLEAN DEFAULT true
);

CREATE TABLE test_procedures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    standard_id UUID REFERENCES test_standards(id),
    procedure_code VARCHAR(50) UNIQUE NOT NULL,
    procedure_name VARCHAR(255) NOT NULL,
    test_sequence INTEGER,
    description TEXT,
    test_conditions JSONB, -- Temperature, humidity, etc.
    acceptance_criteria TEXT,
    equipment_required TEXT[],
    estimated_duration_hours DECIMAL(5,2),
    document_reference VARCHAR(100) -- QSF reference
);

CREATE TABLE test_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_number VARCHAR(50) UNIQUE NOT NULL,
    trq_id UUID REFERENCES test_requests(id),
    sample_id UUID REFERENCES samples(id),
    procedure_id UUID REFERENCES test_procedures(id),
    test_date DATE NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    operator_id UUID,
    equipment_used JSONB, -- [{equipment_id, equipment_name, cal_status}]
    environmental_conditions JSONB, -- {temperature, humidity, pressure}
    test_data JSONB, -- Raw test data (measurements, readings)
    graphs_generated TEXT[], -- Paths to generated graphs
    result VARCHAR(50), -- Pass, Fail, Conditional
    observations TEXT,
    deviations TEXT,
    reviewed_by UUID,
    reviewed_at TIMESTAMP,
    approved_by UUID,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_number VARCHAR(50) UNIQUE NOT NULL, -- RPT-YYYY-XXXX format
    trq_id UUID REFERENCES test_requests(id),
    sample_id UUID REFERENCES samples(id),
    report_type VARCHAR(100), -- IEC 61215, IEC 61730, IEC 61701
    report_date DATE NOT NULL DEFAULT CURRENT_DATE,
    test_period_start DATE,
    test_period_end DATE,
    overall_result VARCHAR(50), -- Pass, Fail, Conditional
    executive_summary TEXT,
    report_content JSONB, -- Structured report data
    graphs_included TEXT[], -- Paths to graphs
    certificate_number VARCHAR(100),
    certificate_path TEXT,
    qr_code_path TEXT, -- Digital certificate verification
    prepared_by UUID,
    reviewed_by UUID,
    approved_by UUID,
    issued_date DATE,
    validity_date DATE,
    status VARCHAR(50) DEFAULT 'Draft', -- Draft, Under Review, Approved, Issued
    pdf_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SESSION 7: Non-Conformance & CAPA Management
-- ============================================================================

CREATE TABLE nonconformances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nc_number VARCHAR(50) UNIQUE NOT NULL, -- NC-YYYY-XXX format
    nc_date DATE NOT NULL DEFAULT CURRENT_DATE,
    source VARCHAR(100), -- Internal Audit, Customer Complaint, Process Monitoring, Calibration
    nc_type VARCHAR(100), -- Product, Process, System, Documentation
    severity VARCHAR(50), -- Critical, Major, Minor
    department VARCHAR(100),
    process_area VARCHAR(255),
    related_document VARCHAR(100), -- TRQ, Equipment ID, Document Number
    description TEXT NOT NULL,
    immediate_action TEXT,
    containment_action TEXT,
    reported_by UUID,
    assigned_to UUID,
    target_closure_date DATE,
    actual_closure_date DATE,
    status VARCHAR(50) DEFAULT 'Open', -- Open, Under Investigation, CAPA Initiated, Closed, Cancelled
    root_cause_analysis_id UUID,
    ai_suggested_root_causes TEXT[], -- AI suggestions based on historical data
    effectiveness_verified BOOLEAN DEFAULT false,
    verification_date DATE,
    verified_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE root_cause_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nc_id UUID REFERENCES nonconformances(id) ON DELETE CASCADE,
    analysis_method VARCHAR(100), -- 5-Why, Fishbone, Fault Tree
    analysis_date DATE NOT NULL,
    team_members TEXT[],
    problem_statement TEXT,
    five_why_analysis JSONB, -- {why1, why2, why3, why4, why5, root_cause}
    fishbone_analysis JSONB, -- {man, machine, method, material, measurement, environment}
    root_cause_identified TEXT,
    contributing_factors TEXT[],
    analyzed_by UUID,
    reviewed_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE capa_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    capa_number VARCHAR(50) UNIQUE NOT NULL, -- CAPA-YYYY-XXX format
    nc_id UUID REFERENCES nonconformances(id),
    rca_id UUID REFERENCES root_cause_analysis(id),
    action_type VARCHAR(50), -- Corrective, Preventive
    action_description TEXT NOT NULL,
    responsible_person UUID,
    target_date DATE NOT NULL,
    completion_date DATE,
    status VARCHAR(50) DEFAULT 'Planned', -- Planned, In Progress, Completed, Verified
    verification_method TEXT,
    verification_date DATE,
    verified_by UUID,
    effectiveness_check_date DATE,
    effectiveness_rating VARCHAR(50), -- Effective, Partially Effective, Not Effective
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SESSION 8: Audit & Risk Management
-- ============================================================================

CREATE TABLE audit_program (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_year INTEGER NOT NULL,
    program_name VARCHAR(255) NOT NULL, -- e.g., "Annual Internal Audit Program 2024"
    scope TEXT, -- ISO 17025, ISO 9001, specific processes
    objectives TEXT[],
    audit_criteria TEXT,
    total_planned_audits INTEGER,
    status VARCHAR(50) DEFAULT 'Active', -- Active, Completed, Cancelled
    approved_by UUID,
    approved_date DATE,
    form_reference VARCHAR(50) DEFAULT 'QSF1701',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_schedule (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id UUID REFERENCES audit_program(id),
    audit_number VARCHAR(50) UNIQUE NOT NULL,
    audit_type VARCHAR(100), -- Internal, External, Surveillance, Special
    audit_area VARCHAR(255), -- Department, Process, or ISO Clause
    planned_date DATE NOT NULL,
    actual_date DATE,
    duration_days INTEGER DEFAULT 1,
    lead_auditor UUID,
    audit_team TEXT[], -- Array of auditor names/IDs
    auditee_department VARCHAR(100),
    auditee_contact UUID,
    checklist_reference VARCHAR(100),
    status VARCHAR(50) DEFAULT 'Scheduled', -- Scheduled, In Progress, Completed, Cancelled
    findings_count INTEGER DEFAULT 0,
    nc_count INTEGER DEFAULT 0,
    obs_count INTEGER DEFAULT 0,
    report_issued_date DATE,
    report_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_findings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_id UUID REFERENCES audit_schedule(id) ON DELETE CASCADE,
    finding_number VARCHAR(50) UNIQUE NOT NULL,
    finding_type VARCHAR(50), -- Non-Conformance, Observation, Opportunity for Improvement
    severity VARCHAR(50), -- Critical, Major, Minor (for NCs)
    clause_reference VARCHAR(100), -- ISO clause or process reference
    finding_description TEXT NOT NULL,
    objective_evidence TEXT,
    requirement TEXT, -- What was expected
    nc_id UUID REFERENCES nonconformances(id), -- Link to NC if raised
    response_required_by DATE,
    responsible_person UUID,
    status VARCHAR(50) DEFAULT 'Open', -- Open, Response Received, Closed, Verified
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE risk_register (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    risk_id VARCHAR(50) UNIQUE NOT NULL, -- RISK-YYYY-XXX format
    risk_date DATE NOT NULL DEFAULT CURRENT_DATE,
    process_area VARCHAR(255),
    department VARCHAR(100),
    risk_category VARCHAR(100), -- Operational, Technical, Financial, Compliance, Reputational
    risk_description TEXT NOT NULL,
    risk_owner UUID,
    likelihood INTEGER CHECK (likelihood BETWEEN 1 AND 5), -- 1=Rare, 5=Almost Certain
    consequence INTEGER CHECK (consequence BETWEEN 1 AND 5), -- 1=Insignificant, 5=Catastrophic
    inherent_risk_score INTEGER, -- likelihood * consequence
    inherent_risk_level VARCHAR(50), -- Low, Medium, High, Very High, Extreme
    existing_controls TEXT[],
    control_effectiveness VARCHAR(50), -- Effective, Partially Effective, Ineffective
    residual_likelihood INTEGER CHECK (residual_likelihood BETWEEN 1 AND 5),
    residual_consequence INTEGER CHECK (residual_consequence BETWEEN 1 AND 5),
    residual_risk_score INTEGER,
    residual_risk_level VARCHAR(50),
    treatment_plan TEXT,
    treatment_owner UUID,
    treatment_target_date DATE,
    review_frequency_days INTEGER DEFAULT 90,
    last_review_date DATE,
    next_review_date DATE,
    status VARCHAR(50) DEFAULT 'Active', -- Active, Mitigated, Closed, Monitoring
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SESSION 9: Analytics & Customer Portal
-- ============================================================================

CREATE TABLE dashboard_kpis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    kpi_date DATE NOT NULL,
    kpi_name VARCHAR(100) NOT NULL,
    kpi_value DECIMAL(12,2),
    target_value DECIMAL(12,2),
    unit VARCHAR(50),
    category VARCHAR(100), -- Quality, Operational, Financial
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(kpi_date, kpi_name)
);

CREATE TABLE customer_portal_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id),
    session_token TEXT UNIQUE NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT true
);

-- ============================================================================
-- SESSION 10: AI/ML Model Metadata & Predictions
-- ============================================================================

CREATE TABLE ai_model_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(255) NOT NULL,
    model_type VARCHAR(100), -- Predictive Maintenance, NLP, Regression, Classification
    model_version VARCHAR(50) NOT NULL,
    algorithm VARCHAR(100), -- RandomForest, XGBoost, LSTM, BERT, etc.
    framework VARCHAR(50), -- scikit-learn, TensorFlow, PyTorch
    training_date TIMESTAMP,
    model_path TEXT,
    performance_metrics JSONB, -- {accuracy, precision, recall, f1_score, rmse, etc.}
    feature_importance JSONB,
    is_active BOOLEAN DEFAULT true,
    deployed_date TIMESTAMP,
    created_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE equipment_failure_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    equipment_id UUID REFERENCES equipment_master(id),
    prediction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    model_id UUID REFERENCES ai_model_registry(id),
    failure_probability DECIMAL(5,2), -- 0-100%
    predicted_failure_date DATE,
    confidence_score DECIMAL(5,2),
    risk_factors JSONB, -- Contributing factors
    recommended_actions TEXT[],
    prediction_status VARCHAR(50) DEFAULT 'Active', -- Active, Validated, False Positive
    actual_failure_date DATE, -- For model validation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE nc_root_cause_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nc_id UUID REFERENCES nonconformances(id),
    model_id UUID REFERENCES ai_model_registry(id),
    suggestion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    suggested_root_causes JSONB, -- [{cause, confidence, similar_nc_ids}]
    similar_cases TEXT[], -- Historical NC numbers
    confidence_score DECIMAL(5,2),
    was_accepted BOOLEAN,
    actual_root_cause TEXT, -- For model training feedback
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test_duration_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trq_id UUID REFERENCES test_requests(id),
    model_id UUID REFERENCES ai_model_registry(id),
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    predicted_duration_days INTEGER,
    confidence_interval JSONB, -- {lower_bound, upper_bound}
    factors_considered JSONB, -- {test_type, sample_count, complexity, etc.}
    actual_duration_days INTEGER, -- For model validation
    prediction_accuracy DECIMAL(5,2), -- Calculated after completion
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE document_ai_classifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES qms_documents(id),
    model_id UUID REFERENCES ai_model_registry(id),
    classification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    predicted_category VARCHAR(100),
    confidence_score DECIMAL(5,2),
    suggested_tags TEXT[],
    extracted_entities JSONB, -- Named entities, dates, references
    was_validated BOOLEAN DEFAULT false,
    manual_override BOOLEAN DEFAULT false,
    actual_category VARCHAR(100), -- For model training
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Audit Trail & System Tables
-- ============================================================================

CREATE TABLE audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    operation VARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by UUID,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent TEXT,
    module VARCHAR(100) -- Document, Equipment, LIMS, NC, Audit, etc.
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(255),
    employee_code VARCHAR(50),
    department VARCHAR(100),
    designation VARCHAR(100),
    role VARCHAR(50), -- Admin, QA Manager, Lab Technician, Auditor, etc.
    permissions JSONB, -- Role-based permissions
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    data_type VARCHAR(50), -- string, integer, boolean, json
    category VARCHAR(100), -- General, Email, AI Models, Notifications
    is_sensitive BOOLEAN DEFAULT false,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID
);

-- ============================================================================
-- Indexes for Performance Optimization
-- ============================================================================

-- Document Management Indexes
CREATE INDEX idx_qms_documents_doc_number ON qms_documents(doc_number);
CREATE INDEX idx_qms_documents_status ON qms_documents(status);
CREATE INDEX idx_qms_documents_type ON qms_documents(doc_type);
CREATE INDEX idx_qms_documents_tags ON qms_documents USING GIN(tags);

-- Equipment Indexes
CREATE INDEX idx_equipment_master_equipment_id ON equipment_master(equipment_id);
CREATE INDEX idx_equipment_master_status ON equipment_master(status);
CREATE INDEX idx_equipment_next_cal ON equipment_master(next_calibration_date);
CREATE INDEX idx_calibration_records_equipment ON calibration_records(equipment_id);
CREATE INDEX idx_calibration_records_date ON calibration_records(calibration_date);

-- Training Indexes
CREATE INDEX idx_training_matrix_employee ON employee_training_matrix(employee_id);
CREATE INDEX idx_training_matrix_status ON employee_training_matrix(competency_status);
CREATE INDEX idx_training_matrix_expiry ON employee_training_matrix(expiry_date);

-- LIMS Indexes
CREATE INDEX idx_test_requests_trq_number ON test_requests(trq_number);
CREATE INDEX idx_test_requests_customer ON test_requests(customer_id);
CREATE INDEX idx_test_requests_status ON test_requests(status);
CREATE INDEX idx_test_requests_date ON test_requests(request_date);
CREATE INDEX idx_samples_sample_id ON samples(sample_id);
CREATE INDEX idx_samples_trq ON samples(trq_id);
CREATE INDEX idx_samples_status ON samples(sample_status);

-- NC & CAPA Indexes
CREATE INDEX idx_nonconformances_nc_number ON nonconformances(nc_number);
CREATE INDEX idx_nonconformances_status ON nonconformances(status);
CREATE INDEX idx_nonconformances_date ON nonconformances(nc_date);
CREATE INDEX idx_capa_actions_capa_number ON capa_actions(capa_number);
CREATE INDEX idx_capa_actions_nc ON capa_actions(nc_id);

-- Audit & Risk Indexes
CREATE INDEX idx_audit_schedule_date ON audit_schedule(planned_date);
CREATE INDEX idx_audit_schedule_status ON audit_schedule(status);
CREATE INDEX idx_risk_register_risk_id ON risk_register(risk_id);
CREATE INDEX idx_risk_register_level ON risk_register(residual_risk_level);

-- Audit Trail Indexes
CREATE INDEX idx_audit_trail_table ON audit_trail(table_name);
CREATE INDEX idx_audit_trail_record ON audit_trail(record_id);
CREATE INDEX idx_audit_trail_timestamp ON audit_trail(changed_at);
CREATE INDEX idx_audit_trail_user ON audit_trail(changed_by);

-- AI Model Indexes
CREATE INDEX idx_equipment_predictions_equipment ON equipment_failure_predictions(equipment_id);
CREATE INDEX idx_nc_suggestions_nc ON nc_root_cause_suggestions(nc_id);
CREATE INDEX idx_test_predictions_trq ON test_duration_predictions(trq_id);

-- ============================================================================
-- Views for Analytics & Reporting
-- ============================================================================

CREATE VIEW v_calibration_due_alerts AS
SELECT
    e.equipment_id,
    e.equipment_name,
    e.category,
    e.location,
    e.next_calibration_date,
    CASE
        WHEN e.next_calibration_date < CURRENT_DATE THEN 'Overdue'
        WHEN e.next_calibration_date <= CURRENT_DATE + INTERVAL '7 days' THEN '7 Days'
        WHEN e.next_calibration_date <= CURRENT_DATE + INTERVAL '15 days' THEN '15 Days'
        WHEN e.next_calibration_date <= CURRENT_DATE + INTERVAL '30 days' THEN '30 Days'
    END as alert_status,
    e.next_calibration_date - CURRENT_DATE as days_remaining
FROM equipment_master e
WHERE e.status = 'Active'
  AND e.next_calibration_date <= CURRENT_DATE + INTERVAL '30 days'
ORDER BY e.next_calibration_date;

CREATE VIEW v_training_expiry_alerts AS
SELECT
    em.employee_id,
    em.employee_name,
    em.department,
    tm.training_name,
    em.completion_date,
    em.expiry_date,
    CASE
        WHEN em.expiry_date < CURRENT_DATE THEN 'Expired'
        WHEN em.expiry_date <= CURRENT_DATE + INTERVAL '7 days' THEN '7 Days'
        WHEN em.expiry_date <= CURRENT_DATE + INTERVAL '15 days' THEN '15 Days'
        WHEN em.expiry_date <= CURRENT_DATE + INTERVAL '30 days' THEN '30 Days'
    END as alert_status
FROM employee_training_matrix em
JOIN training_master tm ON em.training_id = tm.id
WHERE em.expiry_date IS NOT NULL
  AND em.expiry_date <= CURRENT_DATE + INTERVAL '30 days'
ORDER BY em.expiry_date;

CREATE VIEW v_open_nonconformances AS
SELECT
    nc.nc_number,
    nc.nc_date,
    nc.source,
    nc.nc_type,
    nc.severity,
    nc.department,
    nc.description,
    nc.status,
    nc.target_closure_date,
    COUNT(ca.id) as capa_count
FROM nonconformances nc
LEFT JOIN capa_actions ca ON nc.id = ca.nc_id
WHERE nc.status != 'Closed'
GROUP BY nc.id
ORDER BY nc.severity, nc.target_closure_date;

CREATE VIEW v_test_request_summary AS
SELECT
    tr.trq_number,
    c.customer_name,
    tr.request_date,
    tr.product_type,
    tr.test_standard,
    tr.status,
    COUNT(DISTINCT s.id) as sample_count,
    COUNT(DISTINCT tp.id) as test_parameter_count,
    tr.estimated_duration_days,
    tr.expected_completion_date
FROM test_requests tr
LEFT JOIN customers c ON tr.customer_id = c.id
LEFT JOIN samples s ON tr.id = s.trq_id
LEFT JOIN test_parameters tp ON tr.id = tp.trq_id
GROUP BY tr.id, c.customer_name
ORDER BY tr.request_date DESC;

-- ============================================================================
-- Initial Data Seeding
-- ============================================================================

-- System Config Defaults
INSERT INTO system_config (config_key, config_value, description, data_type, category) VALUES
('company_name', 'Solar PV Testing Laboratory', 'Organization name', 'string', 'General'),
('iso17025_accreditation', 'NABL-TC-XXXX', 'ISO 17025 accreditation number', 'string', 'General'),
('iso9001_certification', 'ISO-9001-XXXX', 'ISO 9001 certification number', 'string', 'General'),
('calibration_alert_days', '30,15,7', 'Days before calibration due for alerts', 'string', 'General'),
('training_alert_days', '30,15,7', 'Days before training expiry for alerts', 'string', 'General'),
('ai_models_enabled', 'true', 'Enable AI/ML features', 'boolean', 'AI Models'),
('ai_prediction_confidence_threshold', '75', 'Minimum confidence % for AI predictions', 'integer', 'AI Models'),
('backup_retention_days', '90', 'Database backup retention period', 'integer', 'General'),
('smtp_host', '', 'SMTP server for email notifications', 'string', 'Email'),
('smtp_port', '587', 'SMTP port', 'integer', 'Email');

-- Test Standards
INSERT INTO test_standards (standard_code, standard_name, version, category) VALUES
('IEC 61215', 'Crystalline silicon terrestrial photovoltaic (PV) modules - Design qualification and type approval', '2021', 'Module Testing'),
('IEC 61730', 'Photovoltaic (PV) module safety qualification', '2016', 'Safety Testing'),
('IEC 61701', 'Salt mist corrosion testing of photovoltaic (PV) modules', '2020', 'Environmental Testing');

-- Default Admin User (password: admin123 - CHANGE IN PRODUCTION!)
INSERT INTO users (username, email, password_hash, full_name, role, is_active) VALUES
('admin', 'admin@solarlims.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIIHhRzTBi', 'System Administrator', 'Admin', true);

COMMENT ON DATABASE postgres IS 'LIMS-QMS Platform - AI-Powered Laboratory Information Management System & Quality Management System for Solar PV Testing';
