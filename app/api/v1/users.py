"""
User profile routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.address import Address
from app.schemas.user import UserResponse, UserUpdate
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/users", tags=["Users"])


class AddressCreate(BaseModel):
    """Schema for creating an address."""
    street_address: str
    city: str
    state: str
    postal_code: str
    country: str = "USA"
    additional_instructions: Optional[str] = None
    is_default: bool = False


class AddressUpdate(BaseModel):
    """Schema for updating an address."""
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    additional_instructions: Optional[str] = None
    is_default: Optional[bool] = None


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User profile data
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile.
    
    Args:
        user_data: Update data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Updated user profile
    """
    update_data = user_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/addresses")
async def get_user_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's saved addresses.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of addresses
    """
    addresses = db.query(Address).filter(Address.user_id == current_user.id).all()
    return addresses


@router.post("/me/addresses", status_code=status.HTTP_201_CREATED)
async def create_address(
    address_data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new address for the user.
    
    Args:
        address_data: Address data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Created address
    """
    # If this is set as default, unset other defaults
    if address_data.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.is_default == True
        ).update({"is_default": False})
    
    address = Address(
        user_id=current_user.id,
        **address_data.dict()
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


@router.put("/me/addresses/{address_id}")
async def update_address(
    address_id: str,
    address_data: AddressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an address.
    
    Args:
        address_id: Address UUID
        address_data: Update data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Updated address
    
    Raises:
        HTTPException: If address not found
    """
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    update_data = address_data.dict(exclude_unset=True)
    
    # If setting as default, unset other defaults
    if update_data.get("is_default"):
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.id != address_id,
            Address.is_default == True
        ).update({"is_default": False})
    
    for field, value in update_data.items():
        setattr(address, field, value)
    
    db.commit()
    db.refresh(address)
    return address


@router.delete("/me/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an address.
    
    Args:
        address_id: Address UUID
        current_user: Current authenticated user
        db: Database session
    
    Raises:
        HTTPException: If address not found
    """
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    db.delete(address)
    db.commit()
