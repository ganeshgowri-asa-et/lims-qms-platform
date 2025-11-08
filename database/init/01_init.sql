-- Database initialization script for LIMS-QMS Platform
-- This script runs automatically when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set timezone
SET timezone = 'UTC';

-- Create initial schema comment
COMMENT ON DATABASE lims_qms_db IS 'LIMS-QMS Platform Database - Laboratory Information Management System & Quality Management System';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE lims_qms_db TO lims_user;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'LIMS-QMS Database initialized successfully!';
END $$;
