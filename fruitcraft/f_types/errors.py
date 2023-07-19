


class UnknownError(Exception):
    """Exception raised for unknown errors."""
    
    server_response: str = None
    
    """_summary_
        Initializes the exception.
    """
    def __init__(self, message, server_response=None):
        self.message = message
        self.server_response = server_response
        super().__init__(self.message)

class PlayerLoadException(Exception):
    """Exception raised for errors while loading the player."""
    
    server_response = None
    
    """_summary_
        Initializes the exception.
    """
    def __init__(self, message, server_response=None):
        self.message = message
        self.server_response = server_response
        super().__init__(self.message)
