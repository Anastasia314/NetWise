from aiogram.fsm.state import StatesGroup, State

class ConnectionTrustStates(StatesGroup):
    """States for collecting connection trust information."""
    connection_type = State()  # State for selecting how users know each other
    trust_score = State()     # State for selecting trust level 