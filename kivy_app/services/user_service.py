"""
User profile and address service for Kivy app.
"""
from typing import List, Optional
from kivy_app.services.api_client import api_client


def get_profile() -> dict:
    """Get the current user's profile."""
    return api_client.get("/api/v1/users/me")


def update_profile(full_name: Optional[str] = None, phone_number: Optional[str] = None) -> dict:
    """
    Update the current user's profile.

    Args:
        full_name: New full name (omitted if None)
        phone_number: New phone number (omitted if None)

    Returns:
        Updated user profile
    """
    payload = {}
    if full_name is not None:
        payload["full_name"] = full_name
    if phone_number is not None:
        payload["phone_number"] = phone_number
    return api_client.put("/api/v1/users/me", payload)


def get_addresses() -> List[dict]:
    """Get the current user's saved delivery addresses."""
    return api_client.get("/api/v1/users/me/addresses")


def create_address(address_data: dict) -> dict:
    """
    Create a new delivery address.

    Args:
        address_data: street_address, city, state, postal_code, country,
            additional_instructions, is_default

    Returns:
        Created address
    """
    return api_client.post("/api/v1/users/me/addresses", address_data)


def update_address(address_id: str, address_data: dict) -> dict:
    """Update an existing address."""
    return api_client.put(f"/api/v1/users/me/addresses/{address_id}", address_data)


def delete_address(address_id: str) -> None:
    """Delete an address."""
    api_client.delete(f"/api/v1/users/me/addresses/{address_id}")
