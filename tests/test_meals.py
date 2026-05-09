"""
Tests for meal endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

# ------------------------------------------------------------------ #
# Module-level client (used by original simple tests)                 #
# ------------------------------------------------------------------ #
client = TestClient(app)

SAMPLE_MEAL = {
    "name": "Test Burger",
    "description": "A juicy test burger",
    "price": "12.99",
    "category": "Lunch",
    "available_month": "2024-06-01",
    "is_available": True,
    "image_url": None,
}


# ------------------------------------------------------------------ #
# Public read tests                                                    #
# ------------------------------------------------------------------ #

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


# ------------------------------------------------------------------ #
# Admin CRUD tests (use fixtures from conftest)                        #
# ------------------------------------------------------------------ #

class TestAdminMealCRUD:
    """Admin meal create / update / delete tests."""

    def test_admin_create_meal(self, client, admin_token):
        """Admin can create a new meal."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post("/api/v1/meals/", json=SAMPLE_MEAL, headers=headers)
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["name"] == SAMPLE_MEAL["name"]
        assert float(data["price"]) == float(SAMPLE_MEAL["price"])
        assert data["category"] == SAMPLE_MEAL["category"]
        assert data["is_available"] is True

    def test_admin_create_meal_invalid_price(self, client, admin_token):
        """Admin cannot create a meal with invalid (negative) price."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        bad_meal = {**SAMPLE_MEAL, "price": "-5.00"}
        response = client.post("/api/v1/meals/", json=bad_meal, headers=headers)
        assert response.status_code == 422  # validation error

    def test_admin_update_meal(self, client, admin_token):
        """Admin can update an existing meal."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Create a meal first
        create_resp = client.post("/api/v1/meals/", json=SAMPLE_MEAL, headers=headers)
        assert create_resp.status_code == 201
        meal_id = create_resp.json()["id"]

        # Update it
        update_resp = client.put(
            f"/api/v1/meals/{meal_id}",
            json={"name": "Updated Burger", "price": "14.99"},
            headers=headers,
        )
        assert update_resp.status_code == 200, update_resp.text
        updated = update_resp.json()
        assert updated["name"] == "Updated Burger"
        assert float(updated["price"]) == 14.99

    def test_admin_update_nonexistent_meal(self, client, admin_token):
        """Updating a non-existent meal returns 404."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        fake_id = "00000000-0000-0000-0000-000000000099"
        response = client.put(
            f"/api/v1/meals/{fake_id}",
            json={"name": "Ghost"},
            headers=headers,
        )
        assert response.status_code == 404

    def test_admin_toggle_availability(self, client, admin_token):
        """Admin can toggle meal availability."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_resp = client.post("/api/v1/meals/", json=SAMPLE_MEAL, headers=headers)
        assert create_resp.status_code == 201
        meal_id = create_resp.json()["id"]

        # Toggle to unavailable
        toggle_resp = client.put(
            f"/api/v1/meals/{meal_id}",
            json={"is_available": False},
            headers=headers,
        )
        assert toggle_resp.status_code == 200
        assert toggle_resp.json()["is_available"] is False

    def test_admin_delete_meal(self, client, admin_token):
        """Admin can delete a meal."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_resp = client.post("/api/v1/meals/", json=SAMPLE_MEAL, headers=headers)
        assert create_resp.status_code == 201
        meal_id = create_resp.json()["id"]

        del_resp = client.delete(f"/api/v1/meals/{meal_id}", headers=headers)
        assert del_resp.status_code == 204

        # Verify it's gone
        get_resp = client.get(f"/api/v1/meals/{meal_id}")
        assert get_resp.status_code == 404

    def test_admin_delete_nonexistent_meal(self, client, admin_token):
        """Deleting a non-existent meal returns 404."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        fake_id = "00000000-0000-0000-0000-000000000099"
        response = client.delete(f"/api/v1/meals/{fake_id}", headers=headers)
        assert response.status_code == 404

    def test_non_admin_cannot_create_meal(self, client, user_token):
        """A regular user cannot create a meal (403 Forbidden)."""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.post("/api/v1/meals/", json=SAMPLE_MEAL, headers=headers)
        assert response.status_code == 403

    def test_non_admin_cannot_update_meal(self, client, admin_token, user_token):
        """A regular user cannot update a meal (403 Forbidden)."""
        # Admin creates a meal
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        create_resp = client.post(
            "/api/v1/meals/", json=SAMPLE_MEAL, headers=admin_headers
        )
        assert create_resp.status_code == 201
        meal_id = create_resp.json()["id"]

        # Regular user tries to update
        user_headers = {"Authorization": f"Bearer {user_token}"}
        update_resp = client.put(
            f"/api/v1/meals/{meal_id}",
            json={"name": "Hacked"},
            headers=user_headers,
        )
        assert update_resp.status_code == 403

    def test_non_admin_cannot_delete_meal(self, client, admin_token, user_token):
        """A regular user cannot delete a meal (403 Forbidden)."""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        create_resp = client.post(
            "/api/v1/meals/", json=SAMPLE_MEAL, headers=admin_headers
        )
        assert create_resp.status_code == 201
        meal_id = create_resp.json()["id"]

        user_headers = {"Authorization": f"Bearer {user_token}"}
        del_resp = client.delete(f"/api/v1/meals/{meal_id}", headers=user_headers)
        assert del_resp.status_code == 403

    def test_unauthenticated_cannot_create_meal(self, client):
        """Unauthenticated request cannot create a meal (403 or 401)."""
        response = client.post("/api/v1/meals/", json=SAMPLE_MEAL)
        assert response.status_code in (401, 403)

    def test_meal_filters_by_availability(self, client, admin_token):
        """Only available meals are returned when is_available=True filter applied."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Create an unavailable meal
        unavailable_meal = {**SAMPLE_MEAL, "name": "Hidden Meal", "is_available": False}
        client.post("/api/v1/meals/", json=unavailable_meal, headers=headers)

        # Available meals list should not contain the hidden meal
        resp = client.get("/api/v1/meals/", params={"is_available": True})
        assert resp.status_code == 200
        names = [m["name"] for m in resp.json()]
        assert "Hidden Meal" not in names
