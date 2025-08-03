"""Configuration for darkfield CLI"""

import os

# API Configuration
DARKFIELD_API_URL = os.getenv("DARKFIELD_API_URL", "https://api.darkfield.ai")
DARKFIELD_AUTH_URL = os.getenv("DARKFIELD_AUTH_URL", "https://auth.darkfield.ai")

# For local development
if os.getenv("DARKFIELD_ENV") == "development":
    DARKFIELD_API_URL = "http://localhost:8000"
    DARKFIELD_AUTH_URL = "http://localhost:8000/auth"

# CLI Configuration
DEFAULT_OUTPUT_FORMAT = os.getenv("DARKFIELD_OUTPUT_FORMAT", "table")
DISABLE_ANALYTICS = os.getenv("DARKFIELD_NO_ANALYTICS", "false").lower() == "true"