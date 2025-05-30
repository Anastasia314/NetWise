# **Current Feature Plan: Bot User Profile Setup States**

**Feature Description:**
This feature involves defining the Finite State Machine (FSM) states required for the user profile setup and editing process within the Telegram bot. These states will guide the user through a multi-step conversation to collect their profile information (name, role, industry, skills, goals, interests). This structure is essential for managing conversation flow and context.

**Tasks:**

- [x] **FEAT: Create `bot/states` directory and `user_states.py` file**
    *   Create the directory `bot/states/` if it doesn't exist.
    *   Create a new Python file `bot/states/user_states.py`.

- [x] **FEAT: Define `ProfileSetup` StatesGroup in `user_states.py`**
    *   Import `StatesGroup` and `State` from `aiogram.fsm.state`.
    *   Define a class `ProfileSetup(StatesGroup)` inheriting from `StatesGroup`.
    *   Inside the `ProfileSetup` class, define individual states as class attributes using `State()`:
        *   `ASK_NAME = State()`
        *   `ASK_ROLE = State()`
        *   `ASK_INDUSTRY = State()`
        *   `ASK_SKILLS = State()`
        *   `ASK_GOALS = State()`
        *   `ASK_INTERESTS = State()`
        *   (Consider adding a `CONFIRMATION = State()` if a summary and confirmation step is desired before saving).

- [x] **DOC: Add docstrings to `ProfileSetup` StatesGroup and individual states**
    *   Add a class-level docstring to `ProfileSetup` explaining its purpose.
    *   Add brief docstrings to each `State` explaining what information is being requested in that state.

- [x] **TEST: (Placeholder) Basic import test for `user_states.py`**
    *   Create `tests/bot/states/test_user_states.py`.
    *   Add a simple test to ensure `ProfileSetup` and its states can be imported without error. (More meaningful tests will come when these states are used in handlers).

**Files Involved:**
*   `bot/states/user_states.py` (New file)
*   `tests/bot/states/test_user_states.py` (New file)

**External Dependencies:**
*   `aiogram`: Specifically `aiogram.fsm.state.StatesGroup` and `aiogram.fsm.state.State`.
*   `pytest`: For running the basic import test.

**Notes:**
*   The order of states defined usually reflects the intended conversation flow.
*   These states will be used by `aiogram`'s `Dispatcher` and `FSMContext` to manage the user's current position in the profile setup dialogue.
*   The names of the states (`ASK_NAME`, `ASK_ROLE`, etc.) should be descriptive and clearly indicate the purpose of each step in the profile creation/editing process.
*   This task only defines the states; the handlers that utilize these states will be implemented in a subsequent task ("Bot: User Handlers").