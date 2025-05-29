-- Enable pg_vector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Add new columns to users table
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS role TEXT,
    ADD COLUMN IF NOT EXISTS industry TEXT,
    ADD COLUMN IF NOT EXISTS skills TEXT[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS goals TEXT[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS interests TEXT[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS social_points INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS free_requests_remaining INTEGER NOT NULL DEFAULT 5,
    ADD COLUMN IF NOT EXISTS subscription_tier TEXT,
    ADD COLUMN IF NOT EXISTS subscription_expires_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS last_active_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS is_active_in_search BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS profile_embedding vector(1536);

-- Verify name column exists and is TEXT type
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name = 'name'
    ) THEN
        ALTER TABLE users ADD COLUMN name TEXT;
    END IF;
END $$;

-- Create or replace the updated_at trigger function
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger if it doesn't exist
DROP TRIGGER IF EXISTS on_users_updated ON users;
CREATE TRIGGER on_users_updated
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at(); 