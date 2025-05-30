import pytest
from bot.utils.formatters import format_user_profile_message

def test_format_user_profile_message_complete():
    """Test formatting with all profile fields present."""
    profile_data = {
        "name": "John Doe",
        "role": "Software Engineer",
        "industry": "Technology",
        "skills": ["Python", "JavaScript", "Docker"],
        "goals": ["Learn Rust", "Contribute to Open Source"],
        "interests": ["AI", "Web Development"],
        "social_points": 100
    }
    
    result = format_user_profile_message(profile_data)
    
    # Check basic info
    assert "👤 *Profile:* John Doe" in result
    assert "💼 *Role:* Software Engineer" in result
    assert "🏢 *Industry:* Technology" in result
    
    # Check lists
    assert "🎯 *Goals:*" in result
    assert "• Learn Rust" in result
    assert "• Contribute to Open Source" in result
    
    assert "🛠️ *Skills:*" in result
    assert "• Python" in result
    assert "• JavaScript" in result
    assert "• Docker" in result
    
    assert "💡 *Interests:*" in result
    assert "• AI" in result
    assert "• Web Development" in result
    
    # Check points
    assert "🏆 *Social Points:* 100" in result

def test_format_user_profile_message_empty():
    """Test formatting with empty profile data."""
    profile_data = {}
    
    result = format_user_profile_message(profile_data)
    
    # Check that all fields show "Not set"
    assert "👤 *Profile:* Not set" in result
    assert "💼 *Role:* Not set" in result
    assert "🏢 *Industry:* Not set" in result
    assert "🎯 *Goals:*" in result
    assert "Not set" in result
    assert "🛠️ *Skills:*" in result
    assert "💡 *Interests:*" in result
    assert "🏆 *Social Points:* 0" in result

def test_format_user_profile_message_partial():
    """Test formatting with some fields missing or None."""
    profile_data = {
        "name": "Jane Smith",
        "role": None,
        "industry": "Finance",
        "skills": [],
        "goals": ["Career Growth"],
        "interests": None,
        "social_points": 50
    }
    
    result = format_user_profile_message(profile_data)
    
    # Check present fields
    assert "👤 *Profile:* Jane Smith" in result
    assert "🏢 *Industry:* Finance" in result
    assert "• Career Growth" in result
    assert "🏆 *Social Points:* 50" in result
    
    # Check missing/None fields
    assert "💼 *Role:* Not set" in result
    assert "🛠️ *Skills:*" in result
    assert "Not set" in result
    assert "💡 *Interests:*" in result
    assert "Not set" in result 