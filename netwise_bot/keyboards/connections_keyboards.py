from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_connection_type_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for selecting connection type."""
    keyboard = [
        [
            InlineKeyboardButton(
                text="Worked together",
                callback_data="conn_type_worked_together"
            )
        ],
        [
            InlineKeyboardButton(
                text="Introduction made",
                callback_data="conn_type_intro_made"
            )
        ],
        [
            InlineKeyboardButton(
                text="Met at event",
                callback_data="conn_type_met_at_event"
            )
        ],
        [
            InlineKeyboardButton(
                text="Other",
                callback_data="conn_type_other"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_trust_score_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for selecting trust level."""
    keyboard = [
        [
            InlineKeyboardButton(
                text="1 - New acquaintance",
                callback_data="trust_score_1"
            )
        ],
        [
            InlineKeyboardButton(
                text="2 - Known well",
                callback_data="trust_score_2"
            )
        ],
        [
            InlineKeyboardButton(
                text="3 - Close connection",
                callback_data="trust_score_3"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_connection_list_keyboard(
    page: int,
    total_pages: int,
    current_filter: str = None,
    current_sort: str = None
) -> InlineKeyboardMarkup:
    """Create keyboard for connection list actions."""
    keyboard = []
    
    # Filter buttons
    filter_row = []
    filters = [
        ("All", "filter_all"),
        ("Trust 3", "filter_trust_3"),
        ("Trust 2", "filter_trust_2"),
        ("Trust 1", "filter_trust_1")
    ]
    for label, data in filters:
        filter_row.append(
            InlineKeyboardButton(
                text=f"✓ {label}" if current_filter == data else label,
                callback_data=data
            )
        )
    keyboard.append(filter_row)
    
    # Sort buttons
    sort_row = []
    sorts = [
        ("Name", "sort_name"),
        ("Trust", "sort_trust"),
        ("Date", "sort_date")
    ]
    for label, data in sorts:
        sort_row.append(
            InlineKeyboardButton(
                text=f"✓ {label}" if current_sort == data else label,
                callback_data=data
            )
        )
    keyboard.append(sort_row)
    
    # Pagination buttons
    pagination_row = []
    if page > 1:
        pagination_row.append(
            InlineKeyboardButton(
                text="⬅️ Previous",
                callback_data=f"page_{page-1}"
            )
        )
    if page < total_pages:
        pagination_row.append(
            InlineKeyboardButton(
                text="Next ➡️",
                callback_data=f"page_{page+1}"
            )
        )
    if pagination_row:
        keyboard.append(pagination_row)
        
    # Action buttons
    action_row = [
        InlineKeyboardButton(
            text="🔄 Refresh",
            callback_data="refresh_connections"
        ),
        InlineKeyboardButton(
            text="📊 Stats",
            callback_data="connection_stats"
        )
    ]
    keyboard.append(action_row)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_connection_stats_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for connection statistics."""
    keyboard = [
        [
            InlineKeyboardButton(
                text="⬅️ Back to List",
                callback_data="back_to_connections"
            )
        ],
        [
            InlineKeyboardButton(
                text="📈 Export Stats",
                callback_data="export_stats"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 