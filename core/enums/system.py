from enum import Enum

class SystemState(str, Enum):
    """
    Possible states of the Atena system.
    
    States:
        ACTIVE: System is operational and ready to process messages
        ERROR: System encountered an error and needs to be restarted
        ENDED: System has finished its execution normally
    """
    ACTIVE = "active"
    ERROR = "error"
    ENDED = "ended"
    NOT_STARTED = "not_started"