class NebulaClientException(Exception):
    """Base exception for Nebula client errors."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class NebulaException(Exception):
    """Base exception for Nebula API errors."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message) 