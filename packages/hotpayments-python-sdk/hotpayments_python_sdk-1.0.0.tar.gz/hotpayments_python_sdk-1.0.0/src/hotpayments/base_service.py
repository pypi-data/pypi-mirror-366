"""Base service class for HotPayments API services"""

import json
from typing import Dict, Any, Optional, Type, TypeVar
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel

from .exceptions import HotpaymentsException

T = TypeVar('T', bound=BaseModel)


class BaseService:
    """Base class for all API services"""
    
    def __init__(self, client: 'Hotpayments') -> None:
        self.client = client
        self.base_url = client.base_url
        self.api_key = client.api_key
        self.timeout = client.timeout
        
    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"HotPayments-Python-SDK/{self.client.version}"
        }
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        return urljoin(self.base_url, endpoint.lstrip('/'))
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions"""
        try:
            data = response.json()
        except (ValueError, json.JSONDecodeError):
            raise HotpaymentsException(
                f"Invalid JSON response: {response.text}",
                status_code=response.status_code
            )
        
        if response.status_code >= 400:
            message = data.get('message', f'HTTP {response.status_code} error')
            raise HotpaymentsException(message, status_code=response.status_code)
        
        return data
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an async HTTP request to the API"""
        url = self._build_url(endpoint)
        headers = self._get_headers()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params
                )
                return self._handle_response(response)
            except httpx.RequestError as e:
                raise HotpaymentsException(f"Request error: {str(e)}")
    
    def _make_sync_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a synchronous HTTP request to the API"""
        url = self._build_url(endpoint)
        headers = self._get_headers()
        
        with httpx.Client(timeout=self.timeout) as client:
            try:
                response = client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params
                )
                return self._handle_response(response)
            except httpx.RequestError as e:
                raise HotpaymentsException(f"Request error: {str(e)}")
    
    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make async GET request"""
        return await self._make_request("GET", endpoint, params=params)
    
    async def _post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make async POST request"""
        return await self._make_request("POST", endpoint, data=data)
    
    def _get_sync(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make synchronous GET request"""
        return self._make_sync_request("GET", endpoint, params=params)
    
    def _post_sync(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make synchronous POST request"""
        return self._make_sync_request("POST", endpoint, data=data)
    
    def _validate_and_serialize(self, data: BaseModel) -> Dict[str, Any]:
        """Validate and serialize Pydantic model to dict"""
        return data.model_dump(exclude_none=True, by_alias=True)
    
    def _parse_response(self, response_data: Dict[str, Any], model_class: Type[T]) -> T:
        """Parse response data into Pydantic model"""
        if 'data' in response_data:
            return model_class.model_validate(response_data['data'])
        return model_class.model_validate(response_data)