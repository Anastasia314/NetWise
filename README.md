# NetWise

A modern Python-based project combining FastAPI and Telegram bot capabilities.

## Project Structure

```
NetWise/
├── app/           # FastAPI application
├── bot/           # Telegram bot implementation
├── tests/         # Test suite
├── scripts/       # Utility scripts
└── .github/       # GitHub workflows and configurations
```

## Tech Stack

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
- **Pydantic**: Data validation and settings management
- **Aiogram**: Modern Telegram bot framework
- **HTTPX**: Modern HTTP client
- **Python-dotenv**: Environment variable management

## Setup

1. Clone the repository
2. Install Poetry (if not already installed)
3. Install dependencies:
   ```bash
   poetry install
   ```
4. Copy `.env.example` to `.env` and configure your environment variables
5. Run the application:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

## Development

This project uses Poetry for dependency management. Make sure to:
- Add new dependencies using `poetry add <package-name>`
- Update the lock file with `poetry lock`
- Keep the `pyproject.toml` file up to date

## License

[License information to be added]