# **Current Feature Plan: Basic Telegram Bot Setup (aiogram)**

**Feature description:**
This feature establishes the foundational structure for the NetWise Telegram bot using the `aiogram` library. It includes initializing the bot dispatcher, loading the bot token securely from environment variables, and implementing a basic `/start` command handler to confirm the bot is operational and responsive.

**Tasks:**
- [ ] `feat(bot): Initialize aiogram Bot and Dispatcher structure in bot/main.py`
    - [ ] Create `bot/main.py`.
    - [ ] Add imports for `aiogram.Bot`, `aiogram.Dispatcher`, `aiogram.types`, `asyncio`.
    - [ ] Initialize `Dispatcher` instance.
    - [ ] Implement basic `async def main():` function to initialize `Bot` (with a placeholder token for now) and start polling using `dp.start_polling(bot)`.
    - [ ] Add `if __name__ == '__main__': asyncio.run(main())`.
    - [ ] Add `aiogram` to project dependencies.
- [ ] `feat(bot): Load Telegram Bot Token from environment variables`
    - [ ] Create `bot/core/config.py`.
    - [ ] Implement settings loading for `TELEGRAM_BOT_TOKEN` (e.g., using `os.getenv` or `pydantic-settings` with `python-dotenv`).
    - [ ] Update `bot/main.py` to import and use `TELEGRAM_BOT_TOKEN` from `bot.core.config` for `Bot` initialization.
    - [ ] Add `TELEGRAM_BOT_TOKEN=""` to `.env.example`.
    - [ ] Add `python-dotenv` (and `pydantic-settings` if used) to project dependencies.
- [ ] `feat(bot): Implement basic /start command handler`
    - [ ] Create `bot/handlers/common_handlers.py`.
    - [ ] Import `aiogram.types` and `aiogram.filters.CommandStart`.
    - [ ] Define `async def handle_start(message: types.Message):` that replies with a welcome message (e.g., `await message.answer("Welcome to NetWise!")`).
    - [ ] In `bot/main.py`, import `handle_start` and `CommandStart`.
    - [ ] Register the handler in `main()`: `dp.message.register(handle_start, CommandStart())`.
- [ ] `test(bot): Verify bot starts and responds to /start command`
    - [ ] Locally run the bot.
    - [ ] Send `/start` command to the bot in Telegram and verify the welcome message is received.

**Files involved:**
*   `bot/main.py` (new/modified)
*   `bot/core/config.py` (new)
*   `bot/handlers/common_handlers.py` (new)
*   `.env.example` (modified)
*   `.env` (modified by user locally)
*   `pyproject.toml` or `requirements.txt` (modified for new dependencies)

**External dependencies:**
*   `aiogram`
*   `python-dotenv`
*   `pydantic-settings` (optional, if chosen for settings management)

**Notes:**
*   A `TELEGRAM_BOT_TOKEN` must be obtained from BotFather on Telegram and added to the local `.env` file for testing.
*   This setup uses polling for simplicity in MVP. Webhooks can be considered later for production scalability.
*   Ensure the `bot` directory is created at the root of the project.