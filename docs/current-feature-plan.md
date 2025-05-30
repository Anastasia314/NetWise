# **Current Feature Plan: Bot Core User Command Handlers (Start & Profile)**

**Feature Description:**
This feature implements the initial user interaction points: the `/start` command for onboarding and greeting, and the `/profile` command for users to view their current profile information. The `/start` command will attempt to onboard the user via the API client and, based on their profile status, either initiate the profile setup flow or show the main menu. The `/profile` command will fetch and display the user's profile and offer an option to edit it.

**Tasks:**

- [ ] **FEAT: Create `bot/handlers` directory and `user_handlers.py` file**
    *   Create the directory `bot/handlers/` if it doesn't exist.
    *   Add an `__init__.py` file to `bot/handlers/` to mark it as a package.
    *   Create a new Python file `bot/handlers/user_handlers.py`.
    *   Import necessary `aiogram` modules (`Router`, `types`, `FSMContext`, `CommandStart`, `Command`).
    *   Import `APIClient` (or its access mechanism), `ProfileSetup` states, keyboard builders, and `format_user_profile_message`.

- [ ] **FEAT: Implement `/start` command handler in `user_handlers.py`**
    *   Define an `async def handle_start(message: types.Message, state: FSMContext, api_client: APIClient):` (adjust `api_client` injection as per DI setup).
    *   Register this handler for the `CommandStart()` filter.
    *   Inside the handler:
        *   Extract `telegram_id`, `name` (first_name), and `username` from `message.from_user`.
        *   Call `api_client.onboard_user(telegram_id, name, username)`.
        *   Handle potential `APIClientError` exceptions gracefully (e.g., log error, inform user of a temporary issue).
        *   If onboarding is successful, fetch the user's profile using `api_client.get_user_profile(telegram_id)`.
        *   Check if the profile is complete (e.g., essential fields like `role`, `industry`, `skills` are filled).
            *   If incomplete (or new user):
                *   Send a welcome message explaining the need to set up a profile.
                *   Set the state to the first step of `ProfileSetup` FSM (e.g., `await state.set_state(ProfileSetup.ASK_NAME)`).
                *   Send the first question for profile setup (e.g., "What is your name/preferred display name?").
            *   If complete:
                *   Send a welcome back message.
                *   Display the main menu using `main_menu_keyboard()`.
                *   Clear any previous state: `await state.clear()`.

- [ ] **FEAT: Implement `/profile` command handler in `user_handlers.py`**
    *   Define an `async def handle_profile(message: types.Message, api_client: APIClient):`.
    *   Register this handler for the `Command("profile")` filter.
    *   Inside the handler:
        *   Get `telegram_id` from `message.from_user`.
        *   Call `api_client.get_user_profile(telegram_id)`.
        *   Handle potential `APIClientError` (e.g., user not found, API down).
        *   If successful:
            *   Format the profile data using `format_user_profile_message(profile_data)`.
            *   Send the formatted profile message to the user.
            *   Include the `edit_profile_keyboard()` as `reply_markup`.

- [ ] **REFACTOR: Register `user_handlers` router in `bot/main.py`**
    *   In `bot/handlers/user_handlers.py`, create a `Router` instance (e.g., `user_router = Router()`).
    *   Attach the `handle_start` and `handle_profile` handlers to this `user_router`.
    *   In `bot/main.py` (or where the main dispatcher is configured), import `user_router` and include it in the main dispatcher (e.g., `dp.include_router(user_router)`).

- [ ] **TEST: Unit test for `/start` handler - new user/incomplete profile**
    *   Create `tests/bot/handlers/test_user_handlers.py`.
    *   Mock `APIClient` methods (`onboard_user`, `get_user_profile` to return an incomplete profile).
    *   Mock `FSMContext.set_state`.
    *   Verify that `onboard_user` and `get_user_profile` are called.
    *   Verify the correct welcome message is sent.
    *   Verify `state.set_state` is called with the initial `ProfileSetup` state.
    *   Verify the first profile question is sent.

- [ ] **TEST: Unit test for `/start` handler - existing user/complete profile**
    *   Mock `APIClient` methods (`onboard_user`, `get_user_profile` to return a complete profile).
    *   Mock `FSMContext.clear`.
    *   Verify `onboard_user` and `get_user_profile` are called.
    *   Verify the welcome back message is sent.
    *   Verify `main_menu_keyboard` is used.
    *   Verify `state.clear` is called.

- [ ] **TEST: Unit test for `/profile` handler - successful profile fetch**
    *   Mock `APIClient.get_user_profile` to return valid profile data.
    *   Mock `format_user_profile_message`.
    *   Mock `edit_profile_keyboard`.
    *   Verify `get_user_profile` is called.
    *   Verify `format_user_profile_message` is called with the profile data.
    *   Verify the formatted message is sent with the `edit_profile_keyboard`.

- [ ] **TEST: Unit test for `/profile` handler - API error**
    *   Mock `APIClient.get_user_profile` to raise an `APIClientError`.
    *   Verify an appropriate error message is sent to the user.

**Files Involved:**
*   `bot/handlers/__init__.py` (New or existing)
*   `bot/handlers/user_handlers.py` (New file)
*   `bot/main.py` (Or relevant bot initialization module, for router registration)
*   `tests/bot/handlers/test_user_handlers.py` (New file)
*   (Uses existing: `bot/services/api_client.py`, `bot/states/user_states.py`, `bot/keyboards/inline_keyboards.py`, `bot/keyboards/reply_keyboards.py`, `bot/utils/formatters.py`)

**External Dependencies:**
*   `aiogram`: Core for handlers, types, FSMContext, Command filters.
*   `pytest`, `pytest-asyncio`: For testing.
*   (Relies on `APIClient` which uses `httpx` and `respx` for its tests).

**Notes:**
*   The "profile completeness check" in the `/start` handler needs a clear definition. For MVP, it might be checking if `role`, `industry`, and at least one `skill` are present.
*   Error messages to the user should be user-friendly and avoid exposing technical details.
*   The dependency injection for `APIClient` (and potentially other services like database access if not fully encapsulated by `APIClient`) needs to be consistent. `aiogram` middleware or passing context through the dispatcher are common ways. For simplicity in this plan, it's shown as a parameter.
*   This plan defers the implementation of the FSM state handlers for profile setup and the "Edit Profile" callback query handler to the next feature plan.
```