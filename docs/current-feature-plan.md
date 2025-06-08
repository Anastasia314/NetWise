**Title** — Core Application Bootstrap and Database Schema Definition

**Feature description** — This feature transitions the project from a file skeleton to a runnable application. It involves setting up the database connection components, defining the data structure both as Python ORM models and as a manual SQL script, and implementing the bot's main entry point. The feature is considered complete when the bot can be launched and responds to a basic health-check command. This feature explicitly uses a manual SQL script for database setup instead of a migration tool like Alembic.

**Tasks**
- [ ] Implement the configuration loader in `app/config.py` to securely read secrets.
- [ ] Define the SQLAlchemy ORM models (`User`, `Tag`, `UserTag`) in `app/db/models.py`.
- [ ] Create a `schema.sql` file and write the `CREATE TABLE` statements that mirror the ORM models.
- [ ] **(Manual Step)** Execute the contents of `schema.sql` in the Supabase SQL Editor to create the database tables.
- [ ] Implement the main application runner in `bot.py` to initialize and start the bot.
- [ ] Add a simple `/ping` command handler to verify that the bot is running and processing commands.
- [ ] Register the new handler in `bot.py`'s dispatcher.

**Files involved**
*   `requirements.txt` (modified)
*   `app/config.py` (modified)
*   `app/db/models.py` (created)
*   `schema.sql` (created)
*   `bot.py` (modified)
*   `app/handlers/common.py` (created, optional but recommended)

**External dependencies**
*   `sqlalchemy`
*   `asyncpg`

**Notes**
*   This feature is critical as it establishes the connection between the application code and the database.
*   **Crucial:** The developer is responsible for manually executing `schema.sql` on every database instance (local, staging, production).
*   Any future changes to `app/db/models.py` will require a corresponding manual `ALTER TABLE` statement to be written in `schema.sql` and executed on the database. This is the main trade-off for not using Alembic.
*   The `/ping` command serves as a simple, effective "health check" to confirm the bot is online and the core components are wired up correctly before building more complex features.