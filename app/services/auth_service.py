"""
Authentication service for user login and registration.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.cart import Cart
from app.schemas.user import UserCreate
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.
    
    Args:
        db: Database session
        email: User email
        password: Plain text password
    
    Returns:
        User object if authentication successful, None otherwise
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user account.
    
    Args:
        db: Database session
        user_data: User registration data
    
    Returns:
        Created user object
    """
    hashed_password = get_password_hash(user_data.password)
    
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        password_hash=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create cart for the new user
    cart = Cart(user_id=db_user.id)
    db.add(cart)
    db.commit()
    
    return db_user


def generate_tokens(user: User) -> dict:
    """
    Generate access and refresh tokens for a user.
    
    Args:
        user: User object
    
    Returns:
        Dictionary with access_token and refresh_token
    """
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
