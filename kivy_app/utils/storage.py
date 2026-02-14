"""
Local storage utility for tokens and settings.
"""
import json
import os
from pathlib import Path

# Storage file path
STORAGE_DIR = Path.home() / ".foodapp"
STORAGE_FILE = STORAGE_DIR / "config.json"


def _ensure_storage():
    """Ensure storage directory exists."""
    STORAGE_DIR.mkdir(exist_ok=True)


def _load_storage() -> dict:
    """Load storage data."""
    _ensure_storage()
    if STORAGE_FILE.exists():
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    return {}


def _save_storage(data: dict):
    """Save storage data."""
    _ensure_storage()
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f)


def save_token(token: str):
    """Save authentication token."""
    data = _load_storage()
    data['token'] = token
    _save_storage(data)


def get_token() -> str:
    """Get saved authentication token."""
    data = _load_storage()
    return data.get('token')


def clear_token():
    """Clear authentication token."""
    data = _load_storage()
    data.pop('token', None)
    _save_storage(data)
