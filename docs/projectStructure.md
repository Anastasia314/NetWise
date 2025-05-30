## Project Structure: NetWise Telegram Bot MVP

```
netwise/
├── .env.example                  # Example environment variables
├── .gitignore                    # Files to ignore in git
├── README.md                     # Project overview, setup, and usage
├── requirements.txt              # Python dependencies
├── main.py                       # Main application entry point
│
├── netwise_bot/                  # Main bot application package
│   ├── __init__.py
│   ├── config.py                 # Handles configuration and environment variables
│   ├── bot_instance.py           # Initializes and exports bot and dispatcher instances
│   │
│   ├── handlers/                 # Telegram update handlers
│   │   ├── __init__.py
│   │   ├── common.py             # Common handlers (start, help, cancel)
│   │   ├── profile.py            # Handlers for profile creation and management
│   │   ├── connections.py        # Handlers for inviting friends, managing connections
│   │   ├── requests.py           # Handlers for creating and managing requests
│   │   └── interactions.py       # Handlers for responding to requests, daily digests
│   │
│   ├── services/                 # Business logic and interactions with external services
│   │   ├── __init__.py
│   │   ├── user_service.py       # Logic for user profiles, social points, subscriptions
│   │   ├── graph_service.py      # Logic for connection graph, trust scores
│   │   ├── request_service.py    # Logic for request creation, lifecycle
│   │   ├── matching_service.py   # AI matching logic (keywords, embeddings)
│   │   ├── notification_service.py # Logic for daily digests, reminders
│   │   ├── supabase_client.py    # Wrapper for all Supabase interactions
│   │   ├── openai_client.py      # Wrapper for OpenAI API interactions
│   │   └── payment_service.py    # Logic for payment processing (Stripe, etc.)
│   │
│   ├── keyboards/                # UI elements: Inline and Reply keyboards
│   │   ├── __init__.py
│   │   ├── common_keyboards.py
│   │   ├── profile_keyboards.py
│   │   └── request_keyboards.py
│   │
│   ├── states/                   # FSM states for conversation flows
│   │   ├── __init__.py
│   │   ├── profile_states.py
│   │   └── request_states.py
│   │
│   ├── utils/                    # Utility functions and constants
│   │   ├── __init__.py
│   │   ├── helpers.py            # General helper functions
│   │   └── constants.py          # Application-wide constants (e.g., social points values)
│   │
│   └── scheduler.py              # APScheduler setup for background tasks
│
└── tests/                        # Unit and integration tests
    ├── __init__.py
    ├── conftest.py               # Pytest fixtures
    ├── handlers/
    │   └── test_common_handlers.py
    │   └── ... (other handler tests)
    └── services/
        └── test_user_service.py
        └── ... (other service tests)
```