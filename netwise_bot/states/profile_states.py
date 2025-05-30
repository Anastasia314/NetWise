from aiogram.fsm.state import StatesGroup, State

class ProfileStates(StatesGroup):
    """States for the profile creation flow."""
    name = State()
    role = State()
    industry = State()
    skills = State()
    goals = State()
    interests = State() 