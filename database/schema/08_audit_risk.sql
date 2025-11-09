-- ================================================================
-- Session 8: Audit & Risk Management System
-- ================================================================
-- Tables: audit_program, audit_schedule, audit_findings, risk_register
-- Features: QSF1701 annual program, 5x5 risk matrix, audit findings with NC linkage

-- ================================================================
-- 1. AUDIT PROGRAM TABLE (QSF1701 Annual Audit Program)
-- ================================================================
CREATE TABLE IF NOT EXISTS audit_program (
    id SERIAL PRIMARY KEY,
    program_year INTEGER NOT NULL,
    program_number VARCHAR(50) UNIQUE NOT NULL, -- QSF1701-YYYY
    program_title VARCHAR(255) NOT NULL,
    scope TEXT,
    objectives TEXT,
    prepared_by VARCHAR(100),
    reviewed_by VARCHAR(100),
    approved_by VARCHAR(100),
    status VARCHAR(50) DEFAULT 'DRAFT', -- DRAFT, APPROVED, ACTIVE, COMPLETED
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_program_year CHECK (program_year >= 2024)
);

CREATE INDEX idx_audit_program_year ON audit_program(program_year);
CREATE INDEX idx_audit_program_status ON audit_program(status);

-- ================================================================
-- 2. AUDIT SCHEDULE TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS audit_schedule (
    id SERIAL PRIMARY KEY,
    audit_number VARCHAR(50) UNIQUE NOT NULL, -- AUD-YYYY-XXX
    program_id INTEGER REFERENCES audit_program(id) ON DELETE CASCADE,
    audit_type VARCHAR(50) NOT NULL, -- INTERNAL, EXTERNAL, SURVEILLANCE, CERTIFICATION
    audit_scope VARCHAR(100) NOT NULL, -- DEPARTMENT, PROCESS, SYSTEM, PRODUCT
    department VARCHAR(100),
    process_area VARCHAR(100),
    standard_reference VARCHAR(100), -- ISO 17025, ISO 9001, IEC 61215, etc.
    planned_date DATE NOT NULL,
    actual_date DATE,
    duration_days INTEGER,
    lead_auditor VARCHAR(100),
    audit_team TEXT, -- Comma-separated auditor names
    auditee VARCHAR(100),
    status VARCHAR(50) DEFAULT 'SCHEDULED', -- SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_schedule_number ON audit_schedule(audit_number);
CREATE INDEX idx_audit_schedule_program ON audit_schedule(program_id);
CREATE INDEX idx_audit_schedule_status ON audit_schedule(status);
CREATE INDEX idx_audit_schedule_date ON audit_schedule(planned_date);

-- ================================================================
-- 3. AUDIT FINDINGS TABLE (with NC linkage)
-- ================================================================
CREATE TABLE IF NOT EXISTS audit_findings (
    id SERIAL PRIMARY KEY,
    finding_number VARCHAR(50) UNIQUE NOT NULL, -- FND-YYYY-XXX
    audit_id INTEGER REFERENCES audit_schedule(id) ON DELETE CASCADE,
    finding_type VARCHAR(50) NOT NULL, -- NCR (Non-Conformance), OFI (Opportunity for Improvement), OBS (Observation)
    severity VARCHAR(50), -- MAJOR, MINOR, CRITICAL (for NCRs)
    category VARCHAR(100), -- DOCUMENTATION, PROCESS, EQUIPMENT, PERSONNEL, CALIBRATION
    clause_reference VARCHAR(100), -- ISO clause reference (e.g., 5.6, 6.4.1)
    area_audited VARCHAR(100),
    description TEXT NOT NULL,
    objective_evidence TEXT,
    requirement TEXT, -- What was the requirement
    root_cause TEXT,
    corrective_action TEXT,
    responsible_person VARCHAR(100),
    target_date DATE,
    actual_closure_date DATE,
    status VARCHAR(50) DEFAULT 'OPEN', -- OPEN, IN_PROGRESS, CLOSED, VERIFIED
    nc_reference VARCHAR(50), -- Link to NC-YYYY-XXX from nonconformances table
    effectiveness_verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(100),
    verified_date DATE,
    attachments TEXT, -- JSON array of file paths
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_findings_number ON audit_findings(finding_number);
CREATE INDEX idx_audit_findings_audit ON audit_findings(audit_id);
CREATE INDEX idx_audit_findings_type ON audit_findings(finding_type);
CREATE INDEX idx_audit_findings_status ON audit_findings(status);
CREATE INDEX idx_audit_findings_nc ON audit_findings(nc_reference);

-- ================================================================
-- 4. RISK REGISTER TABLE (5x5 Risk Matrix)
-- ================================================================
CREATE TABLE IF NOT EXISTS risk_register (
    id SERIAL PRIMARY KEY,
    risk_number VARCHAR(50) UNIQUE NOT NULL, -- RISK-YYYY-XXX
    risk_category VARCHAR(100) NOT NULL, -- OPERATIONAL, STRATEGIC, FINANCIAL, COMPLIANCE, TECHNICAL
    process_area VARCHAR(100),
    department VARCHAR(100),
    risk_description TEXT NOT NULL,
    risk_source VARCHAR(255), -- What causes this risk
    consequences TEXT, -- What could happen if risk materializes
    existing_controls TEXT, -- Current mitigation measures

    -- INHERENT RISK (Before controls)
    inherent_likelihood INTEGER CHECK (inherent_likelihood BETWEEN 1 AND 5), -- 1=Rare, 5=Almost Certain
    inherent_impact INTEGER CHECK (inherent_impact BETWEEN 1 AND 5), -- 1=Insignificant, 5=Catastrophic
    inherent_risk_score INTEGER GENERATED ALWAYS AS (inherent_likelihood * inherent_impact) STORED,
    inherent_risk_level VARCHAR(20) GENERATED ALWAYS AS (
        CASE
            WHEN (inherent_likelihood * inherent_impact) BETWEEN 1 AND 4 THEN 'LOW'
            WHEN (inherent_likelihood * inherent_impact) BETWEEN 5 AND 12 THEN 'MEDIUM'
            WHEN (inherent_likelihood * inherent_impact) BETWEEN 13 AND 16 THEN 'HIGH'
            ELSE 'CRITICAL'
        END
    ) STORED,

    -- RESIDUAL RISK (After controls)
    residual_likelihood INTEGER CHECK (residual_likelihood BETWEEN 1 AND 5),
    residual_impact INTEGER CHECK (residual_impact BETWEEN 1 AND 5),
    residual_risk_score INTEGER GENERATED ALWAYS AS (residual_likelihood * residual_impact) STORED,
    residual_risk_level VARCHAR(20) GENERATED ALWAYS AS (
        CASE
            WHEN (residual_likelihood * residual_impact) BETWEEN 1 AND 4 THEN 'LOW'
            WHEN (residual_likelihood * residual_impact) BETWEEN 5 AND 12 THEN 'MEDIUM'
            WHEN (residual_likelihood * residual_impact) BETWEEN 13 AND 16 THEN 'HIGH'
            ELSE 'CRITICAL'
        END
    ) STORED,

    risk_treatment VARCHAR(50), -- ACCEPT, MITIGATE, TRANSFER, AVOID
    treatment_plan TEXT, -- Additional actions to reduce risk
    risk_owner VARCHAR(100),
    target_date DATE,
    review_frequency VARCHAR(50), -- MONTHLY, QUARTERLY, ANNUALLY
    last_review_date DATE,
    next_review_date DATE,
    status VARCHAR(50) DEFAULT 'ACTIVE', -- ACTIVE, CLOSED, MONITORING
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_register_number ON risk_register(risk_number);
CREATE INDEX idx_risk_register_category ON risk_register(risk_category);
CREATE INDEX idx_risk_register_level ON risk_register(residual_risk_level);
CREATE INDEX idx_risk_register_owner ON risk_register(risk_owner);
CREATE INDEX idx_risk_register_status ON risk_register(status);

-- ================================================================
-- 5. RISK REVIEW HISTORY TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS risk_review_history (
    id SERIAL PRIMARY KEY,
    risk_id INTEGER REFERENCES risk_register(id) ON DELETE CASCADE,
    review_date DATE NOT NULL,
    reviewed_by VARCHAR(100),
    likelihood_before INTEGER,
    impact_before INTEGER,
    likelihood_after INTEGER,
    impact_after INTEGER,
    changes_made TEXT,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_review_risk_id ON risk_review_history(risk_id);

-- ================================================================
-- 6. COMPLIANCE TRACKING TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS compliance_tracking (
    id SERIAL PRIMARY KEY,
    standard_name VARCHAR(100) NOT NULL, -- ISO 17025:2017, ISO 9001:2015
    clause_number VARCHAR(50) NOT NULL,
    clause_title VARCHAR(255),
    requirement TEXT,
    compliance_status VARCHAR(50) DEFAULT 'COMPLIANT', -- COMPLIANT, NON_COMPLIANT, PARTIAL, NOT_APPLICABLE
    evidence_reference TEXT, -- Links to documents, procedures
    last_audit_date DATE,
    next_audit_date DATE,
    responsible_person VARCHAR(100),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(standard_name, clause_number)
);

CREATE INDEX idx_compliance_standard ON compliance_tracking(standard_name);
CREATE INDEX idx_compliance_status ON compliance_tracking(compliance_status);

-- ================================================================
-- SAMPLE DATA
-- ================================================================

-- Insert sample audit program
INSERT INTO audit_program (program_year, program_number, program_title, scope, objectives, prepared_by, reviewed_by, approved_by, status, start_date, end_date)
VALUES
(2025, 'QSF1701-2025', 'Annual Internal Audit Program 2025',
 'Complete QMS and LIMS coverage including ISO 17025 and ISO 9001 requirements',
 'Verify compliance with ISO 17025:2017 and ISO 9001:2015; Identify improvement opportunities; Ensure process effectiveness',
 'Quality Manager', 'Technical Manager', 'CEO', 'APPROVED',
 '2025-01-01', '2025-12-31');

-- Insert sample audit schedules
INSERT INTO audit_schedule (audit_number, program_id, audit_type, audit_scope, department, process_area, standard_reference, planned_date, lead_auditor, audit_team, auditee, status)
VALUES
('AUD-2025-001', 1, 'INTERNAL', 'PROCESS', 'Testing Lab', 'Sample Management', 'ISO 17025:2017 - Clause 7.4', '2025-02-15', 'John Smith', 'John Smith, Mary Johnson', 'Lab Manager', 'SCHEDULED'),
('AUD-2025-002', 1, 'INTERNAL', 'SYSTEM', 'Quality Department', 'Document Control', 'ISO 9001:2015 - Clause 7.5', '2025-03-20', 'Sarah Lee', 'Sarah Lee, Tom Brown', 'Quality Manager', 'SCHEDULED'),
('AUD-2025-003', 1, 'INTERNAL', 'DEPARTMENT', 'Calibration Lab', 'Equipment Calibration', 'ISO 17025:2017 - Clause 6.4', '2025-04-10', 'Michael Chen', 'Michael Chen, Lisa Wang', 'Calibration Manager', 'SCHEDULED');

-- Insert sample risks
INSERT INTO risk_register (
    risk_number, risk_category, process_area, department, risk_description, risk_source,
    consequences, existing_controls, inherent_likelihood, inherent_impact,
    residual_likelihood, residual_impact, risk_treatment, treatment_plan, risk_owner,
    review_frequency, last_review_date, next_review_date, status
)
VALUES
('RISK-2025-001', 'TECHNICAL', 'Testing', 'Testing Lab',
 'Equipment breakdown during critical testing period',
 'Equipment age, heavy usage, environmental conditions',
 'Delayed test results, customer dissatisfaction, revenue loss, accreditation impact',
 'Preventive maintenance schedule, calibration program, spare parts inventory',
 4, 4, 2, 3, 'MITIGATE',
 'Implement predictive maintenance; Maintain backup equipment; Train additional operators',
 'Technical Manager', 'QUARTERLY', '2025-01-15', '2025-04-15', 'ACTIVE'),

('RISK-2025-002', 'COMPLIANCE', 'Quality Management', 'Quality Department',
 'Non-compliance with ISO 17025 requirements leading to accreditation suspension',
 'Inadequate training, poor document control, process deviations',
 'Loss of accreditation, business closure, legal implications, reputation damage',
 'Internal audit program, management review, competency assessment, document control system',
 3, 5, 1, 3, 'MITIGATE',
 'Enhanced training program; Monthly compliance reviews; Real-time monitoring dashboard',
 'Quality Manager', 'MONTHLY', '2025-01-10', '2025-02-10', 'ACTIVE'),

('RISK-2025-003', 'OPERATIONAL', 'Sample Management', 'Testing Lab',
 'Sample mix-up or contamination leading to incorrect test results',
 'Manual labeling errors, inadequate sample storage, cross-contamination',
 'Wrong test results reported, customer complaints, accreditation non-conformance',
 'Barcode system, sample tracking software, dedicated storage areas, SOPs',
 2, 4, 1, 2, 'MITIGATE',
 'Implement automated sample tracking with RFID; Enhanced training on sample handling',
 'Lab Manager', 'QUARTERLY', '2025-01-05', '2025-04-05', 'ACTIVE');

-- Insert compliance tracking for ISO 17025
INSERT INTO compliance_tracking (standard_name, clause_number, clause_title, requirement, compliance_status, responsible_person)
VALUES
('ISO 17025:2017', '4.1', 'Impartiality', 'Laboratory shall undertake its activities impartially and structure and manage them to safeguard impartiality', 'COMPLIANT', 'Quality Manager'),
('ISO 17025:2017', '6.2', 'Personnel', 'Laboratory personnel shall be competent to perform laboratory activities and to evaluate the significance of deviations', 'COMPLIANT', 'HR Manager'),
('ISO 17025:2017', '6.4', 'Equipment', 'Laboratory shall have access to equipment required for correct performance of laboratory activities', 'COMPLIANT', 'Technical Manager'),
('ISO 17025:2017', '7.4', 'Handling of test items', 'Laboratory shall have a procedure for handling, transport, storage, and disposal of test items', 'COMPLIANT', 'Lab Manager');

-- ================================================================
-- VIEWS
-- ================================================================

-- View for upcoming audits
CREATE OR REPLACE VIEW v_upcoming_audits AS
SELECT
    a.audit_number,
    a.audit_type,
    a.department,
    a.process_area,
    a.planned_date,
    a.lead_auditor,
    a.status,
    p.program_number,
    p.program_year
FROM audit_schedule a
LEFT JOIN audit_program p ON a.program_id = p.id
WHERE a.status IN ('SCHEDULED', 'IN_PROGRESS')
ORDER BY a.planned_date;

-- View for high-risk items
CREATE OR REPLACE VIEW v_high_risks AS
SELECT
    risk_number,
    risk_category,
    process_area,
    risk_description,
    residual_risk_score,
    residual_risk_level,
    risk_owner,
    status,
    next_review_date
FROM risk_register
WHERE residual_risk_level IN ('HIGH', 'CRITICAL')
    AND status = 'ACTIVE'
ORDER BY residual_risk_score DESC;

-- View for open findings
CREATE OR REPLACE VIEW v_open_findings AS
SELECT
    f.finding_number,
    f.finding_type,
    f.severity,
    f.area_audited,
    f.description,
    f.responsible_person,
    f.target_date,
    f.status,
    a.audit_number,
    a.audit_type,
    CASE
        WHEN f.target_date < CURRENT_DATE THEN 'OVERDUE'
        WHEN f.target_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'DUE_SOON'
        ELSE 'ON_TRACK'
    END as urgency
FROM audit_findings f
LEFT JOIN audit_schedule a ON f.audit_id = a.id
WHERE f.status IN ('OPEN', 'IN_PROGRESS')
ORDER BY f.target_date;

-- View for compliance summary
CREATE OR REPLACE VIEW v_compliance_summary AS
SELECT
    standard_name,
    COUNT(*) as total_clauses,
    SUM(CASE WHEN compliance_status = 'COMPLIANT' THEN 1 ELSE 0 END) as compliant_count,
    SUM(CASE WHEN compliance_status = 'NON_COMPLIANT' THEN 1 ELSE 0 END) as non_compliant_count,
    SUM(CASE WHEN compliance_status = 'PARTIAL' THEN 1 ELSE 0 END) as partial_count,
    ROUND(100.0 * SUM(CASE WHEN compliance_status = 'COMPLIANT' THEN 1 ELSE 0 END) / COUNT(*), 2) as compliance_percentage
FROM compliance_tracking
GROUP BY standard_name;

-- ================================================================
-- FUNCTIONS
-- ================================================================

-- Function to generate next audit number
CREATE OR REPLACE FUNCTION generate_audit_number()
RETURNS VARCHAR(50) AS $$
DECLARE
    current_year INTEGER;
    next_seq INTEGER;
    new_number VARCHAR(50);
BEGIN
    current_year := EXTRACT(YEAR FROM CURRENT_DATE);

    SELECT COALESCE(MAX(CAST(SUBSTRING(audit_number FROM 10) AS INTEGER)), 0) + 1
    INTO next_seq
    FROM audit_schedule
    WHERE audit_number LIKE 'AUD-' || current_year || '-%';

    new_number := 'AUD-' || current_year || '-' || LPAD(next_seq::TEXT, 3, '0');
    RETURN new_number;
END;
$$ LANGUAGE plpgsql;

-- Function to generate next finding number
CREATE OR REPLACE FUNCTION generate_finding_number()
RETURNS VARCHAR(50) AS $$
DECLARE
    current_year INTEGER;
    next_seq INTEGER;
    new_number VARCHAR(50);
BEGIN
    current_year := EXTRACT(YEAR FROM CURRENT_DATE);

    SELECT COALESCE(MAX(CAST(SUBSTRING(finding_number FROM 10) AS INTEGER)), 0) + 1
    INTO next_seq
    FROM audit_findings
    WHERE finding_number LIKE 'FND-' || current_year || '-%';

    new_number := 'FND-' || current_year || '-' || LPAD(next_seq::TEXT, 3, '0');
    RETURN new_number;
END;
$$ LANGUAGE plpgsql;

-- Function to generate next risk number
CREATE OR REPLACE FUNCTION generate_risk_number()
RETURNS VARCHAR(50) AS $$
DECLARE
    current_year INTEGER;
    next_seq INTEGER;
    new_number VARCHAR(50);
BEGIN
    current_year := EXTRACT(YEAR FROM CURRENT_DATE);

    SELECT COALESCE(MAX(CAST(SUBSTRING(risk_number FROM 11) AS INTEGER)), 0) + 1
    INTO next_seq
    FROM risk_register
    WHERE risk_number LIKE 'RISK-' || current_year || '-%';

    new_number := 'RISK-' || current_year || '-' || LPAD(next_seq::TEXT, 3, '0');
    RETURN new_number;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_audit_program_updated_at BEFORE UPDATE ON audit_program
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_audit_schedule_updated_at BEFORE UPDATE ON audit_schedule
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_audit_findings_updated_at BEFORE UPDATE ON audit_findings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_risk_register_updated_at BEFORE UPDATE ON risk_register
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_compliance_tracking_updated_at BEFORE UPDATE ON compliance_tracking
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
