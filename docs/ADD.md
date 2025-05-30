# **Architectural Design Document (ADD)**

**Product Name:** NetWise
**Owner:** Anastasia314
**Date:** 2025-05-28

**Version:** 1.0 (MVP - Simplified Telegram Bot Focus)

---

## 1. **Introduction**

### 1.1. Purpose
This document outlines the architectural design for the NetWise Minimum Viable Product (MVP), an intelligent networking assistant delivered as a Telegram bot. It details the bot's internal structure, its interaction with the data store (Supabase), AI matching logic, technology stack, and deployment strategy. The architecture prioritizes simplicity and rapid development for the initial launch.

### 1.2. Scope
The scope of this document covers the MVP features of NetWise, implemented entirely within the Telegram Bot application:
*   Telegram Bot interface for user interaction.
*   User profile creation and management.
*   Friend invitation system and personal connection graph (1st and 2nd degree).
*   Request formulation and AI-powered matching.
*   Daily request digests.
*   Activity history and "social points" system.
*   Request economy (free tier, per-request charges, subscriptions).
*   Trust scoring mechanism.
*   User activity monitoring and management.

Future features like a Telegram Mini App are considered for extensibility but are outside the scope of this initial MVP architecture.

### 1.3. Definitions, Acronyms, and Abbreviations
*   **PRD:** Product Requirements Document
*   **ADD:** Architectural Design Document
*   **MVP:** Minimum Viable Product
*   **DB:** Database
*   **AI:** Artificial Intelligence
*   **CI/CD:** Continuous Integration/Continuous Deployment
*   **PaaS:** Platform as a Service
*   **TWA:** Telegram Web App (Mini App - Post-MVP)

---

## 2. **Architectural Goals and Constraints**

### 2.1. Goals
*   **Rapid Development & Deployment:** Leverage PaaS for quick MVP launch of the bot.
*   **Simplicity:** A single, manageable Python application for the Telegram bot.
*   **Scalability (User Base):** Design for growth in users and data within the Supabase and bot infrastructure.
*   **Maintainability:** Clean, modular code within the bot application for easy updates and bug fixes.
*   **Cost-Effectiveness:** Optimize for low operational costs (target ~$100/month for 1000 users).
*   **User Experience:** Prioritize responsiveness and ease of use within the Telegram bot interface.
*   **Data Integrity & Security:** Ensure user data is handled securely via Supabase and relationships are accurately represented.

### 2.2. Constraints
*   **Sole Platform:** Telegram Bot is the only interface for MVP.
*   **Technology Stack:** Adherence to the stack: Python (aiogram) for the bot, Supabase for data, OpenAI for embeddings, Railway for hosting.
*   **MVP Focus:** Prioritize core features; defer non-essential functionalities.
*   **Telegram UI Limitations:** Work within the native bot UI limitations.
*   **AI Dependency:** Reliance on OpenAI for embeddings, subject to their API availability and costs.

---

## 3. **System Overview**

NetWise MVP will be a cloud-hosted application consisting of two primary tiers:

1.  **Application Tier:** The Telegram Bot, built with Python (aiogram). This single application handles all user interactions, business logic, AI matching coordination, and direct communication with the data tier.
2.  **Data Tier:** Supabase (PostgreSQL) for data persistence, user authentication (via Telegram ID), and potentially serverless functions for simple scheduled tasks if not handled by the bot's internal scheduler.

**User Interaction Flow (Example: Making a Request):**
1.  User interacts with the Telegram Bot (e.g., `/new_request` command).
2.  The Telegram Bot (aiogram Python application):
    a.  Receives the message and authenticates the user (via Telegram ID).
    b.  Validates the request.
    c.  Stores the request details directly in Supabase using the Supabase Python client library.
    d.  (Optionally) Generates embeddings for the request text by calling the OpenAI API.
    e.  Queries Supabase for the user's 1st and 2nd-degree connections and their profiles.
    f.  Performs AI matching (keyword or embedding-based) considering trust scores and relevance, using data retrieved from Supabase.
    g.  Formats and displays the list of potential helpers back to the user in Telegram.

---

## 4. **Component Design**

### 4.1. Telegram Bot Application
*   **Technology:** Python (aiogram), Supabase Python Client, OpenAI Python Client.
*   **Responsibilities:**
    *   Handle all user commands and messages from Telegram.
    *   Manage conversation flows (finite state machine for multi-step processes).
    *   Format and display data to the user.
    *   Directly perform CRUD operations on Supabase for user profiles, connections, requests, etc.
    *   Implement business logic for social points, request economy, and subscription status checks (querying Supabase).
    *   Call the OpenAI API for embeddings generation.
    *   Execute the AI matching algorithm (keyword-based or vector similarity search against Supabase data).
    *   Schedule and send daily digests/notifications (e.g., using `apscheduler` library within the bot process).
    *   Generate unique invitation links.
    *   Handle payment integration callbacks (if a payment provider's webhook directly calls an endpoint exposed by the bot, or through polling/manual checks based on payment provider integration).
*   **Key Internal Modules (Conceptual within the Python application):**
    *   `handlers/`: Contains modules for command handlers, message handlers, callback query handlers.
    *   `fsm_states/`: Defines states for conversation flows.
    *   `services/supabase_service.py`: A wrapper for all Supabase client interactions (CRUD operations, custom queries).
    *   `services/ai_matching_service.py`: Contains logic for keyword extraction, OpenAI API calls, embedding generation, and performing matching queries against Supabase (e.g., using `pg_vector` functions via the Supabase client).
    *   `services/user_service.py`: Manages user profile logic, social points, subscription status.
    *   `services/graph_service.py`: Manages connection logic and trust scores.
    *   `services/request_service.py`: Manages request creation and lifecycle.
    *   `services/notification_service.py`: Manages creation and sending of daily digests.
    *   `services/payment_service.py`: (If applicable for MVP) Stubs or basic integration for payment provider interactions.
    *   `scheduler.py`: Configures and runs scheduled tasks like daily digests.
    *   `main.py` / `bot.py`: Entry point, initializes bot, dispatcher, and services.

### 4.2. Data Storage (Supabase)
*   **Technology:** Supabase (PostgreSQL backend, REST APIs, Auth, Storage, `pg_vector` extension)
*   **Responsibilities:**
    *   Persistent storage for all application data.
    *   User authentication using Telegram User ID as the primary identifier.
    *   Data access through the Supabase Python client library by the Telegram Bot application.
    *   Row Level Security (RLS) to enforce data access policies, providing an additional layer of security even with direct client access.
    *   Storing and indexing vector embeddings for AI matching (`pg_vector`).
*   **Key Tables (Schema Sketch - same as PRD):**
    *   **`users`**:
        *   `telegram_id` (PK, BigInt, unique), `name` (Text), `role` (Text), `industry` (Text), `skills` (Text[]), `goals` (Text[]), `interests` (Text[]), `profile_embedding` (Vector), `social_points` (Int), `free_requests_remaining` (Int), `subscription_tier` (Text), `subscription_expires_at` (Timestamp), `last_active_at` (Timestamp), `is_active_in_search` (Boolean), `created_at`, `updated_at`.
    *   **`connections`**:
        *   `id` (UUID, PK), `user1_id` (FK), `user2_id` (FK), `connection_type` (Enum), `trust_score` (Int), `status` (Enum), `created_at`.
    *   **`requests`**:
        *   `id` (UUID, PK), `requester_id` (FK), `description_text` (Text), `description_embedding` (Vector), `status` (Enum), `created_at`, `expires_at`.
    *   **`request_matches_log`**:
        *   `id` (UUID, PK), `request_id` (FK), `suggested_user_id` (FK), `introducer_user_id` (FK), `match_score` (Float), `status` (Enum), `created_at`.
    *   **`activity_history`**:
        *   `id` (UUID, PK), `user_id` (FK), `action_type` (Enum), `related_request_id` (FK), `points_change` (Int), `timestamp`.
    *   **`subscriptions`**:
        *   `id` (UUID, PK), `user_id` (FK), `plan_name` (Text), `payment_provider_subscription_id` (Text), `start_date`, `end_date`, `status` (Enum).

### 4.3. AI Matching Logic (MVP: Keyword/Profile-based within Bot Application)
*   **Technology (MVP):** Python logic within the bot application, direct SQL queries to Supabase (via its client) using `ILIKE` or PostgreSQL Full-Text Search (FTS).
*   **Post-MVP Enhancement:** OpenAI Embeddings API (called from bot application), vector storage in Supabase (`pg_vector`), and cosine similarity queries executed via Supabase client.
*   **Responsibilities (MVP):**
    *   Bot application receives a user's request.
    *   Bot application extracts keywords from the request description.
    *   Bot application queries Supabase for profiles of 1st and 2nd-degree connections.
    *   Bot application performs keyword matching against profile attributes (`skills`, `role`, `industry`, etc.).
    *   Bot application ranks helpers based on match score, connection degree, trust score, and activity.
*   **Logic Flow (MVP - executed by the bot application):**
    1.  Input: Request text, requester's Telegram ID.
    2.  Keyword Extraction: Bot extracts keywords from request text.
    3.  Candidate Retrieval: Bot queries Supabase for 1st/2nd degree friends and their profiles.
    4.  Candidate Evaluation: For each candidate, bot compares request keywords with profile fields. Score based on matches.
    5.  Score Weighting: Adjust score by connection degree, trust score (from Supabase), user activity.
    6.  Filtering & Ranking: Bot filters low-score candidates and ranks the rest.
    7.  Output: Bot presents top N candidates to the requester.

### 4.4. Payment Integration
*   **Technology:** Stripe (or similar) Python SDK.
*   **Responsibilities (within Bot application):**
    *   Bot application guides users through subscription sign-up (e.g., sending a Stripe checkout link).
    *   Bot application may need a simple, secure webhook endpoint (if Railway allows incoming HTTP to bot process easily) or rely on periodic checks/manual updates for payment success.
    *   Bot application updates user subscription status and quotas in Supabase based on payment confirmations.

---

## 5. **Data Design**

Refer to Section 4.2 (Data Storage - Supabase) for the database schema.

### 5.1. Data Flow
*   **User Onboarding:** Telegram -> Bot App -> Supabase (create user).
*   **Profile Update:** Telegram -> Bot App -> Supabase (update user).
*   **Making a Request:** Telegram -> Bot App (processes, calls OpenAI if needed, queries Supabase for graph/profiles, performs matching) -> Supabase (store request, log matches) -> Bot App -> Telegram.
*   **Responding to Digest:** Telegram -> Bot App -> Supabase (update `request_matches_log`, `activity_history`, `social_points`).

### 5.2. Data Backup and Recovery
*   Supabase provides automated daily backups and Point-in-Time Recovery (PITR) capabilities. This will be the primary mechanism.

---

## 6. **Integration and APIs**

*   **External APIs used by the Bot Application:**
    *   **Telegram Bot API:** Used by `aiogram` to send/receive messages.
    *   **Supabase API:** Primarily via Supabase Python client library for database operations and auth.
    *   **OpenAI API:** For generating text embeddings.
    *   **Payment Gateway API (e.g., Stripe):** Via Python SDK for processing payments.

---

## 7. **Deployment and Infrastructure**

### 7.1. Hosting
*   **Telegram Bot Application (Python/aiogram):** Railway. Railway hosts the single Python application.
*   **Database:** Supabase (managed PostgreSQL).

### 7.2. CI/CD
*   **Source Control:** Git (e.g., GitHub).
*   **CI/CD Pipeline:** GitHub Actions (or Railway's native Git integration) to automatically build and deploy the bot application to Railway upon pushes to the main branch.

### 7.3. Environment Configuration
*   Separate configurations for `development` and `production` environments.
*   Sensitive information (Telegram Bot Token, Supabase URL/keys, OpenAI API key, payment provider keys) managed via environment variables in Railway.

---

## 8. **Security Considerations**

*   **Authentication:** User identity tied to their unique Telegram User ID. The bot application uses this for all operations.
*   **Authorization:**
    *   Bot logic ensures users can only modify their own data.
    *   Supabase Row Level Security (RLS) configured to provide database-level protection, ensuring the bot's API key for Supabase has appropriately restricted access.
*   **Data Privacy:**
    *   Adherence to data privacy best practices.
*   **API Key Security:**
    *   Supabase API keys, OpenAI key, and other sensitive keys stored securely as environment variables on Railway, not in code.
    *   Use Supabase's `anon` key for client-side operations if ever doing direct DB calls from a TWA (post-MVP), and `service_role` key securely within the bot application. For bot-only MVP, `service_role` key is used by the bot.
*   **Input Validation:** The bot application validates all user inputs to prevent errors and basic injection-style attacks before interacting with Supabase or other services.
*   **Spam/Abuse Prevention:**
    *   Social points system and paid requests as deterrents.
    *   Rate limiting for bot commands handled by `aiogram` middleware if necessary.

---

## 9. **Scalability and Performance**

*   **Bot Application:** `aiogram` is asynchronous. Railway can scale the service running the bot application if needed (e.g., by increasing resources or running multiple instances if the bot is stateless or state is managed externally).
*   **Database:** Supabase can scale its PostgreSQL instances. Proper indexing in Supabase tables is crucial.
*   **AI Matching:**
    *   OpenAI API calls are external; bot handles them asynchronously.
    *   Vector search in Supabase (`pg_vector`) needs appropriate indexing (HNSW).
*   **Asynchronous Tasks:** `aiogram` handles I/O-bound tasks asynchronously. CPU-bound tasks within matching or digest generation should be optimized or run in a way that doesn't block the main bot event loop (e.g., `asyncio.to_thread` for short tasks, or if Railway supports, separate worker processes for heavy jobs like daily digest generation for many users). For MVP, `apscheduler` within the bot process should be sufficient.

---

## 10. **Monitoring and Logging**

*   **Application Logging:** Structured logging within the `aiogram` bot application. Logs streamed to Railway's logging service.
*   **Error Tracking:** Integrate a service like Sentry for real-time error reporting.
*   **Supabase Monitoring:** Supabase dashboard provides insights into database performance and usage.
*   **Key Metrics to Monitor (Technical):** Bot response times, error rates, Supabase query performance, OpenAI API latency.

---

## 11. **Future Considerations (Post-MVP Architectural Evolution)**

*   **Telegram Mini App (TWA):** The bot application might evolve to expose a few simple, secure HTTP endpoints (e.g., using `aiohttp` alongside `aiogram`) for the TWA, or the TWA could interact with Supabase directly (secured with RLS and user-specific JWTs from Supabase Auth). This is the primary planned evolution for UI enhancement.
*   **Dedicated Backend Service:** If the bot application's logic becomes too complex or if more robust API capabilities are needed for the TWA or other future integrations, a dedicated FastAPI backend service could be developed. The bot would then communicate with this backend.
*   **Graph Database:** If graph queries become a bottleneck, consider migration.
*   **Advanced AI/ML & Real-time Features:** As per original ADD.

---

## 12. **Risks and Mitigation (Technical)**

*   **Cold Start - User Graph Density:**
    *   *Risk:* Users have few connections, making matching ineffective.
    *   *Mitigation:* Design efficient "invite friend" flows.
*   **AI Matching Accuracy:**
    *   *Risk:* AI provides irrelevant matches.
    *   *Mitigation:* Start with simpler keyword matching. Implement feedback.
*   **Scalability of Bot Application:**
    *   *Risk:* Single bot process becomes a bottleneck for CPU-bound tasks or managing too many concurrent users/scheduled jobs.
    *   *Mitigation:* Optimize code. Ensure heavy tasks are non-blocking. Plan for potential separation of concerns (e.g., scheduler to a separate small worker) if Railway supports it easily or if moving to a more flexible hosting.
*   **Supabase Limitations/Costs:**
    *   *Risk:* Hitting Supabase free/paid tier limits unexpectedly.
    *   *Mitigation:* Monitor usage. Optimize queries. Business logic largely in Python, allowing easier migration of compute if needed.
*   **Telegram Bot API Limitations:**
    *   *Risk:* UI constraints, rate limits.
    *   *Mitigation:* Design interactions efficiently. Plan for TWA. Handle API rate limits in code.
*   **Monolithic Bot Complexity:**
    *   *Risk:* The single Python application becomes difficult to maintain as features grow.
    *   *Mitigation:* Strict modular design within the bot application. Clear separation of concerns into services/modules. Be prepared to refactor parts into a dedicated backend service (see Future Considerations) if complexity grows beyond manageable limits for a single bot codebase.

---