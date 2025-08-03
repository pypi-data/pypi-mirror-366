"""Main HotPayments client class"""

from typing import Optional

from .services.customers import CustomersService
from .services.transactions import TransactionsService
from .services.subscriptions import SubscriptionsService
from .services.subscription_plans import SubscriptionPlansService


class Hotpayments:
    """Main HotPayments client"""
    
    _api_key: Optional[str] = None
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://rgpay.test/api",
        timeout: float = 30.0,
        version: str = "1.0.0"
    ) -> None:
        """
        Initialize HotPayments client
        
        Args:
            api_key: Your HotPayments API key
            base_url: API base URL (default: https://rgpay.test/api)
            timeout: Request timeout in seconds (default: 30.0)
            version: SDK version
        """
        self.api_key = api_key or self._api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.version = version
        
        if not self.api_key:
            raise ValueError("API key is required. Set it via Hotpayments.auth() or pass it to the constructor.")
        
        # Initialize services
        self._customers_service = CustomersService(self)
        self._transactions_service = TransactionsService(self)
        self._subscriptions_service = SubscriptionsService(self)
        self._subscription_plans_service = SubscriptionPlansService(self)
    
    @classmethod
    def auth(cls, api_key: str) -> None:
        """
        Set the global API key for all instances
        
        Args:
            api_key: Your HotPayments API key
        """
        cls._api_key = api_key
    
    def customers(self) -> CustomersService:
        """Get customers service"""
        return self._customers_service
    
    def transactions(self) -> TransactionsService:
        """Get transactions service"""
        return self._transactions_service
    
    def subscriptions(self) -> SubscriptionsService:
        """Get subscriptions service"""
        return self._subscriptions_service
    
    def subscription_plans(self) -> SubscriptionPlansService:
        """Get subscription plans service"""
        return self._subscription_plans_service