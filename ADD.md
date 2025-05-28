# **Architectural Design Document (ADD)**

**Product Name:** NetWise

**Owner:** Anastasia314

**Version:** 1.0 (MVP)

**Date:** 2025-05-27

---

## 1. **Introduction**

### 1.1. Purpose
This document outlines the architectural design for NetWise, an intelligent networking assistant. It details the system's components, their interactions, data models, technology stack, and deployment strategy for the Minimum Viable Product (MVP) focused on a Telegram bot. The architecture is designed to be scalable for future enhancements, including a Telegram Mini App and a full mobile application.

### 1.2. Scope
The scope of this document covers the MVP features of NetWise:
*   Telegram Bot interface for user interaction.
*   User profile creation and management.
*   Friend invitation system and personal connection graph (1st and 2nd degree).
*   Request formulation and AI-powered matching.
*   Daily request digests.
*   Activity history and "social points" system.
*   Request economy (free tier, per-request charges, subscriptions).
*   Trust scoring mechanism.
*   User activity monitoring and management.

Future features like the Telegram Mini App, mobile application, random-coffee recommendations, and advanced paid features are considered for extensibility but not detailed for MVP implementation.

### 1.3. Definitions, Acronyms, and Abbreviations
*   **PRD:** Product Requirements Document
*   **ADD:** Architectural Design Document
*   **MVP:** Minimum Viable Product
*   **API:** Application Programming Interface
*   **DB:** Database
*   **AI:** Artificial Intelligence
*   **NLP:** Natural Language Processing
*   **CI/CD:** Continuous Integration/Continuous Deployment
*   **PaaS:** Platform as a Service
*   **BaaS:** Backend as a Service
*   **TWA:** Telegram Web App (Mini App)

---

## 2. **Architectural Goals and Constraints**

### 2.1. Goals
*   **Rapid Development & Deployment:** Leverage PaaS/BaaS for quick MVP launch.
*   **Scalability:** Design for growth in users, data, and feature set (especially towards mobile app).
*   **Maintainability:** Clean, modular code for easy updates and bug fixes.
*   **Cost-Effectiveness:** Optimize for low operational costs, especially in the early stages (target ~$100/month for 1000 users).
*   **User Experience:** Prioritize responsiveness and ease of use within the Telegram bot interface.
*   **Data Integrity & Security:** Ensure user data is handled securely and relationships are accurately represented.
*   **Extensibility:** The backend API should be designed to support future TWA and mobile clients with minimal changes.

### 2.2. Constraints
*   **Initial Platform:** Telegram Bot is the primary interface for MVP.
*   **Technology Stack:** Adherence to the stack defined in the PRD (Python/FastAPI, Supabase, aiogram, OpenAI, Railway).
*   **MVP Focus:** Prioritize core features; defer non-essential functionalities.
*   **Telegram UI Limitations:** Acknowledge and work within the native bot UI limitations, with TWA as a planned improvement.
*   **AI Dependency:** Reliance on OpenAI for embeddings, subject to their API availability and costs.

---

## 3. **System Overview**

NetWise will be a cloud-hosted application with a three-tier architecture:

1.  **Presentation Tier:** Telegram Bot (user interface).
2.  **Application Tier:** Python backend (FastAPI) handling business logic, AI matching, and API services.
3.  **Data Tier:** Supabase (PostgreSQL) for data persistence and BaaS features.

![System Architecture Diagram](https://i.imgur.com/Z0zJ31W.png)
*(Conceptual Diagram - replace with a more detailed one if using a diagramming tool)*

**User Interaction Flow (Example: Making a Request):**
1.  User interacts with the Telegram Bot (e.g., `/new_request` command).
2.  Telegram Bot (aiogram) receives the message and forwards it to the Backend API.
3.  Backend API (FastAPI):
    a.  Authenticates the user (via Telegram ID).
    b.  Validates the request.
    c.  Stores the request details in Supabase.
    d.  (Optionally) Generates embeddings for the request text using OpenAI API.
    e.  Queries Supabase for the user's 1st and 2nd-degree connections.
    f.  Retrieves profiles and potentially pre-computed embeddings of these connections.
    g.  Performs AI matching (keyword or embedding-based) considering trust scores and relevance.
    h.  Returns a list of potential helpers to the Telegram Bot.
4.  Telegram Bot formats and displays the list to the user.

---

## 4. **Component Design**

### 4.1. Telegram Bot (Client)
*   **Technology:** Python (aiogram)
*   **Responsibilities:**
    *   Handle user commands and messages.
    *   Manage conversation flows (finite state machine for multi-step processes like profile creation).
    *   Format and display data received from the backend.
    *   Send user inputs to the Backend API.
    *   Handle inline keyboards and callback queries for interactive elements.
    *   Generate unique invitation links.
*   **Key Modules (Conceptual):**
    *   `CommandHandler`: Processes `/start`, `/profile`, `/new_request`, etc.
    *   `MessageHandler`: Handles free-text inputs.
    *   `CallbackQueryHandler`: Manages button presses.
    *   `FSMContext`: Manages user state for multi-step interactions.
    *   `APIClient`: Wrapper for making requests to the Backend API.

### 4.2. Backend API
*   **Technology:** Python (FastAPI)
*   **Responsibilities:**
    *   Expose RESTful APIs for the Telegram Bot (and future clients).
    *   User authentication and authorization (based on Telegram User ID).
    *   Business logic for all core features.
    *   Interact with Supabase for data CRUD operations.
    *   Integrate with the AI Matching Service.
    *   Manage social points economy.
    *   Handle subscription and payment logic.
    *   Schedule and trigger daily digests/notifications.
*   **Key API Endpoints (Illustrative):**
    *   `POST /users/register` (implicit on first interaction)
    *   `PUT /users/{telegram_id}/profile`
    *   `GET /users/{telegram_id}/profile`
    *   `POST /users/{telegram_id}/invite` (generates link)
    *   `POST /connections` (when an invite is accepted or manually added)
    *   `PUT /connections/{connection_id}/trust`
    *   `POST /requests`
    *   `GET /requests/{telegram_id}/active`
    *   `GET /requests/match/{request_id}`
    *   `POST /requests/{request_id}/respond` (user indicates willingness to help)
    *   `GET /users/{telegram_id}/digest` (for daily suggestions)
    *   `POST /payments/subscribe`
    *   `POST /payments/webhook` (for payment provider callbacks)
*   **Modules (Conceptual):**
    *   `routers/user_router.py`: User profile, authentication.
    *   `routers/graph_router.py`: Connection management, trust.
    *   `routers/request_router.py`: Request creation, matching initiation.
    *   `routers/payment_router.py`: Subscription, one-off payments.
    *   `services/ai_matching_service.py`: Interface to AI capabilities.
    *   `services/notification_service.py`: Handles daily digests, reminders.
    *   `services/social_points_service.py`: Manages point economy.
    *   `core/security.py`: Authentication helpers.

### 4.3. Data Storage (Supabase)
*   **Technology:** Supabase (PostgreSQL backend, REST APIs, Auth, Storage)
*   **Responsibilities:**
    *   Persistent storage for all application data.
    *   User authentication (leveraging Supabase Auth if suitable, or custom logic with Telegram ID).
    *   Potentially serverless functions for specific tasks (e.g., cron jobs for daily digests if not handled by backend).
    *   Row Level Security (RLS) to enforce data access policies.
*   **Key Tables (Schema Sketch):**
    *   **`users`**:
        *   `telegram_id` (PK, BigInt, unique)
        *   `name` (Text)
        *   `role` (Text)
        *   `industry` (Text)
        *   `skills` (Text[])
        *   `goals` (Text[])
        *   `interests` (Text[])
        *   `profile_embedding` (Vector, optional, if pre-calculating)
        *   `social_points` (Int, default: 0)
        *   `free_requests_remaining` (Int, default: 5)
        *   `subscription_tier` (Text, nullable)
        *   `subscription_expires_at` (Timestamp, nullable)
        *   `last_active_at` (Timestamp)
        *   `is_active_in_search` (Boolean, default: true)
        *   `created_at` (Timestamp)
        *   `updated_at` (Timestamp)
    *   **`connections`**:
        *   `id` (UUID, PK)
        *   `user1_id` (BigInt, FK to `users.telegram_id`)
        *   `user2_id` (BigInt, FK to `users.telegram_id`)
        *   `connection_type` (Enum: "worked_together", "intro_made", "personal", "chat_help")
        *   `trust_score` (Int, 1-3)
        *   `status` (Enum: "pending", "accepted", default: "accepted" for MVP direct adds)
        *   `created_at` (Timestamp)
        *   *(Unique constraint on (`user1_id`, `user2_id`))*
    *   **`requests`**:
        *   `id` (UUID, PK)
        *   `requester_id` (BigInt, FK to `users.telegram_id`)
        *   `description_text` (Text)
        *   `description_embedding` (Vector, if using embeddings)
        *   `status` (Enum: "open", "pending_intro", "intro_made", "resolved", "closed")
        *   `created_at` (Timestamp)
        *   `expires_at` (Timestamp, e.g., 7 days after creation)
    *   **`request_matches_log`**: (Tracks who was suggested for what)
        *   `id` (UUID, PK)
        *   `request_id` (UUID, FK to `requests.id`)
        *   `suggested_user_id` (BigInt, FK to `users.telegram_id`)
        *   `introducer_user_id` (BigInt, FK to `users.telegram_id`, nullable)
        *   `match_score` (Float, optional)
        *   `status` (Enum: "suggested", "intro_requested_by_requester", "helper_accepted_intro", "helper_declined_intro", "intro_made_by_introducer")
        *   `created_at` (Timestamp)
    *   **`activity_history`**:
        *   `id` (UUID, PK)
        *   `user_id` (BigInt, FK to `users.telegram_id`)
        *   `action_type` (Enum: "helped_on_request", "sent_request", "received_intro")
        *   `related_request_id` (UUID, FK to `requests.id`, nullable)
        *   `points_change` (Int)
        *   `timestamp` (Timestamp)
    *   **`subscriptions`**: (If managing subscription details beyond user table)
        *   `id` (UUID, PK)
        *   `user_id` (BigInt, FK to `users.telegram_id`)
        *   `plan_name` (Text, e.g., "tier_500_friends")
        *   `stripe_subscription_id` (Text, unique, nullable)
        *   `start_date` (Timestamp)
        *   `end_date` (Timestamp)
        *   `status` (Enum: "active", "canceled", "past_due")

### 4.4. AI Matching Service
*   **Technology:** OpenAI Embeddings API, Cosine Similarity / Faiss (if vector search needed at scale, Supabase `pg_vector` can handle this initially).
*   **Responsibilities:**
    *   Generate embeddings for user profiles (skills, goals, interests) and request descriptions.
    *   Perform similarity searches to find relevant users for a given request.
    *   Incorporate trust scores, connection degrees (1st, 2nd), and request freshness into the matching algorithm.
*   **Logic Flow:**
    1.  Receive request text and requester's graph (friends, friends of friends).
    2.  Generate embedding for request text (via OpenAI).
    3.  For each candidate in the graph:
        a.  Retrieve their profile data/embedding.
        b.  Calculate relevance score (cosine similarity between request embedding and profile embedding, or keyword matching score).
        c.  Apply weights/boosts based on:
            *   Connection degree (Friend > Friend of Friend).
            *   Trust score (higher is better).
            *   User activity/freshness.
    4.  Filter and rank candidates.
    5.  Return top N candidates.
*   **Fallback:** For MVP, if OpenAI embedding integration is complex or costly initially, a simpler keyword-matching algorithm can be used as a baseline, with embeddings as a planned upgrade. Supabase `pg_vector` extension is ideal for storing and querying embeddings.

### 4.5. Payment Integration
*   **Technology:** Stripe (or similar, like Paddle, LemonSqueezy). Supabase can integrate with Stripe.
*   **Responsibilities:**
    *   Handle subscription sign-ups and recurring payments.
    *   Process one-time payments for additional requests.
    *   Manage webhook events from the payment provider (e.g., `payment_succeeded`, `subscription_canceled`).
    *   Update user subscription status and free request quotas in Supabase.

---

## 5. **Data Design**

Refer to Section 4.3 (Data Storage - Supabase) for the preliminary database schema.

### 5.1. Data Flow
*   **User Onboarding:** Telegram -> Bot -> API -> Supabase (create user).
*   **Profile Update:** Telegram -> Bot -> API -> Supabase (update user).
*   **Making a Request:** Telegram -> Bot -> API (store request, call AI service) -> AI Service (OpenAI, internal logic) -> API -> Supabase (store matches) -> Bot -> Telegram.
*   **Responding to Digest:** Telegram -> Bot -> API -> Supabase (update `request_matches_log`, `activity_history`, `social_points`).

### 5.2. Data Backup and Recovery
*   Supabase provides automated daily backups and Point-in-Time Recovery (PITR) capabilities depending on the plan. This will be the primary mechanism.

---

## 6. **Integration and APIs**

*   **Internal APIs:** The FastAPI backend will expose RESTful APIs as described in section 4.2. These APIs will be consumed by the `aiogram` bot.
*   **External APIs:**
    *   **Telegram Bot API:** Used by `aiogram` to send/receive messages.
    *   **OpenAI API:** For generating text embeddings.
    *   **Payment Gateway API (e.g., Stripe):** For processing payments.

---

## 7. **Deployment and Infrastructure**

### 7.1. Hosting
*   **Backend API (FastAPI) & Telegram Bot (aiogram):** Railway. Railway provides a PaaS environment suitable for Python applications, with auto-scaling and managed infrastructure. The bot and API can run as separate services or combined in one for simplicity initially.
*   **Database:** Supabase (managed PostgreSQL).

### 7.2. CI/CD
*   **Source Control:** Git (e.g., GitHub, GitLab).
*   **CI/CD Pipeline:** GitHub Actions (or Railway's native Git integration) to automatically build, test, and deploy the backend API and bot to Railway upon pushes to the main branch.

### 7.3. Environment Configuration
*   Separate configurations for `development`, `staging` (optional), and `production` environments.
*   Sensitive information (API keys, database credentials) managed via environment variables (e.g., Railway's environment variable management, Supabase Vault for secrets).

---

## 8. **Security Considerations**

*   **Authentication:** User identity primarily tied to their unique Telegram User ID. Backend API will validate requests based on this ID.
*   **Authorization:**
    *   Users can only modify their own profiles and requests.
    *   Supabase Row Level Security (RLS) will be configured to enforce data access rules at the database layer.
*   **Data Privacy:**
    *   Comply with relevant data privacy regulations (e.g., GDPR if applicable).
    *   Clearly communicate data usage to users.
*   **API Security:**
    *   HTTPS for all API communication.
    *   Input validation on all API endpoints to prevent injection attacks (FastAPI Pydantic models help here).
    *   Rate limiting on API endpoints to prevent abuse.
*   **Secret Management:** Use Railway's environment variables and Supabase Vault for API keys, database credentials, etc. Do not commit secrets to the repository.
*   **Spam/Abuse Prevention:**
    *   Monitor for unusual activity.
    *   Mechanism for reporting inappropriate requests or users.
    *   The social points system and paid requests can act as a deterrent.

---

## 9. **Scalability and Performance**

*   **Backend API:** FastAPI is asynchronous and highly performant. Railway allows for horizontal scaling of services.
*   **Database:** Supabase can scale its underlying PostgreSQL instances. Proper indexing of tables (especially on FKs, frequently queried columns, and for vector similarity search) will be crucial.
*   **AI Matching:**
    *   OpenAI API calls can be a bottleneck; consider asynchronous processing or batching.
    *   For vector search, Supabase `pg_vector` with HNSW indexing is efficient for millions of vectors. If scale exceeds this, dedicated vector DBs (e.g., Pinecone, Weaviate) or Faiss on a separate service could be considered in the future.
*   **Caching:** Implement caching (e.g., Redis, or FastAPI-Cache with a simple backend) for frequently accessed, less dynamic data (e.g., user profiles for active users, popular help categories) if performance bottlenecks are identified.
*   **Asynchronous Tasks:** For long-running operations like sending daily digests to many users or complex AI processing, use background task managers (e.g., Celery with RabbitMQ/Redis, or FastAPI's `BackgroundTasks`). Railway might have simpler solutions for background jobs.

---

## 10. **Monitoring and Logging**

*   **Application Logging:** Structured logging within the FastAPI application and aiogram bot. Logs will be streamed to Railway's logging service.
*   **Error Tracking:** Integrate a service like Sentry for real-time error reporting and monitoring.
*   **Performance Monitoring:** Railway provides basic metrics. For more detailed APM, tools like Datadog or New Relic could be integrated later.
*   **Supabase Monitoring:** Supabase dashboard provides insights into database performance and usage.
*   **Key Metrics to Monitor (Technical):** API response times, error rates, database query performance, AI service latency, message queue lengths (if using).

---

## 11. **Future Considerations (Post-MVP Architectural Evolution)**

*   **Telegram Mini App (TWA):** The existing FastAPI backend will serve the TWA. The TWA itself will be a React Native (or simple HTML/JS/CSS) application hosted and loaded within Telegram.
*   **Mobile Application (React Native):** The same FastAPI backend will be used. API authentication might need to be enhanced (e.g., JWTs) if users can sign up outside of Telegram.
*   **Graph Database:** If graph traversal queries become complex and a performance bottleneck on PostgreSQL at very large scale, migrating the graph data to a dedicated graph database (e.g., Neo4j) could be considered. Supabase's Postgres with recursive CTEs should suffice for a long time.
*   **Advanced AI/ML:**
    *   Fine-tuning models for better domain-specific matching.
    *   Developing more sophisticated trust and reputation algorithms.
*   **Microservices:** If the application grows significantly in complexity, certain components (e.g., AI Matching, Notifications, Payments) could be broken out into separate microservices. For now, a modular monolith is preferred.
*   **Real-time Features:** For instant notifications or chat within intros, WebSockets might be integrated (FastAPI supports this).

---

## 12. **Risks and Mitigation (Technical)**

*   **Cold Start - User Graph Density:**
    *   *Risk:* Users have few connections, making matching ineffective.
    *   *Mitigation (Technical):* Design efficient "invite friend" flows. Explore options for importing contacts (with user permission) if Telegram API allows or if shifting to mobile.
*   **AI Matching Accuracy:**
    *   *Risk:* AI provides irrelevant matches, frustrating users.
    *   *Mitigation:* Start with simpler keyword matching alongside embeddings. Implement a feedback mechanism for users to rate match quality. Continuously refine algorithms and potentially allow A/B testing of different matching strategies.
*   **Scalability of AI Matching:**
    *   *Risk:* OpenAI API costs or latency become prohibitive at scale. Vector DB queries become slow.
    *   *Mitigation:* Optimize embedding usage. Cache embeddings. Explore smaller, self-hostable embedding models for some tasks. Ensure `pg_vector` is properly indexed and configured.
*   **Supabase Lock-in/Limitations:**
    *   *Risk:* Over-reliance on Supabase-specific features might make migration hard. Limitations in BaaS offerings.
    *   *Mitigation:* Use Supabase primarily for its PostgreSQL core and standard BaaS features (Auth, Storage). Business logic resides in the FastAPI backend, making it portable.
*   **Telegram Bot API Limitations:**
    *   *Risk:* UI constraints, rate limits.
    *   *Mitigation:* Design interactions to be efficient. Plan for TWA to overcome UI limitations. Handle Telegram API rate limits gracefully.

---