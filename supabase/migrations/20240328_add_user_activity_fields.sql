-- Add activity tracking fields to users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS last_active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS is_active_in_search BOOLEAN DEFAULT TRUE;

-- Create index for faster queries on last_active_at
CREATE INDEX IF NOT EXISTS idx_users_last_active_at ON users(last_active_at);

-- Create index for faster queries on is_active_in_search
CREATE INDEX IF NOT EXISTS idx_users_is_active_in_search ON users(is_active_in_search);

-- Update existing users to have current timestamp as last_active_at
UPDATE users
SET last_active_at = CURRENT_TIMESTAMP
WHERE last_active_at IS NULL;

-- Add comment to explain the fields
COMMENT ON COLUMN users.last_active_at IS 'Timestamp of the user''s last activity';
COMMENT ON COLUMN users.is_active_in_search IS 'Whether the user is visible in search results'; 