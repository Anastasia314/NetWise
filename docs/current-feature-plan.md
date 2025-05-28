# Current Feature Plan

Title: Configure Linters and Formatters (Ruff & Black)

Feature Description:
This task involves choosing, installing, and configuring code linters and formatters to ensure code quality, consistency, and adherence to style guides across the NetWise project (both backend and bot code). We will use Ruff as an efficient linter (which can also handle some formatting and import sorting) and Black as the primary code formatter. Configuration files will be created to define the rules and settings for these tools.

Tasks:
- [ ] Choose Tools:
    - [x] Confirm Ruff as the linter (for its speed and comprehensive checks, including Flake8, isort, etc.).
    - [x] Confirm Black as the code formatter (for its opinionated, consistent formatting).
- [ ] Install Tools:
    - [ ] Add ruff and black to the project's development dependencies.
        - [ ] If using Poetry: poetry add ruff black --group dev.
        - [ ] If using requirements-dev.txt: Add ruff and black to requirements-dev.txt (and potentially create this file if it doesn't exist).
- [ ] Configure Black:
    - [ ] Create a pyproject.toml file at the root of the project if it doesn't exist (or update it).
    - [ ] Add a [tool.black] section to pyproject.toml to specify any Black configurations (e.g., line-length). For NetWise, we'll start with Black's defaults primarily but set a common line length (e.g., 88 or 100, matching ADD's target of 100 users ~ $100 budget implies larger complexity, maybe 100 or 120 is better, but PRD/ADD code style is not explicitly defined, let's pick 88 as a common Python default to start). Let's aim for line-length = 88 for initial setup.
- [ ] Configure Ruff:
    - [ ] Add a [tool.ruff] section to pyproject.toml.
    - [ ] Specify line-length consistent with Black.
    - [ ] Select a base set of rules to enable (e.g., select = ["E", "F", "W", "I"] - for Pyflakes errors, Flake8 warnings, and isort for import sorting).
    - [ ] Configure any specific rules to ignore if necessary (e.g., ignore = []).
    - [ ] Set up Ruff's import sorting (equivalent to isort). [tool.ruff.isort]
    - [ ] Consider enabling Ruff's formatter if desired, or ensure it doesn't conflict with Black if Black is the primary formatter. (For now, Black will be primary formatter, Ruff for linting and import sorting).
- [ ] Initial Application:
    - [ ] Run Black on the existing codebase (backend and bot) to format files.
    - [ ] Run Ruff on the existing codebase (backend and bot) to identify and (where possible) auto-fix linting issues.
- [ ] Documentation/Instructions:
    - [ ] Briefly document how to run Black and Ruff locally in the project's README.md or a CONTRIBUTING.md.
    - [ ] Recommend VS Code extensions for Ruff and Black for real-time feedback during development.

Files Involved:
*   pyproject.toml (new or modified)
*   poetry.lock and pyproject.toml (if using Poetry, for dependency updates)
*   requirements-dev.txt (if using pip for dev dependencies)
*   Potentially all *.py files in the backend/ and bot/ directories (will be formatted/linted)
*   README.md or CONTRIBUTING.md (for usage instructions)

External Dependencies:
*   ruff (Python package)
*   black (Python package)
*   Poetry or pip (for installing dev dependencies)

Notes:
*   The pyproject.toml file is the standard place for configuring modern Python tools like Black and Ruff.
*   A common line length should be agreed upon. The ADD mentions maintainability and clean code. 88 is a common default for Black.
*   This task focuses on setting up and configuring the tools. The next task will integrate these checks into the CI/CD pipeline.
*   Applying the formatters/linters initially might result in a large number of changed files. This is expected.