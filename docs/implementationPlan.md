## NetWise Telegram Bot MVP: Detailed Implementation Plan (MVP Focus)

**Legend:**
*   `- [ ]` Pending Task
*   `- [x]` Completed Task

---

### **Phase 0: Project Setup & Foundational Elements (1-2 days)**

*   **Task 0.1: Project Initialization & Version Control**
    *   `- [x]` Create project directory (`netwise`).
    *   `- [x]` Initialize Git repository (`git init`).
    *   `- [x]` Create initial `.gitignore` file.
    *   `- [x]` Create `README.md` with basic project info.
    *   `- [x]` Set up remote repository (e.g., GitHub, GitLab).
*   **Task 0.2: Environment & Dependency Management**
    *   `- [x]` Set up Python virtual environment (e.g., `venv`).
    *   `- [x]` Install core dependencies: `aiogram`, `python-dotenv`, `supabase`, `apscheduler`. (OpenAI client removed for now).
    *   `- [x]` Create `requirements.txt` (`pip freeze > requirements.txt`).
    *   `- [x]` Create `.env.example` file with all necessary environment variables (excluding OpenAI API key for now).
    *   `- [x]` Create local `.env` file and populate with actual (test/dev) credentials (Telegram Bot Token, Supabase URL/Key).
*   **Task 0.3: Basic Project Structure**
    *   `- [x]` Create main package directory `netwise_bot/` and `__init__.py`.
    *   `- [x]` Create `main.py` at the root.
    *   `- [x]` Create `netwise_bot/config.py`.
    *   `- [x]` Create `netwise_bot/bot_instance.py`.
*   **Task 0.4: Initial Supabase Setup**
    *   `- [x]` Create Supabase project.
    *   `- [x]` Design and create initial DB tables (start with `users` table).
        *   `- [x]` Define `users` table schema (columns, types, constraints).
        *   `- [x]` Implement `users` table in Supabase Studio.
    *   `- [x]` Get Supabase URL and Service Role Key for `.env`.
*   **Task 0.5: Basic Bot Connection & "Hello World"**
    *   `- [x]` **Implement `netwise_bot/config.py`:** Load environment variables.
    *   `- [x]` **Implement `netwise_bot/bot_instance.py`:** Initialize `Bot` and `Dispatcher`.
    *   `- [x]` **Implement basic `main.py`:**
        *   `- [x]` Load config.
        *   `- [x]` Initialize bot & dispatcher.
        *   `- [x]` Create a simple `/start` handler in `main.py` (or a new `handlers/common.py`) that replies "Hello NetWise!"
        *   `- [x]` Start polling.
    *   `- [x]` **Test:** Run `main.py` and send `/start` to your bot in Telegram.
        *   *Checkpoint:* Bot responds "Hello NetWise!".
*   **Task 0.6: Logging Setup**
    *   `- [x]` Configure basic logging in `main.py` (e.g., to console, `INFO` level).

---

### **Phase 1: Core User Management & Profile (3-5 days)**

*   **Task 1.1: User Service - Basic CRUD**
    *   `- [x]` Create `netwise_bot/services/supabase_client.py`.
        *   `- [x]` Implement `__init__` to initialize Supabase client.
        *   `- [x]` Implement `fetch_user_by_telegram_id(telegram_id)` function.
        *   `- [x]` Implement `create_user(telegram_id, name=None, defaults=...)` function.
    *   `- [x]` Create `netwise_bot/services/user_service.py`.
        *   `- [x]` Implement `get_or_create_user(telegram_id, name=None)` using `supabase_client`.
*   **Task 1.2: `/start` Handler Enhancement**
    *   `- [x]` Create `netwise_bot/handlers/common.py`.
    *   `- [x]` Move `/start` logic to `handlers/common.py`.
    *   `- [x]` Modify `/start` handler to use `user_service.get_or_create_user()`.
    *   `- [x]` Differentiate welcome message for new vs. existing users.
    *   `- [x]` Create `netwise_bot/keyboards/common_keyboards.py`.
    *   `- [x]` Implement `get_initial_setup_keyboard()` (e.g., "Create Profile" button for new users).
    *   `- [x]` **Test:** `/start` command behavior for new and existing users.
*   **Task 1.3: Profile Creation Flow - FSM & Handlers**
    *   `- [x]` Create `netwise_bot/states/profile_states.py` with `ProfileStates(StatesGroup)`.
        *   `- [x]` Define states: `name`, `role`, `industry`, `skills`, `goals`, `interests`.
    *   `- [x]` Create `netwise_bot/handlers/profile.py`.
    *   `- [x]` Implement handler to initiate profile creation (e.g., callback from "Create Profile" button).
        *   `- [x]` Set initial state (`ProfileStates.name`).
        *   `- [x]` Ask user for their name.
    *   `- [x]` Implement message handlers for each profile field (name, role, etc.):
        *   `- [x]` Validate input (basic validation for now).
        *   `- [x]` Store data in FSM context (`state.update_data(...)`).
        *   `- [x]` Transition to the next state (`state.set_state(...)`).
        *   `- [x]` Ask for the next piece of information.
*   **Task 1.4: Profile Service - Update & Get**
    *   `- [x]` **`supabase_client.py`:**
        *   `- [x]` Implement `update_user_profile(telegram_id, profile_data)`.
        *   `- [x]` Implement `fetch_user_profile(telegram_id)`.
        *   `- [x]` Add error handling and validation.
    *   `- [x]` **`user_service.py`:**
        *   `- [x]` Implement `update_profile(telegram_id, profile_data)`.
        *   `- [x]` Implement `get_profile(telegram_id)`.
        *   `- [x]` Add profile data validation.
        *   `- [x]` Add error handling and logging.
*   **Task 1.5: Completing Profile Creation & `/myprofile`**
    *   `- [x]` **`handlers/profile.py`:**
        *   `- [x]` Implement handler for the last profile field.
        *   `- [x]` On completion, retrieve all data from FSM context.
        *   `- [x]` Call `user_service.update_profile()`.
        *   `- [x]` Send confirmation message.
        *   `- [x]` Finish FSM state (`state.clear()`).
    *   `- [x]` Implement `/myprofile` command in `handlers/profile.py`:
        *   `- [x]` Call `user_service.get_profile()`.
        *   `- [x]` Format and display profile information.
        *   `- [x]` Add "Edit Profile" button.
    *   `- [x]` **Test:** Full profile creation flow and `/myprofile` command.
        *   *Checkpoint:* User can create a profile, data is saved to Supabase, and `/myprofile` shows it.
*   **Task 1.6: User Activity Tracking (Basic)**
    *   `- [x]` **`users` table (Supabase):** Add `last_active_at` (Timestamp) and `is_active_in_search` (Boolean, default: true).
    *   `- [x]` **`supabase_client.py`:** Implement `update_user_last_active(telegram_id)`.
    *   `- [x]` **`user_service.py`:** Implement `update_user_activity(telegram_id)`.
    *   `- [x]` Integrate `update_user_activity` call in relevant handlers (e.g., on `/start`, after sending any message). Consider a middleware for this.

---

### **Phase 2: Connection Graph & Trust (3-4 days)**

*   **Task 2.1: Connections Table & Service Foundation**
    *   `- [x]` **Supabase:** Design and create `connections` table (user1_id, user2_id, connection_type, trust_score, status).
    *   `- [x]` Create `netwise_bot/services/graph_service.py`.
    *   `- [x]` **`supabase_client.py`:**
        *   `- [x]` Implement `create_connection(user1_id, user2_id, type, trust, status)`.
        *   `- [x]` Implement `fetch_connections(user_id)`.
*   **Task 2.2: Invite Friends Functionality**
    *   `- [x]` Create `netwise_bot/handlers/connections.py`.
    *   `- [x]` **`graph_service.py`:**
        *   `- [x]` Implement `generate_invite_link(telegram_id)` (simple strategy: `t.me/YourBotName?start=invite_{telegram_id}`).
    *   `- [x]` **`handlers/connections.py`:**
        *   `- [x]` Implement `/invite` command to call `graph_service.generate_invite_link()` and display it.
    *   `- [x]` **Test:** `/invite` generates a usable link.
*   **Task 2.3: Handling Invite Links (Deep Linking)**
    *   `- [x]` **`handlers/common.py` (`/start` handler):**
        *   `- [x]` Modify `/start` to check for payload (e.g., `invite_{inviter_id}`).
        *   `- [x]` If invite payload exists, extract `inviter_id`.
    *   `- [x]` **`graph_service.py`:**
        *   `- [x]` Implement `accept_invite(inviter_id, invitee_telegram_id)`.
            *   `- [x]` Ensure users exist.
            *   `- [x]` Check for existing connection.
            *   `- [x]` Call `supabase_client.create_connection()` with default trust/type or prompt.
    *   `- [x]` **`handlers/common.py` (`/start` handler):**
        *   `- [x]` Call `graph_service.accept_invite()`.
        *   `- [x]` Send confirmation to both inviter (if online) and invitee.
*   **Task 2.4: "How do you know?" & Trust Score**
    *   `- [x]` Create `netwise_bot/states/connection_states.py` with `ConnectionTrustStates`.
    *   `- [x]` Create `netwise_bot/keyboards/profile_keyboards.py` (or a new `connections_keyboards.py`).
        *   `- [x]` Implement keyboard for "How do you know?" options (Worked together, Intro made, etc.).
        *   `- [x]` Implement keyboard for trust score (1-3).
    *   `- [x]` **`handlers/connections.py` (or modify `accept_invite` flow):**
        *   `- [x]` After connection is made (or before final save), prompt invitee with "How do you know [InviterName]?" using keyboard.
        *   `- [x]` Store `connection_type` in FSM.
        *   `- [x]` Prompt for trust score (1-3) using keyboard.
        *   `- [x]` Store `trust_score` in FSM.
    *   `- [x]` **`supabase_client.py`:** Implement `update_connection_details(connection_id, type, trust)`.
    *   `- [x]` **`graph_service.py`:** Implement `set_connection_details(...)` to update DB.
    *   `- [x]` **Test:** Full invite flow, including setting connection type and trust score.
        *   *Checkpoint:* Two users can connect, connection details are saved.
*   **Task 2.5: Viewing Connections**
    *   `- [x]` Implement `/myconnections` command
    *   `- [x]` Add filtering by trust score and connection type
    *   `- [x]` Add sorting by name, trust score, and date
    *   `- [x]` Add pagination for large connection lists
    *   `- [x]` Add connection statistics view
    *   `- [x]` Test all connection viewing features

---

### **Phase 3: Requests & Keyword-Based Matching (4-6 days)**

*   **Task 3.1: Requests Table & Service Foundation**
    *   `- [x]` **Supabase:** Design and create `requests` table (id, requester_id, description_text, status, created_at, expires_at).
    *   `- [x]` Create `netwise_bot/services/request_service.py`.
    *   `- [x]` **`supabase_client.py`:**
        *   `- [x]` Implement `create_request_record(requester_id, description, status)`.
        *   `- [x]` Implement `fetch_user_requests(requester_id, status=None)`.
*   **Task 3.2: Formulate Request Flow (FSM & Handlers)**
    *   `- [x]` Create `netwise_bot/states/request_states.py` with `RequestStates`.
        *   `- [x]` Define state: `description`.
    *   `- [x]` Create `netwise_bot/handlers/requests.py`.
    *   `- [x]` Create `netwise_bot/keyboards/request_keyboards.py`.
    *   `- [x]` Implement `/newrequest` command:
        *   `- [x]` Set initial state (`RequestStates.description`).
        *   `- [x]` Ask user to describe their problem.
    *   `- [x]` Implement message handler for request description:
        *   `- [x]` Store description in FSM.
        *   `- [x]` Show summary and "Submit Request" / "Cancel" keyboard.
*   **Task 3.3: Social Points & Request Economy (MVP)**
    *   `- [x]` **`users` table (Supabase):** Add `social_points` (Int, default: 0), `free_requests_remaining` (Int, default: 5).
    *   `- [x]` **`netwise_bot/utils/constants.py`:** Define `POINTS_PER_HELP`, `FREE_REQUESTS_PER_MONTH`.
    *   `- [x]` **`user_service.py`:**
        *   `- [x]` Implement `add_social_points(telegram_id, points)` for earning points by helping others.
        *   `- [x]` Implement `get_social_points(telegram_id)` to display points.
        *   `- [x]` Implement `use_free_request(telegram_id)`:
            *   `- [x]` Checks `free_requests_remaining`. If > 0, decrement.
            *   `- [x]` Return success/failure with appropriate message.
        *   `- [x]` Implement `reset_monthly_free_requests()` (for scheduler).
*   **Task 3.4: Submitting Request & Keyword-Based Matching Logic**
    *   `- [x]` Create `netwise_bot/services/matching_service.py`.
    *   `- [x]` **`matching_service.py` (MVP Keyword Logic):**
        *   `- [x]` Implement `extract_keywords_from_text(text)` (simple split, stop-word removal).
        *   `- [x]` Implement `find_keyword_matches(request_description, requester_id)`:
            *   `- [x]` Get requester's 1st and 2nd degree connections (from `graph_service`).
            *   `- [x]` For each connection, fetch their profile (`user_service.get_profile`).
            *   `- [x]` Extract keywords from request description.
            *   `- [x]` Compare request keywords with profile fields (`skills`, `role`, `industry`, `goals`, `interests`).
            *   `- [x]` Implement a simple scoring mechanism (e.g., +1 per keyword match in skills/role, +0.5 in interests/goals).
            *   `- [x]` Weight score by connection degree (1st degree > 2nd degree) and trust score.
            *   `- [x]` Filter out users with `is_active_in_search = false`.
            *   `- [x]` Return ranked list of potential helpers (user_id, score).
    *   `- [x]` **`request_service.py`:**
        *   `- [x]` Implement `create_request(requester_id, description)`:
            *   `- [x]` Call `user_service.use_free_request_or_points()`. If fails, inform user.
            *   `- [x]` Call `supabase_client.create_request_record()`.
            *   `- [x]` Return request ID.
    *   `- [x]` **`handlers/requests.py` (Submit Request callback):**
        *   `- [x]` Retrieve description from FSM.
        *   `- [x]` Call `request_service.create_request()`. If successful:
            *   `- [x]` Call `matching_service.find_keyword_matches()`.
            *   `- [x]` Format and display list of relevant candidates to the user.
                *   `- [x]` Each candidate with "Спросить, готов ли помочь" button (callback_data: `ask_help_{request_id}_{helper_id}_{introducer_id_if_2nd_degree}`).
            *   `- [x]` If no matches, inform user.
        *   `- [x]` Finish FSM.
    *   `- [x]` **Test:** Full request creation and keyword-based matching.
        *   *Checkpoint:* User can create a request, points/free quota are used, and a list of (mocked or real) potential helpers is shown.
*   **Task 3.5: "Спросить, готов ли помочь" Interaction**
    *   `- [x]` Create new handler file `netwise_bot/handlers/interactions.py`
        *   `- [x]` Implement handler for "Ask for help" button
        *   `- [x]` Add handlers for helper responses (accept/decline)
        *   `- [x]` Add handlers for introducer responses (facilitate/decline)
        *   `- [x]` Implement state management for interaction flow
        *   `- [x]` Add error handling and logging
    *   `- [x]` Create new table `request_matches_log` in Supabase
        *   `- [x]` Add columns: id, request_id, suggested_user_id, introducer_user_id, status
        *   `- [x]` Add appropriate indexes and constraints
        *   `- [x]` Set up RLS policies
        *   `- [x]` Add trigger for updated_at
    *   `- [x]` Update `user_service.py`
        *   `- [x]` Add method to get connection type between users
        *   `- [x]` Add method to find common connection for indirect connections
        *   `- [x]` Update error handling and logging
    *   `- [x]` Create new keyboard file `netwise_bot/keyboards/interaction_keyboards.py`
        *   `- [x]` Add keyboard for helper responses
        *   `- [x]` Add keyboard for introducer responses
        *   `- [x]` Implement callback data handling
    *   `- [x]` Test interaction flow
        *   `- [x]` Test direct connection flow
        *   `- [x]` Test indirect connection flow
        *   `- [x]` Test error cases and edge conditions
        *   `- [x]` Verify proper logging and state management

*   **Task 3.6: Request Management System**
    *   `- [ ]` Create `/myrequests` command in `handlers/requests.py`
        *   `- [ ]` Implement pagination for request list (10 requests per page)
        *   `- [ ]` Add filtering by request status (open, pending_intro, intro_made, closed, expired)
        *   `- [ ]` Add sorting by creation date and status
        *   `- [ ]` Display request details including:
            *   `- [ ]` Request description
            *   `- [ ]` Creation date
            *   `- [ ]` Status
            *   `- [ ]` Number of potential helpers found
            *   `- [ ]` Number of help offers received
    *   `- [ ]` Create request management keyboards in `keyboards/request_keyboards.py`
        *   `- [ ]` Add keyboard for request list actions (edit, delete, refresh)
        *   `- [ ]` Add keyboard for request details view
        *   `- [ ]` Add keyboard for request editing
        *   `- [ ]` Add keyboard for request deletion confirmation
    *   `- [ ]` Implement request editing functionality
        *   `- [ ]` Add FSM states for request editing in `states/request_states.py`
        *   `- [ ]` Implement edit request handler
        *   `- [ ]` Add validation for edited request text
        *   `- [ ]` Update request in database
        *   `- [ ]` Notify helpers about request update
    *   `- [ ]` Implement request deletion functionality
        *   `- [ ]` Add confirmation step before deletion
        *   `- [ ]` Implement soft delete (update status to 'deleted')
        *   `- [ ]` Notify helpers about request deletion
        *   `- [ ]` Update request matches log
    *   `- [ ]` Add request statistics
        *   `- [ ]` Show total number of requests
        *   `- [ ]` Show requests by status
        *   `- [ ]` Show average response time
        *   `- [ ]` Show success rate (requests with help offers)
    *   `- [ ]` Test request management system
        *   `- [ ]` Test request listing and pagination
        *   `- [ ]` Test request editing flow
        *   `- [ ]` Test request deletion flow
        *   `- [ ]` Test error handling and edge cases
        *   `- [ ]` Verify proper notifications to helpers

---

### **Phase 4: Daily Digests & Notifications (2-3 days)**

*   **Task 4.1: Scheduler Setup**
    *   `- [x]` Create `netwise_bot/scheduler.py`.
    *   `- [x]` **`scheduler.py`:**
        *   `- [x]` Initialize `AsyncIOScheduler`.
        *   `- [x]` Function to add jobs (e.g., daily digest, monthly free request reset).
        *   `- [x]` Function to start the scheduler.
    *   `- [x]` Integrate scheduler start in `main.py`.
*   **Task 4.2: Daily Digest Logic**
    *   `- [x]` Create `netwise_bot/services/notification_service.py`.
    *   `- [x]` **`request_service.py`:**
        *   `- [x]` Implement `get_requests_user_can_help_with(telegram_id, limit=20)`:
            *   `- [x]` Find open requests NOT from this user.
            *   `- [x]` For each request, use `matching_service.find_keyword_matches()` (or a simplified version checking if this user is a good match for *other's* requests).
            *   `- [x]` Prioritize based on match score, freshness.
    *   `- [x]` **`notification_service.py`:**
        *   `- [x]` Implement `generate_daily_digest_for_user(telegram_id)`:
            *   `- [x]` Call `request_service.get_requests_user_can_help_with()`.
            *   `- [x]` Format a message listing up to X requests. Each with "Готов помочь" button (callback_data: `offer_help_{request_id}_{requester_id_of_that_request}`).
    *   `- [x]` **`scheduler.py`:**
        *   `- [x]` Create `async def send_daily_digests_job()`:
            *   `- [x]` Fetch all active users.
            *   `- [x]` For each user, call `notification_service.generate_daily_digest_for_user()` and send the message via bot instance.
            *   `- [x]` Add this job to run daily (e.g., `scheduler.add_job(..., "cron", hour=9)`).
*   **Task 4.3: "Готов помочь" Interaction**
    *   `- [x]` **`handlers/interactions.py`:**
        *   `- [x]` Implement callback handler for `offer_help_...`:
            *   `- [x]` Parse `request_id`, `original_requester_id`.
            *   `- [x]` Get current user's ID (the one offering help).
            *   `- [x]` Notify `original_requester_id`: "[HelperName] saw your request '[Request snippet]' and is willing to help! You can contact them at @[HelperUsername]."
            *   `- [x]` (Optional) Notify helper: "You've offered to help with request '[Request snippet]'. [RequesterName] has been notified."
            *   `- [x]` **Call `user_service.add_social_points(helper_id, POINTS_PER_HELP)`**
            *   `- [x]` **Supabase:** Create `activity_history` table (user_id, action_type: "helped_on_request", related_request_id, points_change, timestamp). Log this action.
            *   `- [x]` Update `requests` table status to "pending_intro" or "intro_made".
    *   `- [x]` **Test:** Daily digest is sent, "Готов помочь" button works, points are awarded, activity logged.
        *   *Checkpoint:* Users receive digests and can offer help.
*   **Task 4.4: Inactivity Management**
    *   `- [x]` Implement `deactivate_inactive_users(days_inactive_threshold)` in `user_service.py`
    *   `- [x]` Add job in `scheduler.py` to run deactivation process daily
    *   `- [x]` Implement `send_inactive_reminders` in `notification_service.py`
    *   `- [x]` Test the inactivity management system

---

### **Phase 5: Monetization (MVP - $1/request & Basic Subscription) (2-4 days)**

*   **Task 5.1: Payment Provider Setup (e.g., Stripe)**
    *   `- [ ]` Create Stripe account (or other provider).
    *   `- [ ]` Get API keys (secret key, webhook secret) and add to `.env`.
    *   `- [ ]` Define products/prices in Stripe dashboard (e.g., "$1 per extra request", subscription tiers).
*   **Task 5.2: Payment Service Implementation**
    *   `- [ ]` Create `netwise_bot/services/payment_service.py`.
    *   `- [ ]` Add payment provider SDK (e.g., `stripe`) to `requirements.txt`.
    *   `- [ ]` **`payment_service.py`:**
        *   `- [ ]` Implement `create_checkout_session_for_extra_request(telegram_id, request_count)` (returns Stripe checkout URL).
        *   `- [ ]` Implement `create_checkout_session_for_subscription(telegram_id, plan_id)` (returns Stripe checkout URL).
*   **Task 5.3: Integrating Payment Prompts**
    *   `- [ ]` **`request_service.py` (`create_request`):**
        *   `- [ ]` Modify `user_service.use_free_request_or_points()` to return a status indicating "needs_payment" if out of free/points.
        *   `- [ ]` If "needs_payment", prompt user in `handlers/requests.py` with "Pay $1 for this request?" button.
        *   `- [ ]` On button click, call `payment_service.create_checkout_session_for_extra_request()` and send link to user.
*   **Task 5.4: Webhook Handling (Payment Confirmation)**
    *   `- [ ]` **Webhook Endpoint (Challenge for Bots on PaaS like Railway):**
        *   *Option 1 (Preferred if feasible):* If Railway allows the bot process to expose a simple HTTP endpoint (e.g., using `aiohttp.web` alongside `aiogram`), create it.
        *   *Option 2 (Simpler but less real-time):* User manually confirms payment via a command/button after paying, and bot verifies with Stripe API (`retrieve_checkout_session`).
        *   *Option 3 (More complex):* Use a separate serverless function (e.g., Supabase Function, Railway separate service) just for the webhook, which then updates Supabase DB.
    *   `- [ ]` **`payment_service.py`:**
        *   `- [ ]` Implement `handle_stripe_webhook(payload, signature)` (if using Option 1 or 3).
            *   `- [ ]` Verify signature.
            *   `- [ ]` Process `checkout.session.completed` event.
            *   `- [ ]` Extract `telegram_id` (from `client_reference_id` or `metadata` set during checkout creation).
            *   `- [ ]` Update user's `social_points` or grant access for the request / update `subscription_tier` and `subscription_expires_at` in `users` table (via `user_service`).
    *   `- [ ]` **`users` table (Supabase):** Add `subscription_tier` (Text), `subscription_expires_at` (Timestamp).
    *   `- [ ]` **`subscriptions` table (Supabase):** (Optional, for more detailed subscription history).
    *   `- [ ]` **Test:** Full payment flow for extra request and basic subscription.
        *   *Checkpoint:* Users can pay, and their quotas/subscriptions are updated.

---

### **Phase 6: Refinements, Testing & Deployment Prep (3-5 days)**

*   **Task 6.1: Comprehensive Manual Testing**
    *   `- [ ]` Perform end-to-end testing of all user flows.
    *   `- [ ]` Test edge cases and error handling.
    *   `- [ ]` Test with multiple concurrent users (if possible locally or in a staging env).
*   **Task 6.2: UI/UX Review & Polish**
    *   `- [ ]` Review all bot messages for clarity, conciseness, and tone.
    *   `- [ ]` Check keyboard layouts for intuitiveness.
    *   `- [ ]` Ensure consistent `/cancel` functionality in all FSM flows.
    *   `- [ ]` Add `/help` command with comprehensive information in `handlers/common.py`.
*   **Task 6.3: Security Review**
    *   `- [ ]` Ensure all sensitive data is handled appropriately.
    *   `- [ ]` Check for potential injection points (though ORM/Supabase client helps).
    *   `- [ ]` Verify Supabase RLS policies if implemented.
*   **Task 6.4: Documentation**
    *   `- [ ]` Update `README.md` with final setup and usage instructions.
    *   `- [ ]` Add code comments/docstrings where needed.
    *   `- [ ]` Document Supabase schema.
*   **Task 6.5: Railway Deployment Setup**
    *   `- [ ]` Create Railway project.
    *   `- [ ]` Configure build settings (e.g., Python version, start command: `python main.py`).
    *   `- [ ]` Set up environment variables in Railway dashboard.
    *   `- [ ]` Configure Supabase connection from Railway.
    *   `- [ ]` Set up CI/CD with GitHub (if using GitHub Actions or Railway's Git integration).
*   **Task 6.6: Final Deployment & Smoke Testing on Production**
    *   `- [ ]` Deploy to Railway.
    *   `- [ ]` Perform smoke tests on the live production bot.

---

### **Phase 7: Post-Launch Monitoring & Iteration**

*   **Task 7.1: Setup Monitoring & Alerting**
    *   `- [ ]` Monitor Railway logs and metrics.
    *   `- [ ]` Integrate Sentry or similar for error tracking (if not done earlier).
*   **Task 7.2: Gather User Feedback**
*   **Task 7.3: Plan for V1.1 (based on feedback and PRD Future Features, e.g., AI Matching, Mini App)**

---