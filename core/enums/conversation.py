from enum import Enum

class ConversationState(Enum):
    """Possible conversation states."""
    ACTIVE = "active"
    ENDED = "ended"
    ERROR = "error"