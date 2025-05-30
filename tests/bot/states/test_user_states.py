import pytest
from bot.states.user_states import ProfileSetup

def test_profile_setup_states_import():
    """Test that ProfileSetup states can be imported and accessed."""
    # Test that the class exists
    assert ProfileSetup is not None
    
    # Test that all expected states exist
    assert hasattr(ProfileSetup, 'ASK_NAME')
    assert hasattr(ProfileSetup, 'ASK_ROLE')
    assert hasattr(ProfileSetup, 'ASK_INDUSTRY')
    assert hasattr(ProfileSetup, 'ASK_SKILLS')
    assert hasattr(ProfileSetup, 'ASK_GOALS')
    assert hasattr(ProfileSetup, 'ASK_INTERESTS')
    assert hasattr(ProfileSetup, 'CONFIRMATION')
    
    # Test that states are instances of State
    assert isinstance(ProfileSetup.ASK_NAME, type(ProfileSetup.ASK_NAME))
    assert isinstance(ProfileSetup.ASK_ROLE, type(ProfileSetup.ASK_ROLE))
    assert isinstance(ProfileSetup.ASK_INDUSTRY, type(ProfileSetup.ASK_INDUSTRY))
    assert isinstance(ProfileSetup.ASK_SKILLS, type(ProfileSetup.ASK_SKILLS))
    assert isinstance(ProfileSetup.ASK_GOALS, type(ProfileSetup.ASK_GOALS))
    assert isinstance(ProfileSetup.ASK_INTERESTS, type(ProfileSetup.ASK_INTERESTS))
    assert isinstance(ProfileSetup.CONFIRMATION, type(ProfileSetup.CONFIRMATION)) 