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


def get_all_orders_admin(status: str = None, skip: int = 0, limit: int = 100) -> List[dict]:
    """
    Get all orders across all users (admin only).

    Args:
        status: Optional OrderStatus value to filter by
        skip: Number of records to skip
        limit: Maximum number of records

    Returns:
        List of orders
    """
    params = {"skip": skip, "limit": limit}
    if status:
        params["status"] = status
    return api_client.get("/api/v1/admin/orders", params=params)


def update_order_status_admin(order_id: str, order_status: str) -> dict:
    """
    Update an order's status (admin only).

    Args:
        order_id: Order UUID
        order_status: New OrderStatus value

    Returns:
        Updated order
    """
    return api_client.patch(f"/api/v1/admin/orders/{order_id}/status", {"order_status": order_status})


def get_revenue_analytics(days: int = 30) -> dict:
    """
    Get revenue analytics (admin only).

    Args:
        days: Number of days to analyze

    Returns:
        Revenue statistics
    """
    return api_client.get("/api/v1/admin/analytics/revenue", params={"days": days})


def get_popular_meals(limit: int = 10) -> List[dict]:
    """
    Get most popular meals by order volume (admin only).

    Args:
        limit: Number of meals to return

    Returns:
        List of popular meals with order counts
    """
    return api_client.get("/api/v1/admin/analytics/popular-meals", params={"limit": limit})
