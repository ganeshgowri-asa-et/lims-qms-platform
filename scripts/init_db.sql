-- Initialize LIMS-QMS Database
-- This script runs automatically when the PostgreSQL container is created

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE lims_qms_db TO lims_user;

-- Create schema for versioning (optional)
-- CREATE SCHEMA IF NOT EXISTS version_history;

-- Log
SELECT 'Database initialized successfully' AS status;
