from aiogram.fsm.state import State, StatesGroup

class RequestStates(StatesGroup):
    """States for the request creation flow."""
    description = State()  # State for collecting request description
    waiting_for_description = State()  # State for waiting for request description 