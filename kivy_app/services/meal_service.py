"""
Meal service for Kivy app.
"""
from kivy_app.services.api_client import api_client
from typing import List, Optional


def get_meals(month: Optional[int] = None, year: Optional[int] = None, 
              is_available: bool = True, category: Optional[str] = None) -> List[dict]:
    """
    Get meals from API.
    
    Args:
        month: Filter by month
        year: Filter by year
        is_available: Filter by availability
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
