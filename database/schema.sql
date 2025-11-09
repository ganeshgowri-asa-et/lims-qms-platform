-- LIMS-QMS Platform Database Schema
-- PostgreSQL Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- SESSION 2: DOCUMENT MANAGEMENT SYSTEM
-- ============================================================================

CREATE TABLE qms_documents (
    id SERIAL PRIMARY KEY,
    doc_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    owner VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'Draft',
    current_revision VARCHAR(20) DEFAULT '0.1',
    effective_date DATE,
    review_date DATE,
    file_path VARCHAR(500),
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE document_revisions (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES qms_documents(id) ON DELETE CASCADE,
    revision VARCHAR(20) NOT NULL,
    change_description TEXT,
    revised_by VARCHAR(100) NOT NULL,
    revision_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(500),
    doer VARCHAR(100),
    checker VARCHAR(100),
    approver VARCHAR(100),
    doer_signature VARCHAR(500),
    checker_signature VARCHAR(500),
    approver_signature VARCHAR(500),
    doer_date TIMESTAMP,
    checker_date TIMESTAMP,
    approver_date TIMESTAMP,
    approval_status VARCHAR(50) DEFAULT 'Pending'
);

CREATE TABLE document_distribution (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES qms_documents(id) ON DELETE CASCADE,
    copy_number INTEGER NOT NULL,
    issued_to VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    issue_date DATE NOT NULL,
    acknowledgment_date DATE,
    is_controlled BOOLEAN DEFAULT TRUE,
    status VARCHAR(50) DEFAULT 'Active'
);

-- ============================================================================
-- SESSION 3: EQUIPMENT CALIBRATION & MAINTENANCE
-- ============================================================================

CREATE TABLE equipment_master (
    id SERIAL PRIMARY KEY,
    equipment_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(200),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    purchase_date DATE,
    installation_date DATE,
    location VARCHAR(200),
    responsible_person VARCHAR(100),
    status VARCHAR(50) DEFAULT 'Active',
    qr_code_path VARCHAR(500),
    specifications JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE calibration_records (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER REFERENCES equipment_master(id) ON DELETE CASCADE,
    calibration_date DATE NOT NULL,
    next_due_date DATE NOT NULL,
    calibrated_by VARCHAR(100) NOT NULL,
    calibration_agency VARCHAR(200),
    certificate_number VARCHAR(100),
    certificate_path VARCHAR(500),
    result VARCHAR(50) DEFAULT 'Pass',
    remarks TEXT,
    notification_30_sent BOOLEAN DEFAULT FALSE,
    notification_15_sent BOOLEAN DEFAULT FALSE,
    notification_7_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE preventive_maintenance_schedule (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER REFERENCES equipment_master(id) ON DELETE CASCADE,
    maintenance_type VARCHAR(100) NOT NULL,
    frequency VARCHAR(50) NOT NULL,
    last_maintenance_date DATE,
    next_maintenance_date DATE NOT NULL,
    performed_by VARCHAR(100),
    status VARCHAR(50) DEFAULT 'Scheduled',
    findings TEXT,
    actions_taken TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE oee_tracking (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER REFERENCES equipment_master(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    planned_production_time INTEGER,
    actual_production_time INTEGER,
    downtime_minutes INTEGER DEFAULT 0,
    units_produced INTEGER,
    defective_units INTEGER DEFAULT 0,
    availability_percent DECIMAL(5,2),
    performance_percent DECIMAL(5,2),
    quality_percent DECIMAL(5,2),
    oee_percent DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SESSION 4: TRAINING & COMPETENCY MANAGEMENT
-- ============================================================================

CREATE TABLE training_master (
    id SERIAL PRIMARY KEY,
    training_code VARCHAR(50) UNIQUE NOT NULL,
    training_name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- Internal, External, On-the-job, E-learning
    duration_hours DECIMAL(5,2),
    validity_months INTEGER, -- Certificate validity period
    trainer VARCHAR(100),
    training_material_path VARCHAR(500),
    prerequisites TEXT,
    competency_level VARCHAR(50), -- Basic, Intermediate, Advanced, Expert
    applicable_roles TEXT[], -- Array of job roles
    status VARCHAR(50) DEFAULT 'Active',
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employee_training_matrix (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    employee_name VARCHAR(200) NOT NULL,
    department VARCHAR(100) NOT NULL,
    job_role VARCHAR(100) NOT NULL,
    training_id INTEGER REFERENCES training_master(id) ON DELETE CASCADE,
    required BOOLEAN DEFAULT TRUE,
    current_level VARCHAR(50), -- Untrained, Basic, Intermediate, Advanced, Expert
    target_level VARCHAR(50),
    last_trained_date DATE,
    certificate_valid_until DATE,
    status VARCHAR(50) DEFAULT 'Required', -- Required, In Progress, Completed, Expired
    competency_score DECIMAL(5,2),
    competency_status VARCHAR(50), -- Competent, Not Competent, Needs Refresher
    gap_analysis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, training_id)
);

CREATE TABLE training_attendance (
    id SERIAL PRIMARY KEY,
    training_id INTEGER REFERENCES training_master(id) ON DELETE CASCADE,
    training_date DATE NOT NULL,
    training_end_date DATE,
    location VARCHAR(200),
    trainer_name VARCHAR(200),
    trainer_qualification VARCHAR(200),
    employee_id VARCHAR(50) NOT NULL,
    employee_name VARCHAR(200) NOT NULL,
    department VARCHAR(100),
    attendance_status VARCHAR(50) DEFAULT 'Present', -- Present, Absent, Partial
    pre_test_score DECIMAL(5,2),
    post_test_score DECIMAL(5,2),
    practical_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),
    pass_fail VARCHAR(20) DEFAULT 'Pass',
    certificate_number VARCHAR(100),
    certificate_issue_date DATE,
    certificate_valid_until DATE,
    certificate_path VARCHAR(500),
    feedback_rating INTEGER, -- 1-5 rating
    feedback_comments TEXT,
    effectiveness_score DECIMAL(5,2),
    qsf_form VARCHAR(20), -- QSF0203, QSF0205, QSF0206
    form_path VARCHAR(500),
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE training_effectiveness (
    id SERIAL PRIMARY KEY,
    attendance_id INTEGER REFERENCES training_attendance(id) ON DELETE CASCADE,
    evaluation_date DATE NOT NULL,
    evaluator VARCHAR(100) NOT NULL,
    knowledge_retention DECIMAL(5,2),
    practical_application DECIMAL(5,2),
    behavior_change DECIMAL(5,2),
    business_impact DECIMAL(5,2),
    overall_effectiveness DECIMAL(5,2),
    comments TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE competency_assessment (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    employee_name VARCHAR(200) NOT NULL,
    assessment_date DATE NOT NULL,
    assessor VARCHAR(100) NOT NULL,
    job_role VARCHAR(100) NOT NULL,
    competencies JSONB, -- JSON array of competency assessments
    overall_competency_level VARCHAR(50),
    gaps_identified TEXT,
    development_plan TEXT,
    next_assessment_date DATE,
    status VARCHAR(50) DEFAULT 'Completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Document Management Indexes
CREATE INDEX idx_qms_documents_status ON qms_documents(status);
CREATE INDEX idx_qms_documents_type ON qms_documents(type);
CREATE INDEX idx_qms_documents_owner ON qms_documents(owner);

-- Equipment Indexes
CREATE INDEX idx_equipment_status ON equipment_master(status);
CREATE INDEX idx_equipment_category ON equipment_master(category);
CREATE INDEX idx_calibration_next_due ON calibration_records(next_due_date);
CREATE INDEX idx_maintenance_next_due ON preventive_maintenance_schedule(next_maintenance_date);

-- Training Indexes
CREATE INDEX idx_training_category ON training_master(category);
CREATE INDEX idx_training_status ON training_master(status);
CREATE INDEX idx_employee_training_employee ON employee_training_matrix(employee_id);
CREATE INDEX idx_employee_training_status ON employee_training_matrix(status);
CREATE INDEX idx_training_attendance_employee ON training_attendance(employee_id);
CREATE INDEX idx_training_attendance_date ON training_attendance(training_date);
CREATE INDEX idx_competency_employee ON competency_assessment(employee_id);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Calibration Due Alerts View
CREATE OR REPLACE VIEW v_calibration_alerts AS
SELECT
    em.equipment_id,
    em.name,
    em.category,
    em.location,
    em.responsible_person,
    cr.next_due_date,
    cr.next_due_date - CURRENT_DATE as days_remaining,
    CASE
        WHEN cr.next_due_date < CURRENT_DATE THEN 'Overdue'
        WHEN cr.next_due_date - CURRENT_DATE <= 7 THEN 'Critical'
        WHEN cr.next_due_date - CURRENT_DATE <= 15 THEN 'Warning'
        WHEN cr.next_due_date - CURRENT_DATE <= 30 THEN 'Upcoming'
        ELSE 'OK'
    END as alert_level
FROM equipment_master em
JOIN calibration_records cr ON em.id = cr.equipment_id
WHERE em.status = 'Active'
ORDER BY cr.next_due_date;

-- Training Competency Gap View
CREATE OR REPLACE VIEW v_competency_gaps AS
SELECT
    etm.employee_id,
    etm.employee_name,
    etm.department,
    etm.job_role,
    tm.training_name,
    tm.category,
    etm.current_level,
    etm.target_level,
    etm.status,
    etm.competency_status,
    etm.last_trained_date,
    etm.certificate_valid_until,
    CASE
        WHEN etm.certificate_valid_until < CURRENT_DATE THEN 'Expired'
        WHEN etm.certificate_valid_until - CURRENT_DATE <= 30 THEN 'Expiring Soon'
        WHEN etm.current_level IS NULL OR etm.current_level = 'Untrained' THEN 'Not Trained'
        WHEN etm.current_level != etm.target_level THEN 'Gap Exists'
        ELSE 'Competent'
    END as gap_status
FROM employee_training_matrix etm
JOIN training_master tm ON etm.training_id = tm.id
WHERE etm.required = TRUE
ORDER BY etm.employee_id, gap_status;

-- Document Control View
CREATE OR REPLACE VIEW v_document_status AS
SELECT
    d.doc_number,
    d.title,
    d.type,
    d.category,
    d.owner,
    d.status,
    d.current_revision,
    d.effective_date,
    d.review_date,
    CASE
        WHEN d.review_date < CURRENT_DATE THEN 'Review Overdue'
        WHEN d.review_date - CURRENT_DATE <= 30 THEN 'Review Due Soon'
        ELSE 'Current'
    END as review_status
FROM qms_documents d
ORDER BY d.doc_number;
