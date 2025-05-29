## `current-feature-plan.md`

**Title:** Backend: User Repository Implementation

**Feature Description:**
This feature involves creating the User Repository module (`user_repo.py`) responsible for all direct database interactions related to the `users` table. It will include functions for creating, retrieving, and updating user records in Supabase. Each function will be accompanied by unit tests that mock the Supabase client to ensure an isolated and reliable testing environment. The repository functions will utilize the Pydantic models defined in the previous step for data input and output.

**Tasks:**
*   `- [x] REPO: Create `app/db/` directory if it doesn't exist.`
*   `- [x] REPO: Create `app/db/__init__.py` and `app/db/user_repo.py` files.`
*   `- [x] REPO: Import necessary Pydantic models (`UserCreate`, `UserProfileUpdate`, `UserResponse`) and Supabase client type hint into `user_repo.py`.`
*   `- [x] REPO: Implement `get_user_by_telegram_id(db_client: Client, telegram_id: int) -> Optional[UserResponse]` function in `user_repo.py` to fetch a user by their Telegram ID from the Supabase `users` table.`
*   `- [x] TEST: Create `tests/db/` directory and `tests/db/test_user_repo.py` file.`
*   `- [x] TEST: Write unit test for `get_user_by_telegram_id` (user found scenario), mocking Supabase client response and asserting correct `UserResponse` object is returned.`
*   `- [x] TEST: Write unit test for `get_user_by_telegram_id` (user not found scenario), mocking Supabase client response and asserting `None` is returned.`
*   `- [x] REPO: Implement `create_user(db_client: Client, user_in: UserCreate) -> UserResponse` function in `user_repo.py` to insert a new user into the Supabase `users` table.`
*   `- [x] TEST: Write unit test for `create_user` (successful creation), mocking Supabase client's insert operation and asserting correct `UserResponse` object is returned.`
*   `- [x] TEST: Write unit test for `create_user` (handling potential database error, e.g., duplicate `telegram_id`), mocking Supabase client to raise an exception and asserting the repository function handles or re-raises it appropriately.`
*   `- [x] REPO: Implement `update_user_profile(db_client: Client, telegram_id: int, profile_data: UserProfileUpdate) -> Optional[UserResponse]` function in `user_repo.py` to update an existing user's profile in the Supabase `users` table. Ensure only provided fields are updated (e.g., using `model_dump(exclude_unset=True)`).`
*   `- [x] TEST: Write unit test for `update_user_profile` (successful update of a subset of fields), mocking Supabase client's update operation and asserting correct `UserResponse` object is returned with updated fields.`
*   `- [x] TEST: Write unit test for `update_user_profile` (user not found scenario), mocking Supabase client's update operation (e.g., if it returns no updated rows or an empty list) and asserting `None` is returned.`

**Files Involved:**
*   `app/db/user_repo.py`
*   `app/db/__init__.py`
*   `tests/db/test_user_repo.py`
*   `tests/db/__init__.py` (if `tests` is a package)
*   `app/models/user_models.py` (for imports)
*   `app/db/supabase_client.py` (for importing Supabase client type, if defined there, or directly `supabase.Client`)

**External Dependencies:**
*   `supabase-py` (for `supabase.Client` type hinting and mocked interactions)
*   `pytest` (for running tests)
*   `pytest-mock` or `unittest.mock` (for mocking the Supabase client)
*   `pydantic` (for `UserCreate`, `UserProfileUpdate`, `UserResponse` models)

**Notes:**
*   The Supabase client instance (`db_client: Client`) will be passed as an argument to each repository function. This promotes dependency injection and testability.
*   Repository functions should generally return Pydantic models (e.g., `UserResponse`) to provide a consistent data structure to the service layer.
*   `model_dump(exclude_unset=True)` on Pydantic models is crucial for update operations to ensure only fields explicitly set in the `UserProfileUpdate` model are sent to the database, allowing for partial updates.
*   Error handling: The repository layer can either re-raise database exceptions or handle them and return `None` / specific error indicators. For this stage, re-raising specific custom exceptions or letting Supabase client exceptions propagate for the service layer to handle is a common approach. The tasks assume returning `Optional[UserResponse]` for operations that might not find a user or fail gracefully at this level.
*   The test for `create_user` handling a DB error (like unique constraint violation) ensures the repository doesn't crash unexpectedly or mask the error. The exact behavior (re-raise, custom exception) should be decided and tested.

---