"""Subscription plans service for HotPayments API"""

from typing import Dict, Optional, List

from ..base_service import BaseService
from ..types import SubscriptionPlan, PaginatedResponse


class SubscriptionPlansService(BaseService):
    """Service for managing subscription plans"""
    
    async def list(
        self, 
        page: int = 1,
        per_page: int = 15,
        currency: Optional[str] = None
    ) -> PaginatedResponse:
        """
        List subscription plans with pagination
        
        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 15, max: 50)
            currency: Currency code to filter plans (e.g., "BRL")
            
        Returns:
            PaginatedResponse: Paginated subscription plans data
            
        Raises:
            HotpaymentsException: For API errors
        """
        params = {
            "page": page,
            "perPage": per_page  # API uses perPage instead of per_page
        }
        if currency:
            params["currency"] = currency
            
        response = await self._get("/v1/subscriptions/plans", params)
        
        # Parse plans data
        plans_data = []
        if "data" in response and isinstance(response["data"], list):
            plans_data = [SubscriptionPlan.model_validate(item) for item in response["data"]]
        elif "data" in response and "data" in response["data"]:
            plans_data = [SubscriptionPlan.model_validate(item) for item in response["data"]["data"]]
        
        # Create paginated response
        paginated_data = response.get("data", response)
        paginated_data["data"] = plans_data
        
        return PaginatedResponse.model_validate(paginated_data)
    
    def list_sync(
        self, 
        page: int = 1,
        per_page: int = 15,
        currency: Optional[str] = None
    ) -> PaginatedResponse:
        """
        List subscription plans with pagination (synchronous)
        
        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 15, max: 50)
            currency: Currency code to filter plans (e.g., "BRL")
            
        Returns:
            PaginatedResponse: Paginated subscription plans data
        """
        params = {
            "page": page,
            "perPage": per_page  # API uses perPage instead of per_page
        }
        if currency:
            params["currency"] = currency
            
        response = self._get_sync("/v1/subscriptions/plans", params)
        
        # Parse plans data
        plans_data = []
        if "data" in response and isinstance(response["data"], list):
            plans_data = [SubscriptionPlan.model_validate(item) for item in response["data"]]
        elif "data" in response and "data" in response["data"]:
            plans_data = [SubscriptionPlan.model_validate(item) for item in response["data"]["data"]]
        
        # Create paginated response
        paginated_data = response.get("data", response)
        paginated_data["data"] = plans_data
        
        return PaginatedResponse.model_validate(paginated_data)
    
    async def all(self, currency: Optional[str] = None) -> List[SubscriptionPlan]:
        """
        Get all subscription plans (alias for list with default parameters)
        
        Args:
            currency: Currency code to filter plans (e.g., "BRL")
            
        Returns:
            List[SubscriptionPlan]: List of all subscription plans
        """
        response = await self.list(currency=currency)
        return response.data
    
    def all_sync(self, currency: Optional[str] = None) -> List[SubscriptionPlan]:
        """
        Get all subscription plans (synchronous, alias for list_sync)
        
        Args:
            currency: Currency code to filter plans (e.g., "BRL")
            
        Returns:
            List[SubscriptionPlan]: List of all subscription plans
        """
        response = self.list_sync(currency=currency)
        return response.data