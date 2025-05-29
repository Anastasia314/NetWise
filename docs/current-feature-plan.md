## `current-feature-plan.md`

**Title:** Backend: User API Endpoints Implementation

**Feature Description:**
This feature involves creating the API endpoints for user management using FastAPI. These endpoints will allow clients (initially the Telegram bot) to onboard new users, retrieve user profiles, and update user profiles. It also includes setting up a basic dependency for extracting user identity (Telegram ID) from requests. Integration tests will be written to verify the functionality of these endpoints.

**Tasks:**
*   `- [x] API: Create `app/api/` directory if it doesn't exist.`
*   `- [x] API: Create `app/api/__init__.py` and `app/api/users.py` files.`
*   `- [x] API: In `app/api/users.py`, create an `APIRouter` instance for user-related endpoints.`
*   `- [x] API: Import necessary Pydantic models (`UserCreate`, `UserProfileUpdate`, `UserResponse`), service functions (`user_service`), Supabase client, and FastAPI components (`APIRouter`, `Depends`, `HTTPException`, `Header`).`
*   `- [x] API: Create `app/api/deps.py` for API dependencies.`
*   `- [x] API: Implement `get_supabase_client()` dependency in `app/api/deps.py` to provide a Supabase client instance to endpoint functions. (This might use a global client or initialize one per request depending on `supabase-py` best practices).`
*   `- [x] API: Implement `get_current_telegram_id(x_telegram_id: int = Header(...))` dependency in `app/api/deps.py` to extract `telegram_id` from a custom request header `X-Telegram-Id`.`
*   `- [x] API: Implement `POST /users/onboard` endpoint in `app/api/users.py`.
    *   It should accept `telegram_id: int`, `name: Optional[str] = None`, `username: Optional[str] = None` in the request body (or derive `telegram_id` from header and other details from body via a `UserOnboardRequest` Pydantic model).
    *   Call `user_service.create_or_get_user_service`.
    *   Return `UserResponse` with status code 200 (if user exists) or 201 (if user created).`
*   `- [x] TEST: Create `tests/api/` directory and `tests/api/test_user_api.py` file.`
*   `- [x] TEST: Write integration test for `POST /users/onboard` (new user creation), mocking service layer, and asserting correct response code and body.`
*   `- [x] TEST: Write integration test for `POST /users/onboard` (existing user retrieval), mocking service layer, and asserting correct response code and body.`
*   `- [x] API: Implement `GET /users/{path_telegram_id}/profile` endpoint in `app/api/users.py`.
    *   Accept `path_telegram_id: int` as a path parameter.
    *   (Security check: Ensure `path_telegram_id` matches `current_telegram_id` from `get_current_telegram_id` dependency, or allow admins to fetch any). For MVP, assume user can only fetch their own.
    *   Call `user_service.get_user_profile_service`.
    *   Return `UserResponse` or 404 if not found.`
*   `- [x] TEST: Write integration test for `GET /users/{telegram_id}/profile` (user found), mocking service layer, and asserting correct response.`
*   `- [x] TEST: Write integration test for `GET /users/{telegram_id}/profile` (user not found), mocking service layer, and asserting 404 response.`
*   `- [x] TEST: Write integration test for `GET /users/{telegram_id}/profile` (unauthorized access if `path_telegram_id` doesn't match header `X-Telegram-Id`, if security check is implemented), asserting 403 response.`
*   `- [x] API: Implement `PUT /users/{path_telegram_id}/profile` endpoint in `app/api/users.py`.
    *   Accept `path_telegram_id: int` as a path parameter and `profile_update_data: UserProfileUpdate` in the request body.
    *   Security check: Ensure `path_telegram_id` matches `current_telegram_id` from `get_current_telegram_id` dependency.
    *   Call `user_service.update_user_profile_service`.
    *   Return updated `UserResponse` or 404 if not found.`
*   `- [x] TEST: Write integration test for `PUT /users/{telegram_id}/profile` (successful update), mocking service layer, and asserting correct response.`
*   `- [x] TEST: Write integration test for `PUT /users/{telegram_id}/profile` (user not found), mocking service layer, and asserting 404 response.`
*   `- [x] TEST: Write integration test for `PUT /users/{telegram_id}/profile` (unauthorized access), mocking service layer, and asserting 403 response.`
*   `- [x] API: Register the user `APIRouter` in the main FastAPI app (`app/main.py`) with a prefix like `/api/v1`.`