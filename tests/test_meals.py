"""
Tests for meal endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_meals():
    """Test getting meals list."""
    response = client.get("/api/v1/meals/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_meals_with_filters():
    """Test getting meals with filters."""
    response = client.get(
        "/api/v1/meals/",
        params={"month": 1, "year": 2024, "is_available": True}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_nonexistent_meal():
    """Test getting a meal that doesn't exist."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/meals/{fake_id}")
    assert response.status_code == 404
