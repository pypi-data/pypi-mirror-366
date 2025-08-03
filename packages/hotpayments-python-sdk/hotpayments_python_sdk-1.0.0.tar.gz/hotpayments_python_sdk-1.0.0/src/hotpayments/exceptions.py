"""HotPayments SDK Exception Classes"""

from typing import Dict, Optional, Any


class HotpaymentsException(Exception):
    """Exception raised for HotPayments API errors"""
    
    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code