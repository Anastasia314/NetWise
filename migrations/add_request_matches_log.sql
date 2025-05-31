-- Create request_matches_log table
CREATE TABLE IF NOT EXISTS request_matches_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
    suggested_user_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    introducer_user_id BIGINT REFERENCES users(telegram_id) ON DELETE SET NULL,
    status TEXT NOT NULL CHECK (status IN ('suggested', 'intro_requested', 'helper_accepted', 'helper_declined')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_request_matches_log_request_id ON request_matches_log(request_id);
CREATE INDEX IF NOT EXISTS idx_request_matches_log_suggested_user_id ON request_matches_log(suggested_user_id);
CREATE INDEX IF NOT EXISTS idx_request_matches_log_introducer_user_id ON request_matches_log(introducer_user_id);
CREATE INDEX IF NOT EXISTS idx_request_matches_log_status ON request_matches_log(status);

-- Add RLS policies
ALTER TABLE request_matches_log ENABLE ROW LEVEL SECURITY;

-- Policy for reading matches (users can only see matches related to their requests or where they are the suggested helper)
CREATE POLICY "Users can view their own request matches" ON request_matches_log
    FOR SELECT
    USING (
        request_id IN (
            SELECT id FROM requests WHERE requester_id = auth.uid()
        )
        OR suggested_user_id = auth.uid()
        OR introducer_user_id = auth.uid()
    );

-- Policy for inserting matches (only the system can insert matches)
CREATE POLICY "System can insert matches" ON request_matches_log
    FOR INSERT
    WITH CHECK (true);

-- Policy for updating matches (only the system can update matches)
CREATE POLICY "System can update matches" ON request_matches_log
    FOR UPDATE
    USING (true);

-- Add trigger for updated_at
CREATE TRIGGER set_timestamp
    BEFORE UPDATE ON request_matches_log
    FOR EACH ROW
    EXECUTE FUNCTION handle_updated_at();

-- Add comments
COMMENT ON TABLE request_matches_log IS 'Logs of potential helpers suggested for requests and their responses';
COMMENT ON COLUMN request_matches_log.request_id IS 'The request this match is for';
COMMENT ON COLUMN request_matches_log.suggested_user_id IS 'The user suggested as a potential helper';
COMMENT ON COLUMN request_matches_log.introducer_user_id IS 'The user who can introduce the requester to the helper (for 2nd degree connections)';
COMMENT ON COLUMN request_matches_log.status IS 'Current status of the match (suggested, intro_requested, helper_accepted, helper_declined)'; 