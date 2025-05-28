# **Current Feature Plan 1**

**Title:** Create Basic Dockerfile for Backend API

**Feature Description:**
This task involves creating the initial `Dockerfile` for the NetWise backend API (FastAPI application). This `Dockerfile` will define the environment for building a container image of the backend, specifying the base Python image, dependencies, application code, and the command to run the application. This is a foundational step for enabling consistent deployments and integrating with CI/CD pipelines on platforms like Railway.

**Tasks:**
- [ ] Create the `Dockerfile` within the backend service directory (e.g., `backend/Dockerfile`).
- [ ] Select an appropriate official Python base image (e.g., `python:3.11-slim-bullseye`).
- [ ] Set the working directory inside the container (e.g., `WORKDIR /app`).
- [ ] Copy the dependency definition file (`requirements.txt` or `pyproject.toml` and `poetry.lock`) into the container.
- [ ] Add commands to install Python dependencies (e.g., using `pip install -r requirements.txt` or `poetry install`).
- [ ] Copy the backend application code (e.g., the `app` directory containing `main.py`, etc.) into the container.
- [ ] Expose the port the FastAPI application will run on (e.g., `EXPOSE 8000`).
- [ ] Define the default command (`CMD`) to run the application using Uvicorn (e.g., `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`).

**Files Involved:**
*   `backend/Dockerfile` (new file)
*   `backend/requirements.txt` (or `backend/pyproject.toml` and `backend/poetry.lock`) - *existing, but referenced by the Dockerfile*
*   `backend/app/` (directory containing application code) - *existing, but referenced by the Dockerfile*

**External Dependencies:**
*   Docker (for building and testing the Dockerfile locally)
*   Python base image from Docker Hub (e.g., `python:3.11-slim`)
*   Uvicorn (expected to be listed in `requirements.txt` or `pyproject.toml`)

**Notes:**
*   Ensure the Python version specified in the `Dockerfile` matches the version used during development (as per project setup in Phase 0).
*   The `requirements.txt` (or `pyproject.toml`) should be current and include all backend dependencies.
*   This basic `Dockerfile` can be optimized later (e.g., with multi-stage builds to reduce image size or improve build times) if needed.
*   Environment variables required by the application at runtime (e.g., database connection strings, API keys) should not be hardcoded in the `Dockerfile`. They will be injected by the hosting environment (Railway).
*   Consider adding `ENV PYTHONUNBUFFERED=1` for better logging in containerized environments.


# **Current Feature Plan 2**

**Title:** Create Basic Dockerfile for Telegram Bot

**Feature Description:**
This task involves creating the initial `Dockerfile` for the NetWise Telegram Bot (aiogram application). This `Dockerfile` will define the environment for building a container image of the bot, specifying the base Python image, dependencies, bot code, and the command to run the bot. This is a crucial step for enabling consistent deployments and integrating with CI/CD pipelines on platforms like Railway, allowing the bot to run as a separate service.

**Tasks:**
- [ ] Create the `Dockerfile` within the bot service directory (e.g., `bot/Dockerfile`).
- [ ] Select an appropriate official Python base image (e.g., `python:3.11-slim-bullseye`, consistent with the backend).
- [ ] Set the working directory inside the container (e.g., `WORKDIR /app`).
- [ ] Copy the dependency definition file for the bot (e.g., `bot/requirements.txt` or `bot/pyproject.toml` and `bot/poetry.lock`) into the container.
- [ ] Add commands to install Python dependencies for the bot (e.g., using `pip install -r requirements.txt` or `poetry install`).
- [ ] Copy the bot application code (e.g., the `bot` directory containing `main.py`, `handlers/`, `services/`, etc.) into the container.
- [ ] Define the default command (`CMD`) to run the bot application (e.g., `CMD ["python", "bot/main.py"]`).

**Files Involved:**
*   `bot/Dockerfile` (new file)
*   `bot/requirements.txt` (or `bot/pyproject.toml` and `bot/poetry.lock`) - *existing, but referenced by the Dockerfile*
*   `bot/` (directory containing bot application code, e.g., `main.py`) - *existing, but referenced by the Dockerfile*

**External Dependencies:**
*   Docker (for building and testing the Dockerfile locally)
*   Python base image from Docker Hub (e.g., `python:3.11-slim`)
*   aiogram and other bot-specific dependencies (expected to be listed in `bot/requirements.txt` or `bot/pyproject.toml`)

**Notes:**
*   Ensure the Python version specified in the `Dockerfile` matches the version used during development and is consistent with the backend API's Python version.
*   The bot's `requirements.txt` (or `pyproject.toml`) should be current and include all necessary dependencies.
*   This basic `Dockerfile` can be optimized later if needed (e.g., with multi-stage builds).
*   Environment variables required by the bot at runtime (e.g., `BOT_TOKEN`, backend API URL) should not be hardcoded in the `Dockerfile`. They will be injected by the hosting environment (Railway).
*   Consider adding `ENV PYTHONUNBUFFERED=1` for better logging in containerized environments.
*   The bot's Dockerfile might be simpler than the backend's, as it doesn't expose a port like a web server but rather runs a persistent Python script.


# **Current Feature Plan 3**

**Title:** Create Initial GitHub Actions CI Workflow for Backend

**Feature Description:**
This task involves creating the initial GitHub Actions workflow file (`.github/workflows/ci_cd.yml` or a more specific name like `backend-ci.yml`) for the NetWise backend API. This workflow will automate the process of checking out code, setting up the Python environment, and installing dependencies whenever changes are pushed to the `main` branch. It will also include placeholders for future testing and linting steps. This is a foundational step for establishing a CI/CD pipeline.

**Tasks:**
- [ ] Create the directory structure `.github/workflows/` if it doesn't exist.
- [ ] Create a new YAML file (e.g., `backend-ci.yml`) within `.github/workflows/`.
- [ ] Define the workflow name (e.g., `Backend CI`).
- [ ] Configure the workflow to trigger on pushes to the `main` branch.
- [ ] Define a job (e.g., `build-and-test`) that runs on a Linux environment (e.g., `ubuntu-latest`).
- [ ] Add a step to check out the repository's code using `actions/checkout@v3` (or a newer version).
- [ ] Add a step to set up a specific Python version (e.g., 3.11) using `actions/setup-python@v4` (or a newer version).
    - [ ] Specify the Python version consistent with development and Dockerfile.
- [ ] Add a step to install backend dependencies.
    - [ ] If using `requirements.txt`: Cache dependencies, then `pip install -r backend/requirements.txt`.
    - [ ] If using Poetry: Cache dependencies, install Poetry, then `poetry install --no-dev` (or similar, in the `backend` directory).
    - [ ] Ensure this step correctly targets the backend's dependency file (e.g., specify working directory or path).
- [ ] Add placeholder steps for running linters and tests (e.g., a simple echo command or a commented-out section).

**Files Involved:**
*   `.github/workflows/backend-ci.yml` (new file, or similar name like `ci_cd.yml`)
*   `backend/requirements.txt` (or `backend/pyproject.toml` and `backend/poetry.lock`) - *existing, referenced by the workflow*

**External Dependencies:**
*   GitHub Actions platform.
*   `actions/checkout` GitHub Action.
*   `actions/setup-python` GitHub Action.
*   `actions/cache` GitHub Action (recommended for dependencies).
*   Python package manager (pip or Poetry) assumed to be available after Python setup.

**Notes:**
*   This initial workflow focuses on setting up the environment and installing dependencies. The actual deployment to Railway will be added in a subsequent step or task.
*   Ensure the paths to dependency files (e.g., `backend/requirements.txt`) are correct relative to the repository root.
*   If using Poetry, the installation of Poetry itself needs to be part of the workflow.
*   This workflow will initially run on every push to `main`. Branch protection rules and pull request triggers can be configured later.
*   The placeholder for tests and linters should be clearly marked for future implementation.


# **Current Feature Plan 4**

**Title:** Create Initial GitHub Actions CI Workflow for Telegram Bot

**Feature Description:**
This task involves creating an initial GitHub Actions workflow file (e.g., `bot-ci.yml`) for the NetWise Telegram Bot. Similar to the backend CI workflow, this will automate checking out code, setting up the Python environment, and installing dependencies for the bot whenever changes are pushed to the `main` branch. It will also include placeholders for future testing and linting steps. This establishes the CI foundation for the bot service.

**Tasks:**
- [ ] Create a new YAML file (e.g., `bot-ci.yml`) within the `.github/workflows/` directory.
- [ ] Define the workflow name (e.g., `Bot CI`).
- [ ] Configure the workflow to trigger on pushes to the `main` branch.
    - [ ] Consider path filters if bot code resides in a specific directory (e.g., `bot/**`) to avoid running unnecessarily.
- [ ] Define a job (e.g., `build-and-test-bot`) that runs on a Linux environment (e.g., `ubuntu-latest`).
- [ ] Add a step to check out the repository's code using `actions/checkout@v3` (or a newer version).
- [ ] Add a step to set up a specific Python version (e.g., 3.11) using `actions/setup-python@v4` (or a newer version), consistent with the bot's development environment and Dockerfile.
- [ ] Add a step to install bot dependencies.
    - [ ] If using `requirements.txt`: Cache dependencies, then `pip install -r bot/requirements.txt`.
    - [ ] If using Poetry: Cache dependencies, install Poetry, then `poetry install --no-dev` (or similar, in the `bot` directory).
    - [ ] Ensure this step correctly targets the bot's dependency file (e.g., specify working directory or path).
- [ ] Add placeholder steps for running linters and tests for the bot (e.g., a simple echo command or a commented-out section).

**Files Involved:**
*   `.github/workflows/bot-ci.yml` (new file)
*   `bot/requirements.txt` (or `bot/pyproject.toml` and `bot/poetry.lock`) - *existing, referenced by the workflow*

**External Dependencies:**
*   GitHub Actions platform.
*   `actions/checkout` GitHub Action.
*   `actions/setup-python` GitHub Action.
*   `actions/cache` GitHub Action (recommended for dependencies).
*   Python package manager (pip or Poetry) assumed to be available after Python setup.

**Notes:**
*   This workflow mirrors the backend CI workflow but is specific to the bot's codebase and dependencies.
*   The actual deployment of the bot to Railway will be added in a subsequent step or as part of enhancing this workflow.
*   Ensure paths to bot-specific files (e.g., `bot/requirements.txt`) are correct.
*   If the bot and backend share some common libraries managed at the root level, dependency installation might need adjustments, but typically they'll have their own specific dependencies.
*   This workflow will initially run on every push to `main`. Further refinement with path filters or pull request triggers can be added later.