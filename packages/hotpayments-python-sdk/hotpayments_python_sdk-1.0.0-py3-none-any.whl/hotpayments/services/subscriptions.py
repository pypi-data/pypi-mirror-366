"""Subscriptions service for HotPayments API"""

from typing import Dict, Any, Union

from ..base_service import BaseService
from ..types import Subscription, CreateSubscriptionRequest, CancelSubscriptionRequest, SuspendSubscriptionRequest


class SubscriptionsService(BaseService):
    """Service for managing subscriptions"""
    
    async def create(self, subscription_data: Union[CreateSubscriptionRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a new subscription
        
        Args:
            subscription_data: Subscription data (CreateSubscriptionRequest model or dict)
            
        Returns:
            Dict[str, Any]: Created subscription and transaction data
            
        Raises:
            HotpaymentsException: For API errors
        """
        if isinstance(subscription_data, dict):
            subscription_data = CreateSubscriptionRequest.model_validate(subscription_data)
        
        data = self._validate_and_serialize(subscription_data)
        response = await self._post("/v1/subscriptions/subscribe", data)
        return response.get("data", {})
    
    def create_sync(self, subscription_data: Union[CreateSubscriptionRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a new subscription (synchronous)
        
        Args:
            subscription_data: Subscription data (CreateSubscriptionRequest model or dict)
            
        Returns:
            Dict[str, Any]: Created subscription and transaction data
        """
        if isinstance(subscription_data, dict):
            subscription_data = CreateSubscriptionRequest.model_validate(subscription_data)
        
        data = self._validate_and_serialize(subscription_data)
        response = self._post_sync("/v1/subscriptions/subscribe", data)
        return response.get("data", {})
    
    async def show(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get subscription details
        
        Args:
            subscription_id: Subscription ID to retrieve
            
        Returns:
            Dict[str, Any]: Subscription details including plan and transactions
            
        Raises:
            HotpaymentsException: For API errors
        """
        response = await self._get(f"/v1/subscriptions/{subscription_id}")
        return response.get("data", {})
    
    def show_sync(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get subscription details (synchronous)
        
        Args:
            subscription_id: Subscription ID to retrieve
            
        Returns:
            Dict[str, Any]: Subscription details including plan and transactions
        """
        response = self._get_sync(f"/v1/subscriptions/{subscription_id}")
        return response.get("data", {})
    
    async def cancel(
        self, 
        subscription_id: str, 
        cancel_data: Union[CancelSubscriptionRequest, Dict[str, Any], None] = None
    ) -> Subscription:
        """
        Cancel a subscription
        
        Args:
            subscription_id: Subscription ID to cancel
            cancel_data: Cancellation data (CancelSubscriptionRequest model or dict)
            
        Returns:
            Subscription: Updated subscription data
            
        Raises:
            HotpaymentsException: For API errors
        """
        if cancel_data is None:
            cancel_data = CancelSubscriptionRequest()
        elif isinstance(cancel_data, dict):
            cancel_data = CancelSubscriptionRequest.model_validate(cancel_data)
        
        data = self._validate_and_serialize(cancel_data)
        response = await self._post(f"/v1/subscriptions/{subscription_id}/cancel", data)
        
        subscription_data = response.get("data", {}).get("subscription", {})
        return Subscription.model_validate(subscription_data)
    
    def cancel_sync(
        self, 
        subscription_id: str, 
        cancel_data: Union[CancelSubscriptionRequest, Dict[str, Any], None] = None
    ) -> Subscription:
        """
        Cancel a subscription (synchronous)
        
        Args:
            subscription_id: Subscription ID to cancel
            cancel_data: Cancellation data (CancelSubscriptionRequest model or dict)
            
        Returns:
            Subscription: Updated subscription data
        """
        if cancel_data is None:
            cancel_data = CancelSubscriptionRequest()
        elif isinstance(cancel_data, dict):
            cancel_data = CancelSubscriptionRequest.model_validate(cancel_data)
        
        data = self._validate_and_serialize(cancel_data)
        response = self._post_sync(f"/v1/subscriptions/{subscription_id}/cancel", data)
        
        subscription_data = response.get("data", {}).get("subscription", {})
        return Subscription.model_validate(subscription_data)
    
    async def suspend(
        self, 
        subscription_id: str, 
        suspend_data: Union[SuspendSubscriptionRequest, Dict[str, Any], None] = None
    ) -> Subscription:
        """
        Suspend a subscription
        
        Args:
            subscription_id: Subscription ID to suspend
            suspend_data: Suspension data (SuspendSubscriptionRequest model or dict)
            
        Returns:
            Subscription: Updated subscription data
            
        Raises:
            HotpaymentsException: For API errors
        """
        if suspend_data is None:
            suspend_data = SuspendSubscriptionRequest()
        elif isinstance(suspend_data, dict):
            suspend_data = SuspendSubscriptionRequest.model_validate(suspend_data)
        
        data = self._validate_and_serialize(suspend_data)
        response = await self._post(f"/v1/subscriptions/{subscription_id}/suspend", data)
        
        subscription_data = response.get("data", {}).get("subscription", {})
        return Subscription.model_validate(subscription_data)
    
    def suspend_sync(
        self, 
        subscription_id: str, 
        suspend_data: Union[SuspendSubscriptionRequest, Dict[str, Any], None] = None
    ) -> Subscription:
        """
        Suspend a subscription (synchronous)
        
        Args:
            subscription_id: Subscription ID to suspend
            suspend_data: Suspension data (SuspendSubscriptionRequest model or dict)
            
        Returns:
            Subscription: Updated subscription data
        """
        if suspend_data is None:
            suspend_data = SuspendSubscriptionRequest()
        elif isinstance(suspend_data, dict):
            suspend_data = SuspendSubscriptionRequest.model_validate(suspend_data)
        
        data = self._validate_and_serialize(suspend_data)
        response = self._post_sync(f"/v1/subscriptions/{subscription_id}/suspend", data)
        
        subscription_data = response.get("data", {}).get("subscription", {})
        return Subscription.model_validate(subscription_data)
    
    async def reactivate(self, subscription_id: str) -> Subscription:
        """
        Reactivate a suspended subscription
        
        Args:
            subscription_id: Subscription ID to reactivate
            
        Returns:
            Subscription: Updated subscription data
            
        Raises:
            HotpaymentsException: For API errors
        """
        response = await self._post(f"/v1/subscriptions/{subscription_id}/reactivate", {})
        
        subscription_data = response.get("data", {}).get("subscription", {})
        return Subscription.model_validate(subscription_data)
    
    def reactivate_sync(self, subscription_id: str) -> Subscription:
        """
        Reactivate a suspended subscription (synchronous)
        
        Args:
            subscription_id: Subscription ID to reactivate
            
        Returns:
            Subscription: Updated subscription data
        """
        response = self._post_sync(f"/v1/subscriptions/{subscription_id}/reactivate", {})
        
        subscription_data = response.get("data", {}).get("subscription", {})
        return Subscription.model_validate(subscription_data)