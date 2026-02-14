"""
Pydantic schemas for meals.
"""
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, validator


class MealBase(BaseModel):
    """Base meal schema with common fields."""
    name: str
    description: Optional[str] = None
    price: Decimal
    image_url: Optional[str] = None
    available_month: date
    is_available: bool = True
    category: Optional[str] = None
    
    @validator('price')
    def validate_price(cls, v):
        """Validate price is positive."""
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v


class MealCreate(MealBase):
    """Schema for creating a new meal."""
    pass


class MealUpdate(BaseModel):
    """Schema for updating meal information."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    image_url: Optional[str] = None
    available_month: Optional[date] = None
    is_available: Optional[bool] = None
    category: Optional[str] = None
    
    @validator('price')
    def validate_price(cls, v):
        """Validate price is positive."""
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than 0')
        return v


class MealResponse(MealBase):
    """Schema for meal response."""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
