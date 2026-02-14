"""
Cart service for Kivy app.
"""
from kivy_app.services.api_client import api_client


def get_cart() -> dict:
    """
    Get user's cart.
    
    Returns:
        Cart data with items and totals
    """
    return api_client.get("/api/v1/cart/")


def add_to_cart(meal_id: str, quantity: int = 1) -> dict:
    """
    Add item to cart.
    
    Args:
        meal_id: Meal UUID
        quantity: Quantity to add
    
    Returns:
        Added cart item
    """
    return api_client.post("/api/v1/cart/items", {
        "meal_id": meal_id,
        "quantity": quantity
    })


def update_cart_item(item_id: str, quantity: int) -> dict:
    """
    Update cart item quantity.
    
    Args:
        item_id: Cart item UUID
        quantity: New quantity
    
    Returns:
        Updated cart item
    """
    return api_client.put(f"/api/v1/cart/items/{item_id}", {
        "quantity": quantity
    })


def remove_from_cart(item_id: str):
    """
    Remove item from cart.
    
    Args:
        item_id: Cart item UUID
    """
    api_client.delete(f"/api/v1/cart/items/{item_id}")


def clear_cart():
    """Clear all items from cart."""
    api_client.delete("/api/v1/cart/")
