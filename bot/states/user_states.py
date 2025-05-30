from aiogram.fsm.state import StatesGroup, State

class ProfileSetup(StatesGroup):
    """
    States for the user profile setup process.
    This group of states manages the conversation flow for collecting user profile information.
    """
    
    # Basic Information
    ASK_NAME = State()  # Ask for user's full name
    ASK_ROLE = State()  # Ask for user's professional role/title
    ASK_INDUSTRY = State()  # Ask for user's industry
    
    # Professional Details
    ASK_SKILLS = State()  # Ask for user's professional skills
    ASK_GOALS = State()  # Ask for user's professional goals
    
    # Personal Information
    ASK_INTERESTS = State()  # Ask for user's professional interests
    
    # Confirmation
    CONFIRMATION = State()  # Show summary and ask for confirmation before saving 