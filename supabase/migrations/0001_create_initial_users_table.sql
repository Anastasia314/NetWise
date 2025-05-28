-- Create the users table
CREATE TABLE public.users (
    telegram_id BIGINT PRIMARY KEY,
    name TEXT,
    telegram_username TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create a trigger to automatically update the updated_at column
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Add a comment to the table
COMMENT ON TABLE public.users IS 'Stores user information for NetWise application';

-- Add comments to columns
COMMENT ON COLUMN public.users.telegram_id IS 'User''s unique Telegram ID';
COMMENT ON COLUMN public.users.name IS 'User''s display name';
COMMENT ON COLUMN public.users.telegram_username IS 'User''s Telegram username';
COMMENT ON COLUMN public.users.created_at IS 'Timestamp when the user was created';
COMMENT ON COLUMN public.users.updated_at IS 'Timestamp when the user was last updated'; 