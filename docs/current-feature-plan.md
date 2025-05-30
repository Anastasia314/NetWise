# **Current Feature Plan: Bot Profile Setup FSM & Edit Handlers**

**Feature Description:**
This feature implements the conversational flow for user profile creation and editing using aiogram's Finite State Machine (FSM). It includes handlers for each state defined in `ProfileSetup` (e.g., `ASK_NAME`, `ASK_ROLE`, etc.) to prompt the user for information, store their responses, and transition them to the next step. Finally, it covers collecting all data and submitting it to the backend API. It also includes the callback query handler for the "Edit Profile" button to re-initiate this FSM flow.

**Tasks:**

- [ ] **FEAT: Implement FSM handler for `ProfileSetup.ASK_NAME` state**
    *   In `bot/handlers/user_handlers.py`, define `async def process_ask_name(message: types.Message, state: FSMContext):`.
    *   Register this handler for messages received when in the `ProfileSetup.ASK_NAME` state.
    *   Prompt the user for their role (e.g., "Great, {name}! Now, what's your current role or primary function? (e.g., Founder, Software Engineer, Product Manager)").
    *   Store the received name: `await state.update_data(name=message.text.strip())`.
    *   Transition to the next state: `await state.set_state(ProfileSetup.ASK_ROLE)`.

- [ ] **FEAT: Implement FSM handler for `ProfileSetup.ASK_ROLE` state**
    *   Define `async def process_ask_role(message: types.Message, state: FSMContext):`.
    *   Register for `ProfileSetup.ASK_ROLE` state.
    *   Prompt for industry (e.g., "Got it. In which industry do you primarily work or are interested in? (e.g., Fintech, SaaS, HealthTech)").
    *   Store the role: `await state.update_data(role=message.text.strip())`.
    *   Transition: `await state.set_state(ProfileSetup.ASK_INDUSTRY)`.

- [ ] **FEAT: Implement FSM handler for `ProfileSetup.ASK_INDUSTRY` state**
    *   Define `async def process_ask_industry(message: types.Message, state: FSMContext):`.
    *   Register for `ProfileSetup.ASK_INDUSTRY` state.
    *   Prompt for skills (e.g., "What are some of your key skills? Please list them, separated by commas (e.g., Python, Project Management, UI/UX Design).").
    *   Store the industry: `await state.update_data(industry=message.text.strip())`.
    *   Transition: `await state.set_state(ProfileSetup.ASK_SKILLS)`.

- [ ] **FEAT: Implement FSM handler for `ProfileSetup.ASK_SKILLS` state**
    *   Define `async def process_ask_skills(message: types.Message, state: FSMContext):`.
    *   Register for `ProfileSetup.ASK_SKILLS` state.
    *   Prompt for goals (e.g., "What are your current professional goals or things you're looking to achieve? (comma-separated, e.g., Find co-founder, Get investment, Learn new tech).").
    *   Parse skills (split by comma, strip whitespace): `skills = [s.strip() for s in message.text.split(',') if s.strip()]`.
    *   Store skills: `await state.update_data(skills=skills)`.
    *   Transition: `await state.set_state(ProfileSetup.ASK_GOALS)`.

- [ ] **FEAT: Implement FSM handler for `ProfileSetup.ASK_GOALS` state**
    *   Define `async def process_ask_goals(message: types.Message, state: FSMContext):`.
    *   Register for `ProfileSetup.ASK_GOALS` state.
    *   Prompt for interests (e.g., "And finally, what are some of your professional interests? (comma-separated, e.g., AI, Blockchain, Remote Work).").
    *   Parse goals: `goals = [g.strip() for g in message.text.split(',') if g.strip()]`.
    *   Store goals: `await state.update_data(goals=goals)`.
    *   Transition: `await state.set_state(ProfileSetup.ASK_INTERESTS)`.

- [ ] **FEAT: Implement FSM handler for `ProfileSetup.ASK_INTERESTS` state (Final Step)**
    *   Define `async def process_ask_interests(message: types.Message, state: FSMContext, api_client: APIClient):`.
    *   Register for `ProfileSetup.ASK_INTERESTS` state.
    *   Parse interests: `interests = [i.strip() for i in message.text.split(',') if i.strip()]`.
    *   Store interests: `await state.update_data(interests=interests)`.
    *   Retrieve all collected data: `user_data = await state.get_data()`.
    *   Construct `profile_data` payload suitable for `api_client.update_user_profile` (map FSM data keys to API model keys if different).
    *   Call `api_client.update_user_profile(telegram_id=message.from_user.id, profile_data=profile_data)`.
    *   Handle API response:
        *   On success: Send a confirmation message (e.g., "Your profile has been updated!"). Display the main menu keyboard.
        *   On error (`APIClientError`): Send an error message (e.g., "Sorry, there was an issue updating your profile. Please try again.").
    *   Clear the state: `await state.clear()`.

- [ ] **FEAT: Implement callback query handler for "Edit Profile" button**
    *   Define `async def handle_edit_profile_callback(callback_query: types.CallbackQuery, state: FSMContext):`.
    *   Register this handler for callback data `"edit_profile"` (or as defined in `edit_profile_keyboard`).
    *   Answer the callback query: `await callback_query.answer()`.
    *   Send a message indicating profile editing is starting (e.g., "Let's update your profile.").
    *   Set the state to the first step of `ProfileSetup` FSM: `await state.set_state(ProfileSetup.ASK_NAME)`.
    *   Send the first question for profile setup (e.g., "What is your name/preferred display name? If unchanged, just send your current one.").
    *   (Optional: Pre-fill FSMContext with existing data if available, so users see current values and can edit, but this is more complex for MVP).

- [ ] **FEAT: Implement a `/cancel` command handler for FSM**
    *   Define `async def handle_cancel_fsm(message: types.Message, state: FSMContext):`.
    *   Register for `Command("cancel")` and for `StateFilter("*")` (to be active in any state).
    *   If `await state.get_state()` is not `None`:
        *   Send a message: "Profile setup cancelled."
        *   Clear the state: `await state.clear()`.
        *   Show main menu keyboard.
    *   Else (if not in a state): Send a message "You are not in any active process."

- [ ] **REFACTOR: Register FSM and callback handlers in `user_handlers.py` router**
    *   Attach all new FSM state handlers and the "Edit Profile" callback handler to the `user_router`.

- [ ] **TEST: Unit tests for each FSM state handler**
    *   For each `process_ask_<field>` handler in `tests/bot/handlers/test_user_handlers.py`:
        *   Mock `FSMContext` (`update_data`, `set_state`, `get_data`).
        *   Mock `APIClient` for the final state handler.
        *   Verify the correct prompt message is sent.
        *   Verify data is correctly stored in `FSMContext`.
        *   Verify transition to the correct next state.
        *   For the final state, verify `api_client.update_user_profile` is called with compiled data and state is cleared.

- [ ] **TEST: Unit test for "Edit Profile" callback query handler**
    *   Mock `FSMContext.set_state`.
    *   Verify `callback_query.answer()` is called.
    *   Verify the initial message and first profile question are sent.
    *   Verify `state.set_state` is called with the initial `ProfileSetup` state.

- [ ] **TEST: Unit test for `/cancel` FSM command handler**
    *   Test when in a state: mock `FSMContext.get_state` to return a state, mock `clear`. Verify message and state clearing.
    *   Test when not in a state: mock `FSMContext.get_state` to return `None`. Verify appropriate message.

**Files Involved:**
*   `bot/handlers/user_handlers.py` (Major additions)
*   `tests/bot/handlers/test_user_handlers.py` (Major additions)
*   (Uses existing: `bot/services/api_client.py`, `bot/states/user_states.py`, `bot/keyboards/reply_keyboards.py`)

**External Dependencies:**
*   `aiogram`: For FSM, `CallbackQuery`, `StateFilter`.
*   `pytest`, `pytest-asyncio`: For testing.

**Notes:**
*   The prompts for each piece of information should be clear and guide the user.
*   Consider adding a "skip" option for non-essential profile fields during the FSM flow. This would involve adding "skip" buttons to keyboards and handlers for their callback data, which would transition to the next state without storing data for the current field. (This is an enhancement beyond the current task scope but good to keep in mind).
*   Error handling for API calls in the final step is crucial.
*   The `/cancel` command provides an essential escape hatch for users from the FSM flow.
*   The text for prompts can be moved to a separate constants or localization file later for better maintainability.
*   Initial implementation of "Edit Profile" will restart the flow from `ASK_NAME`. A more advanced version might fetch existing data and allow editing field by field, or show current values in prompts. For MVP, a full re-run is simpler.
```