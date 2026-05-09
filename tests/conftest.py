"""
Test configuration and fixtures.
"""
import os
# Override DATABASE_URL before any app imports so SQLite is used for tests
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app

# Test database URL (in-memory SQLite for isolation)
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override get_db to use the test SQLite database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session with clean tables per test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    """Create a test client with SQLite database override."""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def admin_token(client):
    """Create an admin user and return an auth token."""
    from app.models.user import User
    from app.core.security import get_password_hash, create_access_token

    db = TestingSessionLocal()
    try:
        # Create admin user if not present
        admin = db.query(User).filter(User.email == "admin_test@example.com").first()
        if not admin:
            admin = User(
                email="admin_test@example.com",
                username="admin_test",
                full_name="Admin Test",
                password_hash=get_password_hash("AdminPass123!"),
                is_active=True,
                is_admin=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
        token = create_access_token(data={"sub": str(admin.id), "email": admin.email})
    finally:
        db.close()
    return token


@pytest.fixture(scope="module")
def user_token(client):
    """Create a regular user and return an auth token."""
    from app.models.user import User
    from app.core.security import get_password_hash, create_access_token

    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "user_test@example.com").first()
        if not user:
            user = User(
                email="user_test@example.com",
                username="user_test",
                full_name="Regular User",
                password_hash=get_password_hash("UserPass123!"),
                is_active=True,
                is_admin=False,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        token = create_access_token(data={"sub": str(user.id), "email": user.email})
    finally:
        db.close()
    return token
