# **Current Feature Plan: Project Initialization & Environment Setup**

**Feature description:**
This task covers the initial setup of the NetWise project, including version control, directory structure, Python environment initialization with core dependencies, and essential configuration files like `.gitignore` and `.env.example`. This foundational work enables subsequent development phases.

**Tasks:**
- [ ] Commit 1: Initialize local Git repository and add a basic README.
- [ ] Commit 2: Create initial top-level project directory structure.
- [ ] Commit 3: Initialize Poetry and create `pyproject.toml`.
- [ ] Commit 4: Add FastAPI and Uvicorn dependencies.
- [ ] Commit 5: Add Pydantic dependency.
- [ ] Commit 6: Add Aiogram dependency.
- [ ] Commit 7: Add HTTPX dependency.
- [ ] Commit 8: Add python-dotenv dependency.
- [ ] Commit 9: Add Python .gitignore file.
- [ ] Commit 10: Create `.env.example` with initial placeholder variables.

**Files involved:**
*   `README.md` (Created/Modified)
*   `app/` (Created)
*   `bot/` (Created)
*   `tests/` (Created)
*   `scripts/` (Created)
*   `.github/workflows/` (Created)
*   `app/.gitkeep` (Created, example for empty dir)
*   `bot/.gitkeep` (Created, example for empty dir)
*   `tests/.gitkeep` (Created, example for empty dir)
*   `scripts/.gitkeep` (Created, example for empty dir)
*   `.github/workflows/.gitkeep` (Created, example for empty dir)
*   `pyproject.toml` (Created/Modified)
*   `poetry.lock` (Created/Modified)
*   `.gitignore` (Created)
*   `.env.example` (Created)

**External dependencies:**
*   `fastapi`
*   `uvicorn[standard]`
*   `pydantic`
*   `aiogram`
*   `httpx`
*   `python-dotenv`

**Notes:**
*   An external step is to create the remote Git repository on a platform like GitHub before starting local work.
*   The `.env` file itself is for local development secrets and should *not* be committed to the repository (it should be listed in `.gitignore`).
*   Using `.gitkeep` files is a common practice to ensure empty directories are tracked by Git initially. These can be removed once files are added to these directories.
*   This plan assumes the use of Poetry for dependency management. If using `pip` and `requirements.txt`, the steps for dependency addition would differ slightly.