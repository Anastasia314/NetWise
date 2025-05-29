## `current-feature-plan.md`

**Title:** Backend: User Service Implementation

**Feature Description:**
This feature involves creating the User Service module (`user_service.py`), which will encapsulate the business logic for user management. It will interact with the User Repository to perform database operations and will be called by the API endpoints. Key functionalities include handling a user's first interaction (creating or retrieving their profile), updating user profiles, and fetching user profiles. Unit tests will be written to mock the repository layer, ensuring the service logic is tested in isolation.

**Tasks:**
*   `- [x] SERVICE: Create `app/services/` directory if it doesn't exist.`
*   `- [x] SERVICE: Create `app/services/__init__.py` and `app/services/user_service.py` files.`
*   `- [x] SERVICE: Import necessary Pydantic models (`UserCreate`, `UserProfileUpdate`, `UserResponse`) and repository functions (`user_repo`) into `user_service.py`. Import Supabase client type hint.`
*   `- [x] SERVICE: Implement `get_user_profile_service(db_client: Client, telegram_id: int) -> Optional[UserResponse]` in `user_service.py`. This function will call `user_repo.get_user_by_telegram_id`.`
*   `- [x] TEST: Create `tests/services/` directory and `tests/services/test_user_service.py` file.`
*   `- [x] TEST: Write unit test for `get_user_profile_service` (user found), mocking `user_repo.get_user_by_telegram_id` to return a user, and assert the service returns the same user.`
*   `- [x] TEST: Write unit test for `get_user_profile_service` (user not found), mocking `user_repo.get_user_by_telegram_id` to return `None`, and assert the service returns `None` (or raises an appropriate `HTTPException` like `404 Not Found`).`
*   `- [x] SERVICE: Implement `create_or_get_user_service(db_client: Client, telegram_id: int, name: Optional[str], username: Optional[str]) -> UserResponse` in `user_service.py`. Logic:
    *   Attempt to fetch user by `telegram_id` using `user_repo.get_user_by_telegram_id`.
    *   If user exists, return the user.
    *   If user does not exist, create a `UserCreate` object (using `telegram_id` and `name` if provided) and call `user_repo.create_user`. Return the new user.`
*   `- [x] TEST: Write unit test for `create_or_get_user_service` (user exists), mocking `user_repo.get_user_by_telegram_id` to return an existing user and `user_repo.create_user` not to be called. Assert the existing user is returned.`
*   `- [x] TEST: Write unit test for `create_or_get_user_service` (user does not exist), mocking `user_repo.get_user_by_telegram_id` to return `None`, and `user_repo.create_user` to return a new user. Assert the new user is returned and `create_user` was called with correct parameters.`
*   `- [x] SERVICE: Implement `update_user_profile_service(db_client: Client, telegram_id: int, profile_data_in: UserProfileUpdate) -> UserResponse` in `user_service.py`.
    *   Call `user_repo.update_user_profile`.
    *   If update successful (user found and updated), return the updated user.
    *   If user not found (repository returns `None`), raise an `HTTPException(status_code=404, detail="User not found")`.`
*   `- [x] TEST: Write unit test for `update_user_profile_service` (successful update), mocking `user_repo.update_user_profile` to return an updated user. Assert the updated user is returned.`
*   `- [x] TEST: Write unit test for `update_user_profile_service` (user not found), mocking `user_repo.update_user_profile` to return `None`. Assert `HTTPException` with status 404 is raised.`
*   `- [x] SERVICE: Add business logic/validation to `update_user_profile_service` if any specific rules apply before calling the repository (e.g., validating `skills` list length, though Pydantic handles basic type validation). For MVP, this might be minimal beyond what Pydantic provides.`

**Files Involved:**
*   `app/services/user_service.py`
*   `app/services/__init__.py`
*   `tests/services/test_user_service.py`
*   `tests/services/__init__.py` (if `tests` is a package)
*   `app/db/user_repo.py` (for imports)
*   `app/models/user_models.py` (for imports)
*   `fastapi.HTTPException` (for imports)

**External Dependencies:**
*   `fastapi` (for `HTTPException`)
*   `pytest` (for running tests)
*   `pytest-mock` or `unittest.mock` (for mocking the repository functions)
*   `pydantic` (for user models)
*   `supabase-py` (for `supabase.Client` type hinting)

**Notes:**
*   Service layer functions will also take `db_client: Client` as an argument to pass down to the repository layer. This maintains consistency and allows for session management if needed later.
*   The service layer is where business logic, more complex validations (beyond Pydantic's scope), and orchestrations of multiple repository calls would typically reside.
*   Error Handling: Unlike the repository which might return `None`, the service layer often translates these into `HTTPException`s suitable for the API layer to return to the client.
*   The `username` parameter in `create_or_get_user_service` is included as per the task description, though its direct use in `UserCreate` might depend on whether `username` is a distinct field in the `users` table or if `name` is intended to store it. For now, `name`