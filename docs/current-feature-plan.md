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

# Task 2.1: Connections Table & Service Foundation

## Feature Description
Implementation of the core connection system that will allow users to establish and manage their professional network within NetWise. This includes creating the database structure for connections and implementing the basic service layer for managing these connections.

## Tasks
- [ ] Create connections table in Supabase with the following columns:
  - [ ] id (uuid, primary key)
  - [ ] user1_id (uuid, foreign key to users.id)
  - [ ] user2_id (uuid, foreign key to users.id)
  - [ ] connection_type (text, enum: 'worked_together', 'intro_made', 'met_at_event', 'other')
  - [ ] trust_score (integer, range 1-3)
  - [ ] status (text, enum: 'pending', 'active', 'blocked')
  - [ ] created_at (timestamp with time zone)
  - [ ] updated_at (timestamp with time zone)
- [ ] Create graph_service.py with basic connection management functions
- [ ] Implement create_connection function in supabase_client.py
- [ ] Implement fetch_connections function in supabase_client.py
- [ ] Add appropriate indexes and constraints to the connections table
- [ ] Add RLS policies for the connections table

## Files Involved
- netwise_bot/services/graph_service.py (new)
- netwise_bot/services/supabase_client.py (modify)
- Supabase database schema (modify)

## External Dependencies
- supabase-py (already installed)
- uuid (Python standard library)

## Notes
- Need to ensure bidirectional connections (if A is connected to B, B is connected to A)
- Consider adding a unique constraint on (user1_id, user2_id) to prevent duplicate connections
- Trust score should be validated to be between 1-3
- Connection type should be validated against allowed values
- Need to handle edge cases like self-connections

# Task 2.2: Invite Friends Functionality

## Feature Description
Implementation of the invite system that allows users to invite their friends to join NetWise. This includes generating unique invite links, handling deep linking, and managing the invite flow through the bot.

## Tasks
- [ ] Create `netwise_bot/handlers/connections.py`
  - [ ] Create router for connection-related handlers
  - [ ] Implement `/invite` command handler
  - [ ] Add invite link generation and display
  - [ ] Add error handling and user feedback
- [ ] Update `netwise_bot/services/graph_service.py`
  - [ ] Add `generate_invite_link(telegram_id)` method
  - [ ] Implement invite link format: `t.me/YourBotName?start=invite_{telegram_id}`
  - [ ] Add validation for invite links
- [ ] Update `netwise_bot/handlers/common.py`
  - [ ] Modify `/start` handler to check for invite payload
  - [ ] Add invite acceptance flow
  - [ ] Add welcome message for invited users
- [ ] Add invite tracking in Supabase
  - [ ] Create `invites` table with columns:
    - [ ] id (uuid, primary key)
    - [ ] inviter_id (uuid, foreign key to users.id)
    - [ ] invitee_id (uuid, foreign key to users.id)
    - [ ] status (text: 'pending', 'accepted', 'declined')
    - [ ] created_at (timestamp)
    - [ ] updated_at (timestamp)
  - [ ] Add appropriate indexes and constraints
- [ ] Add RLS policies for the invites table
- [ ] Test the invite flow
  - [ ] Test invite link generation
  - [ ] Test invite acceptance
  - [ ] Test error cases

## Files Involved
- `netwise_bot/handlers/connections.py` (new)
- `netwise_bot/handlers/common.py` (modify)
- `netwise_bot/services/graph_service.py` (modify)
- Supabase database schema (new table)

## External Dependencies
- aiogram (already installed)
- supabase-py (already installed)

## Notes
- Invite links should be unique per user
- Consider adding invite limits per user
- Add proper error handling for invalid invites
- Consider adding invite expiration
- Add logging for invite tracking
- Consider adding invite statistics
- Add proper validation for invite acceptance
- Consider adding invite rewards (e.g., bonus social points)

# Handling Invite Links (Deep Linking)

## Feature Description
Implement deep linking functionality to handle invite links in the Telegram bot. When a user clicks an invite link, the bot should process the invitation, create a connection between users, and handle the trust score setup.

## Tasks
- [ ] Modify `/start` handler to check for invite payload
- [ ] Extract inviter_id from payload
- [ ] Implement accept_invite function in graph_service
- [ ] Add connection creation with default trust/type
- [ ] Send confirmation messages to both users
- [ ] Add error handling for invalid invites
- [ ] Test invite flow end-to-end

## Files Involved
- netwise_bot/handlers/common.py
- netwise_bot/services/graph_service.py
- netwise_bot/services/supabase_client.py

## External Dependencies
- aiogram (already installed)
- supabase-py (already installed)

## Notes
- Need to handle cases where inviter_id is invalid
- Should prevent self-invites
- Consider rate limiting invites to prevent spam
- May need to add logging for invite tracking

# "How do you know?" & Trust Score

## Feature Description
Implementation of the connection trust and relationship type system that allows users to specify how they know each other and establish trust levels. This includes creating states for collecting this information, implementing the UI for selection, and storing this data in the connections table.

## Tasks
- [ ] Create `netwise_bot/states/connection_states.py`
  - [ ] Create `ConnectionTrustStates` class inheriting from `StatesGroup`
  - [ ] Define states: `connection_type`, `trust_score`
- [ ] Create `netwise_bot/keyboards/connections_keyboards.py`
  - [ ] Implement `get_connection_type_keyboard()` with options:
    - [ ] "Worked together"
    - [ ] "Introduction made"
    - [ ] "Met at event"
    - [ ] "Other"
  - [ ] Implement `get_trust_score_keyboard()` with options:
    - [ ] "1 - New acquaintance"
    - [ ] "2 - Known well"
    - [ ] "3 - Close connection"
- [ ] Update `netwise_bot/handlers/connections.py`
  - [ ] Add FSM handlers for connection type and trust score
  - [ ] Implement connection type selection handler
  - [ ] Implement trust score selection handler
  - [ ] Add validation and error handling
  - [ ] Update connection in database after completion
- [ ] Update `netwise_bot/services/graph_service.py`
  - [ ] Add method to update connection details
  - [ ] Add validation for trust scores
  - [ ] Add validation for connection types
- [ ] Update `netwise_bot/services/supabase_client.py`
  - [ ] Add method to update connection details
  - [ ] Add validation for updates
- [ ] Test the full flow
  - [ ] Test connection type selection
  - [ ] Test trust score selection
  - [ ] Test database updates
  - [ ] Test error cases

## Files Involved
- `netwise_bot/states/connection_states.py` (new)
- `netwise_bot/keyboards/connections_keyboards.py` (new)
- `netwise_bot/handlers/connections.py` (update)
- `netwise_bot/services/graph_service.py` (update)
- `netwise_bot/services/supabase_client.py` (update)

## External Dependencies
- aiogram (already installed)
- supabase-py (already installed)

## Notes
- Trust scores should be validated (1-3 range)
- Connection types should be validated against allowed values
- Consider adding descriptions for each trust level
- Add proper error handling for invalid selections
- Consider adding the ability to update trust scores later
- Add logging for trust score changes
- Consider adding trust score impact on matching algorithm
- Add proper validation messages for users

# **Task 2.5: Viewing Connections**

**Feature Description:**
Implementation of functionality to view and manage user connections in the NetWise bot. This includes displaying first-degree connections (direct friends) and their details, with options to view connection types and trust scores.

**Tasks:**
- [ ] **`graph_service.py`:**
  - [ ] Implement `get_friends(telegram_id)` method to fetch first-degree connections
  - [ ] Add filtering options (by trust score, connection type)
  - [ ] Add sorting options (by name, trust score, connection date)
  - [ ] Add pagination support for large connection lists
- [ ] **`handlers/connections.py`:**
  - [ ] Implement `/myconnections` command handler
  - [ ] Create keyboard for connection filtering and sorting
  - [ ] Format connection list with user details
  - [ ] Add pagination controls
  - [ ] Add error handling and user feedback
- [ ] **`keyboards/connections_keyboards.py`:**
  - [ ] Add keyboard for connection list actions
  - [ ] Add keyboard for filtering options
  - [ ] Add keyboard for sorting options
  - [ ] Add keyboard for pagination controls

**Files Involved:**
- `netwise_bot/services/graph_service.py` (update)
- `netwise_bot/handlers/connections.py` (update)
- `netwise_bot/keyboards/connections_keyboards.py` (update)

**External Dependencies:**
- `aiogram` (already installed)
- `supabase-py` (already installed)

**Notes:**
- Consider implementing caching for frequently accessed connection lists
- Add proper error handling for database operations
- Consider adding connection statistics (total connections, average trust score)
- Add logging for connection viewing operations
- Consider adding connection search functionality
- Add proper validation for filter and sort parameters
- Consider adding connection export functionality
- Add proper pagination handling for large connection lists

# Requests Table & Service Foundation

## Feature Description
This feature implements the core data structure and service layer for handling user requests in the NetWise bot. It establishes the foundation for users to create and manage their help requests, which will later be matched with potential helpers through the AI matching system.

## Tasks
- [ ] Create requests table in Supabase with required fields
- [ ] Create request_service.py with basic CRUD operations
- [ ] Implement create_request_record in supabase_client.py
- [ ] Implement fetch_user_requests in supabase_client.py
- [ ] Add error handling and validation
- [ ] Add logging for request operations
- [ ] Write tests for request operations

## Files Involved
- `netwise_bot/services/request_service.py` (new)
- `netwise_bot/services/supabase_client.py` (modify)
- `netwise_bot/utils/constants.py` (modify)
- `netwise_bot/utils/logger.py` (modify)

## External Dependencies
- supabase-py
- python-dotenv
- logging

## Notes
- The requests table will store all user requests for help
- Each request will have a unique ID, requester ID, description, status, and timestamps
- The service layer will handle all request-related operations
- Error handling should be comprehensive to ensure data integrity
- Logging should be implemented for debugging and monitoring

# Formulate Request Flow (FSM & Handlers)

## Feature Description
Implementation of the request creation flow using aiogram's Finite State Machine (FSM) to guide users through the process of creating a help request. This includes creating states for collecting request information, implementing handlers for each state, and managing the request submission process.

## Tasks
- [ ] Create `netwise_bot/states/request_states.py`
  - [ ] Create `RequestStates` class inheriting from `StatesGroup`
  - [ ] Define state: `description`
- [ ] Create `netwise_bot/handlers/requests.py`
  - [ ] Create router for request-related handlers
  - [ ] Implement `/newrequest` command handler
  - [ ] Implement message handler for request description
  - [ ] Add validation for request description
  - [ ] Add error handling and user feedback
- [ ] Create `netwise_bot/keyboards/request_keyboards.py`
  - [ ] Create keyboard for request submission confirmation
  - [ ] Create keyboard for request cancellation
  - [ ] Add appropriate callback data for buttons
- [ ] Update `netwise_bot/services/request_service.py`
  - [ ] Add method to validate request description
  - [ ] Add method to check user's request quota
- [ ] Add comprehensive error handling
  - [ ] Handle validation errors
  - [ ] Handle database errors
  - [ ] Handle quota exceeded errors
- [ ] Add logging for debugging
  - [ ] Log request creation attempts
  - [ ] Log validation errors
  - [ ] Log successful submissions

## Files Involved
- `netwise_bot/states/request_states.py` (new)
- `netwise_bot/handlers/requests.py` (new)
- `netwise_bot/keyboards/request_keyboards.py` (new)
- `netwise_bot/services/request_service.py` (update)
- `netwise_bot/handlers/common.py` (update to register request router)

## External Dependencies
- aiogram (already installed)
- supabase-py (already installed)
- python-dotenv (already installed)

## Notes
- The request description should be clear and specific
- Consider adding character limits for descriptions
- Add proper validation messages for users
- Consider adding request templates or examples
- Add proper error messages for all failure cases
- Consider adding request preview before submission
- Add proper logging for monitoring and debugging
- Consider adding request categories or tags for future features

# **Task 3.3: Social Points & Request Economy (MVP)**

**Feature Description:**
Implementation of the social points system and request economy in the NetWise bot. This includes adding social points tracking, managing free request quotas, and implementing the logic for using points or free requests when creating new requests. The system will also include a monthly reset mechanism for free requests.

**Tasks:**
- [ ] Update `users` table in Supabase:
  - [ ] Add `social_points` (Int, default: 0)
  - [ ] Add `free_requests_remaining` (Int, default: 5)
  - [ ] Add appropriate indexes for performance
- [ ] Create/update `netwise_bot/utils/constants.py`:
  - [ ] Define `POINTS_PER_HELP` (e.g., 10)
  - [ ] Define `POINTS_COST_PER_REQUEST` (e.g., 5)
  - [ ] Define `FREE_REQUESTS_PER_MONTH` (e.g., 5)
- [ ] Update `netwise_bot/services/user_service.py`:
  - [ ] Implement `add_social_points(telegram_id, points)` method
  - [ ] Implement `get_social_points(telegram_id)` method
  - [ ] Implement `use_free_request_or_points(telegram_id, points_cost)` method:
    - [ ] Check `free_requests_remaining`
    - [ ] If > 0, decrement and return success
    - [ ] Else, check `social_points`
    - [ ] If sufficient, deduct points and return success
    - [ ] Return failure if neither available
  - [ ] Implement `reset_monthly_free_requests()` method for scheduler
- [ ] Update `netwise_bot/services/supabase_client.py`:
  - [ ] Add methods for updating social points
  - [ ] Add methods for managing free requests
  - [ ] Add methods for resetting monthly quotas
- [ ] Add logging for points and request economy operations
- [ ] Test all new functionality:
  - [ ] Test points addition
  - [ ] Test points deduction
  - [ ] Test free request usage
  - [ ] Test monthly reset
  - [ ] Test error cases

**Files Involved:**
- `netwise_bot/services/user_service.py` (update)
- `netwise_bot/services/supabase_client.py` (update)
- `netwise_bot/utils/constants.py` (update)
- `netwise_bot/utils/logger.py` (update)
- Supabase database schema (update)

**External Dependencies:**
- `supabase-py` (already installed)
- `python-dotenv` (already installed)
- `logging` (Python standard library)

**Notes:**
- Social points should be non-negative
- Free requests should be non-negative
- Consider adding points history for future features
- Add proper error handling for all operations
- Consider adding points expiration
- Add proper validation for all operations
- Consider adding points rewards for other actions
- Add proper logging for monitoring and debugging

# **Task 3.4: Submitting Request & Keyword-Based Matching Logic**

**Feature Description:**
Implementation of the request submission system and keyword-based matching logic to connect users with potential helpers. This includes creating a matching service that analyzes request descriptions and user profiles to find the most relevant connections, considering factors like skills, industry, and trust scores.

**Tasks:**
- [ ] Create `netwise_bot/services/matching_service.py`
  - [ ] Implement `extract_keywords_from_text(text)` function:
    - [ ] Split text into words
    - [ ] Remove stop words
    - [ ] Return list of relevant keywords
  - [ ] Implement `find_keyword_matches(request_description, requester_id)` function:
    - [ ] Get requester's 1st and 2nd degree connections
    - [ ] Fetch profiles for each connection
    - [ ] Extract keywords from request description
    - [ ] Compare keywords with profile fields
    - [ ] Implement scoring mechanism
    - [ ] Weight scores by connection degree and trust
    - [ ] Filter inactive users
    - [ ] Return ranked list of potential helpers

- [ ] Update `netwise_bot/services/request_service.py`:
  - [ ] Implement `create_request(requester_id, description)` method:
    - [ ] Check free request quota
    - [ ] Create request record
    - [ ] Return request ID
  - [ ] Add error handling and validation
  - [ ] Add logging for request creation

- [ ] Update `netwise_bot/handlers/requests.py`:
  - [ ] Implement request submission callback handler:
    - [ ] Get description from FSM
    - [ ] Call request service to create request
    - [ ] Call matching service to find helpers
    - [ ] Format and display potential helpers
    - [ ] Add "Ask for help" buttons
    - [ ] Handle no matches case
    - [ ] Clear FSM state

**Files Involved:**
- `netwise_bot/services/matching_service.py` (new)
- `netwise_bot/services/request_service.py` (update)
- `netwise_bot/handlers/requests.py` (update)
- `netwise_bot/utils/constants.py` (update if needed)

**External Dependencies:**
- `aiogram`: For bot handlers and FSM
- `supabase-py`: For database operations
- `python-dotenv`: For environment variables
- `nltk` or similar: For text processing (optional)

**Notes:**
- The matching algorithm should be efficient and scalable
- Consider caching frequently accessed profiles
- Add proper error handling for all operations
- Implement logging for debugging
- Consider adding request categories or tags
- Add validation for request descriptions
- Consider adding request templates
- Add proper error messages for users
- Consider adding request search functionality
- Add proper pagination for large result sets

# **Task 3.5: "Спросить, готов ли помочь" Interaction**

**Feature Description:**
Implementation of the interaction flow when a user wants to ask a potential helper for assistance. This includes handling both direct connections (1st degree) and introductions through mutual connections (2nd degree), managing the request flow, and logging all interactions in the request matches log.

**Tasks:**
- [ ] Create `netwise_bot/handlers/interactions.py`
  - [ ] Create router for interaction handlers
  - [ ] Implement callback handler for `ask_help_...`:
    - [ ] Parse `request_id`, `helper_id`, `introducer_id`
    - [ ] Handle 1st degree connections:
      - [ ] Send message to helper with request details
      - [ ] Add Yes/No buttons for helper's response
    - [ ] Handle 2nd degree connections:
      - [ ] Send message to introducer for facilitation
      - [ ] Add Yes/No buttons for introducer's response
    - [ ] Inform requester about sent query
- [ ] Create `request_matches_log` table in Supabase:
  - [ ] Add columns: id, request_id, suggested_user_id, introducer_user_id, status
  - [ ] Add appropriate indexes and constraints
  - [ ] Add RLS policies
- [ ] Update `netwise_bot/services/supabase_client.py`:
  - [ ] Add methods for logging to `request_matches_log`
  - [ ] Add methods for updating match status
- [ ] Update `netwise_bot/services/request_service.py`:
  - [ ] Add methods to update `request_matches_log` status
  - [ ] Add methods to handle helper responses
- [ ] Create `netwise_bot/keyboards/interaction_keyboards.py`:
  - [ ] Implement keyboard for helper's Yes/No response
  - [ ] Implement keyboard for introducer's Yes/No response
- [ ] Test the full interaction flow:
  - [ ] Test 1st degree connection flow
  - [ ] Test 2nd degree connection flow
  - [ ] Test error cases and edge conditions

**Files Involved:**
- `netwise_bot/handlers/interactions.py` (new)
- `netwise_bot/keyboards/interaction_keyboards.py` (new)
- `netwise_bot/services/supabase_client.py` (update)
- `netwise_bot/services/request_service.py` (update)
- Supabase database schema (new table)

**External Dependencies:**
- `aiogram`: For bot handlers and keyboards
- `supabase-py`: For database operations
- `python-dotenv`: For environment variables

**Notes:**
- Need to handle both direct and indirect connections
- Consider adding timeouts for responses
- Add proper error handling for all operations
- Implement logging for debugging
- Consider adding notifications for pending responses
- Add proper validation for all operations
- Consider adding response templates
- Add proper error messages for users
- Consider adding response tracking
- Add proper pagination for large result sets

# Daily Digests & Notifications

## Feature Description
Implement a system for sending daily digests to users containing relevant requests they can help with, based on their skills and connections. This includes setting up a scheduler, implementing notification logic, and handling user responses to digest items.

## Tasks
- [ ] Create scheduler setup with AsyncIOScheduler
- [ ] Implement daily digest generation logic
- [ ] Create notification service for sending digests
- [ ] Implement "Готов помочь" (Ready to Help) interaction flow
- [ ] Add activity history tracking for help offers
- [ ] Set up inactivity management system
- [ ] Test daily digest delivery and interaction flow

## Files Involved
- `netwise_bot/scheduler.py` (new)
- `netwise_bot/services/notification_service.py` (new)
- `netwise_bot/services/request_service.py` (modify)
- `netwise_bot/handlers/interactions.py` (modify)
- `netwise_bot/services/user_service.py` (modify)
- `main.py` (modify)

## External Dependencies
- apscheduler
- aiogram
- supabase-py

## Notes
- Scheduler should run daily at 9 AM local time
- Need to handle timezone differences
- Consider rate limiting for digest generation
- Implement proper error handling for failed digest deliveries
- Add logging for monitoring digest delivery success/failure
- Consider implementing a retry mechanism for failed deliveries

# **Task 4.4: Inactivity Management**

**Feature Description:**
Implementation of a system to manage inactive users in the NetWise bot. This includes tracking user activity, deactivating users who haven't been active for a specified period, and optionally sending reminder notifications before deactivation. The system will help maintain an active user base and improve the quality of matches.

**Tasks:**
- [ ] **`user_service.py`:**
  - [ ] Implement `deactivate_inactive_users(days_inactive_threshold)` method:
    - [ ] Query users where `last_active_at` is older than threshold
    - [ ] Set `is_active_in_search = false` for inactive users
    - [ ] Add logging for deactivated users
    - [ ] Return count of deactivated users
- [ ] **`scheduler.py`:**
  - [ ] Add job to run `deactivate_inactive_users_job` daily
  - [ ] Configure job to run at a suitable time (e.g., midnight)
  - [ ] Add error handling and logging
- [ ] **(Optional) `notification_service.py`:**
  - [ ] Implement `send_inactive_reminders` method:
    - [ ] Find users approaching inactivity threshold
    - [ ] Send reminder message about potential deactivation
    - [ ] Add logging for sent reminders
- [ ] **Test the inactivity management system:**
  - [ ] Test user deactivation
  - [ ] Test scheduler job execution
  - [ ] Test reminder notifications (if implemented)
  - [ ] Verify logging and error handling

**Files Involved:**
- `netwise_bot/services/user_service.py` (update)
- `netwise_bot/scheduler.py` (update)
- `netwise_bot/services/notification_service.py` (update)
- `main.py` (update to register scheduler job)

**External Dependencies:**
- `apscheduler` (already installed)
- `aiogram` (already installed)
- `supabase-py` (already installed)

**Notes:**
- Default inactivity threshold should be 30 days
- Consider adding a grace period before deactivation
- Add proper error handling for database operations
- Implement logging for monitoring and debugging
- Consider adding reactivation functionality
- Add proper validation for inactivity threshold
- Consider adding activity statistics
- Add proper error messages for users