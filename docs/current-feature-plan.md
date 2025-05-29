## `current-feature-plan.md`

**Title:** Backend: User API Endpoints Implementation

**Feature Description:**
This feature involves creating the API endpoints for user management using FastAPI. These endpoints will allow clients (initially the Telegram bot) to onboard new users, retrieve user profiles, and update user profiles. It also includes setting up a basic dependency for extracting user identity (Telegram ID) from requests. Integration tests will be written to verify the functionality of these endpoints.

**Tasks:**
*   `- [ ] API: Create `app/api/` directory if it doesn't exist.`
*   `- [ ] API: Create `app/api/__init__.py` and `app/api/users.py` files.`
*   `- [ ] API: In `app/api/users.py`, create an `APIRouter` instance for user-related endpoints.`
*   `- [ ] API: Import necessary Pydantic models (`UserCreate`, `UserProfileUpdate`, `UserResponse`), service functions (`user_service`), Supabase client, and FastAPI components (`APIRouter`, `Depends`, `HTTPException`, `Header`).`
*   `- [ ] API: Create `app/api/deps.py` for API dependencies.`
*   `- [ ] API: Implement `get_supabase_client()` dependency in `app/api/deps.py` to provide a Supabase client instance to endpoint functions. (This might use a global client or initialize one per request depending on `supabase-py` best practices).`
*   `- [ ] API: Implement `get_current_telegram_id(x_telegram_id: int = Header(...))` dependency in `app/api/deps.py` to extract `telegram_id` from a custom request header `X-Telegram-Id`.`
*   `- [ ] API: Implement `POST /users/onboard` endpoint in `app/api/users.py`.
    *   It should accept `telegram_id: int`, `name: Optional[str] = None`, `username: Optional[str] = None` in the request body (or derive `telegram_id` from header and other details from body via a `UserOnboardRequest` Pydantic model).
    *   Call `user_service.create_or_get_user_service`.
    *   Return `UserResponse` with status code 200 (if user exists) or 201 (if user created).`
*   `- [ ] TEST: Create `tests/api/` directory and `tests/api/test_user_api.py` file.`
*   `- [ ] TEST: Write integration test for `POST /users/onboard` (new user creation), mocking service layer, and asserting correct response code and body.`
*   `- [ ] TEST: Write integration test for `POST /users/onboard` (existing user retrieval), mocking service layer, and asserting correct response code and body.`
*   `- [ ] API: Implement `GET /users/{path_telegram_id}/profile` endpoint in `app/api/users.py`.
    *   Accept `path_telegram_id: int` as a path parameter.
    *   (Security check: Ensure `path_telegram_id` matches `current_telegram_id` from `get_current_telegram_id` dependency, or allow admins to fetch any). For MVP, assume user can only fetch their own.
    *   Call `user_service.get_user_profile_service`.
    *   Return `UserResponse` or 404 if not found.`
*   `- [ ] TEST: Write integration test for `GET /users/{telegram_id}/profile` (user found), mocking service layer, and asserting correct response.`
*   `- [ ] TEST: Write integration test for `GET /users/{telegram_id}/profile` (user not found), mocking service layer, and asserting 404 response.`
*   `- [ ] TEST: Write integration test for `GET /users/{telegram_id}/profile` (unauthorized access if `path_telegram_id` doesn't match header `X-Telegram-Id`, if security check is implemented), asserting 403 response.`
*   `- [ ] API: Implement `PUT /users/{path_telegram_id}/profile` endpoint in `app/api/users.py`.
    *   Accept `path_telegram_id: int` as a path parameter and `profile_update_data: UserProfileUpdate` in the request body.
    *   Security check: Ensure `path_telegram_id` matches `current_telegram_id` from `get_current_telegram_id` dependency.
    *   Call `user_service.update_user_profile_service`.
    *   Return updated `UserResponse` or 404 if not found.`
*   `- [ ] TEST: Write integration test for `PUT /users/{telegram_id}/profile` (successful update), mocking service layer, and asserting correct response.`
*   `- [ ] TEST: Write integration test for `PUT /users/{telegram_id}/profile` (user not found), mocking service layer, and asserting 404 response.`
*   `- [ ] TEST: Write integration test for `PUT /users/{telegram_id}/profile` (unauthorized access), mocking service layer, and asserting 403 response.`
*   `- [ ] API: Register the user `APIRouter` in the main FastAPI app (`app/main.py`) with a prefix like `/api/v1`.`

**Files Involved:**
*   `app/api/users.py`
*   `app/api/deps.py`
*   `app/api/__init__.py`
*   `app/main.py` (to include the router)
*   `tests/api/test_user_api.py`
*   `tests/api/__init__.py`
*   `app/services/user_service.py` (for imports)
*   `app/models/user_models.py` (for imports)
*   `app/db/supabase_client.py` (if `get_supabase_client` is defined there)

**External Dependencies:**
*   `fastapi` (for `APIRouter`, `Depends`, `HTTPException`, `Header`, `Path`, `Body`)
*   `uvicorn` (for running the FastAPI app during testing)
*   `httpx` (for making requests to the API in integration tests)
*   `pytest` (for running tests)
*   `pytest-mock` or `unittest.mock` (for mocking the service layer in tests)
*   `pydantic` (for user models)
*   `supabase-py` (for `supabase.Client` type hinting and actual client if used in `deps.py`)

**Notes:**
*   **Authentication/Authorization:** For MVP, a simple `X-Telegram-Id` header is used. In a more robust system, proper authentication (e.g., JWT tokens) would be implemented. The security check (`path_telegram_id` matching header `X-Telegram-Id`) is a basic authorization measure for MVP.
*   **Onboarding Endpoint Design:** The `POST /users/onboard` endpoint can either take all info in the body (requiring a new Pydantic model like `UserOnboardRequest`) or use a combination of path/header for `telegram_id` and body for other optional fields. The task list leans towards a body that might include `telegram_id` initially, or adjust to using the header `telegram_id` as the primary identifier. For consistency, using the `X-Telegram-Id` header for identification and a Pydantic model for optional onboarding data (`name`, `username`) in the body might be cleaner. The `create_or_get_user_service` would then primarily use the header `telegram_id`.
*   **Supabase Client Dependency:** The `get_supabase_client` dependency will manage how the Supabase client is provided to repository/service layers when called from an API endpoint. This might involve initializing the client once globally or per-request based on `supabase-py` and FastAPI best practices for connection management.
*   **Integration Tests:** These tests will use `TestClient` from FastAPI or `httpx` to make actual HTTP requests to the endpoints, mocking the service layer to isolate API logic testing.
*   **API Versioning:** The router is prefixed with `/api/v1` to allow for future API versions.
*   The `username` field in the onboarding request is passed to the service, but its persistence depends on whether it's a distinct DB field.

---