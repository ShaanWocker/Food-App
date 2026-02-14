"""
API client for backend communication.
"""
import requests
from typing import Optional, Dict, Any
import os


class APIClient:
    """HTTP client for communicating with the FastAPI backend."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url
        self.token: Optional[str] = None
    
    def set_token(self, token: str):
        """Set authentication token."""
        self.token = token
    
    def clear_token(self):
        """Clear authentication token."""
        self.token = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make GET request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
        
        Returns:
            Response data
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make POST request.
        
        Args:
            endpoint: API endpoint
            data: Request body data
        
        Returns:
            Response data
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make PUT request.
        
        Args:
            endpoint: API endpoint
            data: Request body data
        
        Returns:
            Response data
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.put(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def delete(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """
        Make DELETE request.
        
        Args:
            endpoint: API endpoint
        
        Returns:
            Response data or None for 204 responses
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.delete(url, headers=self._get_headers())
        response.raise_for_status()
        
        if response.status_code == 204:
            return None
        return response.json()


# Global API client instance
api_client = APIClient()
