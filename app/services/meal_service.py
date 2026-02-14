"""
Meal service for menu management.
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import extract
from app.models.meal import Meal
from app.schemas.meal import MealCreate, MealUpdate


def get_meals(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    month: Optional[int] = None,
    year: Optional[int] = None,
    is_available: Optional[bool] = None,
    category: Optional[str] = None
) -> List[Meal]:
    """
    Get meals with optional filters.
    
    Args:
        db: Database session
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        month: Filter by month
        year: Filter by year
        is_available: Filter by availability
        category: Filter by category
    
    Returns:
        List of meals
    """
    query = db.query(Meal)
    
    if month is not None:
        query = query.filter(extract('month', Meal.available_month) == month)
    
    if year is not None:
        query = query.filter(extract('year', Meal.available_month) == year)
    
    if is_available is not None:
        query = query.filter(Meal.is_available == is_available)
    
    if category:
        query = query.filter(Meal.category == category)
    
    return query.offset(skip).limit(limit).all()


def get_meal_by_id(db: Session, meal_id: str) -> Optional[Meal]:
    """
    Get meal by ID.
    
    Args:
        db: Database session
        meal_id: Meal UUID
    
    Returns:
        Meal object or None
    """
    return db.query(Meal).filter(Meal.id == meal_id).first()


def create_meal(db: Session, meal_data: MealCreate) -> Meal:
    """
    Create a new meal.
    
    Args:
        db: Database session
        meal_data: Meal creation data
    
    Returns:
        Created meal object
    """
    db_meal = Meal(**meal_data.dict())
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal


def update_meal(db: Session, meal_id: str, meal_data: MealUpdate) -> Optional[Meal]:
    """
    Update an existing meal.
    
    Args:
        db: Database session
        meal_id: Meal UUID
        meal_data: Meal update data
    
    Returns:
        Updated meal object or None if not found
    """
    db_meal = get_meal_by_id(db, meal_id)
    if not db_meal:
        return None
    
    update_data = meal_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_meal, field, value)
    
    db.commit()
    db.refresh(db_meal)
    return db_meal


def delete_meal(db: Session, meal_id: str) -> bool:
    """
    Delete a meal.
    
    Args:
        db: Database session
        meal_id: Meal UUID
    
    Returns:
        True if deleted, False if not found
    """
    db_meal = get_meal_by_id(db, meal_id)
    if not db_meal:
        return False
    
    db.delete(db_meal)
    db.commit()
    return True
