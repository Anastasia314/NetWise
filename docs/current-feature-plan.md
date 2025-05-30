# **Current Feature Plan: Bot Profile Message Formatter**

**Feature Description:**
This feature involves creating a utility function to format user profile data into a human-readable string suitable for sending as a message in Telegram. This ensures a consistent and clean presentation of user profiles within the bot. The function will take a dictionary of profile data (as returned by the API client) and output a formatted string, potentially using Markdown for better aesthetics.

**Tasks:**

- [x] **FEAT: Create `bot/utils` directory and `formatters.py` file**
    *   Create the directory `bot/utils/` if it doesn't already exist.
    *   Add an `__init__.py` file to `bot/utils/` to mark it as a package.
    *   Create a new Python file `bot/utils/formatters.py`.

- [x] **FEAT: Implement `format_user_profile_message(profile_data: dict) -> str` function**
    *   Define the function `format_user_profile_message(profile_data: dict) -> str` in `bot/utils/formatters.py`.
    *   The `profile_data` dictionary is expected to match the structure of `UserResponse` from the backend API (containing fields like `name`, `role`, `industry`, `skills`, `goals`, `interests`, `social_points`, etc.).
    *   Construct a multi-line string. Use f-strings or `str.join()` for readability.
    *   Consider using Telegram's MarkdownV2 or HTML formatting for emphasis (e.g., bold labels, bullet points for lists like skills/goals/interests).
        *   Example structure:
            ```
            👤 *Profile:* {name}
            *Role:* {role}
            *Industry:* {industry}

            🎯 *Goals:*
            - Goal 1
            - Goal 2

            🛠️ *Skills:*
            - Skill 1
            - Skill 2

            💡 *Interests:*
            - Interest 1
            - Interest 2

            🏆 *Social Points:* {social_points}
            ```
    *   Handle missing or `None` fields gracefully (e.g., by omitting the line or showing "Not set").
    *   Ensure arrays/lists (like `skills`, `goals`, `interests`) are formatted nicely (e.g., comma-separated, bullet points).
    *   Return the formatted string.
    *   Add a docstring explaining the function's purpose, input, and output.

- [x] **TEST: Add unit tests for `format_user_profile_message`**
    *   Create `tests/bot/utils/test_formatters.py`.
    *   Write tests to verify:
        *   Correct formatting with all profile fields present.
        *   Correct handling of missing or `None` fields (e.g., a field is omitted or shows a placeholder like "N/A").
        *   Correct formatting of list-based fields (skills, goals, interests) – e.g., as comma-separated lists or bullet points.
        *   If using Markdown/HTML, ensure the special characters are correctly escaped or used.
        *   Test with an empty `profile_data` dictionary (should return a sensible default or empty string).
        *   Test with various combinations of filled and empty fields.

**Files Involved:**
*   `bot/utils/__init__.py` (New or existing)
*   `bot/utils/formatters.py` (New file)
*   `tests/bot/utils/test_formatters.py` (New file)

**External Dependencies:**
*   No new external dependencies specifically for this task, but it relies on standard Python string manipulation.
*   If using complex Markdown/HTML generation, a templating engine like Jinja2 could be considered in the future, but for now, direct string formatting is sufficient.

**Notes:**
*   This formatter function will be used by bot handlers (e.g., `/profile` command handler) to display user information.
*   Pay attention to Telegram's message length limits if profiles can be very verbose. The formatter might need to truncate long lists or provide a summary if data is extensive. For MVP, assume data fits.
*   The visual style (emojis, bolding) should be consistent with the overall bot's personality.
*   The fields included should match those defined in `UserResponse` from the backend and deemed relevant for display in the bot.
```