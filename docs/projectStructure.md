## Project Structure: Networking Bot

This structure is designed for modularity and scalability, using the `aiogram` framework.

```
networking_bot/
├── app/
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── group_onboarding.py    # Handles new users in the group
│   │   ├── profile_creation.py    # Handles the FSM for creating a profile
│   │   ├── profile_management.py  # Handles /myprofile, editing, deleting
│   │   └── search.py              # Handles /search and result pagination
│   │
│   ├── keyboards/
│   │   ├── __init__.py
│   │   └── inline.py              # Functions to generate all inline keyboards
│   │
│   ├── states/
│   │   ├── __init__.py
│   │   └── profile_states.py      # FSM State definitions
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py              # SQLAlchemy ORM models
│   │   └── queries.py             # Functions for all database operations (CRUD)
│   │
│   └── config.py                  # Configuration reader (from .env)
│
├── tests/
│   ├── test_handlers.py
│   └── test_db_queries.py
│
├── .env.example                   # Example for environment variables
├── .gitignore
├── bot.py                         # Main entry point of the application
└── requirements.txt               # Project dependencies
```

---

### File Content Details

#### `bot.py` (Main Entry Point)
*   **Purpose:** Initializes and launches the bot.
*   **Implementation:**
    *   Import `asyncio`, `logging`, `Bot`, `Dispatcher` from `aiogram`.
    *   Import the configuration object from `app.config`.
    *   Import all router objects from the `app.handlers` package.
    *   Set up logging.
    *   Create `Bot` and `Dispatcher` instances.
    *   Register all imported routers with the main dispatcher (`dp.include_router(...)`).
    *   Define an `async def main()` function to start polling: `await dp.start_polling(bot)`.
    *   Run `asyncio.run(main())` under `if __name__ == "__main__":`.

#### `app/config.py`
*   **Purpose:** To load and provide configuration from environment variables.
*   **Implementation:**
    *   Use `pydantic_settings.BaseSettings` to create a `Settings` class.
    *   Define fields: `bot_token: str` and `database_url: str`.
    *   Instantiate a single `settings` object to be imported by other modules.

#### `app/handlers/group_onboarding.py`
*   **Purpose:** To welcome new users in the group.
*   **Implementation:**
    *   Create an `aiogram.Router`.
    *   Create a handler that triggers on new chat members: `@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))`.
    *   The handler function receives the `ChatMemberUpdated` event.
    *   It should fetch the user's name and generate a welcome message.
    *   It imports a keyboard generation function from `app.keyboards.inline` to create the `[🚀 Создать профиль]` button.
    *   It sends the welcome message with the keyboard to the **group chat**.

#### `app/handlers/profile_creation.py`
*   **Purpose:** Manages the multi-step process of creating a user profile.
*   **Implementation:**
    *   Create a router.
    *   Define a handler for the `/start` command. This handler begins the process and sets the first FSM state (e.g., `ProfileState.waiting_for_name`).
    *   Define a message handler for each state in the FSM (`waiting_for_name`, `waiting_for_company`, etc.).
    *   Each handler:
        1.  Receives user input.
        2.  Validates the input (e.g., check tag count).
        3.  Saves the data to the FSM context (`await state.update_data(...)`).
        4.  Asks the next question and sets the next state (`await state.set_state(...)`).
    *   The final handler (for `search_tags`) will:
        1.  Gather all data from the FSM context.
        2.  Call a database function from `app.db.queries` to save the profile.
        3.  Clear the state (`await state.clear()`).
        4.  Inform the user of success and perhaps trigger an initial search.

#### `app/handlers/profile_management.py`
*   **Purpose:** To allow users to view, edit, or delete their profile.
*   **Implementation:**
    *   Create a router.
    *   Define a handler for the `/myprofile` command.
        *   This handler fetches the user's profile from the database using a function from `app.db.queries`.
        *   It formats the profile data into a message.
        *   It attaches an inline keyboard with `[✏️ Изменить]` and `[🗑️ Удалить]` buttons.
    *   Define callback query handlers for the "edit" and "delete" callbacks.
        *   The "delete" handler will ask for confirmation, then call a DB function to soft-delete the user (`is_active=False`).
        *   The "edit" handler can either re-trigger the FSM or present another keyboard to choose which field to edit.

#### `app/handlers/search.py`
*   **Purpose:** To find and display matching contacts.
*   **Implementation:**
    *   Create a router.
    *   Define a handler for the `/search` command.
        *   It fetches the user's "search tags" from the database.
        *   It calls the `find_matches` function in `app.db.queries`.
        *   It formats the results into "cards".
        *   It uses keyboard functions to generate profile cards with a "Write to user" button and pagination buttons (`▶️ Next`).
    *   Define a callback query handler for pagination (`callback_data` like `page:next:{page_number}`). This handler will re-query and edit the original message with the new set of results.

#### `app/keyboards/inline.py`
*   **Purpose:** A library of functions that create `InlineKeyboardMarkup` objects.
*   **Implementation:**
    *   `def get_onboarding_keyboard() -> InlineKeyboardMarkup:` Returns the "Create Profile" button.
    *   `def get_profile_management_keyboard() -> InlineKeyboardMarkup:` Returns "Edit" and "Delete" buttons.
    *   `def get_contact_card_keyboard(user_telegram_id: int) -> InlineKeyboardMarkup:` Returns a "Write to user" button with `url=f"tg://user?id={user_telegram_id}"`.
    *   `def get_pagination_keyboard(...) -> InlineKeyboardMarkup:` Returns "Next" and "Previous" buttons.

#### `app/states/profile_states.py`
*   **Purpose:** Defines the states for the Finite State Machine.
*   **Implementation:**
    *   Import `StatesGroup`, `State` from `aiogram.fsm.state`.
    *   `class ProfileState(StatesGroup):`
        *   `waiting_for_name = State()`
        *   `waiting_for_company = State()`
        *   `waiting_for_own_tags = State()`
        *   `waiting_for_search_tags = State()`

#### `app/db/models.py`
*   **Purpose:** Defines the database schema using SQLAlchemy ORM.
*   **Implementation:**
    *   Import necessary components from `sqlalchemy.orm` and `sqlalchemy`.
    *   Define the `User`, `Tag`, and `UserTag` classes as described in the ADD, inheriting from a declarative base.

#### `app/db/queries.py`
*   **Purpose:** Encapsulates all database logic.
*   **Implementation:**
    *   All functions must be `async`.
    *   `async def create_user_profile(session: AsyncSession, data: dict) -> None:` Creates/updates a user and their tags. This will be a complex transaction.
    *   `async def get_user_profile(session: AsyncSession, telegram_id: int) -> User | None:` Fetches a user's profile.
    *   `async def find_matching_users(session: AsyncSession, search_tags: list[str]) -> list[User]:` Implements the core matching logic using SQLAlchemy queries and joins.
    *   `async def set_user_inactive(session: AsyncSession, telegram_id: int) -> None:` Soft-deletes a user.

---

### External Dependencies (`requirements.txt`)

```
aiogram==3.6.0
pydantic-settings==2.2.1
sqlalchemy==2.0.29
asyncpg==0.29.0
alembic==1.13.1
python-dotenv==1.0.1

# For testing
pytest==8.2.0
pytest-asyncio==0.23.6
```

---

### Subtasks Breakdown (for Project Management)

#### T1: Core Setup & Database
-   [ ] **Task:** Implement configuration loading (`app/config.py`).
-   [ ] **Task:** Set up the main bot entry point (`bot.py`).
-   [ ] **Task:** Define SQLAlchemy models (`app/db/models.py`).
-   [ ] **Docs:** Write `README.md` with setup instructions.

#### T2: User Onboarding & Profile Creation (FSM)
-   [ ] **Task:** Implement FSM states (`app/states/profile_states.py`).
-   [ ] **Task:** Implement handler for new members in a group (`app/handlers/group_onboarding.py`).
-   [ ] **Task:** Implement all handlers for the profile creation FSM (`app/handlers/profile_creation.py`).
-   [ ] **Task:** Implement keyboards for the FSM flow (`app/keyboards/inline.py`).
-   [ ] **Task:** Implement the `create_user_profile` database query (`app/db/queries.py`).
-   [ ] **Docs:** Add docstrings to all new handlers and functions.
-   [ ] **Tests:** Write unit tests for the `create_user_profile` query. Write integration tests for the full FSM flow.

#### T3: Profile Management
-   [ ] **Task:** Implement `/myprofile` command handler (`app/handlers/profile_management.py`).
-   [ ] **Task:** Implement "edit" and "delete" callback handlers.
-   [ ] **Task:** Implement `get_user_profile` and `set_user_inactive` database queries.
-   [ ] **Docs:** Update documentation for new commands.
-   [ ] **Tests:** Test that profile data is displayed correctly. Test that profile deletion works as expected.

#### T4: Search & Matching
-   [ ] **Task:** Implement the `find_matching_users` database query. This is the core matching logic.
-   [ ] **Task:** Implement the `/search` command handler (`app/handlers/search.py`).
-   [ ] **Task:** Implement the logic to format results into "cards".
-   [ ] **Task:** Implement pagination logic and its callback handler.
-   [ ] **Task:** Implement all necessary keyboards (`app/keyboards/inline.py`).
-   [ ] **Docs:** Document the matching algorithm and search functionality.
-   [ ] **Tests:** Write extensive tests for the `find_matching_users` query with various tag combinations. Test pagination callbacks.