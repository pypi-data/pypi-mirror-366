"""Type definitions for HotPayments SDK"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class TransactionStatus(str, Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTE = "dispute"
    PROCESSING_REFUND = "processing_refund"


class TransactionType(str, Enum):
    """Transaction type enumeration"""
    CASH_IN = "cash_in"
    CASH_OUT = "cash_out"


class TransactionMethod(str, Enum):
    """Transaction method enumeration"""
    PIX = "pix"
    CREDIT_CARD = "credit_card"


class SplitType(str, Enum):
    """Split type enumeration"""
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class Split(BaseModel):
    """Transaction split model"""
    slug: str = Field(..., description="Company split slug")
    type: SplitType = Field(..., description="Split type")
    value: float = Field(..., ge=0, description="Split value")


class CreateCustomerRequest(BaseModel):
    """Request model for creating a customer"""
    name: str = Field(..., description="Customer name")
    email: str = Field(..., description="Customer email")
    phone_number: str = Field(..., description="Customer phone number")
    document: str = Field(..., description="Customer document (CPF/CNPJ)")


class Customer(BaseModel):
    """Customer model"""
    id: Optional[int] = None
    uuid: Optional[str] = None
    name: str
    email: str
    phone_number: Union[int, str]
    document: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CreateQrCodeRequest(BaseModel):
    """Request model for creating a PIX QR code"""
    amount: float = Field(..., ge=0.01, description="Transaction amount")
    customer_id: str = Field(..., description="Customer ID")
    description: Optional[str] = Field(None, description="Transaction description")
    expires_at: Optional[int] = Field(None, ge=60, description="Expiration time in seconds")
    splits: Optional[List[Split]] = Field(None, description="Transaction splits")


class CashoutRequest(BaseModel):
    """Request model for PIX cashout"""
    amount: float = Field(..., ge=0.01, description="Cashout amount")
    pix_key: str = Field(..., description="PIX key")
    customer_id: str = Field(..., description="Customer ID")
    description: Optional[str] = Field(None, description="Cashout description")


class Transaction(BaseModel):
    """Transaction model"""
    id: Optional[str] = None
    transaction_id: Optional[str] = None
    uuid: Optional[str] = None
    status: TransactionStatus
    type: Optional[TransactionType] = None
    method: Optional[TransactionMethod] = None
    amount: float
    fee: float
    original_amount: Optional[float] = None
    reference: Optional[str] = None
    qr_code: Optional[str] = None
    br_code: Optional[str] = None
    expires_at: Optional[Union[str, int]] = None
    created_at: Optional[Union[str, datetime]] = None


class CreateSubscriptionRequest(BaseModel):
    """Request model for creating a subscription"""
    customer_id: str = Field(..., description="Customer ID")
    plan_id: str = Field(..., description="Plan ID")
    payment_method: str = Field(..., description="Payment method")


class CancelSubscriptionRequest(BaseModel):
    """Request model for cancelling a subscription"""
    reason: Optional[str] = Field(None, max_length=255, description="Cancellation reason")


class SuspendSubscriptionRequest(BaseModel):
    """Request model for suspending a subscription"""
    reason: Optional[str] = Field(None, max_length=255, description="Suspension reason")


class Subscription(BaseModel):
    """Subscription model"""
    id: Optional[str] = None
    uuid: Optional[str] = None
    status: str
    current_period_start: Optional[str] = None
    current_period_end: Optional[str] = None
    trial_end: Optional[str] = None
    next_billing_at: Optional[str] = None
    billing_cycle_count: Optional[int] = None
    failed_payment_count: Optional[int] = None
    price: float
    setup_fee: float
    started_at: Optional[str] = None
    cancelled_at: Optional[str] = None
    suspended_at: Optional[str] = None
    cancel_reason: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SubscriptionPlan(BaseModel):
    """Subscription plan model"""
    id: str
    uuid: Optional[str] = None
    name: str
    description: str
    reference: Optional[str] = None
    price: float
    setup_fee: float
    interval_type: str
    interval_count: int
    billing_cycles: Optional[str] = None
    trial_period_days: Optional[str] = None
    grace_period_days: Optional[str] = None
    auto_charge: Optional[bool] = None


class PaginatedResponse(BaseModel):
    """Generic paginated response model"""
    current_page: int
    data: List[Any]
    first_page_url: Optional[str] = None
    from_: Optional[int] = Field(None, alias="from")
    last_page: int
    last_page_url: Optional[str] = None
    links: List[Dict[str, Any]]
    next_page_url: Optional[str] = None
    path: Optional[str] = None
    per_page: int
    prev_page_url: Optional[str] = None
    to: Optional[int] = None
    total: int


class ApiResponse(BaseModel):
    """Generic API response model"""
    success: bool
    message: str
    data: Optional[Any] = None