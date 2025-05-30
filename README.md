# NetWise Telegram Bot

An intelligent networking assistant that helps users solve professional queries through warm connections in their network.

## Features

- User profile creation and management
- Friend invitation system and personal connection graph
- Request formulation and AI-powered matching
- Daily request digests
- Activity history and social points system
- Trust scoring mechanism
- User activity monitoring

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your credentials:
   - Telegram Bot Token
   - Supabase URL and Key
5. Run the bot:
   ```bash
   python main.py
   ```

## Development

- Python 3.8+
- aiogram for Telegram Bot API
- Supabase for database
- APScheduler for scheduled tasks

## License

MIT License