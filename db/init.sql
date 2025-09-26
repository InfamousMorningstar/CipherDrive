-- CipherDrive Database Initialization Script-- Create the database if it doesn't exist

-- This script sets up the initial database, user, and basic configurationCREATE DATABASE IF NOT EXISTS dropboxlite;



-- Create database if it doesn't exist (handled by PostgreSQL container)-- Use the database

-- CREATE DATABASE IF NOT EXISTS cipherdrive_db;\c dropboxlite;



-- Ensure proper character encoding-- Enable UUID extension

SET CLIENT_ENCODING TO 'UTF8';CREATE EXTENSION IF NOT EXISTS "uuid-ossp";



-- Create extensions for additional functionality-- Create users table

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";CREATE TABLE IF NOT EXISTS users (

CREATE EXTENSION IF NOT EXISTS "pgcrypto";    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    email VARCHAR(255) UNIQUE NOT NULL,

-- Create custom types/enums (these will also be created by Alembic migrations)    username VARCHAR(100) UNIQUE NOT NULL,

-- But we create them here for completeness    password_hash VARCHAR(255) NOT NULL,

DO $$    is_active BOOLEAN DEFAULT TRUE,

BEGIN    is_admin BOOLEAN DEFAULT FALSE,

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN    quota_gb INTEGER DEFAULT 5,

        CREATE TYPE userrole AS ENUM ('admin', 'user', 'cipher');    used_storage_bytes BIGINT DEFAULT 0,

    END IF;    must_change_password BOOLEAN DEFAULT TRUE,

END$$;    two_factor_enabled BOOLEAN DEFAULT FALSE,

    two_factor_secret VARCHAR(32),

DO $$    last_login TIMESTAMP,

BEGIN    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sharestatus') THEN    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        CREATE TYPE sharestatus AS ENUM ('active', 'expired', 'disabled'););

    END IF;

END$$;-- Create password reset tokens table

CREATE TABLE IF NOT EXISTS password_reset_tokens (

-- Grant permissions on types    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

GRANT USAGE ON TYPE userrole TO cipherdrive_user;    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

GRANT USAGE ON TYPE sharestatus TO cipherdrive_user;    token VARCHAR(255) NOT NULL,

    expires_at TIMESTAMP NOT NULL,

-- Create indexes for better performance (additional to what Alembic creates)    used BOOLEAN DEFAULT FALSE,

-- These will be created if tables exist    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- Function to create indexes safely

CREATE OR REPLACE FUNCTION create_index_if_not_exists(index_name TEXT, table_name TEXT, column_spec TEXT)-- Create files table

RETURNS VOID AS $$CREATE TABLE IF NOT EXISTS files (

BEGIN    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = index_name) THEN    filename VARCHAR(255) NOT NULL,

        EXECUTE 'CREATE INDEX ' || index_name || ' ON ' || table_name || ' (' || column_spec || ')';    original_filename VARCHAR(255) NOT NULL,

    END IF;    file_path VARCHAR(500) NOT NULL,

END    file_size BIGINT NOT NULL,

$$ LANGUAGE plpgsql;    mime_type VARCHAR(100),

    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

-- Performance indexes (will be created after Alembic migrations)    parent_folder_id UUID REFERENCES files(id) ON DELETE CASCADE,

DO $$    is_folder BOOLEAN DEFAULT FALSE,

BEGIN    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- User table indexes    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    PERFORM create_index_if_not_exists('idx_users_email_active', 'users', 'email WHERE is_active = true'););

    PERFORM create_index_if_not_exists('idx_users_username_active', 'users', 'username WHERE is_active = true');

    PERFORM create_index_if_not_exists('idx_users_role', 'users', 'role');-- Create shared links table

    PERFORM create_index_if_not_exists('idx_users_created_at', 'users', 'created_at DESC');CREATE TABLE IF NOT EXISTS shared_links (

        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- File metadata indexes    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,

    PERFORM create_index_if_not_exists('idx_file_metadata_owner', 'file_metadata', 'owner_id');    share_token VARCHAR(255) UNIQUE NOT NULL,

    PERFORM create_index_if_not_exists('idx_file_metadata_path', 'file_metadata', 'file_path');    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    PERFORM create_index_if_not_exists('idx_file_metadata_created', 'file_metadata', 'created_at DESC');    expires_at TIMESTAMP,

    PERFORM create_index_if_not_exists('idx_file_metadata_size', 'file_metadata', 'file_size');    max_downloads INTEGER,

    PERFORM create_index_if_not_exists('idx_file_metadata_type', 'file_metadata', 'mime_type');    current_downloads INTEGER DEFAULT 0,

        is_active BOOLEAN DEFAULT TRUE,

    -- Share table indexes    password_hash VARCHAR(255),

    PERFORM create_index_if_not_exists('idx_shares_token', 'shares', 'share_token');    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    PERFORM create_index_if_not_exists('idx_shares_creator', 'shares', 'created_by_id'););

    PERFORM create_index_if_not_exists('idx_shares_file', 'shares', 'file_id');

    PERFORM create_index_if_not_exists('idx_shares_expires', 'shares', 'expires_at');-- Create audit logs table

    PERFORM create_index_if_not_exists('idx_shares_status_active', 'shares', 'status WHERE status = ''active''');CREATE TABLE IF NOT EXISTS audit_logs (

    PERFORM create_index_if_not_exists('idx_shares_created', 'shares', 'created_at DESC');    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

        user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Audit log indexes    action VARCHAR(50) NOT NULL,

    PERFORM create_index_if_not_exists('idx_audit_logs_user', 'audit_logs', 'user_id');    resource_type VARCHAR(50),

    PERFORM create_index_if_not_exists('idx_audit_logs_action', 'audit_logs', 'action');    resource_id UUID,

    PERFORM create_index_if_not_exists('idx_audit_logs_timestamp', 'audit_logs', 'timestamp DESC');    details JSONB,

    PERFORM create_index_if_not_exists('idx_audit_logs_ip', 'audit_logs', 'ip_address');    ip_address INET,

    PERFORM create_index_if_not_exists('idx_audit_logs_resource', 'audit_logs', 'resource_type, resource_id');    user_agent TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    -- User quota indexes);

    PERFORM create_index_if_not_exists('idx_user_quotas_user', 'user_quotas', 'user_id');

    PERFORM create_index_if_not_exists('idx_user_quotas_updated', 'user_quotas', 'last_updated DESC');-- Create thumbnails table

EXCEPTIONCREATE TABLE IF NOT EXISTS thumbnails (

    WHEN undefined_table THEN    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

        -- Tables don't exist yet, skip index creation    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,

        RAISE NOTICE 'Tables not yet created, skipping index creation';    size INTEGER NOT NULL,

END    thumbnail_path VARCHAR(500) NOT NULL,

$$;    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- Drop the helper function

DROP FUNCTION create_index_if_not_exists(TEXT, TEXT, TEXT);-- Create indexes for better performance

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create a function for cleaning up expired shares (housekeeping)CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

CREATE OR REPLACE FUNCTION cleanup_expired_shares()CREATE INDEX IF NOT EXISTS idx_files_owner_id ON files(owner_id);

RETURNS INTEGER AS $$CREATE INDEX IF NOT EXISTS idx_files_parent_folder_id ON files(parent_folder_id);

DECLARECREATE INDEX IF NOT EXISTS idx_shared_links_token ON shared_links(share_token);

    deleted_count INTEGER;CREATE INDEX IF NOT EXISTS idx_shared_links_file_id ON shared_links(file_id);

BEGINCREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);

    -- Update expired sharesCREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

    UPDATE shares CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);

    SET status = 'expired'::sharestatusCREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token);

    WHERE expires_at < NOW() CREATE INDEX IF NOT EXISTS idx_thumbnails_file_id ON thumbnails(file_id);

      AND status = 'active'::sharestatus;

    -- Create trigger to update updated_at column

    GET DIAGNOSTICS deleted_count = ROW_COUNT;CREATE OR REPLACE FUNCTION update_updated_at_column()

    RETURNS TRIGGER AS $$

    RETURN deleted_count;BEGIN

EXCEPTION    NEW.updated_at = CURRENT_TIMESTAMP;

    WHEN undefined_table THEN    RETURN NEW;

        -- Shares table doesn't exist yetEND;

        RETURN 0;$$ language 'plpgsql';

END

$$ LANGUAGE plpgsql;CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users

    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create a function for cleaning up old audit logs

CREATE OR REPLACE FUNCTION cleanup_old_audit_logs(retention_days INTEGER DEFAULT 90)CREATE TRIGGER update_files_updated_at BEFORE UPDATE ON files

RETURNS INTEGER AS $$    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DECLARE

    deleted_count INTEGER;-- Insert default admin user (password will be hashed by the application)

BEGIN-- Default password is 'AdminPassword123!' but user will be forced to change it

    -- Delete old audit logsINSERT INTO users (email, username, password_hash, is_admin, must_change_password)

    DELETE FROM audit_logs VALUES ('admin@example.com', 'admin', '$2b$12$placeholder_hash_will_be_replaced', TRUE, TRUE)

    WHERE timestamp < (NOW() - (retention_days || ' days')::INTERVAL);ON CONFLICT (email) DO NOTHING;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
EXCEPTION
    WHEN undefined_table THEN
        -- Audit logs table doesn't exist yet
        RETURN 0;
END
$$ LANGUAGE plpgsql;

-- Create a function to recalculate user quotas
CREATE OR REPLACE FUNCTION recalculate_user_quotas()
RETURNS TABLE(user_id INTEGER, old_used_bytes BIGINT, new_used_bytes BIGINT) AS $$
BEGIN
    RETURN QUERY
    UPDATE user_quotas 
    SET used_bytes = COALESCE(file_sizes.total_size, 0),
        last_updated = NOW()
    FROM (
        SELECT 
            fm.owner_id,
            SUM(fm.file_size) as total_size
        FROM file_metadata fm
        GROUP BY fm.owner_id
    ) file_sizes
    WHERE user_quotas.user_id = file_sizes.owner_id
    RETURNING user_quotas.user_id, 
              LAG(user_quotas.used_bytes) OVER (ORDER BY user_quotas.user_id) as old_used_bytes,
              user_quotas.used_bytes as new_used_bytes;
EXCEPTION
    WHEN undefined_table THEN
        -- Tables don't exist yet
        RAISE NOTICE 'Tables not yet created, skipping quota recalculation';
        RETURN;
END
$$ LANGUAGE plpgsql;

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION cleanup_expired_shares() TO cipherdrive_user;
GRANT EXECUTE ON FUNCTION cleanup_old_audit_logs(INTEGER) TO cipherdrive_user;
GRANT EXECUTE ON FUNCTION recalculate_user_quotas() TO cipherdrive_user;

-- Create a view for active shares (for easier querying)
-- This will be created after tables exist
DO $$
BEGIN
    -- Try to create the view, ignore if tables don't exist
    EXECUTE '
    CREATE OR REPLACE VIEW active_shares AS
    SELECT 
        s.*,
        u.username as creator_username,
        fm.filename,
        fm.file_size,
        fm.mime_type
    FROM shares s
    JOIN users u ON s.created_by_id = u.id
    JOIN file_metadata fm ON s.file_id = fm.id
    WHERE s.status = ''active''::sharestatus
      AND (s.expires_at IS NULL OR s.expires_at > NOW());
    ';
    
    -- Grant access to the view
    EXECUTE 'GRANT SELECT ON active_shares TO cipherdrive_user';
    
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Tables not yet created, skipping view creation';
END
$$;

-- Database maintenance procedures
-- Function to get database statistics
CREATE OR REPLACE FUNCTION get_database_stats()
RETURNS TABLE(
    table_name TEXT,
    row_count BIGINT,
    table_size TEXT,
    index_size TEXT,
    total_size TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        schemaname||'.'||tablename as table_name,
        n_tup_ins - n_tup_del as row_count,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size,
        pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) as index_size,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size
    FROM pg_stat_user_tables
    WHERE schemaname = 'public'
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
END
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON FUNCTION get_database_stats() TO cipherdrive_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO cipherdrive_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO cipherdrive_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO cipherdrive_user;

-- Log initialization completion
DO $$
BEGIN
    RAISE NOTICE 'CipherDrive database initialization completed successfully';
    RAISE NOTICE 'Database: %', current_database();
    RAISE NOTICE 'User: %', current_user;
    RAISE NOTICE 'Timestamp: %', NOW();
END
$$;