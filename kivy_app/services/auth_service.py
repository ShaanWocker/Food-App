"""
Authentication service for Kivy app.
"""
from kivy_app.services.api_client import api_client
from kivy_app.utils.storage import save_token, get_token, clear_token


def login(email: str, password: str) -> dict:
    """
    Login user and save token.
    
    Args:
        email: User email
        password: User password
    
    Returns:
        User data and tokens
    """
    response = api_client.post("/api/v1/auth/login", {
        "email": email,
        "password": password
    })
    
    # Save token
    token = response.get("access_token")
    if token:
        save_token(token)
        api_client.set_token(token)
    
    return response


def register(username: str, email: str, password: str, full_name: str, phone_number: str = None) -> dict:
    """
    Register a new user.
    
    Args:
        username: Username
        email: User email
        password: User password
        full_name: Full name
        phone_number: Phone number (optional)
    
    Returns:
        Created user data
    """
    return api_client.post("/api/v1/auth/register", {
        "username": username,
        "email": email,
        "password": password,
        "full_name": full_name,
        "phone_number": phone_number
    })


def logout():
    """Logout user and clear token."""
    clear_token()
    api_client.clear_token()


def init_auth():
    """Initialize authentication from stored token."""
    token = get_token()
    if token:
        api_client.set_token(token)
        return True
    return False
