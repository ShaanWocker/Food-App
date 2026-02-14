"""
Pydantic schemas for orders.
"""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.models.order import PaymentStatus, OrderStatus
from app.schemas.meal import MealResponse


class OrderItemResponse(BaseModel):
    """Schema for order item response."""
    id: str
    meal_id: str
    quantity: int
    price_at_purchase: Decimal
    meal: MealResponse
    
    class Config:
        from_attributes = True


class AddressResponse(BaseModel):
    """Schema for address response."""
    id: str
    street_address: str
    city: str
    state: str
    postal_code: str
    country: str
    additional_instructions: Optional[str] = None
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Schema for creating a new order."""
    delivery_address_id: str
    special_instructions: Optional[str] = None


class OrderResponse(BaseModel):
    """Schema for order response."""
    id: str
    user_id: str
    total_price: Decimal
    delivery_address_id: str
    payment_status: str
    order_status: str
    stripe_payment_id: Optional[str] = None
    special_instructions: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemResponse]
    delivery_address: AddressResponse
    
    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    order_status: OrderStatus
