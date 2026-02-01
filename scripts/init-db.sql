-- Database Initialization Script
-- This script runs automatically when the PostgreSQL container is first created

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE job_automation TO postgres;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Database job_automation initialized successfully';
END $$;
