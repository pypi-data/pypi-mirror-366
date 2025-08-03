"""Customers service for HotPayments API"""

from typing import Dict, List, Optional, Any, Union

from ..base_service import BaseService
from ..types import Customer, CreateCustomerRequest, PaginatedResponse


class CustomersService(BaseService):
    """Service for managing customers"""
    
    async def create(self, customer_data: Union[CreateCustomerRequest, Dict[str, Any]]) -> Customer:
        """
        Create a new customer
        
        Args:
            customer_data: Customer data (CreateCustomerRequest model or dict)
            
        Returns:
            Customer: Created customer data
            
        Raises:
            HotpaymentsException: For API errors
        """
        if isinstance(customer_data, dict):
            customer_data = CreateCustomerRequest.model_validate(customer_data)
        
        data = self._validate_and_serialize(customer_data)
        response = await self._post("/v1/customers", data)
        return self._parse_response(response, Customer)
    
    def create_sync(self, customer_data: Union[CreateCustomerRequest, Dict[str, Any]]) -> Customer:
        """
        Create a new customer (synchronous)
        
        Args:
            customer_data: Customer data (CreateCustomerRequest model or dict)
            
        Returns:
            Customer: Created customer data
        """
        if isinstance(customer_data, dict):
            customer_data = CreateCustomerRequest.model_validate(customer_data)
        
        data = self._validate_and_serialize(customer_data)
        response = self._post_sync("/v1/customers", data)
        return self._parse_response(response, Customer)
    
    async def list(
        self, 
        page: int = 1,
        per_page: int = 15,
        search: Optional[str] = None
    ) -> PaginatedResponse:
        """
        List customers with pagination
        
        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 15)
            search: Search query
            
        Returns:
            PaginatedResponse: Paginated customers data
        """
        params = {
            "page": page,
            "per_page": per_page
        }
        if search:
            params["search"] = search
            
        response = await self._get("/v1/customers", params)
        
        # Parse customers data
        customers_data = []
        if "data" in response and isinstance(response["data"], list):
            customers_data = [Customer.model_validate(item) for item in response["data"]]
        elif "data" in response and "data" in response["data"]:
            customers_data = [Customer.model_validate(item) for item in response["data"]["data"]]
        
        # Create paginated response
        paginated_data = response.get("data", response)
        paginated_data["data"] = customers_data
        
        return PaginatedResponse.model_validate(paginated_data)
    
    def list_sync(
        self, 
        page: int = 1,
        per_page: int = 15,
        search: Optional[str] = None
    ) -> PaginatedResponse:
        """
        List customers with pagination (synchronous)
        
        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 15)
            search: Search query
            
        Returns:
            PaginatedResponse: Paginated customers data
        """
        params = {
            "page": page,
            "per_page": per_page
        }
        if search:
            params["search"] = search
            
        response = self._get_sync("/v1/customers", params)
        
        # Parse customers data
        customers_data = []
        if "data" in response and isinstance(response["data"], list):
            customers_data = [Customer.model_validate(item) for item in response["data"]]
        elif "data" in response and "data" in response["data"]:
            customers_data = [Customer.model_validate(item) for item in response["data"]["data"]]
        
        # Create paginated response
        paginated_data = response.get("data", response)
        paginated_data["data"] = customers_data
        
        return PaginatedResponse.model_validate(paginated_data)