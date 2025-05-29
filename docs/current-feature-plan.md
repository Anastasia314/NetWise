## `current-feature-plan.md`

**Title:** Database Schema Expansion (`users` table)

**Feature Description:**
This feature involves expanding the `users` table in the Supabase PostgreSQL database to include all necessary fields for comprehensive user profiles, tracking user activity related to social points and request economy, managing subscription details, and enabling AI matching capabilities. This aligns with the schema defined in the Architectural Design Document (ADD section 4.3) for the `users` table.

**Tasks:**
*   `- [ ] DB: Add `role` (TEXT, NULLABLE) and `industry` (TEXT, NULLABLE) columns to the `users` table.`
*   `- [ ] DB: Add `skills` (TEXT[], NOT NULL, DEFAULT '{}'), `goals` (TEXT[], NOT NULL, DEFAULT '{}'), `interests` (TEXT[], NOT NULL, DEFAULT '{}') columns to the `users` table.`
*   `- [ ] DB: Add `social_points` (INTEGER, NOT NULL, DEFAULT 0) column to the `users` table.`
*   `- [ ] DB: Add `free_requests_remaining` (INTEGER, NOT NULL, DEFAULT 5) column to the `users` table.`
*   `- [ ] DB: Add `subscription_tier` (TEXT, NULLABLE) and `subscription_expires_at` (TIMESTAMPTZ, NULLABLE) columns to the `users` table.`
*   `- [ ] DB: Add `last_active_at` (TIMESTAMPTZ, NULLABLE) and `is_active_in_search` (BOOLEAN, NOT NULL, DEFAULT TRUE) columns to the `users` table.`
*   `- [ ] DB: Enable `pg_vector` extension in Supabase if not already enabled.`
*   `- [ ] DB: Add `profile_embedding` (vector(1536), NULLABLE) column to the `users` table (assuming OpenAI `text-embedding-ada-002` dimensions).`
*   `- [ ] DB: Verify `name` (TEXT) column exists (from Phase 0) and is suitable (e.g., NULLABLE).`
*   `- [ ] DB: Ensure `updated_at` (TIMESTAMPTZ) column is configured to automatically update on row modification (e.g., using a trigger).`

**Files Involved:**
*   SQL migration script(s) (e.g., `supabase/migrations/<timestamp>_expand_users_table.sql`)
*   Potentially Supabase dashboard UI for enabling extensions or quick modifications (changes should be captured in migrations).

**External Dependencies:**
*   Supabase (PostgreSQL)
*   `pg_vector` PostgreSQL extension (for the `profile_embedding` field)

**Notes:**
*   The `telegram_id` (PK, BigInt, unique) and `created_at` (TIMESTAMPTZ, default now()) columns are assumed to have been created correctly during Phase 0.
*   The `name` column was likely created in Phase 0; this task includes verifying its existence and type.
*   The `profile_embedding` field is for future AI matching capabilities. The vector dimension (e.g., 1536) should match the chosen embedding model.
*   Default values for `social_points` and `free_requests_remaining` are based on PRD.
*   `TIMESTAMPTZ` (timestamp with time zone) is generally preferred for timestamp fields.
*   An `updated_at` trigger is a common pattern:
    ```sql
    CREATE OR REPLACE FUNCTION public.handle_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
      NEW.updated_at = NOW();
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER on_users_updated
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();
    ```
    This trigger would need to be created if not already present from Supabase defaults for the `users` table.

---