"""
Authentication service for Kivy app.
"""
from kivy_app.services.api_client import api_client
from kivy_app.utils.storage import save_token, get_token, clear_token, save_user_data, get_user_data, clear_user_data


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
        # Fetch and cache user profile (includes is_admin flag)
        try:
            user_profile = api_client.get("/api/v1/users/me")
            save_user_data(user_profile)
        except Exception:
            pass
    
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
    clear_user_data()
    api_client.clear_token()


def init_auth():
    """Initialize authentication from stored token."""
    token = get_token()
    if token:
        api_client.set_token(token)
        return True
    return False


def is_admin_user() -> bool:
    """Return True if the currently logged-in user is an admin."""
    user = get_user_data()
    return bool(user.get("is_admin", False))
