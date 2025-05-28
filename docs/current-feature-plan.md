# **Current Feature Plan: Supabase Project Setup and Initial `users` Table**

**Feature description:**
Initialize the Supabase project, configure environment variables for the application to connect to Supabase, and set up the initial `users` table schema including basic Row Level Security. This establishes the foundational data storage for user information in NetWise.

**Tasks:**

*   `- [ ]` **(Manual Action)** Create a new project on the Supabase platform (supabase.com).
*   `- [ ]` **(Manual Action)** Securely note the Supabase Project URL, `anon` key, and `service_role` key provided after project creation.
*   `- [ ]` **Commit 1:** Add Supabase URL and Key placeholders to `.env.example`.
    *   Description: Update the `.env.example` file to include `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY` as placeholders for other developers.
*   `- [ ]` **(Local Setup)** Populate the local `.env` file with the actual Supabase credentials obtained in the manual step. This file should be in `.gitignore`.
*   `- [ ]` **Commit 2:** Create SQL migration script for the initial `users` table schema.
    *   Description: Define the DDL for the `users` table.
    *   Table: `users`
    *   Columns:
        *   `telegram_id` (BIGINT, PRIMARY KEY, UNIQUE NOT NULL) - User's unique Telegram ID.
        *   `name` (TEXT, NULLABLE) - User's display name, to be provided during profile setup.
        *   `telegram_username` (TEXT, NULLABLE) - User's Telegram username, can be captured.
        *   `created_at` (TIMESTAMPTZ, NOT NULL, DEFAULT `now()`) - Timestamp of user creation.
        *   `updated_at` (TIMESTAMPTZ, NOT NULL, DEFAULT `now()`) - Timestamp of last user profile update.
    *   Include a trigger function and trigger to automatically update the `updated_at` column on any row modification.
*   `- [ ]` **(Manual/CLI Action)** Apply the `users` table migration script to the Supabase project using the Supabase SQL editor or Supabase CLI.
*   `- [ ]` **Commit 3:** Create SQL migration script for basic Row Level Security (RLS) on the `users` table.
    *   Description: Define RLS policies to control data access.
    *   Enable RLS on the `users` table.
    *   Policy 1: Allow authenticated users to `SELECT` their own record based on `auth.uid()` matching `telegram_id` (if using Supabase Auth) or a custom function checking `telegram_id`. For MVP with bot-driven interaction, using `service_role` key from backend might mean RLS for select/update is primarily to prevent users from accessing each other's data if they somehow got direct DB access with a user-specific role, or if Supabase Auth is used later. For now, policies can be based on `auth.jwt() ->> 'sub'` if we assume Telegram ID will be in the JWT, or more generically, a policy that checks a session variable set by the backend.
    *   Let's simplify for MVP: Backend uses service_role. RLS primarily for direct Supabase API access if `anon` key is used by clients. For bot, service_role bypasses RLS. But for good practice, let's assume policies for authenticated users.
        *   Policy: "Users can view their own profile." (`SELECT` for `auth.uid() = telegram_id` -- this implies `telegram_id` needs to be set as `auth.uid()` or linked, which might be complex if not using Supabase GoTrue for Telegram login directly. A simpler RLS for now if backend always uses service_role could be to defer RLS to when TWA/Mobile app uses anon key with user JWTs. Or, for now, "Allow read access to all authenticated users" if user profiles are meant to be somewhat public within the app, and "Allow update access to owning user".
        *   Given the architecture (bot -> backend API -> Supabase with service_role), RLS primarily serves as a defense-in-depth or for future direct client (TWA/Mobile App) access with user-scoped JWTs.
        *   Let's define basic policies:
            *   Users can select their own data: `USING (auth.uid()::bigint = telegram_id)` (This assumes `telegram_id` is stored as string in `auth.uid()` or can be cast. Or use a helper function). Or, if not using Supabase Auth for bot users initially: `USING (true)` for select if profiles are generally viewable by any logged-in user via the API, and specific restrictions handled by API logic. For ADD: "Users can only modify their own profiles". This implies select might be broader for matching.
            *   Let's use:
                *   Policy for `SELECT`: "Enable read access for authenticated users" - `USING (auth.role() = 'authenticated')`.
                *   Policy for `UPDATE`: "Users can update their own profile." - `USING (auth.uid()::text = telegram_id::text) WITH CHECK (auth.uid()::text = telegram_id::text)` (Assuming `telegram_id` will be passed as `uid` in JWTs later). *Correction: For MVP, backend uses service key. So RLS for bot interaction is less critical. But for future TWA/Mobile this is key.*
                *   A simpler starting RLS given the current setup:
                    *   Enable RLS: `ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;`
                    *   Policy for `SELECT` (allow backend to read all with service key, no specific user policy yet for general select): `CREATE POLICY "Allow service role full access" ON public.users FOR ALL USING (true) WITH CHECK (true);` -- This isn't quite right. Service role bypasses RLS. RLS is for non-service roles.
                    *   Let's target the ADD: "users can only see/edit their own data."
                    *   Policy for `SELECT`: `CREATE POLICY "Users can select their own data." ON public.users FOR SELECT USING (auth.uid()::bigint = telegram_id);`
                    *   Policy for `UPDATE`: `CREATE POLICY "Users can update their own data." ON public.users FOR UPDATE USING (auth.uid()::bigint = telegram_id) WITH CHECK (auth.uid()::bigint = telegram_id);`
                    *   Policy for `INSERT` (if users were to insert themselves with anon key + RLS): `CREATE POLICY "Users can insert their own data." ON public.users FOR INSERT WITH CHECK (auth.uid()::bigint = telegram_id);`
                    *   (Note: `auth.uid()` returns UUID. If `telegram_id` is `BIGINT`, direct comparison won't work. Need to ensure `telegram_id` is in JWT claim and extract, e.g., `auth.jwt()->>'user_telegram_id')::bigint = telegram_id`. For MVP and simplicity, assume the backend API handles authorization and uses the service_role key, making these RLS policies for future client-side auth with Supabase.) For now, we can define them for `anon` and `authenticated` roles and note that the backend (service_role) bypasses them.
                    *   Final RLS approach for this task: Enable RLS. Backend uses service role. For any calls using `anon` or user-specific JWTs (future), they should only be able to operate on their own data.
*   `- [ ]` **(Manual/CLI Action)** Apply the RLS migration script to the `users` table in the Supabase project.

**Files involved:**
*   `.env.example` (modified)
*   `supabase/migrations/0001_create_initial_users_table.sql` (new file)
*   `supabase/migrations/0002_setup_users_rls.sql` (new file)
*   `(Local only, not committed: .env)`

**External dependencies:**
*   None for these specific code/commit tasks (Supabase account and project are an external setup requirement).

**Notes:**
*   The `supabase/migrations/` directory will store SQL DDL and DML changes. This is a common convention and aligns with how Supabase CLI handles migrations.
*   Actual Supabase credentials (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`) must **never** be committed to the repository. They are stored locally in `.env` (which is gitignored) and in production environment variables.
*   The `users` table includes only core fields for this initial setup, as per the "Phase 0" plan. More fields will be added in "Phase 1".
*   The `updated_at` trigger function ensures this timestamp is automatically managed by the database.
*   RLS policies are defined with the assumption that future client applications (Telegram Mini App, Mobile App) might interact with Supabase using user-specific JWTs. For the MVP backend (Python/FastAPI) using the `service_role` key, RLS policies are bypassed, but API logic must enforce authorization. Setting up RLS now is good practice.
*   The exact RLS policies (`auth.uid()`, `auth.jwt()`) depend on how user authentication and JWTs will be structured when/if not using the service role. The provided policies are common starting points.