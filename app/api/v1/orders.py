"""
Order routes for order management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.order import OrderStatus, PaymentStatus
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import (
    create_order_from_cart,
    get_user_orders,
    get_order_by_id
)
from app.services.cart_service import clear_cart

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new order from cart items.
    
    Args:
        order_data: Order creation data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Created order
    
    Raises:
        HTTPException: If cart is empty
    """
    order = create_order_from_cart(db, str(current_user.id), order_data)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty. Add items before creating an order."
        )
    
    return order


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's orders.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of orders
    """
    orders = get_user_orders(db, str(current_user.id), skip, limit)
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific order by ID.
    
    Args:
        order_id: Order UUID
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Order data
    
    Raises:
        HTTPException: If order not found
    """
    order = get_order_by_id(db, order_id, str(current_user.id))
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order
