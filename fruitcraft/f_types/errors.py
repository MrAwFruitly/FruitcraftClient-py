


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
    message: str = ""
    
    """_summary_
        Initializes the exception.
    """
    def __init__(self, message, server_response=None):
        self.message = message
        self.server_response = server_response
        super().__init__(self.message)

class FruitServerException(Exception):
    
    server_response = None
    req_path: str = None
    error_code: int = 0
    message: str = ""
    def __init__(self, req_path: str, error_code: int, message: str, response: str = None) -> None:
        self.req_path = req_path
        self.error_code = error_code
        self.message = message
        self.server_response = response
    
    
    def __str__(self) -> str:
        return f"({self.error_code}): {self.message}"
    
    def __repr__(self) -> str:
        return f"({self.error_code}): {self.message}"
