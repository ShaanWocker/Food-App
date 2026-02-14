"""
Admin routes for order and menu management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from decimal import Decimal
from app.database import get_db
from app.dependencies import get_current_admin_user
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.meal import Meal
from app.schemas.order import OrderResponse, OrderStatusUpdate
from app.services.order_service import (
    get_all_orders,
    get_order_by_id,
    update_order_status
)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/orders", response_model=List[OrderResponse])
async def get_all_orders_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    status: Optional[OrderStatus] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all orders (admin only).
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records
        status: Optional filter by status
        current_user: Current admin user
        db: Database session
    
    Returns:
        List of all orders
    """
    orders = get_all_orders(db, skip, limit, status)
    return orders


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order_admin(
    order_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get specific order details (admin only).
    
    Args:
        order_id: Order UUID
        current_user: Current admin user
        db: Database session
    
    Returns:
        Order data
    
    Raises:
        HTTPException: If order not found
    """
    order = get_order_by_id(db, order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status_admin(
    order_id: str,
    status_data: OrderStatusUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update order status (admin only).
    
    Args:
        order_id: Order UUID
        status_data: New status
        current_user: Current admin user
        db: Database session
    
    Returns:
        Updated order
    
    Raises:
        HTTPException: If order not found
    """
    order = update_order_status(db, order_id, status_data.order_status)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.get("/analytics/revenue")
async def get_revenue_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get revenue analytics (admin only).
    
    Args:
        days: Number of days to analyze
        current_user: Current admin user
        db: Database session
    
    Returns:
        Revenue statistics
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total revenue
    total_revenue = db.query(func.sum(Order.total_price)).filter(
        Order.created_at >= start_date,
        Order.payment_status == "Completed"
    ).scalar() or Decimal("0.00")
    
    # Number of orders
    total_orders = db.query(func.count(Order.id)).filter(
        Order.created_at >= start_date
    ).scalar() or 0
    
    # Orders by status
    status_counts = {}
    for order_status in OrderStatus:
        count = db.query(func.count(Order.id)).filter(
            Order.created_at >= start_date,
            Order.order_status == order_status
        ).scalar() or 0
        status_counts[order_status.value] = count
    
    return {
        "period_days": days,
        "total_revenue": float(total_revenue),
        "total_orders": total_orders,
        "average_order_value": float(total_revenue / total_orders) if total_orders > 0 else 0,
        "orders_by_status": status_counts
    }


@router.get("/analytics/popular-meals")
async def get_popular_meals(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get most popular meals (admin only).
    
    Args:
        limit: Number of meals to return
        current_user: Current admin user
        db: Database session
    
    Returns:
        List of popular meals with order counts
    """
    from app.models.order import OrderItem
    
    popular = db.query(
        Meal.name,
        Meal.id,
        func.sum(OrderItem.quantity).label("total_ordered")
    ).join(OrderItem).group_by(Meal.id, Meal.name).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(limit).all()
    
    return [
        {
            "meal_id": str(item.id),
            "meal_name": item.name,
            "total_ordered": int(item.total_ordered)
        }
        for item in popular
    ]
