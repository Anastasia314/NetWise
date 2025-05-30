# **Current Feature Plan: Bot UI Keyboards**

**Feature Description:**
This feature focuses on creating the user interface elements (keyboards) for the Telegram bot. These include inline keyboards for contextual actions like editing a profile or skipping a question during profile setup, and reply keyboards for persistent options like the main menu. These keyboards enhance user interaction by providing clear, tappable options.

**Tasks:**

- [x] **FEAT: Create `bot/keyboards` directory**
    *   Create the directory `bot/keyboards/` if it doesn't exist.
    *   Add an `__init__.py` file to `bot/keyboards/` to mark it as a package.

- [x] **FEAT: Create `bot/keyboards/inline_keyboards.py` and basic structure**
    *   Create a new Python file `bot/keyboards/inline_keyboards.py`.
    *   Import `InlineKeyboardMarkup` and `InlineKeyboardButton` from `aiogram.types`.

- [x] **FEAT: Implement `edit_profile_keyboard()` in `inline_keyboards.py`**
    *   Define a function `def edit_profile_keyboard() -> InlineKeyboardMarkup:`.
    *   Create an `InlineKeyboardButton` with text like "✏️ Edit Profile" (or similar).
    *   Assign a `callback_data` to this button (e.g., `"edit_profile"`). This data will be used to identify the button press in callback query handlers.
    *   Return an `InlineKeyboardMarkup` containing this button.
    *   Add a docstring explaining the keyboard's purpose.

- [x] **FEAT: Implement `skip_question_keyboard()` in `inline_keyboards.py`**
    *   Define a function `def skip_question_keyboard(question_identifier: str) -> InlineKeyboardMarkup:`.
        *   The `question_identifier` could be used to form part of the callback data if different skip actions are needed, or a generic "skip" callback is fine for now.
    *   Create an `InlineKeyboardButton` with text like "➡️ Skip" or "Пропустить".
    *   Assign a `callback_data` (e.g., `"skip_question"` or `f"skip_{question_identifier}"`).
    *   Return an `InlineKeyboardMarkup` containing this button.
    *   Add a docstring explaining the keyboard's purpose.

- [x] **FEAT: Create `bot/keyboards/reply_keyboards.py` and basic structure**
    *   Create a new Python file `bot/keyboards/reply_keyboards.py`.
    *   Import `ReplyKeyboardMarkup`, `KeyboardButton` from `aiogram.types`.

- [x] **FEAT: Implement `main_menu_keyboard()` in `reply_keyboards.py`**
    *   Define a function `def main_menu_keyboard() -> ReplyKeyboardMarkup:`.
    *   Create `KeyboardButton` instances for main menu options. Based on PRD/ADD, initial options might include:
        *   "👤 My Profile" (corresponds to `/profile` command)
        *   "➕ New Request" (corresponds to `/new_request` command)
        *   "🤝 My Friends" (corresponds to `/my_friends` command)
        *   "🔗 Invite Friend" (corresponds to `/invite` command)
        *   (Consider adding "📊 My Points" or "📜 My Requests" later based on feature rollout)
    *   Build a `ReplyKeyboardMarkup` with these buttons. Consider `resize_keyboard=True` and `one_time_keyboard=False` (or `True` if preferred for some contexts).
    *   Arrange buttons in rows as desired (e.g., using `.row()` or `.add()`).
    *   Return the `ReplyKeyboardMarkup`.
    *   Add a docstring explaining the keyboard's purpose.

- [x] **TEST: (Placeholder) Basic import and construction tests for keyboards**
    *   Create `tests/bot/keyboards/test_inline_keyboards.py`.
    *   Add tests to call `edit_profile_keyboard()` and `skip_question_keyboard()` and verify they return `InlineKeyboardMarkup` instances with the expected number of buttons and callback data.
    *   Create `tests/bot/keyboards/test_reply_keyboards.py`.
    *   Add a test to call `main_menu_keyboard()` and verify it returns a `ReplyKeyboardMarkup` instance with the expected buttons/text.

**Files Involved:**
*   `bot/keyboards/__init__.py` (New file)
*   `bot/keyboards/inline_keyboards.py` (New file)
*   `bot/keyboards/reply_keyboards.py` (New file)
*   `tests/bot/keyboards/test_inline_keyboards.py` (New file)
*   `tests/bot/keyboards/test_reply_keyboards.py` (New file)

**External Dependencies:**
*   `aiogram`: Specifically `aiogram.types.InlineKeyboardMarkup`, `aiogram.types.InlineKeyboardButton`, `aiogram.types.ReplyKeyboardMarkup`, `aiogram.types.KeyboardButton`.
*   `pytest`: For running tests.

**Notes:**
*   Callback data for inline keyboards should be chosen carefully to be unique and easily parsable by handlers.
*   Text for reply keyboard buttons should ideally match the commands they trigger if they are shortcuts for commands, for consistency.
*   Consider localization early if the bot will support multiple languages; keyboard text would be a prime candidate for internationalization. For MVP, hardcoded strings are fine.
*   The specific buttons in `main_menu_keyboard()` might evolve as more features are implemented. This plan reflects a reasonable starting set for user profile and initial interactions.
```