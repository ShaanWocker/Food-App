"""
Cart routes for shopping cart management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse, CartItemResponse
from app.services.cart_service import (
    get_cart,
    add_item_to_cart,
    update_cart_item,
    remove_item_from_cart,
    clear_cart,
    calculate_cart_totals
)

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/", response_model=CartResponse)
async def get_user_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's cart.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Cart with items and totals
    """
    cart = get_cart(db, str(current_user.id))
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    
    totals = calculate_cart_totals(cart)
    
    return {
        "id": str(cart.id),
        "user_id": str(cart.user_id),
        "items": cart.cart_items,
        **totals
    }


@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add item to cart.
    
    Args:
        item_data: Item to add
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Created/updated cart item
    """
    cart_item = add_item_to_cart(db, str(current_user.id), item_data)
    return cart_item


@router.put("/items/{item_id}", response_model=CartItemResponse)
async def update_item(
    item_id: str,
    item_data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update cart item quantity.
    
    Args:
        item_id: Cart item UUID
        item_data: Update data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Updated cart item
    
    Raises:
        HTTPException: If item not found
    """
    cart_item = update_cart_item(db, str(current_user.id), item_id, item_data)
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    return cart_item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove item from cart.
    
    Args:
        item_id: Cart item UUID
        current_user: Current authenticated user
        db: Database session
    
    Raises:
        HTTPException: If item not found
    """
    success = remove_item_from_cart(db, str(current_user.id), item_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_user_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear all items from cart.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    """
    clear_cart(db, str(current_user.id))
