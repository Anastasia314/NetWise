# current-feature-plan.md

**Title:** Basic Backend API Setup (FastAPI)

**Feature Description:**
This feature establishes the foundational structure for the NetWise FastAPI backend application. It includes initializing the FastAPI app, setting up configuration management for environment variables, integrating the Supabase client for database interaction, and creating a basic health check endpoint to verify the application is running. This setup is crucial before any specific business logic or API endpoints are developed.

**Tasks:**
*   `- [x]` **Commit 1: Feat: Initialize basic FastAPI app structure**
    *   Create `app/main.py`.
    *   Instantiate a basic FastAPI application.
*   `- [x]` **Commit 2: Feat: Implement initial configuration loading**
    *   Create `app/core/config.py`.
    *   Define a Pydantic `Settings` class (inheriting from `BaseSettings`) to load basic application settings (e.g., `APP_NAME: str = "NetWise"`).
    *   Update `.env.example` to include `APP_NAME` (or rely on default).
*   `- [x]` **Commit 3: Feat: Add Supabase client setup and configuration**
    *   Add `supabase-py` to project dependencies.
    *   Create `app/db/supabase_client.py` with a function to initialize and return a Supabase client instance.
    *   Update `app/core/config.py` to include and load `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` environment variables.
    *   Update `.env.example` with placeholders for `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`.
*   `- [x]` **Commit 4: Feat: Implement health check endpoint**
    *   Modify `app/main.py` to add a `/health` GET endpoint.
    *   The endpoint should return a simple JSON response, e.g., `{"status": "ok"}`.

**Files Involved:**
*   `app/main.py` (Created then Modified)
*   `app/core/config.py` (Created then Modified)
*   `app/db/supabase_client.py` (Created)
*   `.env.example` (Modified)
*   `pyproject.toml` or `requirements.txt` (Modified for `supabase-py`)
*   (Potentially `app/__init__.py`, `app/core/__init__.py`, `app/db/__init__.py` if they don't exist and are needed for module structure, though Phase 0 implies project structure setup)

**External Dependencies:**
*   `fastapi` (Assumed from Phase 0 "Core Dependencies")
*   `uvicorn` (Assumed from Phase 0 "Core Dependencies")
*   `pydantic` (Assumed from Phase 0 "Core Dependencies")
*   `python-dotenv` (Assumed from Phase 0 "Core Dependencies", Pydantic BaseSettings uses it if available)
*   `supabase-py` (To be added in Commit 3)

**Notes:**
*   This plan assumes that Phase 0 of the `implementationPlan.md` (Project Initialization & Environment Setup) has been completed, meaning the basic project directory structure (`app/`, `app/core/`, `app/db/`) is in place, and core dependencies like `fastapi`, `uvicorn`, `pydantic`, and `python-dotenv` are already part of the project's Python environment.
*   `SUPABASE_SERVICE_KEY` is used as it's more descriptive for backend service role access compared to a generic `SUPABASE_KEY`.
*   Ensure `.env` (local development) is updated with actual Supabase credentials after setting up the Supabase project (as indicated in Phase 0 `Supabase Setup` task).