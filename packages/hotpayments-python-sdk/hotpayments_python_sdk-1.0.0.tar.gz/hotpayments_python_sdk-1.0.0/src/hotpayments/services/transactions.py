"""Transactions service for HotPayments API"""

from typing import Dict, Any, Union

from ..base_service import BaseService
from ..types import Transaction, CreateQrCodeRequest, CashoutRequest


class TransactionsService(BaseService):
    """Service for managing transactions"""
    
    async def create_pix_qr_code(self, qr_data: Union[CreateQrCodeRequest, Dict[str, Any]]) -> Transaction:
        """
        Create a PIX QR code transaction
        
        Args:
            qr_data: QR code data (CreateQrCodeRequest model or dict)
            
        Returns:
            Transaction: Created transaction data
            
        Raises:
            HotpaymentsException: For API errors
        """
        if isinstance(qr_data, dict):
            qr_data = CreateQrCodeRequest.model_validate(qr_data)
        
        data = self._validate_and_serialize(qr_data)
        response = await self._post("/v1/pix/qrcode", data)
        return self._parse_response(response, Transaction)
    
    def create_pix_qr_code_sync(self, qr_data: Union[CreateQrCodeRequest, Dict[str, Any]]) -> Transaction:
        """
        Create a PIX QR code transaction (synchronous)
        
        Args:
            qr_data: QR code data (CreateQrCodeRequest model or dict)
            
        Returns:
            Transaction: Created transaction data
        """
        if isinstance(qr_data, dict):
            qr_data = CreateQrCodeRequest.model_validate(qr_data)
        
        data = self._validate_and_serialize(qr_data)
        response = self._post_sync("/v1/pix/qrcode", data)
        return self._parse_response(response, Transaction)
    
    async def pix_cashout(self, cashout_data: Union[CashoutRequest, Dict[str, Any]]) -> Transaction:
        """
        Request a PIX cashout
        
        Args:
            cashout_data: Cashout data (CashoutRequest model or dict)
            
        Returns:
            Transaction: Cashout transaction data
            
        Raises:
            HotpaymentsException: For API errors
        """
        if isinstance(cashout_data, dict):
            cashout_data = CashoutRequest.model_validate(cashout_data)
        
        data = self._validate_and_serialize(cashout_data)
        response = await self._post("/v1/pix/cashout", data)
        return self._parse_response(response, Transaction)
    
    def pix_cashout_sync(self, cashout_data: Union[CashoutRequest, Dict[str, Any]]) -> Transaction:
        """
        Request a PIX cashout (synchronous)
        
        Args:
            cashout_data: Cashout data (CashoutRequest model or dict)
            
        Returns:
            Transaction: Cashout transaction data
        """
        if isinstance(cashout_data, dict):
            cashout_data = CashoutRequest.model_validate(cashout_data)
        
        data = self._validate_and_serialize(cashout_data)
        response = self._post_sync("/v1/pix/cashout", data)
        return self._parse_response(response, Transaction)
    
    async def check(self, transaction_id: str) -> Transaction:
        """
        Check transaction status
        
        Args:
            transaction_id: Transaction ID to check
            
        Returns:
            Transaction: Transaction data with current status
            
        Raises:
            HotpaymentsException: For API errors
        """
        response = await self._get(f"/v1/transactions/{transaction_id}")
        return self._parse_response(response, Transaction)
    
    def check_sync(self, transaction_id: str) -> Transaction:
        """
        Check transaction status (synchronous)
        
        Args:
            transaction_id: Transaction ID to check
            
        Returns:
            Transaction: Transaction data with current status
        """
        response = self._get_sync(f"/v1/transactions/{transaction_id}")
        return self._parse_response(response, Transaction)