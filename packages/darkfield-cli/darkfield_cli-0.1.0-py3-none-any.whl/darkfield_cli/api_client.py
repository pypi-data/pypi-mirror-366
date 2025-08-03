"""API client for darkfield CLI"""

import os
import requests
from typing import Dict, Any, Optional
import keyring
from .config import DARKFIELD_API_URL

class DarkfieldClient:
    """Client for interacting with darkfield API"""
    
    def __init__(self):
        self.base_url = DARKFIELD_API_URL
        self.api_key = keyring.get_password("darkfield-cli", "api_key")
        
        if not self.api_key:
            raise ValueError("Not authenticated. Please run 'darkfield auth login'")
        
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }
    
    def get(self, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to API"""
        response = requests.get(
            f"{self.base_url}{path}",
            headers=self.headers,
            params=params,
        )
        response.raise_for_status()
        return response.json()
    
    def post(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to API"""
        response = requests.post(
            f"{self.base_url}{path}",
            headers=self.headers,
            json=json,
        )
        response.raise_for_status()
        return response.json()
    
    def delete(self, path: str) -> None:
        """Make DELETE request to API"""
        response = requests.delete(
            f"{self.base_url}{path}",
            headers=self.headers,
        )
        response.raise_for_status()
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get current month usage summary"""
        # Mock data for demo
        return {
            "vectors": 125000,
            "vectors_cost": 62.50,
            "data_gb": 250.5,
            "data_cost": 501.00,
            "monitoring_hours": 720,
            "monitoring_cost": 72.00,
            "api_calls": 500000,
            "api_cost": 125.00,
            "total_cost": 760.50,
        }
    
    def track_usage(self, metric_type: str, amount: float):
        """Track usage for billing (would be server-side in production)"""
        # In production, this would be tracked server-side
        pass