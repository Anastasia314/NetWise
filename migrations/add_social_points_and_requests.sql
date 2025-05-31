-- Create index for social points
CREATE INDEX idx_users_social_points ON users(social_points);

-- Add constraint for social points
ALTER TABLE users
ADD CONSTRAINT check_social_points_non_negative CHECK (social_points >= 0);

-- Add constraint for free requests
ALTER TABLE users
ADD CONSTRAINT check_free_requests_non_negative CHECK (free_requests_remaining >= 0);

-- Add comments
COMMENT ON COLUMN users.social_points IS 'Number of social points earned by helping others';
COMMENT ON COLUMN users.free_requests_remaining IS 'Number of free requests remaining for the current month'; 