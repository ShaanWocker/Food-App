"""
Order service for order management.
"""
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.cart import Cart, CartItem
from app.schemas.order import OrderCreate


def create_order_from_cart(
    db: Session,
    user_id: str,
    order_data: OrderCreate
) -> Optional[Order]:
    """
    Create an order from user's cart.
    
    Args:
        db: Database session
        user_id: User UUID
        order_data: Order creation data
    
    Returns:
        Created order object or None if cart is empty
    """
    # Get user's cart
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart or not cart.cart_items:
        return None
    
    # Calculate total price
    total_price = Decimal("0.00")
    for item in cart.cart_items:
        total_price += item.meal.price * item.quantity
    
    # Add tax (8%)
    tax = total_price * Decimal("0.08")
    total_price += tax
    
    # Create order
    order = Order(
        user_id=user_id,
        total_price=round(total_price, 2),
        delivery_address_id=order_data.delivery_address_id,
        special_instructions=order_data.special_instructions,
        payment_status=PaymentStatus.PENDING,
        order_status=OrderStatus.PENDING
    )
    
    db.add(order)
    db.flush()
    
    # Create order items from cart items
    for cart_item in cart.cart_items:
        order_item = OrderItem(
            order_id=order.id,
            meal_id=cart_item.meal_id,
            quantity=cart_item.quantity,
            price_at_purchase=cart_item.meal.price
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(order)
    
    return order


def get_user_orders(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[Order]:
    """
    Get orders for a user.
    
    Args:
        db: Database session
        user_id: User UUID
        skip: Number of records to skip
        limit: Maximum number of records
    
    Returns:
        List of orders
    """
    return db.query(Order).filter(
        Order.user_id == user_id
    ).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


def get_order_by_id(db: Session, order_id: str, user_id: Optional[str] = None) -> Optional[Order]:
    """
    Get order by ID.
    
    Args:
        db: Database session
        order_id: Order UUID
        user_id: Optional user UUID to verify ownership
    
    Returns:
        Order object or None
    """
    query = db.query(Order).filter(Order.id == order_id)
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    return query.first()


def update_order_status(
    db: Session,
    order_id: str,
    new_status: OrderStatus
) -> Optional[Order]:
    """
    Update order status.
    
    Args:
        db: Database session
        order_id: Order UUID
        new_status: New order status
    
    Returns:
        Updated order or None
    """
    order = get_order_by_id(db, order_id)
    if not order:
        return None
    
    order.order_status = new_status
    db.commit()
    db.refresh(order)
    return order


def update_payment_status(
    db: Session,
    order_id: str,
    payment_status: PaymentStatus,
    stripe_payment_id: Optional[str] = None
) -> Optional[Order]:
    """
    Update payment status for an order.
    
    Args:
        db: Database session
        order_id: Order UUID
        payment_status: New payment status
        stripe_payment_id: Optional Stripe payment ID
    
    Returns:
        Updated order or None
    """
    order = get_order_by_id(db, order_id)
    if not order:
        return None
    
    order.payment_status = payment_status
    if stripe_payment_id:
        order.stripe_payment_id = stripe_payment_id
    
    db.commit()
    db.refresh(order)
    return order


def get_all_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = None
) -> List[Order]:
    """
    Get all orders (admin function).
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records
        status: Optional filter by status
    
    Returns:
        List of orders
    """
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.order_status == status)
    
    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
