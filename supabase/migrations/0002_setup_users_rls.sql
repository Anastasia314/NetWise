-- Enable Row Level Security on the users table
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Create a function to extract telegram_id from JWT claims
CREATE OR REPLACE FUNCTION public.get_telegram_id_from_jwt()
RETURNS BIGINT AS $$
BEGIN
    RETURN (auth.jwt()->>'telegram_id')::BIGINT;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Policy for SELECT: Users can only view their own data
CREATE POLICY "Users can select their own data"
ON public.users
FOR SELECT
USING (get_telegram_id_from_jwt() = telegram_id);

-- Policy for UPDATE: Users can only update their own data
CREATE POLICY "Users can update their own data"
ON public.users
FOR UPDATE
USING (get_telegram_id_from_jwt() = telegram_id)
WITH CHECK (get_telegram_id_from_jwt() = telegram_id);

-- Policy for INSERT: Users can only insert their own data
CREATE POLICY "Users can insert their own data"
ON public.users
FOR INSERT
WITH CHECK (get_telegram_id_from_jwt() = telegram_id);

-- Add comments for documentation
COMMENT ON FUNCTION public.get_telegram_id_from_jwt() IS 'Helper function to extract telegram_id from JWT claims for RLS policies';
COMMENT ON POLICY "Users can select their own data" ON public.users IS 'Allows users to only view their own profile data';
COMMENT ON POLICY "Users can update their own data" ON public.users IS 'Allows users to only update their own profile data';
COMMENT ON POLICY "Users can insert their own data" ON public.users IS 'Allows users to only insert their own profile data'; 