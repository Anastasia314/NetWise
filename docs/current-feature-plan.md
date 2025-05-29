## `current-feature-plan.md`

**Title:** Backend: User Pydantic Models

**Feature Description:**
This feature focuses on defining the Pydantic models for user-related data structures in the FastAPI backend. These models will be used for request and response validation, data serialization/deserialization, and ensuring type safety for user data throughout the application. This includes models for basic user information, user creation, profile updates, and API responses, as well as any common enumerations related to user attributes.

**Tasks:**
*   `- [x] MODEL: Create `app/models/` directory if it doesn't exist.`
*   `- [x] MODEL: Create `app/models/user_models.py` file.`
*   `- [x] MODEL: Define `UserBase(BaseModel)` in `user_models.py` with common user fields: `telegram_id: int`, `name: Optional[str] = None`, `role: Optional[str] = None`, `industry: Optional[str] = None`, `skills: Optional[List[str]] = Field(default_factory=list)`, `goals: Optional[List[str]] = Field(default_factory=list)`, `interests: Optional[List[str]] = Field(default_factory=list)`.`
*   `- [x] MODEL: Define `UserCreate(UserBase)` in `user_models.py` for user registration/initial onboarding, ensuring `telegram_id` is mandatory, and `name` might be derived from Telegram user info.`
*   `- [x] MODEL: Define `UserProfileUpdate(UserBase)` in `user_models.py` for profile editing; all fields should be optional to allow partial updates. Exclude `telegram_id` as it's not updatable.`
*   `- [x] MODEL: Define `UserInDBBase(UserBase)` in `user_models.py` to include database-only fields: `id: int` (or `telegram_id` as primary key if directly used), `social_points: int`, `free_requests_remaining: int`, `subscription_tier: Optional[str] = None`, `subscription_expires_at: Optional[datetime] = None`, `last_active_at: Optional[datetime] = None`, `is_active_in_search: bool`, `created_at: datetime`, `updated_at: Optional[datetime] = None`. Add `Config` class with `orm_mode = True`.`
*   `- [x] MODEL: Define `UserResponse(UserInDBBase)` in `user_models.py` for API responses, inheriting from `UserInDBBase`. This model will be used to return user data from the API.`
*   `- [x] MODEL: Create `app/models/common_models.py` file (if not existing).`
*   `- [x] MODEL: Define `SubscriptionTierEnum(str, Enum)` in `common_models.py` with potential initial values (e.g., `TIER_500 = "tier_500"`, `TIER_1000 = "tier_1000"`) or leave empty for now, as `subscription_tier` in `UserInDBBase` is `Optional[str]`.`
*   `- [x] MODEL: Import `datetime`, `Optional`, `List` from `typing`, `Enum` from `enum`, and `BaseModel`, `Field` from `pydantic` where needed.`

**Files Involved:**
*   `app/models/user_models.py`
*   `app/models/common_models.py`
*   `app/models/__init__.py` (if used for easier imports)

**External Dependencies:**
*   `pydantic` (already listed as a core dependency)
*   Standard Python `typing` module (`Optional`, `List`)
*   Standard Python `datetime` module
*   Standard Python `enum` module

**Notes:**
*   The `UserInDBBase` model is useful for ORM integration (e.g., with Supabase responses if they are mapped to Pydantic models). `orm_mode = True` (or `from_attributes = True` in Pydantic V2) allows Pydantic to read data from ORM objects.
*   Field optionality (`Optional[...]`) and default values (`Field(default_factory=list)`) are crucial for flexibility, especially in update models.
*   `telegram_id` is the primary identifier coming from Telegram and will likely serve as the primary key or a unique indexed field in the `users` table.
*   The `SubscriptionTierEnum` is defined but noted as optional for now in the user model itself, aligning with the PRD's flexible subscription structure.
*   `profile_embedding` is not included in these user-facing models for now, as it's an internal field for matching. It could be added to `UserInDBBase` if needed for internal processing but generally not exposed in `UserResponse` unless specifically required. The task list assumes it's not directly part of these base user interaction models.

---