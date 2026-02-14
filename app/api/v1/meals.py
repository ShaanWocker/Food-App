"""
Meal routes for menu management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.dependencies import get_current_user, get_current_admin_user
from app.models.user import User
from app.schemas.meal import MealCreate, MealUpdate, MealResponse
from app.services.meal_service import (
    get_meals,
    get_meal_by_id,
    create_meal,
    update_meal,
    delete_meal
)

router = APIRouter(prefix="/meals", tags=["Meals"])


@router.get("/", response_model=List[MealResponse])
async def list_meals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    is_available: Optional[bool] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of meals with optional filters.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records
        month: Filter by month (1-12)
        year: Filter by year
        is_available: Filter by availability
        category: Filter by category
        db: Database session
    
    Returns:
        List of meals
    """
    meals = get_meals(
        db,
        skip=skip,
        limit=limit,
        month=month,
        year=year,
        is_available=is_available,
        category=category
    )
    return meals


@router.get("/{meal_id}", response_model=MealResponse)
async def get_meal(meal_id: str, db: Session = Depends(get_db)):
    """
    Get a specific meal by ID.
    
    Args:
        meal_id: Meal UUID
        db: Database session
    
    Returns:
        Meal data
    
    Raises:
        HTTPException: If meal not found
    """
    meal = get_meal_by_id(db, meal_id)
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    return meal


@router.post("/", response_model=MealResponse, status_code=status.HTTP_201_CREATED)
async def create_new_meal(
    meal_data: MealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new meal (admin only).
    
    Args:
        meal_data: Meal creation data
        db: Database session
        current_user: Current admin user
    
    Returns:
        Created meal
    """
    meal = create_meal(db, meal_data)
    return meal


@router.put("/{meal_id}", response_model=MealResponse)
async def update_existing_meal(
    meal_id: str,
    meal_data: MealUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update a meal (admin only).
    
    Args:
        meal_id: Meal UUID
        meal_data: Meal update data
        db: Database session
        current_user: Current admin user
    
    Returns:
        Updated meal
    
    Raises:
        HTTPException: If meal not found
    """
    meal = update_meal(db, meal_id, meal_data)
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    return meal


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_meal(
    meal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a meal (admin only).
    
    Args:
        meal_id: Meal UUID
        db: Database session
        current_user: Current admin user
    
    Raises:
        HTTPException: If meal not found
    """
    success = delete_meal(db, meal_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
