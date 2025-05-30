## NetWise MVP: Detailed Implementation Plan

**Legend:**
*   `- [ ]` Pending
*   `- [x]` Done
*   `Sub-task`
    *   `Sub-sub-task`

---

### Phase 0: Foundation & Setup (Essential Before Feature Development)

*   `- [x]` **Project Initialization & Environment Setup**
    *   `- [x]` Create Git repository (e.g., GitHub).
    *   `- [x]` Set up project structure (folders as outlined in ADD).
    *   `- [x]` Initialize Python environment (Poetry or venv + pip).
        *   `- [x]` Install core dependencies: `fastapi`, `uvicorn`, `pydantic`, `aiogram`, `httpx`, `python-dotenv`.
    *   `- [x]` Create `.gitignore` file.
    *   `- [x]` Create `.env.example` file with initial placeholder variables.
    *   `- [x]` Local `.env` file setup for development.
*   `- [x]` **Supabase Setup**
    *   `- [x]` Create Supabase project.
    *   `- [x]` Note Supabase URL and `anon` & `service_role` keys. Add to `.env`.
    *   `- [x]` Design initial DB schema for `users` table (core fields only for now).
        *   `- [x]` Implement `users` table in Supabase UI or via SQL.
    *   `- [x]` Set up basic RLS for `users` table (users can only see/edit their own data).
*   `- [x]` **Basic Backend API Setup (FastAPI)**
    *   `- [x]` `app/main.py`: Initialize FastAPI app.
    *   `- [x]` `app/core/config.py`: Load environment variables.
    *   `- [x]` `app/db/supabase_client.py`: Function to initialize and provide Supabase client.
    *   `- [x]` Create a simple health check endpoint (e.g., `/health`).
*   `- [x]` **Basic Telegram Bot Setup (aiogram)**
    *   `- [x]` `bot/main.py`: Initialize Bot and Dispatcher.
    *   `- [x]` Load Bot Token from `.env`.
    *   `- [x]` Implement a basic `/start` command handler that replies with a welcome message.
*   `- [x]` **CI/CD Initial Setup (GitHub Actions on Railway)**
    *   `- [x]` Connect Railway to GitHub repository.
    *   `- [x]` Create basic `Dockerfile` for backend API.
    *   `- [x]` Create basic `Dockerfile` for bot (or plan to run in same container if simple enough for now).
    *   `- [x]` Create initial `.github/workflows/ci_cd.yml` for backend:
        *   `- [x]` Trigger on push to `main`.
        *   `- [x]` Checkout code.
        *   `- [x]` Set up Python.
        *   `- [x]` Install dependencies.
        *   `- [x]` (Placeholder for tests & linters).
        *   `- [x]` Deploy to Railway (basic backend service).
    *   `- [x]` Do the same for the bot service on Railway.
*   `- [x]` **Linting & Formatting**
    *   `- [x]` Choose and configure linters/formatters (e.g., Ruff/Black).
    *   `- [x]` Add linting/formatting checks to CI/CD.

---

### Phase 1: Core User Management & Profile (Backend & DB)

*   `- [x]` **Database Schema Expansion (`users` table)**
    *   `- [x]` Add all fields from ADD 4.3 to `users` table in Supabase: `name`, `role`, `industry`, `skills`, `goals`, `interests`, `social_points`, `free_requests_remaining`, `subscription_tier`, `last_active_at`, `is_active_in_search`, etc.
    *   `- [x]` Define appropriate data types, defaults, and constraints.
*   `- [x]` **Backend: User Models (Pydantic)**
    *   `- [x]` `app/models/user_models.py`:
        *   `- [x]` `UserBase`, `UserCreate` (for registration/first interaction).
        *   `- [x]` `UserProfileUpdate` (for profile editing).
        *   `- [x]` `UserResponse` (for API responses).
    *   `- [x]` `app/models/common_models.py`: Basic enums if any are tied to user (e.g., `SubscriptionTier` enum, though nullable for now).
*   `- [x]` **Backend: User Repository (`app/db/user_repo.py`)**
    *   `- [x]` Implement `create_user(client, user_data)`.
    *   `- [x]` Implement `get_user_by_telegram_id(client, telegram_id)`.
    *   `- [x]` Implement `update_user_profile(client, telegram_id, profile_data)`.
    *   `- [x]` Unit tests for repository functions (mocking Supabase client).
*   `- [x]` **Backend: User Service (`app/services/user_service.py`)**
    *   `- [x]` Implement `create_or_get_user(telegram_id, name, username)`: Logic to handle first interaction.
    *   `- [x]` Implement `update_user_profile_service(telegram_id, profile_data)`: Business logic, validation.
    *   `- [x]` Implement `get_user_profile_service(telegram_id)`.
    *   `- [x]` Unit tests for service functions (mocking repository).
*   `- [x]` **Backend: User API Endpoints (`app/api/users.py`)**
    *   `- [x]` Implement `POST /users/register` (or `/users/onboard`): Called by bot on first `/start`.
    *   `- [x]` Implement `GET /users/{telegram_id}/profile`.
    *   `- [x]` Implement `PUT /users/{telegram_id}/profile`.
    *   `- [x]` `app/api/deps.py`: `get_current_user` (simple Telegram ID from header for MVP).
    *   `- [x]` Integration tests for API endpoints.
*   `- [x]` **Documentation:**
    *   `- [x]` Document User API endpoints (OpenAPI via FastAPI docstrings).

---

### Phase 2: Telegram Bot - User Onboarding & Profile Management

*   `- [x]` **Bot: API Client Setup (`bot/services/api_client.py`)**
    *   `- [x]` `APIClient` class initialization.
    *   `- [x]` Implement `onboard_user(telegram_id, name, username)` method.
    *   `- [x]` Implement `get_user_profile(telegram_id)` method.
    *   `- [x]` Implement `update_user_profile(telegram_id, profile_data)` method.
    *   `- [x]` Unit tests for API client methods (mocking `httpx`).
*   `- [x]` **Bot: User States (`bot/states/user_states.py`)**
    *   `- [x]` Define `ProfileSetup` FSM StatesGroup (e.g., `ASK_NAME`, `ASK_ROLE`, `ASK_INDUSTRY`, `ASK_SKILLS`, `ASK_GOALS`, `ASK_INTERESTS`).
*   `- [x]` **Bot: Keyboards (`bot/keyboards/`)**
    *   `- [x]` `inline_keyboards.py`: `edit_profile_keyboard()`, `skip_question_keyboard()`.
    *   `- [x]` `reply_keyboards.py`: `main_menu_keyboard()`.
*   `- [x]` **Bot: Formatters (`bot/utils/formatters.py`)**
    *   `- [x]` `format_user_profile_message(profile_data)`.
*   `- [x]` **Bot: User Handlers (`bot/handlers/user_handlers.py`)**
    *   `- [x]` Update `/start` handler in `common_handlers.py`:
        *   `- [x]` Call `api_client.onboard_user`.
        *   `- [x]` If new user or profile incomplete, initiate profile setup FSM.
        *   `- [x]` Else, show main menu.
    *   `- [x]` Implement `/profile` command:
        *   `- [x]` Fetch profile via `api_client`.
        *   `- [x]` Display profile using `format_user_profile_message`.
        *   `- [x]` Offer "Edit Profile" button.
    *   `- [x]` Implement FSM handlers for each state in `ProfileSetup`:
        *   `- [x]` Ask question.
        *   `- [x]` Store answer in `FSMContext`.
        *   `- [x]` Transition to next state.
        *   `- [x]` On final state, compile data and call `api_client.update_user_profile`.
    *   `- [x]` Implement callback query handler for "Edit Profile" to restart FSM.
*   `- [x]` **Testing:**
    *   `- [x]` Manual E2E testing of user onboarding and profile view/edit flow.
    *   `- [x]` Unit tests for bot handlers (mocking API client and Telegram objects).

---

### Phase 3: Connection Graph & Trust (Backend & DB First, then Bot)

*   `- [ ]` **Database Schema: `connections` table**
    *   `- [ ]` Create `connections` table in Supabase as per ADD 4.3: `id`, `user1_id`, `user2_id`, `connection_type`, `trust_score`, `status`, `created_at`.
    *   `- [ ]` Define PK, FKs, unique constraint on `(user1_id, user2_id)`, enums for `connection_type`, `status`.
*   `- [ ]` **Backend: Connection Models (`app/models/connection_models.py`)**
    *   `- [ ]` `ConnectionBase`, `ConnectionCreate`, `ConnectionResponse`.
    *   `- [ ]` `TrustScoreUpdate`.
    *   `- [ ]` `app/models/common_models.py`: Enums `ConnectionType`, `ConnectionStatus`.
*   `- [ ]` **Backend: Connection Repository (`app/db/connection_repo.py`)**
    *   `- [ ]` Implement `create_connection(...)`.
    *   `- [ ]` Implement `get_connections_by_user_id(user_id, degree=1)` (degree 1 for now).
    *   `- [ ]` Implement `get_connection_by_users(user1_id, user2_id)`.
    *   `- [ ]` Implement `update_trust_score_repo(connection_id, trust_score)`.
    *   `- [ ]` Implement `get_connection_by_id(connection_id)`.
    *   `- [ ]` Unit tests.
*   `- [ ]` **Backend: Connection Service (`app/services/connection_service.py`)**
    *   `- [ ]` Implement `add_connection_service(user1_id, user2_telegram_id_to_connect, connection_type, trust_score)`:
        *   `- [ ]` Find `user2` by `telegram_id`.
        *   `- [ ]` Ensure they are not already connected.
        *   `- [ ]` Create connection.
    *   `- [ ]` Implement `get_user_connections_service(telegram_id)`.
    *   `- [ ]` Implement `update_trust_score_service(connection_id, new_score, user_making_change_id)`.
    *   `- [ ]` Implement `generate_invite_link_data_service(user_id)` (generates a unique token/payload for an invite).
    *   `- [ ]` Implement `accept_invite_service(invite_token, invitee_telegram_id)`:
        *   `- [ ]` Validate token, extract inviter_id.
        *   `- [ ]` Call `add_connection_service` (with a specific `connection_type` like 'invited').
    *   `- [ ]` Unit tests.
*   `- [ ]` **Backend: Connection API Endpoints (`app/api/connections.py`)**
    *   `- [ ]` `POST /connections`: Direct add friend (MVP initial way). Requires `user2_telegram_id`, `connection_type`, `trust_score`.
    *   `- [ ]` `GET /users/{telegram_id}/connections`.
    *   `- [ ]` `PUT /connections/{connection_id}/trust`.
    *   `- [ ]` `POST /users/{telegram_id}/invite` (returns invite link/token).
    *   `- [ ]` `POST /connections/accept_invite` (takes invite token).
    *   `- [ ]` Integration tests.
*   `- [ ]` **Bot: API Client Updates (`bot/services/api_client.py`)**
    *   `- [ ]` Add methods for `add_connection`, `get_my_connections`, `update_trust_score`, `generate_invite_link`, `accept_invite`.
*   `- [ ]` **Bot: Connection Handlers (`bot/handlers/user_handlers.py` or new `connection_handlers.py`)**
    *   `- [ ]` Implement `/invite` command: Call `api_client.generate_invite_link`, send link to user.
    *   `- [ ]` Modify `/start` handler to check for `invite_token` deep link parameter:
        *   `- [ ]` If `invite_token` present, call `api_client.accept_invite` after user onboarding.
    *   `- [ ]` Implement `/add_friend` command (FSM if prompting for connection type/trust):
        *   `- [ ]` Ask for friend's Telegram username/ID (tricky, Telegram IDs are not easily sharable, usernames are better).
        *   `- [ ]` (Bot may need to use `resolve_peer` if only username is given, or backend needs to handle lookup if user ID isn't known to bot yet)
        *   `- [ ]` Prompt for `connection_type` (inline keyboard).
        *   `- [ ]` Prompt for `trust_score` (1-3) (inline keyboard).
        *   `- [ ]` Call `api_client.add_connection`.
    *   `- [ ]` Implement `/my_friends` command: Call `api_client.get_my_connections`, display list.
        *   `- [ ]` For each friend, offer "Update Trust" button.
    *   `- [ ]` Callback query handler for "Update Trust": Prompt for new trust score, call API.
*   `- [ ]` **Documentation:**
    *   `- [ ]` Document Connection API endpoints.
    *   `- [ ]` Document bot commands for connections.

---

### Phase 4: Request Formulation, AI Matching (MVP Keyword), & Digests

*   `- [ ]` **Database Schema: `requests` and `request_matches_log` tables**
    *   `- [ ]` Create `requests` table (ADD 4.3): `id`, `requester_id`, `description_text`, `description_embedding` (nullable for MVP), `status`, `created_at`, `expires_at`.
    *   `- [ ]` Create `request_matches_log` table (ADD 4.3): `id`, `request_id`, `suggested_user_id`, `introducer_user_id`, `match_score`, `status`, `created_at`.
    *   `- [ ]` Define enums.
*   `- [ ]` **Backend: Request Models (`app/models/request_models.py`)**
    *   `- [ ]` `RequestBase`, `RequestCreate`, `RequestResponse`, `RequestUpdate`.
    *   `- [ ]` `RequestMatchLogEntry`.
    *   `- [ ]` `app/models/common_models.py`: Enums `RequestStatus`, `MatchStatus`.
*   `- [ ]` **Backend: Request Repository (`app/db/request_repo.py`)**
    *   `- [ ]` `create_request_repo(...)`.
    *   `- [ ]` `get_request_by_id_repo(...)`.
    *   `- [ ]` `get_active_requests_by_user_repo(requester_id)`.
    *   `- [ ]` `update_request_status_repo(...)`.
    *   `- [ ]` `log_request_match_repo(...)`.
    *   `- [ ]` `get_match_suggestions_for_request_repo(request_id)`.
    *   `- [ ]` `get_requests_for_digest_repo(user_id, potential_helper_ids)`: More complex query to find requests where user's connections could help OR user could help.
    *   `- [ ]` Unit tests.
*   `- [ ]` **Backend: Matching Service (MVP - Keyword) (`app/services/matching_service.py`)**
    *   `- [ ]` Implement `find_matches_for_request(request_id)`:
        *   `- [ ]` Fetch request.
        *   `- [ ]` Fetch requester's 1st and 2nd degree connections (service may need to call `connection_service` or have `connection_repo` access).
        *   `- [ ]` Simple keyword extraction from `request.description_text`.
        *   `- [ ]` Loop through connections, fetch their profiles (`user_repo`).
        *   `- [ ]` Match keywords against profile fields (`skills`, `role`, `industry`, `goals`, `interests`).
        *   `- [ ]` Calculate basic score (factor in connection degree, trust score - from `connection_repo`).
        *   `- [ ]` Log top N matches to `request_matches_log` via `request_repo`.
        *   `- [ ]` Return list of `suggested_user_id`s.
    *   `- [ ]` Unit tests for matching logic.
*   `- [ ]` **Backend: Request Service (`app/services/request_service.py`)**
    *   `- [ ]` Implement `create_request_service(requester_id, description_text)`:
        *   `- [ ]` (Defer social points check to Phase 5).
        *   `- [ ]` Store request.
        *   `- [ ]` (Optional for now: Trigger matching asynchronously if slow, or make it part of the request creation flow).
    *   `- [ ]` Implement `get_active_requests_for_user_service(telegram_id)`.
    *   `- [ ]` Implement `get_request_details_service(request_id)`.
    *   `- [ ]` Implement `process_helper_response_service(request_id, helper_user_id, introducer_user_id_if_2nd_degree, response_status)`: Updates `request_matches_log`. (Defer social points award to Phase 5).
    *   `- [ ]` Implement `update_request_status_service(request_id, new_status, user_id_making_change)`.
    *   `- [ ]` Unit tests.
*   `- [ ]` **Backend: Notification Service (`app/services/notification_service.py`)**
    *   `- [ ]` Implement `get_daily_digest_for_user_service(telegram_id)`:
        *   `- [ ]` Fetch user's profile (`goals`, `skills` etc.).
        *   `- [ ]` Fetch open requests from user's 1st/2nd degree network.
        *   `- [ ]` Perform a lightweight matching (user profile vs open requests in their network).
        *   `- [ ]` Return top N (e.g., 20) requests where user might be helpful.
    *   `- [ ]` Unit tests.
*   `- [ ]` **Backend: Request API Endpoints (`app/api/requests.py`)**
    *   `- [ ]` `POST /requests`.
    *   `- [ ]` `GET /requests/{telegram_id}/active`.
    *   `- [ ]` `GET /requests/match/{request_id}` (invokes `matching_service`).
    *   `- [ ]` `POST /requests/{request_id}/respond` (helper indicates willingness).
    *   `- [ ]` `PUT /requests/{request_id}/status` (requester updates status).
    *   `- [ ]` Integration tests.
*   `- [ ]` **Backend: User API Endpoint (`app/api/users.py`)**
    *   `- [ ]` `GET /users/{telegram_id}/digest` (invokes `notification_service`).
*   `- [ ]` **Bot: API Client Updates (`bot/services/api_client.py`)**
    *   `- [ ]` Add methods for `create_request`, `get_my_active_requests`, `get_matches_for_request`, `respond_to_request_match`, `get_daily_digest`.
*   `- [ ]` **Bot: Request States (`bot/states/request_states.py`)**
    *   `- [ ]` Define `NewRequest` FSM StatesGroup (e.g., `ASK_DESCRIPTION`).
*   `- [ ]` **Bot: Request Handlers (`bot/handlers/request_handlers.py`)**
    *   `- [ ]` `/new_request` command:
        *   `- [ ]` (Defer social points check to Phase 5).
        *   `- [ ]` Start `NewRequest` FSM.
        *   `- [ ]` Handler for description, call `api_client.create_request`.
        *   `- [ ]` On success, inform user, maybe offer to view matches (call `api_client.get_matches_for_request`).
    *   `- [ ]` `/my_requests` command: Fetch and display active requests. For each, show "View Matches" button.
    *   `- [ ]` Callback query for "View Matches": Call `api_client.get_matches_for_request`. Display matches with "Ask for Intro / Willing to Help" button.
    *   `- [ ]` Callback query for "Ask for Intro / Willing to Help": Call `api_client.respond_to_request_match`.
*   `- [ ]` **Bot: Daily Digest Sending (Manual Trigger or Scheduled)**
    *   `- [ ]` `scripts/send_digests.py` OR internal scheduler (APScheduler in backend or Railway cron job) that calls `GET /users/{telegram_id}/digest` for active users and sends message via bot.
    *   `- [ ]` Bot handler to receive digest payload and format it with "Готов помочь" buttons.
    *   `- [ ]` Callback query for "Готов помочь" on digest: Call `api_client.respond_to_request_match`.
*   `- [ ]` **Future AI Embeddings (OpenAI)**
    *   `- [ ]` (Defer full implementation to post-MVP or if keyword matching is too poor).
    *   `- [ ]` `app/services/matching_service.py`: Add `_generate_embedding(text)` using OpenAI client.
    *   `- [ ]` Update Supabase `requests` and `users` tables with `vector` columns (use `pg_vector` extension).
    *   `- [ ]` Logic to generate and store embeddings on profile update and request creation.
    *   `- [ ]` Update `find_matches_for_request` to use vector similarity search.
*   `- [ ]` **Documentation:**
    *   `- [ ]` Document Request API endpoints.
    *   `- [ ]` Document bot commands for requests and digests.

---

### Phase 5: Social Points, Request Economy & Activity

*   `- [ ]` **Database Schema: `activity_history` table**
    *   `- [ ]` Create `activity_history` table (ADD 4.3): `id`, `user_id`, `action_type`, `related_request_id`, `points_change`, `timestamp`.
    *   `- [ ]` Define enums for `action_type`.
*   `- [ ]` **Backend: Activity Models (`app/models/user_models.py` or new `activity_models.py`)**
    *   `- [ ]` `ActivityLogEntry`.
    *   `- [ ]` `app/models/common_models.py`: Enum `ActivityActionType`.
*   `- [ ]` **Backend: Activity Repository (`app/db/activity_repo.py`)**
    *   `- [ ]` `log_activity(...)`.
    *   `- [ ]` `get_activity_history_for_user(...)`.
    *   `- [ ]` Unit tests.
*   `- [ ]` **Backend: User Repository (`app/db/user_repo.py`) Updates**
    *   `- [ ]` `update_user_social_points(client, telegram_id, points_to_add_or_subtract)`.
    *   `- [ ]` `decrement_free_requests_remaining(client, telegram_id)`.
    *   `- [ ]` `get_user_economy_status(client, telegram_id)` (points, free requests, subscription status).
*   `- [ ]` **Backend: Social Points Service (`app/services/social_points_service.py`)**
    *   `- [ ]` Define constants: `POINTS_FOR_HELPING`, `POINTS_PER_REQUEST_COST`, `INITIAL_FREE_REQUESTS`.
    *   `- [ ]` `award_points_for_help(user_id, request_id)`: Updates `user.social_points` via `user_repo`, logs to `activity_history` via `activity_repo`.
    *   `- [ ]` `can_make_request(user_id)`: Checks `user.free_requests_remaining` or `user.social_points` or subscription (subscription part later).
    *   `- [ ]` `charge_for_request(user_id)`: Decrements free requests or social points via `user_repo`.
    *   `- [ ]` Unit tests.
*   `- [ ]` **Backend: Service Modifications**
    *   `- [ ]` `request_service.py -> create_request_service`: Call `social_points_service.can_make_request` and `charge_for_request`.
    *   `- [ ]` `request_service.py -> process_helper_response_service`: If "willing to help", call `social_points_service.award_points_for_help`.
*   `- [ ]` **Backend: User API Endpoint (`app/api/users.py`) Updates**
    *   `- [ ]` `GET /users/{telegram_id}/activity`: Fetch activity history.
    *   `- [ ]` `PUT /users/{telegram_id}/activity_settings`: Update `is_active_in_search`, `last_active_at` automatically on interaction.
*   `- [ ]` **Bot: API Client Updates (`bot/services/api_client.py`)**
    *   `- [ ]` `get_user_activity_history`.
*   `- [ ]` **Bot: Handler Updates**
    *   `- [ ]` `request_handlers.py -> /new_request`: Before FSM, check if user can make request (call backend or embed logic in bot if preferred after fetching user economy status).
    *   `- [ ]` Add `/my_points` or similar command to show current social points and free requests.
    *   `- [ ]` Add `/activity_history` command.
*   `- [ ]` **Documentation:**
    *   `- [ ]` Update relevant API docs.
    *   `- [ ]` Document new bot commands.

---

### Phase 6: Payment Integration (Stripe)

*   `- [ ]` **Stripe Account Setup**
    *   `- [ ]` Create Stripe account.
    *   `- [ ]` Define products and prices for subscriptions (e.g., "NetWise Tier 1", "NetWise Tier 2") and one-time request purchases.
    *   `- [ ]` Get Stripe API Keys (Publishable and Secret). Add to `.env`.
    *   `- [ ]` Set up webhook endpoint in Stripe dashboard (e.g., `https://your-app.railway.app/api/v1/payments/webhook`). Note webhook secret.
*   `- [ ]` **Database Schema: `subscriptions` table (optional, or extend `users`)**
    *   `- [ ]` If using separate `subscriptions` table as per ADD 4.3: `id`, `user_id`, `plan_name`, `stripe_subscription_id`, `start_date`, `end_date`, `status`.
    *   `- [ ]` Or add `stripe_customer_id`, `stripe_subscription_id`, `subscription_tier`, `subscription_expires_at` directly to `users` table.
*   `- [ ]` **Backend: Payment Models (`app/models/payment_models.py`)**
    *   `- [ ]` `SubscriptionRequest`, `CheckoutSessionResponse`, `PortalSessionResponse`.
*   `- [ ]` **Backend: Payment Service (`app/services/payment_service.py`)**
    *   `- [ ]` Initialize Stripe client.
    *   `- [ ]` `create_subscription_checkout_session(user_id, plan_id)`:
        *   `- [ ]` Get/create Stripe customer ID for user (store in `users` table).
        *   `- [ ]` Create Stripe Checkout session.
    *   `- [ ]` `create_billing_portal_session(user_id)`.
    *   `- [ ]` `handle_webhook_event(payload, sig_header)`:
        *   `- [ ]` Verify Stripe signature.
        *   `- [ ]` Handle `checkout.session.completed`: Update user's subscription status, grant free requests/social points if part of plan.
        *   `- [ ]` Handle `invoice.payment_succeeded`: Renew subscription.
        *   `- [ ]` Handle `customer.subscription.deleted` / `customer.subscription.updated` (e.g., canceled).
        *   `- [ ]` Handle one-time purchase success: Grant N requests.
    *   `- [ ]` Unit tests (mocking Stripe API).
*   `- [ ]` **Backend: Payment API Endpoints (`app/api/payments.py`)**
    *   `- [ ]` `POST /payments/subscribe` (returns checkout URL).
    *   `- [ ]` `POST /payments/portal` (returns portal URL).
    *   `- [ ]` `POST /payments/webhook`.
    *   `- [ ]` Integration tests.
*   `- [ ]` **Backend: Service Modifications**
    *   `- [ ]` `social_points_service.py -> can_make_request`: Check for active subscription status.
*   `- [ ]` **Bot: API Client Updates (`bot/services/api_client.py`)**
    *   `- [ ]` `create_checkout_session(plan_id)`.
    *   `- [ ]` `create_portal_session()`.
*   `- [ ]` **Bot: Payment Handlers (e.g., in `user_handlers.py`)**
    *   `- [ ]` `/subscribe` command: Show available plans (buttons).
    *   `- [ ]` Callback query for plan selection: Call `api_client.create_checkout_session`, send link.
    *   `- [ ]` `/buy_requests` command (for one-time purchase).
    *   `- [ ]` `/manage_subscription` command: Call `api_client.create_portal_session`, send link.
*   `- [ ]` **Documentation:**
    *   `- [ ]` Document Payment API endpoints, especially webhook.
    *   `- [ ]` Notes on Stripe setup in README.

---

### Phase 7: Testing, Polish, User Activity Monitoring & Deployment Prep

*   `- [ ]` **Comprehensive Testing**
    *   `- [ ]` Review and expand unit tests for all backend services and repositories (aim for >80% coverage).
    *   `- [ ]` Review and expand integration tests for all API endpoints.
    *   `- [ ]` Review and expand unit tests for bot handlers and FSM logic.
    *   `- [ ]` End-to-End (E2E) manual testing of all user flows.
        *   `- [ ]` User Onboarding & Profile
        *   `- [ ]` Adding Friends & Trust
        *   `- [ ]` Creating Requests & Getting Matches
        *   `- [ ]` Responding to Digest/Matches
        *   `- [ ]` Social Points & Free Tier Logic
        *   `- [ ]` Subscription & Payment Flows
*   `- [ ]` **User Activity Monitoring & Management (Backend)**
    *   `- [ ]` `user_service.py`: Implement logic to update `last_active_at` on most user interactions via API.
    *   `- [ ]` `matching_service.py`: Add filter to exclude users with `is_active_in_search = false` or old `last_active_at`.
    *   `- [ ]` Scheduled task (Railway cron / APScheduler):
        *   `- [ ]` Identify inactive users (e.g., no activity for X days).
        *   `- [ ]` Send reminder notifications (via bot or direct if bot has send capability).
        *   `- [ ]` Set `is_active_in_search = false` for users inactive for Y days (Y > X).
*   `- [ ]` **Bot: Polish & UX**
    *   `- [ ]` Review all bot messages for clarity, tone, and typos.
    *   `- [ ]` Ensure consistent use of keyboards and commands.
    *   `- [ ]` Add `/help` command detailing all features.
    *   `- [ ]` Handle potential errors gracefully (e.g., API down, invalid input).
*   `- [ ]` **Security Review**
    *   `- [ ]` Verify Supabase Row Level Security policies are comprehensive.
    *   `- [ ]` Ensure all API inputs are validated (Pydantic helps).
    *   `- [ ]` Check for any hardcoded secrets (should be in `.env`).
    *   `- [ ]` Ensure Stripe webhook secret is used for verification.
*   `- [ ]` **Documentation Review & Finalization**
    *   `- [ ]` Update `README.md` with setup, deployment, and usage instructions.
    *   `- [ ]` Ensure all API endpoints are documented via OpenAPI.
    *   `- [ ]` Add code comments where necessary.
*   `- [ ]` **Railway Deployment Configuration**
    *   `- [ ]` Finalize `Dockerfile`(s) and `Procfile` (if used).
    *   `- [ ]` Set up all production environment variables in Railway for both backend and bot services.
    *   `- [ ]` Configure Railway health checks.
    *   `- [ ]` Configure custom domain if applicable.
    *   `- [ ]` Set up Railway cron jobs for scheduled tasks (digests, inactivity checks).
*   `- [ ]` **Monitoring & Logging Setup**
    *   `- [ ]` Ensure structured logging is in place for both backend and bot.
    *   `- [ ]` Review Railway's logging and metrics dashboards.
    *   `- [ ]` (Optional MVP+) Integrate Sentry for error tracking.

---

### Phase 8: MVP Launch & Post-Launch Monitoring

*   `- [ ]` **Pre-Launch Checklist**
    *   `- [ ]` Final E2E testing on a staging-like environment (if possible, or production with test users).
    *   `- [ ]` All critical bugs fixed.
    *   `- [ ]` Backup Supabase data.
*   `- [ ]` **Launch!**
    *   `- [ ]` Announce to target users.
*   `- [ ]` **Post-Launch Monitoring**
    *   `- [ ]` Closely monitor Railway logs and metrics.
    *   `- [ ]` Monitor Supabase performance.
    *   `- [ ]` Track Stripe payments and webhook events.
    *   `- [ ]` Gather user feedback.
    *   `- [ ]` Be prepared for hotfixes.

---

This plan is comprehensive. You can adjust the granularity of sub-tasks further. Good luck with NetWise!