from typing import Dict, List, Optional

def format_user_profile_message(profile_data: Dict) -> str:
    """
    Format user profile data into a human-readable message string.
    
    Args:
        profile_data: Dictionary containing user profile data with fields like:
            - name: str
            - role: str
            - industry: str
            - skills: List[str]
            - goals: List[str]
            - interests: List[str]
            - social_points: int
            
    Returns:
        str: Formatted message string using MarkdownV2 formatting
    """
    # Helper function to format list items
    def format_list(items: Optional[List[str]]) -> str:
        if not items:
            return "Not set"
        return "\n".join(f"• {item}" for item in items)
    
    # Helper function to format a field
    def format_field(label: str, value: Optional[str], emoji: str = "") -> str:
        if not value:
            return f"{emoji} *{label}:* Not set"
        return f"{emoji} *{label}:* {value}"
    
    # Basic Information
    basic_info = [
        format_field("Profile", profile_data.get("name"), "👤"),
        format_field("Role", profile_data.get("role"), "💼"),
        format_field("Industry", profile_data.get("industry"), "🏢")
    ]
    
    # Goals Section
    goals = format_list(profile_data.get("goals"))
    goals_section = ["\n🎯 *Goals:*", goals]
    
    # Skills Section
    skills = format_list(profile_data.get("skills"))
    skills_section = ["\n🛠️ *Skills:*", skills]
    
    # Interests Section
    interests = format_list(profile_data.get("interests"))
    interests_section = ["\n💡 *Interests:*", interests]
    
    # Social Points
    points = profile_data.get("social_points", 0)
    points_section = [f"\n🏆 *Social Points:* {points}"]
    
    # Combine all sections
    sections = [
        *basic_info,
        *goals_section,
        *skills_section,
        *interests_section,
        *points_section
    ]
    
    return "\n".join(sections) 