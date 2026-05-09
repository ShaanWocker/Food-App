"""
Meal service for Kivy app.
"""
from kivy_app.services.api_client import api_client
from typing import List, Optional


def get_meals(month: Optional[int] = None, year: Optional[int] = None,
              is_available: Optional[bool] = True, category: Optional[str] = None) -> List[dict]:
    """
    Get meals from API.

    Args:
        month: Filter by month
        year: Filter by year
        is_available: Filter by availability (None = no filter)
        category: Filter by category

    Returns:
        List of meals
    """
    params = {}
    if month:
        params["month"] = month
    if year:
        params["year"] = year
    if is_available is not None:
        params["is_available"] = is_available
    if category:
        params["category"] = category

    return api_client.get("/api/v1/meals/", params=params)


def get_meal(meal_id: str) -> dict:
    """
    Get specific meal by ID.

    Args:
        meal_id: Meal UUID

    Returns:
        Meal data
    """
    return api_client.get(f"/api/v1/meals/{meal_id}")


def create_meal(meal_data: dict) -> dict:
    """
    Create a new meal (admin only).

    Args:
        meal_data: Meal fields (name, description, price, category,
                   available_month, is_available, image_url)

    Returns:
        Created meal data
    """
    return api_client.post("/api/v1/meals/", meal_data)


def update_meal(meal_id: str, meal_data: dict) -> dict:
    """
    Update an existing meal (admin only).

    Args:
        meal_id: Meal UUID
        meal_data: Fields to update

    Returns:
        Updated meal data
    """
    return api_client.put(f"/api/v1/meals/{meal_id}", meal_data)


def delete_meal(meal_id: str) -> None:
    """
    Delete a meal (admin only).

    Args:
        meal_id: Meal UUID
    """
    return api_client.delete(f"/api/v1/meals/{meal_id}")
