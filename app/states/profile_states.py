from aiogram.fsm.state import State, StatesGroup

class ProfileState(StatesGroup):
    """Profile creation states"""
    
    # Basic information
    waiting_for_first_name = State()  # Waiting for user's first name
    waiting_for_last_name = State()  # Waiting for user's last name
    waiting_for_company = State()  # Waiting for company name
    waiting_for_title = State()  # Waiting for job title
    waiting_for_industry = State()  # Waiting for industry selection
    waiting_for_own_tags = State()  # Waiting for user's own tags selection
    
    # Confirmation
    waiting_for_confirmation = State()  # Waiting for user to confirm profile data
    
    # Edit mode
    waiting_for_edit_field = State()  # Waiting for user to choose which field to edit
    editing_mode = State()  # New state for editing mode 