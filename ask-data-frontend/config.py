"""
Simple frontend configuration.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Backend API
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8015")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

# App Configuration
APP_TITLE = os.getenv("APP_TITLE", "AskData Analytics")
APP_ICON = os.getenv("APP_ICON", "🔍")

# API Endpoints
API_BASE_URL = f"{BACKEND_URL}/api/v1"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"
SCHEMA_ENDPOINT = f"{API_BASE_URL}/schema"
GENERATE_SQL_ENDPOINT = f"{API_BASE_URL}/generate-sql"