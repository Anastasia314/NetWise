from aiogram.fsm.state import State, StatesGroup

class ProfileState(StatesGroup):
    """States for profile creation process"""
    
    # Basic information
    waiting_for_name = State()  # Waiting for user's full name
    waiting_for_company = State()  # Waiting for company name
    waiting_for_position = State()  # Waiting for job position
    waiting_for_industry = State()  # Waiting for industry
    
    # Tags
    waiting_for_own_tags = State()  # Waiting for user's own tags (self-description)
    waiting_for_search_tags = State()  # Waiting for search tags (what user is looking for)
    
    # Confirmation
    waiting_for_confirmation = State()  # Waiting for user to confirm profile data
    
    # Edit mode
    waiting_for_edit_field = State()  # Waiting for user to choose which field to edit 