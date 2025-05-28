**Project Root Name:** `netwise`

```
netwise/
├── .github/
│   └── workflows/
│       └── ci_cd.yml           # GitHub Actions for CI/CD
├── .vscode/                    # Optional: VSCode specific settings
│   └── settings.json
├── app/                        # FastAPI Backend Application
│   ├── __init__.py
│   ├── api/                    # API Routers (Endpoints)
│   │   ├── __init__.py
│   │   ├── deps.py             # FastAPI dependencies (e.g., get_current_user)
│   │   ├── users.py            # User profile, registration, activity
│   │   ├── connections.py      # Connection graph, invites, trust
│   │   ├── requests.py         # Request creation, matching, responses
│   │   └── payments.py         # Payment and subscription handling
│   ├── core/                   # Core settings, configurations, security
│   │   ├── __init__.py
│   │   ├── config.py           # Environment variables, app settings
│   │   └── security.py         # Authentication helpers (Telegram ID based)
│   ├── db/                     # Database interaction layer
│   │   ├── __init__.py
│   │   ├── supabase_client.py  # Supabase client setup and utility functions
│   │   ├── user_repo.py        # Repository for user data operations
│   │   ├── connection_repo.py  # Repository for connection data operations
│   │   ├── request_repo.py     # Repository for request data operations
│   │   └── activity_repo.py    # Repository for activity history
│   ├── models/                 # Pydantic models for data validation & serialization
│   │   ├── __init__.py
│   │   ├── user_models.py
│   │   ├── connection_models.py
│   │   ├── request_models.py
│   │   ├── payment_models.py
│   │   └── common_models.py    # Common response models, enums
│   ├── services/               # Business logic services
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── connection_service.py
│   │   ├── request_service.py
│   │   ├── matching_service.py   # MVP: Keyword/profile matching; Future: AI embeddings
│   │   ├── notification_service.py # Daily digests, reminders
│   │   ├── payment_service.py    # Stripe integration logic
│   │   └── social_points_service.py # Manages social points economy
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   └── helpers.py          # General helper functions
│   └── main.py                 # FastAPI application entry point
├── bot/                        # Aiogram Telegram Bot Application
│   ├── __init__.py
│   ├── handlers/               # Bot command, message, callback handlers
│   │   ├── __init__.py
│   │   ├── common_handlers.py  # /start, /help, unknown commands
│   │   ├── user_handlers.py    # Profile creation/update, invites
│   │   ├── request_handlers.py # New request, view requests, respond to digests
│   │   └── admin_handlers.py   # (Optional) For bot admin tasks
│   ├── keyboards/              # Inline and reply keyboard layouts
│   │   ├── __init__.py
│   │   ├── inline_keyboards.py
│   │   └── reply_keyboards.py
│   ├── middlewares/            # (Optional) Aiogram middlewares
│   │   └── __init__.py
│   ├── states/                 # FSM states for conversation flows
│   │   ├── __init__.py
│   │   ├── user_states.py
│   │   └── request_states.py
│   ├── services/               # Services specific to the bot
│   │   ├── __init__.py
│   │   └── api_client.py       # Client to communicate with the FastAPI backend
│   ├── utils/                  # Bot-specific utility functions
│   │   ├── __init__.py
│   │   └── formatters.py       # Functions to format messages for Telegram
│   └── main.py                 # Aiogram bot entry point
├── scripts/                    # Utility scripts (e.g., one-off tasks, cron job definitions if not in Railway)
│   └── send_digests.py         # (If running digests via a separate script/cron)
├── tests/                      # Unit and integration tests
│   ├── __init__.py
│   ├── app_tests/              # Tests for the FastAPI backend
│   │   ├── __init__.py
│   │   ├── test_users_api.py
│   │   ├── test_connections_api.py
│   │   ├── test_requests_api.py
│   │   └── test_matching_service.py
│   └── bot_tests/              # Tests for the Telegram bot
│       ├── __init__.py
│       └── test_user_handlers.py
├── .env.example                # Example environment variables
├── .gitignore
├── Dockerfile                  # For containerizing the app (Backend + Bot or separate)
├── Procfile                    # For Railway deployment (if not using Dockerfile solely)
├── pyproject.toml              # For Poetry (or requirements.txt for pip)
├── README.md
└── supabase_schema.sql         # SQL script to define Supabase tables, RLS, functions (optional, for reference/backup)
```

---

## What to implement in each file (detailed)

### `netwise/.github/workflows/ci_cd.yml`
*   **Implementation:** Define GitHub Actions workflow.
    *   Trigger on push/PR to `main` (and `develop` if used).
    *   Set up Python environment.
    *   Install dependencies (from `pyproject.toml` or `requirements.txt`).
    *   Run linters (e.g., Ruff/Flake8, Black).
    *   Run tests (pytest).
    *   Build Docker image (if using Docker).
    *   Deploy to Railway (using Railway CLI or GitHub integration).
*   **Subtasks:**
    *   **Implement:** Workflow steps.
    *   **Test:** Run workflow on a test branch.
    *   **Docs:** Comments in YAML, README section on deployment.

---

### `netwise/app/` (FastAPI Backend)

#### `app/main.py`
*   **Implementation:**
    *   Create FastAPI app instance.
    *   Include API routers (users, connections, requests, payments).
    *   Configure CORS (if TWA or other web clients need it).
    *   Add global exception handlers.
    *   (Optional) Lifespan events for startup/shutdown (e.g., init Supabase client).
*   **Subtasks:**
    *   **Implement:** Basic FastAPI app setup.
    *   **Test:** Simple health check endpoint.
    *   **Docs:** Docstring for the module.

#### `app/api/deps.py`
*   **Implementation:**
    *   `get_supabase_client()`: Dependency to provide Supabase client to path operations.
    *   `get_current_user(telegram_id: int = Header(...))`: Dependency to "authenticate" user based on Telegram ID passed in a header (or from a token if evolving). Fetches basic user info. For MVP, this might be simple; for security, a signed token from the bot could be better.
*   **Subtasks:**
    *   **Implement:** Dependency functions.
    *   **Test:** Unit test with mock Supabase client, mock headers.
    *   **Docs:** Docstrings for functions.

#### `app/api/users.py` (`router_users`)
*   **Endpoints from ADD 4.2:**
    *   `POST /users/register` (or implicit on first interaction logic, called by bot):
        *   **Implementation:** Receives Telegram user data. Calls `user_service.create_or_get_user`.
        *   **Subtasks:** Implement, test (new user, existing user), docs.
    *   `PUT /users/{telegram_id}/profile`:
        *   **Implementation:** Receives `UserProfileUpdate` model. Calls `user_service.update_user_profile`. Uses `get_current_user` to ensure user updates own profile.
        *   **Subtasks:** Implement, test (valid update, invalid data, auth), docs.
    *   `GET /users/{telegram_id}/profile`:
        *   **Implementation:** Calls `user_service.get_user_profile`.
        *   **Subtasks:** Implement, test (user found, not found), docs.
    *   `POST /users/{telegram_id}/invite`: (Handled by `connections.py` as it relates to graph)
    *   `GET /users/{telegram_id}/digest`:
        *   **Implementation:** Calls `notification_service.get_daily_digest_for_user`.
        *   **Subtasks:** Implement, test (digest content, empty digest), docs.
    *   `GET /users/{telegram_id}/activity`:
        *   **Implementation:** Calls `user_service.get_user_activity_history`.
        *   **Subtasks:** Implement, test (history present, empty history), docs.
    *   `PUT /users/{telegram_id}/activity_settings`:
        *   **Implementation:** For `is_active_in_search` updates. Calls `user_service.update_activity_settings`.
        *   **Subtasks:** Implement, test, docs.
*   **Subtasks (General for file):**
    *   **Implement:** All endpoint functions.
    *   **Test:** Integration tests for each endpoint, unit tests for logic if complex within endpoint.
    *   **Docs:** OpenAPI docs via FastAPI docstrings, README updates.

#### `app/api/connections.py` (`router_connections`)
*   **Endpoints from ADD 4.2:**
    *   `POST /users/{telegram_id}/invite`:
        *   **Implementation:** Calls `connection_service.generate_invite_link` (or simply returns data for bot to make link).
        *   **Subtasks:** Implement, test, docs.
    *   `POST /connections/accept_invite`: (or similar, when an invite link is used)
        *   **Implementation:** Receives inviter ID (from link payload) and invitee (current user). Calls `connection_service.accept_invite`.
        *   **Subtasks:** Implement, test (valid invite, invalid, already connected), docs.
    *   `POST /connections`: (For direct "add friend" if not using invites initially)
        *   **Implementation:** `user1_id` (current user), `user2_id` (friend's Telegram ID), `connection_type`. Calls `connection_service.create_connection`.
        *   **Subtasks:** Implement, test, docs.
    *   `GET /users/{telegram_id}/connections`:
        *   **Implementation:** Calls `connection_service.get_user_connections` (1st degree).
        *   **Subtasks:** Implement, test, docs.
    *   `PUT /connections/{connection_id}/trust`:
        *   **Implementation:** Receives `TrustScoreUpdate` model. Calls `connection_service.update_trust_score`. Ensure user making update is part of the connection.
        *   **Subtasks:** Implement, test, docs.
*   **Subtasks (General for file):**
    *   **Implement:** All endpoint functions.
    *   **Test:** Integration tests for each endpoint.
    *   **Docs:** OpenAPI docs.

#### `app/api/requests.py` (`router_requests`)
*   **Endpoints from ADD 4.2:**
    *   `POST /requests`:
        *   **Implementation:** Receives `RequestCreate` model. Calls `request_service.create_request`. Deducts social points or checks free tier/subscription via `social_points_service`.
        *   **Subtasks:** Implement, test (success, insufficient points/quota), docs.
    *   `GET /requests/{telegram_id}/active`:
        *   **Implementation:** Calls `request_service.get_active_requests_for_user`.
        *   **Subtasks:** Implement, test, docs.
    *   `GET /requests/match/{request_id}`:
        *   **Implementation:** Calls `matching_service.find_matches_for_request`.
        *   **Subtasks:** Implement, test (matches found, no matches), docs.
    *   `POST /requests/{request_id}/respond`:
        *   **Implementation:** User (helper) indicates willingness. `request_id`, `helper_telegram_id`, `response_status` ("willing_to_help", "not_interested"). Calls `request_service.process_helper_response`. Updates `request_matches_log`. If "willing_to_help", notifies requester. Awards social points via `social_points_service`.
        *   **Subtasks:** Implement, test, docs.
    *   `PUT /requests/{request_id}/status`:
        *   **Implementation:** Requester updates request status (e.g., "resolved", "closed"). Calls `request_service.update_request_status`.
        *   **Subtasks:** Implement, test, docs.
*   **Subtasks (General for file):**
    *   **Implement:** All endpoint functions.
    *   **Test:** Integration tests for each endpoint.
    *   **Docs:** OpenAPI docs.

#### `app/api/payments.py` (`router_payments`)
*   **Endpoints from ADD 4.2:**
    *   `POST /payments/subscribe`:
        *   **Implementation:** Receives `SubscriptionRequest` (plan_id). Calls `payment_service.create_subscription_checkout_session` (e.g., Stripe). Returns checkout URL.
        *   **Subtasks:** Implement, test (mock Stripe API), docs.
    *   `POST /payments/portal`:
        *   **Implementation:** Calls `payment_service.create_billing_portal_session` (e.g., Stripe). Returns portal URL.
        *   **Subtasks:** Implement, test (mock Stripe API), docs.
    *   `POST /payments/webhook`:
        *   **Implementation:** Receives webhook events from payment provider (e.g., Stripe). Calls `payment_service.handle_webhook_event`. Verifies webhook signature.
        *   **Subtasks:** Implement, test (different event types, signature verification), docs.
*   **Subtasks (General for file):**
    *   **Implement:** All endpoint functions.
    *   **Test:** Integration tests, careful mocking of Stripe.
    *   **Docs:** OpenAPI docs, notes on Stripe webhook setup.

#### `app/core/config.py`
*   **Implementation:**
    *   `Settings` class (using Pydantic `BaseSettings`) to load env vars:
        *   `SUPABASE_URL`, `SUPABASE_KEY` (service role key for backend)
        *   `OPENAI_API_KEY`
        *   `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET`
        *   `BOT_TOKEN` (though bot might manage its own)
        *   `BACKEND_API_URL` (for bot to know where backend is)
        *   `ENVIRONMENT` (dev, prod)
        *   Free request limits, social points costs.
*   **Subtasks:**
    *   **Implement:** Settings class and variable definitions.
    *   **Test:** Check loading from dummy .env.
    *   **Docs:** Comments explaining each setting.

#### `app/core/security.py`
*   **Implementation:**
    *   For MVP, Telegram ID might be passed in a header.
    *   `verify_telegram_id_header(telegram_id: int = Header(...))`: Simple check.
    *   Future: Functions for creating/verifying JWTs if moving beyond simple header auth.
*   **Subtasks:**
    *   **Implement:** Auth helper functions.
    *   **Test:** Unit tests for verification logic.
    *   **Docs:** Docstrings.

#### `app/db/supabase_client.py`
*   **Implementation:**
    *   Initialize Supabase client using `supabase-py`.
    *   `get_db()`: Function to return an initialized client instance (can be used by FastAPI `Depends`).
*   **Subtasks:**
    *   **Implement:** Client initialization.
    *   **Test:** Mock connection or test a simple Supabase call.
    *   **Docs:** Module docstring.

#### `app/db/user_repo.py`, `connection_repo.py`, `request_repo.py`, `activity_repo.py`
*   **Implementation (General for all repos):**
    *   Classes or sets of functions for CRUD operations on respective Supabase tables.
    *   Use `supabase-py` client methods (`table().select()`, `insert()`, `update()`, `delete()`, `rpc()`).
    *   Handle potential Supabase errors.
    *   Example `user_repo.py`:
        *   `get_user_by_telegram_id(client, telegram_id)`
        *   `create_user(client, user_data)`
        *   `update_user(client, telegram_id, update_data)`
        *   `get_user_social_points(client, telegram_id)`
        *   `update_user_social_points(client, telegram_id, new_points)`
        *   `decrement_free_requests(client, telegram_id)`
*   **Subtasks (For each repo file):**
    *   **Implement:** CRUD functions for all necessary operations on the corresponding table(s).
    *   **Test:** Unit tests mocking Supabase client responses for each function.
    *   **Docs:** Docstrings for each function.

#### `app/models/user_models.py`, `connection_models.py`, `request_models.py`, `payment_models.py`, `common_models.py`
*   **Implementation (General for all models):**
    *   Pydantic models for:
        *   API request bodies (e.g., `UserProfileUpdate`, `RequestCreate`, `TrustScoreUpdate`).
        *   API response bodies (e.g., `UserProfileResponse`, `RequestDetails`).
        *   Internal data structures if needed.
        *   Enums defined in `common_models.py` (e.g., `RequestStatus`, `ConnectionType`, `SubscriptionTier`).
    *   Example `user_models.py`:
        *   `UserBase(BaseModel)`: common fields.
        *   `UserCreate(UserBase)`: for registration.
        *   `UserProfileUpdate(BaseModel)`: fields for profile update.
        *   `UserResponse(UserBase)`: for API responses, includes `id`, `created_at`, etc.
*   **Subtasks (For each model file):**
    *   **Implement:** Define Pydantic models based on DB schema and API needs.
    *   **Test:** Pydantic models are self-validating; no specific tests usually needed unless custom validators.
    *   **Docs:** Docstrings for models and fields (FastAPI uses these for OpenAPI).

#### `app/services/user_service.py`
*   **Implementation:** Business logic for user operations.
    *   `create_or_get_user(telegram_id, name, username, etc.)`: Uses `user_repo`.
    *   `update_user_profile(telegram_id, profile_data)`: Uses `user_repo`. Validates data.
    *   `get_user_profile(telegram_id)`: Uses `user_repo`.
    *   `get_user_activity_history(telegram_id)`: Uses `activity_repo`.
    *   `update_activity_settings(telegram_id, settings_data)`: Uses `user_repo`.
*   **Subtasks (For each function):**
    *   **Implement:** Business logic, calls to repository.
    *   **Test:** Unit tests with mocked repository.
    *   **Docs:** Docstrings.

#### `app/services/connection_service.py`
*   **Implementation:**
    *   `generate_invite_link_data(telegram_id)`: Creates data for an invite link.
    *   `accept_invite(inviter_id, invitee_telegram_id, connection_type, trust_score)`: Uses `connection_repo`. Checks for existing connections.
    *   `create_connection(user1_id, user2_id, connection_type, trust_score)`: Uses `connection_repo`.
    *   `get_user_connections(telegram_id, degree=1)`: Uses `connection_repo`. For degree 2, might involve more complex queries or multiple calls.
    *   `update_trust_score(connection_id, new_score, user_making_change_id)`: Uses `connection_repo`.
*   **Subtasks (For each function):**
    *   **Implement:** Business logic.
    *   **Test:** Unit tests with mocked repository.
    *   **Docs:** Docstrings.

#### `app/services/request_service.py`
*   **Implementation:**
    *   `create_request(requester_id, description_text)`: Uses `request_repo`. Calls `social_points_service` to deduct points/check quota.
    *   `get_active_requests_for_user(telegram_id)`: Uses `request_repo`.
    *   `process_helper_response(request_id, helper_id, response_status)`: Uses `request_repo` to update `request_matches_log`. Calls `notification_service` to notify requester. Calls `social_points_service` to award points if help offered.
    *   `update_request_status(request_id, new_status, user_id)`: Uses `request_repo`. Ensure `user_id` is the requester.
*   **Subtasks (For each function):**
    *   **Implement:** Business logic.
    *   **Test:** Unit tests with mocked dependencies.
    *   **Docs:** Docstrings.

#### `app/services/matching_service.py`
*   **Implementation (MVP: Keyword/Profile-based):**
    *   `find_matches_for_request(request_id)`:
        1.  Fetch request details (`request_repo`).
        2.  Fetch requester's 1st and 2nd degree connections (`connection_repo`, `user_repo`).
        3.  Extract keywords from request description.
        4.  Loop through connections:
            *   Fetch connection's profile (`user_repo`).
            *   Match keywords against `skills`, `role`, `industry`, `goals`, `interests`.
            *   Calculate a relevance score (consider connection degree, trust score, activity).
        5.  Filter and rank potential helpers.
        6.  Log suggestions in `request_matches_log` (`request_repo`).
        7.  Return top N matches.
    *   Future: `_generate_embedding(text)` using OpenAI. `_find_similar_vectors(...)` using Supabase pg_vector.
*   **Subtasks:**
    *   **Implement:** Keyword extraction, profile matching logic, scoring.
    *   **Test:** Unit tests with mock profiles and requests, testing scoring logic.
    *   **Docs:** Docstrings, explanation of matching algorithm.

#### `app/services/notification_service.py`
*   **Implementation:**
    *   `get_daily_digest_for_user(telegram_id)`:
        1.  Fetch requests where this user might be a good match (based on pre-calculated matches or run a light version of `matching_service`).
        2.  Limit to 20 relevant requests.
        3.  Format for display.
    *   `send_request_match_notification(requester_id, helper_id, request_id)`: (To notify requester when someone offers help - called by bot or direct from backend).
    *   `send_activity_reminder(telegram_id)`: Logic for inactive user reminders.
*   **Subtasks:**
    *   **Implement:** Digest generation, notification logic.
    *   **Test:** Unit tests for digest content, reminder conditions.
    *   **Docs:** Docstrings.

#### `app/services/payment_service.py`
*   **Implementation:**
    *   `initialize_stripe()`: Set up Stripe API key.
    *   `create_subscription_checkout_session(user_id, plan_id)`: Interact with Stripe API. Store `stripe_customer_id` on user if not present.
    *   `create_billing_portal_session(user_id)`: Interact with Stripe API.
    *   `handle_webhook_event(payload, sig_header)`:
        *   Verify Stripe signature.
        *   Process events like `checkout.session.completed`, `invoice.payment_succeeded`, `customer.subscription.deleted`, etc.
        *   Update user's subscription status, `free_requests_remaining`, `social_points` in DB via `user_repo` and `subscriptions` table.
*   **Subtasks:**
    *   **Implement:** Stripe API interactions, webhook handling logic.
    *   **Test:** Unit tests mocking Stripe API calls and webhook payloads.
    *   **Docs:** Docstrings, notes on Stripe setup.

#### `app/services/social_points_service.py`
*   **Implementation:**
    *   `POINTS_FOR_HELPING`, `POINTS_PER_REQUEST_COST`.
    *   `award_points_for_help(user_id, request_id)`: Update `user.social_points`, log in `activity_history` via respective repos.
    *   `can_make_request(user_id)`: Check `user.free_requests_remaining` or `user.social_points` or subscription.
    *   `charge_for_request(user_id)`: Decrement free requests or social points. If neither, return error/status.
*   **Subtasks:**
    *   **Implement:** Points logic.
    *   **Test:** Unit tests for different scenarios (free tier, points, subscription).
    *   **Docs:** Docstrings.

#### `app/utils/helpers.py`
*   **Implementation:** Generic utility functions, e.g., date formatting, string manipulation, not specific to any domain.
*   **Subtasks:**
    *   **Implement:** As needed.
    *   **Test:** Unit tests.
    *   **Docs:** Docstrings.

---

### `netwise/bot/` (Aiogram Telegram Bot)

#### `bot/main.py`
*   **Implementation:**
    *   Initialize `Bot` and `Dispatcher` instances.
    *   Load settings (API token, backend URL).
    *   Initialize `APIClient`.
    *   Register handlers (command, message, callback).
    *   Register middlewares (if any).
    *   Start polling or set up webhook.
*   **Subtasks:**
    *   **Implement:** Bot setup and startup.
    *   **Test:** Basic bot response to `/start`.
    *   **Docs:** Module docstring.

#### `bot/handlers/common_handlers.py`
*   **Implementation:**
    *   `cmd_start(message: Message, state: FSMContext, api_client: APIClient)`: Handle `/start`. Register/get user via `api_client`. Send welcome message, main menu keyboard.
    *   `cmd_help(message: Message)`: Send help message.
    *   `unknown_command_handler(message: Message)`: Gentle reply for unknown commands.
*   **Subtasks:**
    *   **Implement:** Handler functions.
    *   **Test:** Unit tests mocking `Message` and `APIClient`.
    *   **Docs:** Docstrings.

#### `bot/handlers/user_handlers.py`
*   **Implementation:**
    *   Profile creation/update flow (using FSM - `UserStates`):
        *   `cmd_profile(message: Message, state: FSMContext, api_client: APIClient)`: Show current profile, offer edit.
        *   Handlers for each profile field input (name, role, industry, etc.).
        *   Save profile data via `api_client`.
    *   Invite friends flow:
        *   `cmd_invite(message: Message, api_client: APIClient)`: Get invite link data from backend, format and send to user.
    *   View activity history:
        *   `cmd_activity(message: Message, api_client: APIClient)`: Fetch and display activity.
*   **Subtasks:**
    *   **Implement:** Handler functions, FSM logic.
    *   **Test:** Unit tests for FSM transitions and API calls.
    *   **Docs:** Docstrings.

#### `bot/handlers/request_handlers.py`
*   **Implementation:**
    *   New request flow (using FSM - `RequestStates`):
        *   `cmd_new_request(message: Message, state: FSMContext, api_client: APIClient)`: Start request creation. Check if user can make request (points/quota) via `api_client`.
        *   Handler for request description input.
        *   Confirm and send request via `api_client`.
    *   View active requests:
        *   `cmd_my_requests(message: Message, api_client: APIClient)`: Fetch and display user's active requests.
    *   Daily digest interaction:
        *   Callback query handler for "Готов помочь" button on digest items. Sends response to backend via `api_client`.
    *   Responding to a match suggestion:
        *   Callback query handler for "Спросить, готов ли помочь" button. Sends this intent to backend.
*   **Subtasks:**
    *   **Implement:** Handler functions, FSM logic.
    *   **Test:** Unit tests for FSM and API calls.
    *   **Docs:** Docstrings.

#### `bot/keyboards/inline_keyboards.py`, `reply_keyboards.py`
*   **Implementation:**
    *   Functions that generate `InlineKeyboardMarkup` and `ReplyKeyboardMarkup` objects.
    *   Examples: Main menu, profile edit options, request confirmation, digest action buttons.
*   **Subtasks:**
    *   **Implement:** Keyboard generation functions.
    *   **Test:** Visual inspection during bot testing.
    *   **Docs:** Comments explaining keyboard purpose.

#### `bot/states/user_states.py`, `request_states.py`
*   **Implementation:**
    *   Define FSM `StatesGroup` and `State` objects for multi-step conversations (profile creation, new request).
*   **Subtasks:**
    *   **Implement:** State definitions.
    *   **Test:** Covered by handler tests using these states.
    *   **Docs:** Docstrings for state groups.

#### `bot/services/api_client.py`
*   **Implementation:**
    *   `APIClient` class with methods to make HTTP requests to the FastAPI backend.
    *   Uses `httpx` (async HTTP client).
    *   Methods like `register_user`, `update_profile`, `create_request`, `get_matches`, `respond_to_request`, etc.
    *   Handles adding `telegram_id` header.
    *   Error handling for API responses.
*   **Subtasks:**
    *   **Implement:** Client class and API call methods.
    *   **Test:** Unit tests mocking `httpx` responses.
    *   **Docs:** Docstrings for class and methods.

#### `bot/utils/formatters.py`
*   **Implementation:**
    *   Functions to format data from API into user-friendly Telegram messages (e.g., `format_user_profile`, `format_request_summary`, `format_digest_item`).
    *   Handles Markdown/HTML formatting for Telegram.
*   **Subtasks:**
    *   **Implement:** Formatting functions.
    *   **Test:** Unit tests for output strings.
    *   **Docs:** Docstrings.

---

### `netwise/scripts/send_digests.py` (if not using a PaaS scheduler or Supabase cron)
*   **Implementation:**
    *   Script to be run daily by a cron job.
    *   Fetches all active users.
    *   For each user, calls backend API endpoint `/users/{telegram_id}/digest`.
    *   Sends the digest message directly via Telegram Bot API (or calls a bot endpoint to do it).
    *   Alternatively, the backend API could have a `/trigger-digests` endpoint that iterates and sends (or queues for sending).
*   **Subtasks:**
    *   **Implement:** Script logic.
    *   **Test:** Manually run script, check logs, check a test user receives digest.
    *   **Docs:** Comments, README on how to set up cron.

---

### `netwise/tests/`
*   **Implementation:**
    *   Use `pytest` and `pytest-asyncio`.
    *   `app_tests/`: Integration tests for API endpoints (mocking Supabase calls or using a test DB instance if feasible). Unit tests for services and complex logic.
    *   `bot_tests/`: Unit tests for handlers (mocking `Message`, `CallbackQuery`, `APIClient`).
*   **Subtasks:** Write tests for each implemented module/function as outlined above.

---

### Root Directory Files

#### `.env.example`
*   **Implementation:** List all required environment variables with placeholder or example values.
    ```
    # Backend Settings
    SUPABASE_URL=your_supabase_url
    SUPABASE_KEY=your_supabase_service_role_key # For backend
    OPENAI_API_KEY=your_openai_key
    STRIPE_API_KEY=your_stripe_secret_key
    STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
    ENVIRONMENT=development # development or production

    # Bot Settings
    BOT_TOKEN=your_telegram_bot_token
    BACKEND_API_BASE_URL=http://localhost:8000/api/v1 # URL for bot to reach backend

    # Application Logic Settings
    FREE_REQUESTS_PER_MONTH=5
    SOCIAL_POINTS_COST_PER_REQUEST=1
    SOCIAL_POINTS_AWARD_FOR_HELP=10
    ```
*   **Subtasks:** Create and maintain.

#### `Dockerfile`
*   **Implementation:**
    *   Choose a Python base image.
    *   Set up working directory.
    *   Copy `pyproject.toml` and `poetry.lock` (or `requirements.txt`).
    *   Install dependencies.
    *   Copy application code (`app/`, `bot/`).
    *   Define `CMD` to run Uvicorn for the backend API. If bot runs in same container, use a process manager like `supervisor` or run bot as background process. Simpler to have two services on Railway.
*   **Subtasks:** Write Dockerfile, test build.

#### `Procfile` (If not using Dockerfile solely for Railway, or for local dev with `honcho`/`foreman`)
*   **Implementation:**
    *   `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
    *   `bot: python bot/main.py`
    *   (Railway might run these as separate services from same repo)
*   **Subtasks:** Define process types.

#### `pyproject.toml` (using Poetry)
*   **Implementation:** Define project metadata, dependencies, dev dependencies (pytest, ruff).
*   **Subtasks:** Initialize Poetry (`poetry init`), add dependencies (`poetry add ...`).

#### `README.md`
*   **Implementation:** Project overview, setup instructions (local dev, env vars), deployment info, API usage notes (if needed beyond OpenAPI).
*   **Subtasks:** Write and maintain.

#### `supabase_schema.sql`
*   **Implementation:** (Optional, but good for tracking)
    *   `CREATE TABLE` statements for `users`, `connections`, `requests`, `request_matches_log`, `activity_history`, `subscriptions`.
    *   Define PKs, FKs, constraints, indexes (including on `telegram_id`, vector columns).
    *   Define Enums.
    *   Row Level Security policies.
    *   (Can be generated/managed via Supabase UI, but having a script is good for version control).
*   **Subtasks:** Define schema based on ADD 4.3.

---

## External Dependencies (for `pyproject.toml` or `requirements.txt`)

**Core Backend (`app/`):**
*   `fastapi`
*   `uvicorn[standard]` (for running FastAPI)
*   `pydantic[email]` (for email validation if needed, BaseModel is core)
*   `supabase-py` (Supabase Python client)
*   `httpx` (for OpenAI and other external HTTP calls from backend)
*   `openai`
*   `python-dotenv` (for loading .env files)
*   `stripe` (Python SDK for Stripe)
*   `apscheduler` (If handling scheduled tasks like digests within the app, or use Railway Cron)
*   `passlib[bcrypt]` (if custom password hashing needed later, not for MVP with Telegram ID)
*   `python-jose[cryptography]` (if JWTs are used later)

**Telegram Bot (`bot/`):**
*   `aiogram`
*   `httpx` (for `api_client.py`)
*   `python-dotenv`

**Development & Testing:**
*   `pytest`
*   `pytest-asyncio` (for testing async code)
*   `pytest-cov` (for coverage reports)
*   `ruff` (linter and formatter) or `flake8`, `black`, `isort`
*   `mypy` (static type checker)
*   `httpx` (also for test client in FastAPI)

---

This detailed structure should provide a solid foundation for NetWise MVP development. Remember to implement features incrementally and test thoroughly at each stage.