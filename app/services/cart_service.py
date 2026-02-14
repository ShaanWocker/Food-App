"""
Cart service for shopping cart management.
"""
from typing import Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.cart import Cart, CartItem
from app.models.meal import Meal
from app.schemas.cart import CartItemCreate, CartItemUpdate


TAX_RATE = Decimal("0.08")  # 8% tax rate


def get_or_create_cart(db: Session, user_id: str) -> Cart:
    """
    Get or create a cart for a user.
    
    Args:
        db: Database session
        user_id: User UUID
    
    Returns:
        Cart object
    """
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def get_cart(db: Session, user_id: str) -> Optional[Cart]:
    """
    Get user's cart with items.
    
    Args:
        db: Database session
        user_id: User UUID
    
    Returns:
        Cart object or None
    """
    return db.query(Cart).filter(Cart.user_id == user_id).first()


def add_item_to_cart(db: Session, user_id: str, item_data: CartItemCreate) -> CartItem:
    """
    Add item to cart or update quantity if already exists.
    
    Args:
        db: Database session
        user_id: User UUID
        item_data: Cart item data
    
    Returns:
        Created or updated cart item
    """
    cart = get_or_create_cart(db, user_id)
    
    # Check if item already exists in cart
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.meal_id == item_data.meal_id
    ).first()
    
    if existing_item:
        existing_item.quantity += item_data.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    
    # Create new cart item
    cart_item = CartItem(
        cart_id=cart.id,
        meal_id=item_data.meal_id,
        quantity=item_data.quantity
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item


def update_cart_item(db: Session, user_id: str, item_id: str, item_data: CartItemUpdate) -> Optional[CartItem]:
    """
    Update cart item quantity.
    
    Args:
        db: Database session
        user_id: User UUID
        item_id: Cart item UUID
        item_data: Update data
    
    Returns:
        Updated cart item or None
    """
    cart = get_cart(db, user_id)
    if not cart:
        return None
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        return None
    
    cart_item.quantity = item_data.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item


def remove_item_from_cart(db: Session, user_id: str, item_id: str) -> bool:
    """
    Remove item from cart.
    
    Args:
        db: Database session
        user_id: User UUID
        item_id: Cart item UUID
    
    Returns:
        True if removed, False if not found
    """
    cart = get_cart(db, user_id)
    if not cart:
        return False
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        return False
    
    db.delete(cart_item)
    db.commit()
    return True


def clear_cart(db: Session, user_id: str) -> bool:
    """
    Clear all items from cart.
    
    Args:
        db: Database session
        user_id: User UUID
    
    Returns:
        True if cleared, False if cart not found
    """
    cart = get_cart(db, user_id)
    if not cart:
        return False
    
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    return True


def calculate_cart_totals(cart: Cart) -> dict:
    """
    Calculate cart subtotal, tax, and total.
    
    Args:
        cart: Cart object with items loaded
    
    Returns:
        Dictionary with subtotal, tax, and total
    """
    subtotal = Decimal("0.00")
    
    for item in cart.cart_items:
        subtotal += item.meal.price * item.quantity
    
    tax = subtotal * TAX_RATE
    total = subtotal + tax
    
    return {
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "total": round(total, 2)
    }
