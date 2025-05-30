# **Current Feature Plan: Bot API Client Setup**

**Feature Description:**
This feature involves creating a dedicated API client within the Telegram bot application. This client will be responsible for all communication with the NetWise backend FastAPI application. For this initial setup, it will handle interactions related to user onboarding (registration) and profile management (fetching and updating user profiles). The client will use `httpx` for asynchronous HTTP requests and include robust error handling.

**Tasks:**

- [x] **FEAT: Initialize `APIClient` class in `bot/services/api_client.py`**
    *   Create the file `bot/services/api_client.py`.
    *   Define an `APIClient` class.
    *   Implement an `__init__` method that accepts `base_url: str` (for the backend API) and an optional `timeout: float` (defaulting to ~10 seconds).
    *   Initialize an `httpx.AsyncClient` instance within the `__init__` method, configured with the base URL and timeout.
    *   Define custom exception classes (e.g., `APIClientError` as a base, `APIClientResponseError` for non-2xx HTTP responses) either in this file or a shared `bot/utils/exceptions.py`.
    *   Ensure the `API_BASE_URL` can be loaded from a configuration file (e.g., `bot/core/config.py` sourcing from environment variables).

- [x] **FEAT: Implement `onboard_user` method in `APIClient`**
    *   Define an `async def onboard_user(self, telegram_id: int, name: str, username: Optional[str] = None) -> Dict:` method in `APIClient`.
    *   Construct the JSON payload: `{"telegram_id": telegram_id, "name": str(name), "username": username}`. (Ensuring `name` is stringified as Telegram's `first_name` can be complex).
    *   Make an asynchronous POST request to the backend's `/users/onboard` endpoint (or `/users/register` as per final backend implementation).
    *   Implement error handling:
        *   Catch `httpx.RequestError` (and subtypes like `ConnectTimeout`, `ReadTimeout`) and raise a custom `APIClientError`.
        *   Check the HTTP response status. If not 2xx (e.g., 200, 201), raise `APIClientResponseError` with status code and response content.
    *   On success, parse the JSON response and return it as a dictionary.

- [x] **FEAT: Implement `get_user_profile` method in `APIClient`**
    *   Define an `async def get_user_profile(self, telegram_id: int) -> Dict:` method in `APIClient`.
    *   Make an asynchronous GET request to the backend's `/users/{telegram_id}/profile` endpoint.
    *   Implement error handling similar to the `onboard_user` method.
    *   On success, parse the JSON response and return it as a dictionary.

- [x] **FEAT: Implement `update_user_profile` method in `APIClient`**
    *   Define an `async def update_user_profile(self, telegram_id: int, profile_data: Dict) -> Dict:` method in `APIClient`.
    *   The `profile_data` dictionary should correspond to the backend's `UserProfileUpdate` Pydantic model.
    *   Make an asynchronous PUT request to the backend's `/users/{telegram_id}/profile` endpoint, sending `profile_data` as the JSON body.
    *   Implement error handling similar to the `onboard_user` method.
    *   On success, parse the JSON response and return it as a dictionary.

- [x] **TEST: Add unit tests for `APIClient` initialization and basic error handling**
    *   Create `tests/bot/services/test_api_client.py`.
    *   Write tests to verify:
        *   Correct instantiation of `APIClient` with `base_url` and `httpx.AsyncClient`.
        *   Custom exceptions (`APIClientError`, `APIClientResponseError`) are raised appropriately (can use `respx` to mock a generic failing request for this).

- [x] **TEST: Add unit tests for `APIClient.onboard_user` method**
    *   Use `respx` to mock the `/users/onboard` (or `/users/register`) endpoint.
    *   Test the successful case (e.g., 201 Created response) and verify the returned data.
    *   Test API error responses (e.g., 400 Bad Request, 422 Unprocessable Entity, 500 Internal Server Error) and ensure correct exceptions are raised.
    *   Test network errors (e.g., `httpx.ConnectTimeout`) and ensure `APIClientError` is raised.

- [x] **TEST: Add unit tests for `APIClient.get_user_profile` method**
    *   Use `respx` to mock the `/users/{telegram_id}/profile` endpoint.
    *   Test the successful case (200 OK response) and verify the returned data.
    *   Test API error responses (e.g., 404 Not Found, 500 Internal Server Error).
    *   Test network errors.

- [x] **TEST: Add unit tests for `APIClient.update_user_profile` method**
    *   Use `respx` to mock the `/users/{telegram_id}/profile` endpoint.
    *   Test the successful case (200 OK response) and verify the returned data.
    *   Test API error responses (e.g., 400 Bad Request, 404 Not Found, 422 Unprocessable Entity, 500 Internal Server Error).
    *   Test network errors.

- [x] **REFACTOR: Integrate `APIClient` instance into bot's context or DI system**
    *   Update `bot/main.py` (or where bot/dispatcher are initialized) to:
        *   Load `API_BASE_URL` from configuration.
        *   Instantiate the `APIClient`.
        *   Make the `APIClient` instance available to handlers (e.g., by passing it through `aiogram`'s dispatcher context, using middleware, or a simple DI approach).

**Files Involved:**
*   `bot/services/api_client.py` (New file)
*   `bot/core/config.py` (For `API_BASE_URL` configuration)
*   `bot/main.py` (Or relevant bot initialization module, for `APIClient` instantiation and DI)
*   `tests/bot/services/test_api_client.py` (New file)
*   `bot/utils/exceptions.py` (Potentially new, for custom API client exceptions)

**External Dependencies:**
*   `httpx`: For making asynchronous HTTP requests.
*   `pytest`: For running unit tests.
*   `pytest-asyncio`: For testing asynchronous code with pytest.
*   `respx`: For mocking `httpx` requests in tests.

**Notes:**
*   The API endpoints (`/users/onboard`, `/users/{telegram_id}/profile`) and expected JSON payloads/responses must align with the backend API implemented in Phase 1.
*   The `APIClient` should be designed to be easily extensible for future API methods.
*   Consider adding a `async def close(self)` method to the `APIClient` to properly close the `httpx.AsyncClient` session, and call this during bot shutdown.
*   Logging within the `APIClient` methods (e.g., logging outgoing requests, received responses/errors) would be beneficial for debugging.
```