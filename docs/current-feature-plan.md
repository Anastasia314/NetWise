
## `current-feature-plan.md`

**Title:** API Documentation: User Endpoints (OpenAPI)

**Feature Description:**
This feature focuses on adding comprehensive OpenAPI documentation to the User API endpoints implemented in `app/api/users.py`. By leveraging FastAPI's automatic documentation generation capabilities through Pydantic models and Python docstrings, we will ensure that all user-related endpoints (`/onboard`, `/profile`) are clearly described, including their purpose, request parameters, request bodies, and possible responses. This documentation is crucial for developers interacting with the API, including the team building the Telegram bot.

**Tasks:**
*   `- [ ] DOC: Add detailed docstrings to the `POST /users/onboard` endpoint function in `app/api/users.py`. Include a summary, description, and details about the request body (referencing the Pydantic model) and expected responses (e.g., 200, 201, 422).`
*   `- [ ] DOC: Add `tags=["Users"]` parameter to the `APIRouter` decorator for the `POST /users/onboard` endpoint to group it in the OpenAPI documentation.`
*   `- [ ] DOC: Add `response_model=UserResponse` to the decorator for `POST /users/onboard` to specify the successful response schema. Define `responses` for different status codes (e.g., 201 for created, 200 for existing).`
*   `- [ ] DOC: Add detailed docstrings to the `GET /users/{path_telegram_id}/profile` endpoint function in `app/api/users.py`. Include summary, description, path parameter details, header parameter (`X-Telegram-Id`) details, and expected responses (e.g., 200, 404, 403).`
*   `- [ ] DOC: Add `tags=["Users"]` parameter to the `APIRouter` decorator for the `GET /users/{path_telegram_id}/profile` endpoint.`
*   `- [ ] DOC: Add `response_model=UserResponse` to the decorator for `GET /users/{path_telegram_id}/profile`. Define `responses` for different status codes (e.g., 404, 403).`
*   `- [ ] DOC: Add detailed docstrings to the `PUT /users/{path_telegram_id}/profile` endpoint function in `app/api/users.py`. Include summary, description, path parameter details, header parameter (`X-Telegram-Id`) details, request body (referencing `UserProfileUpdate`), and expected responses (e.g., 200, 404, 403, 422).`
*   `- [ ] DOC: Add `tags=["Users"]` parameter to the `APIRouter` decorator for the `PUT /users/{path_telegram_id}/profile` endpoint.`
*   `- [ ] DOC: Add `response_model=UserResponse` to the decorator for `PUT /users/{path_telegram_id}/profile`. Define `responses` for different status codes (e.g., 404, 403).`
*   `- [ ] DOC: Review Pydantic models (`UserCreate`, `UserProfileUpdate`, `UserResponse`, and any request-specific models for onboarding) in `app/models/user_models.py` to ensure field descriptions (`Field(description="...")`) are present for clarity in the OpenAPI schema.`
*   `- [ ] DOC: Verify that the main FastAPI application instance in `app/main.py` has appropriate `title`, `description`, and `version` parameters set for the overall OpenAPI documentation.`
*   `- [ ] DOC: Run the FastAPI application locally and access the auto-generated OpenAPI documentation (usually at `/docs` and `/redoc`) to verify correctness and completeness of the User endpoints documentation.`

**Files Involved:**
*   `app/api/users.py` (primary file for adding docstrings and decorator parameters)
*   `app/models/user_models.py` (for adding descriptions to Pydantic model fields)
*   `app/main.py` (for setting global OpenAPI metadata)

**External Dependencies:**
*   `fastapi` (provides the OpenAPI generation capabilities)
*   `pydantic` (models are used to generate schemas)

**Notes:**
*   FastAPI uses the function docstring as the description for the endpoint. The first line is the summary.
*   Pydantic model field descriptions (e.g., `Field(..., description="User's primary role")`) will appear in the schema definitions.
*   The `tags` parameter in endpoint decorators helps organize endpoints in the UI.
*   The `responses` parameter in endpoint decorators allows specifying schemas and descriptions for different HTTP status codes, enhancing documentation clarity. Example:
    ```python
    @router.get(
        "/{item_id}",
        response_model=Item,
        responses={
            404: {"description": "Item not found"},
            200: {
                "description": "The item requested by Id",
                "content": {
                    "application/json": {
                        "example": {"id": "foo", "title": "Foo", "description": "A very nice Item"}
                    }
                },
            },
        },
    )
    ```
*   Thoroughly reviewing the generated `/docs` page is key to ensure the documentation is accurate and user-friendly.

---

This concludes Phase 1. The next phase will be **Phase 2: Telegram Bot - User Onboarding & Profile Management**.