"""
Simple API client for backend communication.
"""

import requests
from typing import Dict, Any, Tuple
import config

class APIClient:
    """Simple API client."""
    
    def __init__(self):
        self.timeout = config.API_TIMEOUT
    
    def _request(self, method: str, url: str, **kwargs) -> Tuple[bool, Dict[str, Any]]:
        """Make request with error handling."""
        try:
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {"error": f"HTTP {response.status_code}", "message": response.text[:100]}
        except Exception as e:
            return False, {"error": "Connection", "message": str(e)}
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        """Check backend health."""
        return self._request("GET", config.HEALTH_ENDPOINT)
    
    def get_schema(self) -> Tuple[bool, Dict[str, Any]]:
        """Get schema info."""
        return self._request("GET", config.SCHEMA_ENDPOINT)
    
    def generate_sql(self, question: str, max_tables: int = 4, execute_sql: bool = True) -> Tuple[bool, Dict[str, Any]]:
        """Generate SQL."""
        payload = {"question": question, "max_tables": max_tables, "execute_sql": execute_sql}
        return self._request("POST", config.GENERATE_SQL_ENDPOINT, json=payload)

# Global instance
api = APIClient()