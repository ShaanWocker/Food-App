"""
Pydantic schemas for cart management.
"""
from typing import List
from decimal import Decimal
from pydantic import BaseModel, validator
from app.schemas.meal import MealResponse


class CartItemBase(BaseModel):
    """Base cart item schema."""
    meal_id: str
    quantity: int
    
    @validator('quantity')
    def validate_quantity(cls, v):
        """Validate quantity is positive."""
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


class CartItemCreate(CartItemBase):
    """Schema for adding item to cart."""
    pass


class CartItemUpdate(BaseModel):
    """Schema for updating cart item."""
    quantity: int
    
    @validator('quantity')
    def validate_quantity(cls, v):
        """Validate quantity is positive."""
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


class CartItemResponse(BaseModel):
    """Schema for cart item response."""
    id: str
    meal_id: str
    quantity: int
    meal: MealResponse
    
    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """Schema for cart response."""
    id: str
    user_id: str
    items: List[CartItemResponse]
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    
    class Config:
        from_attributes = True
