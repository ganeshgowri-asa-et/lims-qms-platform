-- LIMS-QMS Platform Database Initialization
-- This script creates the base tables and audit trail functionality

-- Enable UUID extension (useful for future features)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL,
    user_id INTEGER REFERENCES users(user_id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    old_values JSONB,
    new_values JSONB
);

-- Create indexes for audit_log table
CREATE INDEX IF NOT EXISTS idx_audit_log_table_name ON audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_record_id ON audit_log(record_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);

-- Audit trail trigger function
-- This function can be attached to any table to automatically log changes
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    audit_user_id INTEGER;
BEGIN
    -- Try to get user_id from current setting (can be set by application)
    BEGIN
        audit_user_id := current_setting('app.current_user_id')::INTEGER;
    EXCEPTION
        WHEN OTHERS THEN
            audit_user_id := NULL;
    END;

    IF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_log (
            table_name,
            record_id,
            action,
            user_id,
            old_values,
            new_values
        ) VALUES (
            TG_TABLE_NAME,
            OLD.user_id,  -- Assumes table has a primary key column, adjust as needed
            'DELETE',
            audit_user_id,
            row_to_json(OLD),
            NULL
        );
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit_log (
            table_name,
            record_id,
            action,
            user_id,
            old_values,
            new_values
        ) VALUES (
            TG_TABLE_NAME,
            NEW.user_id,  -- Assumes table has a primary key column, adjust as needed
            'UPDATE',
            audit_user_id,
            row_to_json(OLD),
            row_to_json(NEW)
        );
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_log (
            table_name,
            record_id,
            action,
            user_id,
            old_values,
            new_values
        ) VALUES (
            TG_TABLE_NAME,
            NEW.user_id,  -- Assumes table has a primary key column, adjust as needed
            'INSERT',
            audit_user_id,
            NULL,
            row_to_json(NEW)
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Example: Apply audit trigger to users table
CREATE TRIGGER users_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Create a default admin user (password: admin123 - CHANGE IN PRODUCTION!)
-- Password hash for 'admin123' using bcrypt
INSERT INTO users (username, email, password_hash, full_name, role, is_active)
VALUES (
    'admin',
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqZQwkQ5JO',  -- admin123
    'System Administrator',
    'admin',
    TRUE
) ON CONFLICT (username) DO NOTHING;

-- Grant necessary permissions (adjust as needed for your environment)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO lims_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO lims_user;
