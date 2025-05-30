# **Current Feature Plan: Bot Profile Setup FSM & Edit Handlers**

**Feature Description:**
This feature implements the conversational flow for user profile creation and editing using aiogram's Finite State Machine (FSM). It includes handlers for each state defined in `ProfileSetup` (e.g., `ASK_NAME`, `ASK_ROLE`, etc.) to prompt the user for information, store their responses, and transition them to the next step. Finally, it covers collecting all data and submitting it to the backend API. It also includes the callback query handler for the "Edit Profile" button to re-initiate this FSM flow.

**Tasks:**

- [x] **FEAT: Implement FSM handler for `ProfileSetup.ASK_NAME` state**
    *   In `bot/handlers/user_handlers.py`, define `async def process_ask_name(message: types.Message, state: FSMContext):`.
    *   Register this handler for messages received when in the `ProfileSetup.ASK_NAME` state.
    *   Prompt the user for their role (e.g., "Great, {name}! Now, what's your current role or primary function? (e.g., Founder, Software Engineer, Product Manager)").
    *   Store the received name: `await state.update_data(name=message.text.strip())`.
    *   Transition to the next state: `await state.set_state(ProfileSetup.ASK_ROLE)`.

- [x] **FEAT: Implement FSM handler for `ProfileSetup.ASK_ROLE` state**
    *   Define `async def process_ask_role(message: types.Message, state: FSMContext):`.
    *   Register for `ProfileSetup.ASK_ROLE` state.
    *   Prompt for industry (e.g., "Got it. In which industry do you primarily work or are interested in? (e.g., Fintech, SaaS, HealthTech)").
    *   Store the role: `await state.update_data(role=message.text.strip())`.
    *   Transition: `await state.set_state(ProfileSetup.ASK_INDUSTRY)`.

- [x] **FEAT: Implement FSM handler for `ProfileSetup.ASK_INDUSTRY` state**
    *   Define `async def process_ask_industry(message: types.Message, state: FSMContext):`.
    *   Register for `ProfileSetup.ASK_INDUSTRY` state.
    *   Prompt for skills (e.g., "What are some of your key skills? Please list them, separated by commas (e.g., Python, Project Management, UI/UX Design).").
    *   Store the industry: `await state.update_data(industry=message.text.strip())`.
    *   Transition: `await state.set_state(ProfileSetup.ASK_SKILLS)`.

- [x] **FEAT: Implement FSM handler for `ProfileSetup.ASK_SKILLS` state**
    *   Define `async def process_ask_skills(message: types.Message, state: FSMContext):`.
    *   Register for `ProfileSetup.ASK_SKILLS` state.
    *   Prompt for goals (e.g., "What are your current professional goals or things you're looking to achieve? (comma-separated, e.g., Find co-founder, Get investment, Learn new tech).").
    *   Parse skills (split by comma, strip whitespace): `skills = [s.strip() for s in message.text.split(',') if s.strip()]`.
    *   Store skills: `await state.update_data(skills=skills)`.
    *   Transition: `await state.set_state(ProfileSetup.ASK_GOALS)`.

- [x] **FEAT: Implement FSM handler for `ProfileSetup.ASK_GOALS` state**
    *   Define `async def process_ask_goals(message: types.Message, state: FSMContext):`.
    *   Register for `ProfileSetup.ASK_GOALS` state.
    *   Prompt for interests (e.g., "And finally, what are some of your professional interests? (comma-separated, e.g., AI, Blockchain, Remote Work).").
    *   Parse goals: `goals = [g.strip() for g in message.text.split(',') if g.strip()]`.
    *   Store goals: `await state.update_data(goals=goals)`.
    *   Transition: `await state.set_state(ProfileSetup.ASK_INTERESTS)`.

- [x] **FEAT: Implement FSM handler for `ProfileSetup.ASK_INTERESTS` state (Final Step)**
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

- [x] **FEAT: Implement callback query handler for "Edit Profile" button**
    *   Define `async def handle_edit_profile_callback(callback_query: types.CallbackQuery, state: FSMContext):`.
    *   Register this handler for callback data `"edit_profile"` (or as defined in `edit_profile_keyboard`).
    *   Answer the callback query: `await callback_query.answer()`.
    *   Send a message indicating profile editing is starting (e.g., "Let's update your profile.").
    *   Set the state to the first step of `ProfileSetup` FSM: `await state.set_state(ProfileSetup.ASK_NAME)`.
    *   Send the first question for profile setup (e.g., "What is your name/preferred display name? If unchanged, just send your current one.").
    *   (Optional: Pre-fill FSMContext with existing data if available, so users see current values and can edit, but this is more complex for MVP).

- [x] **FEAT: Implement a `/cancel` command handler for FSM**
    *   Define `async def handle_cancel_fsm(message: types.Message, state: FSMContext):`.
    *   Register for `Command("cancel")` and for `StateFilter("*")` (to be active in any state).
    *   If `await state.get_state()` is not `None`:
        *   Send a message: "Profile setup cancelled."
        *   Clear the state: `await state.clear()`.
        *   Show main menu keyboard.
    *   Else (if not in a state): Send a message "You are not in any active process."

- [x] **REFACTOR: Register FSM and callback handlers in `user_handlers.py` router**
    *   Attach all new FSM state handlers and the "Edit Profile" callback handler to the `user_router`.

- [x] **TEST: Unit tests for each FSM state handler**
    *   For each `process_ask_<field>` handler in `tests/bot/handlers/test_user_handlers.py`:
        *   Mock `FSMContext` (`update_data`, `set_state`, `get_data`).
        *   Mock `APIClient` for the final state handler.
        *   Verify the correct prompt message is sent.
        *   Verify data is correctly stored in `FSMContext`.
        *   Verify transition to the correct next state.
        *   For the final state, verify `api_client.update_user_profile` is called with compiled data and state is cleared.

- [x] **TEST: Unit test for "Edit Profile" callback query handler**
    *   Mock `FSMContext.set_state`.
    *   Verify `callback_query.answer()` is called.
    *   Verify the initial message and first profile question are sent.
    *   Verify `state.set_state` is called with the initial `ProfileSetup` state.

- [x] **TEST: Unit test for `/cancel` FSM command handler**
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

# **Project Setup & Foundational Elements**

**Title** — Project Setup & Foundational Elements

**Feature description** — Initial setup of the NetWise Telegram bot project, including directory structure, version control, environment configuration, and basic bot functionality.

**Tasks**
- [ ] Create project directory (`netwise`)
- [ ] Initialize Git repository (`git init`)
- [ ] Create initial `.gitignore` file
- [ ] Create `README.md` with basic project info
- [ ] Set up remote repository (e.g., GitHub, GitLab)
- [ ] Set up Python virtual environment (e.g., `venv`)
- [ ] Install core dependencies: `aiogram`, `python-dotenv`, `supabase`, `apscheduler`
- [ ] Create `requirements.txt`
- [ ] Create `.env.example` file
- [ ] Create local `.env` file
- [ ] Create main package directory `netwise_bot/` and `__init__.py`
- [ ] Create `main.py` at the root
- [ ] Create `netwise_bot/config.py`
- [ ] Create `netwise_bot/bot_instance.py`
- [ ] Create Supabase project
- [ ] Design and create initial DB tables (start with `users` table)
- [ ] Get Supabase URL and Service Role Key for `.env`
- [ ] Implement `netwise_bot/config.py`: Load environment variables
- [ ] Implement `netwise_bot/bot_instance.py`: Initialize `Bot` and `Dispatcher`
- [ ] Implement basic `main.py`:
  - [ ] Load config
  - [ ] Initialize bot & dispatcher
  - [ ] Create a simple `/start` handler
  - [ ] Start polling
- [ ] Test: Run `main.py` and send `/start` to bot
- [ ] Configure basic logging in `main.py`

**Files involved**
- `.gitignore`
- `README.md`
- `requirements.txt`
- `.env.example`
- `.env`
- `main.py`
- `netwise_bot/__init__.py`
- `netwise_bot/config.py`
- `netwise_bot/bot_instance.py`

**External dependencies**
- Python 3.8+
- aiogram
- python-dotenv
- supabase-py
- apscheduler

**Notes**
- The project will be structured as a Python package
- Environment variables will be used for sensitive data
- Basic logging will be configured for development
- The initial bot will have a simple `/start` command
- Supabase will be used as the database backend
- The project will be hosted on Railway

# User Service - Basic CRUD

## Feature Description
Implementation of the basic user service functionality to handle user creation and retrieval in the NetWise bot. This service will be responsible for managing user data in Supabase, providing a clean interface for other parts of the application to interact with user data.

## Tasks
- [ ] Create `netwise_bot/services/supabase_client.py`
  - [ ] Implement `__init__` to initialize Supabase client
  - [ ] Implement `fetch_user_by_telegram_id(telegram_id)` function
  - [ ] Implement `create_user(telegram_id, name=None, defaults=...)` function
- [ ] Create `netwise_bot/services/user_service.py`
  - [ ] Implement `get_or_create_user(telegram_id, name=None)` using `supabase_client`

## Files Involved
- `netwise_bot/services/supabase_client.py` (new)
- `netwise_bot/services/user_service.py` (new)
- `netwise_bot/config.py` (existing, will be used for Supabase configuration)

## External Dependencies
- `supabase-py`: Python client for Supabase
- `python-dotenv`: For environment variable management

## Notes
- The Supabase client will be initialized with credentials from environment variables
- User creation should handle both new and existing users gracefully
- The service should be designed to be easily extended for future user-related functionality
- Error handling should be implemented for database operations
- The service should follow the singleton pattern for the Supabase client instance

# `/start` Handler Enhancement

## Feature Description
Enhancement of the `/start` command handler to provide a better user experience for both new and existing users. The handler will use the UserService to manage user data and provide appropriate welcome messages and keyboard options based on whether the user is new or returning.

## Tasks
- [ ] Create `netwise_bot/handlers/common.py`
  - [ ] Import necessary dependencies (aiogram, UserService)
  - [ ] Create router for common handlers
  - [ ] Move existing `/start` logic to this file
  - [ ] Enhance `/start` handler to use UserService
  - [ ] Add different welcome messages for new vs existing users
- [ ] Create `netwise_bot/keyboards/common_keyboards.py`
  - [ ] Create `get_initial_setup_keyboard()` function
  - [ ] Implement keyboard with "Create Profile" button for new users
  - [ ] Add appropriate callback data for buttons
- [ ] Test the enhanced `/start` command behavior
  - [ ] Test with new users
  - [ ] Test with existing users
  - [ ] Verify keyboard display
  - [ ] Verify user creation/retrieval

## Files Involved
- `netwise_bot/handlers/common.py` (new)
- `netwise_bot/keyboards/common_keyboards.py` (new)
- `netwise_bot/services/user_service.py` (existing, will be used)
- `main.py` (will need to import and register new handlers)

## External Dependencies
- `aiogram`: For bot handlers and keyboard creation
- `supabase-py`: Already included via UserService

## Notes
- The welcome message should be friendly and informative
- The keyboard should be intuitive and guide users to the next step
- Error handling should be implemented for user service operations
- The handler should be registered in the main router
- Consider adding logging for debugging purposes

# Profile Creation Flow - FSM & Handlers

## Feature Description
Implementation of the profile creation flow using aiogram's Finite State Machine (FSM) to guide users through a step-by-step process of creating their professional profile. The flow will collect information about the user's role, industry, skills, goals, and interests, storing the data in the FSM context before saving it to the database.

## Tasks
- [ ] Create `netwise_bot/states/profile_states.py`
  - [ ] Create `ProfileStates` class inheriting from `StatesGroup`
  - [ ] Define states: `name`, `role`, `industry`, `skills`, `goals`, `interests`
- [ ] Create `netwise_bot/handlers/profile.py`
  - [ ] Import necessary dependencies (aiogram, FSM, UserService)
  - [ ] Create router for profile handlers
  - [ ] Implement callback handler for "Create Profile" button
  - [ ] Implement message handlers for each profile state:
    - [ ] `name` state handler
    - [ ] `role` state handler
    - [ ] `industry` state handler
    - [ ] `skills` state handler
    - [ ] `goals` state handler
    - [ ] `interests` state handler
  - [ ] Implement validation for each field
  - [ ] Implement state transitions
  - [ ] Implement final profile submission
- [ ] Create `netwise_bot/keyboards/profile_keyboards.py`
  - [ ] Create keyboard for confirming profile submission
  - [ ] Create keyboard for canceling profile creation
- [ ] Update UserService
  - [ ] Add method to update user profile data
- [ ] Test the profile creation flow
  - [ ] Test each state transition
  - [ ] Test validation
  - [ ] Test profile submission
  - [ ] Test cancellation

## Files Involved
- `netwise_bot/states/profile_states.py` (new)
- `netwise_bot/handlers/profile.py` (new)
- `netwise_bot/keyboards/profile_keyboards.py` (new)
- `netwise_bot/services/user_service.py` (update)
- `netwise_bot/handlers/common.py` (update to register profile router)

## External Dependencies
- `aiogram`: For FSM, handlers, and keyboards
- `supabase-py`: Already included via UserService

## Notes
- Each state should have clear instructions for the user
- Validation should be user-friendly with helpful error messages
- The flow should be cancellable at any point
- Consider adding a way to skip optional fields
- Store intermediate data in FSM context
- Handle errors gracefully
- Add logging for debugging
- Consider adding a way to edit profile later

# Profile Service - Update & Get

## Feature Description
Implementation of additional profile service functionality to handle profile updates and retrieval in the NetWise bot. This service will extend the existing UserService to provide methods for updating user profiles and retrieving profile information, ensuring proper data management and error handling.

## Tasks
- [ ] Update `netwise_bot/services/supabase_client.py`
  - [ ] Implement `update_user_profile(telegram_id, profile_data)` function
  - [ ] Implement `fetch_user_profile(telegram_id)` function
- [ ] Update `netwise_bot/services/user_service.py`
  - [ ] Implement `update_profile(telegram_id, profile_data)` method
  - [ ] Implement `get_profile(telegram_id)` method
- [ ] Add error handling and validation
  - [ ] Validate profile data before updates
  - [ ] Handle database errors gracefully
  - [ ] Add appropriate error messages
- [ ] Add logging for debugging
  - [ ] Log successful profile updates
  - [ ] Log profile retrieval
  - [ ] Log errors with appropriate context

## Files Involved
- `netwise_bot/services/supabase_client.py` (update)
- `netwise_bot/services/user_service.py` (update)

## External Dependencies
- `supabase-py`: Already included via UserService
- `python-dotenv`: Already included for environment variables

## Notes
- Profile updates should be atomic (all or nothing)
- Profile data should be validated before updates
- Error messages should be user-friendly
- Consider adding profile data caching for frequently accessed profiles
- Add appropriate logging for monitoring and debugging
- Consider adding profile versioning for future features
- Ensure proper error handling for database operations

# Completing Profile Creation & `/myprofile`

## Feature Description
Implementation of the final steps in profile creation flow and the `/myprofile` command to view profile information. This includes completing the profile creation process by saving the collected data, implementing profile viewing functionality, and adding profile editing capabilities.

## Tasks
- [ ] Complete profile creation flow in `handlers/profile.py`
  - [ ] Implement handler for the last profile field (interests)
  - [ ] Add profile data collection from FSM context
  - [ ] Implement profile submission to UserService
  - [ ] Add success/error messages
  - [ ] Clear FSM state after completion
- [ ] Implement `/myprofile` command
  - [ ] Create command handler in `handlers/profile.py`
  - [ ] Fetch profile data using UserService
  - [ ] Format profile information for display
  - [ ] Add "Edit Profile" button
  - [ ] Handle cases where profile doesn't exist
- [ ] Add profile editing functionality
  - [ ] Create edit profile keyboard
  - [ ] Implement edit profile callback handler
  - [ ] Reuse existing FSM flow for editing
  - [ ] Pre-fill FSM with existing data
- [ ] Add comprehensive error handling
  - [ ] Handle database errors
  - [ ] Handle missing profile data
  - [ ] Add user-friendly error messages
- [ ] Add logging for debugging
  - [ ] Log profile creation completion
  - [ ] Log profile viewing
  - [ ] Log profile editing attempts

## Files Involved
- `netwise_bot/handlers/profile.py` (major updates)
- `netwise_bot/keyboards/profile_keyboards.py` (add edit keyboard)
- `netwise_bot/services/user_service.py` (already updated)

## External Dependencies
- `aiogram`: For command handlers and FSM
- `supabase-py`: Already included via UserService

## Notes
- Profile display should be well-formatted and easy to read
- Consider adding profile completion percentage
- Add validation for profile data before saving
- Consider adding profile privacy settings
- Add rate limiting for profile editing
- Consider caching profile data for frequent views
- Add proper error messages for all failure cases
- Consider adding profile statistics (e.g., connections, requests)

# User Activity Tracking (Basic)

## Feature Description
Implementation of basic user activity tracking functionality to monitor user engagement and manage active/inactive users. This includes tracking last active timestamps, managing user visibility in search, and implementing activity updates across various user interactions.

## Tasks
- [ ] Update Supabase `users` table
  - [ ] Add `last_active_at` (Timestamp) column
  - [ ] Add `is_active_in_search` (Boolean, default: true) column
  - [ ] Add appropriate indexes for performance
- [ ] Update Supabase client
  - [ ] Add `update_user_last_active(telegram_id)` method
  - [ ] Add error handling and logging
  - [ ] Add method to update `is_active_in_search` status
- [ ] Update UserService
  - [ ] Add `update_user_activity(telegram_id)` method
  - [ ] Add `deactivate_inactive_users(days_inactive_threshold)` method
  - [ ] Add activity status checks
- [ ] Implement activity tracking middleware
  - [ ] Create `netwise_bot/middleware/activity_middleware.py`
  - [ ] Track activity on message handling
  - [ ] Track activity on callback queries
  - [ ] Add rate limiting for activity updates
- [ ] Add activity tracking to existing handlers
  - [ ] Update `/start` handler
  - [ ] Update profile handlers
  - [ ] Update command handlers
- [ ] Add logging and monitoring
  - [ ] Log activity updates
  - [ ] Log user deactivations
  - [ ] Add activity statistics

## Files Involved
- `netwise_bot/services/supabase_client.py` (update)
- `netwise_bot/services/user_service.py` (update)
- `netwise_bot/middleware/activity_middleware.py` (new)
- `netwise_bot/handlers/common.py` (update)
- `netwise_bot/handlers/profile.py` (update)

## External Dependencies
- `aiogram`: For middleware and handlers
- `supabase-py`: Already included via UserService
- `python-dateutil`: For date handling (optional)

## Notes
- Activity updates should be rate-limited to prevent excessive database writes
- Consider caching activity status for frequently accessed users
- Add appropriate indexes in Supabase for efficient queries
- Consider adding activity statistics for future features
- Add proper error handling for database operations
- Consider adding activity-based features (e.g., rewards for active users)
- Add monitoring for inactive users
- Consider adding activity-based search filters