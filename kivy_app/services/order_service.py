"""
Order service for Kivy app.
"""
from kivy_app.services.api_client import api_client
from typing import List


def create_order(delivery_address_id: str, special_instructions: str = None) -> dict:
    """
    Create a new order from cart.
    
    Args:
        delivery_address_id: Address UUID
        special_instructions: Optional instructions
    
    Returns:
        Created order
    """
    return api_client.post("/api/v1/orders/", {
        "delivery_address_id": delivery_address_id,
        "special_instructions": special_instructions
    })


def get_orders() -> List[dict]:
    """
    Get user's orders.
    
    Returns:
        List of orders
    """
    return api_client.get("/api/v1/orders/")


def get_order(order_id: str) -> dict:
    """
    Get specific order by ID.
    
    Args:
        order_id: Order UUID
    
    Returns:
        Order data
    """
    return api_client.get(f"/api/v1/orders/{order_id}")
