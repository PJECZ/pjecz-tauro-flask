"""
Tests config
"""

import os

from dotenv import load_dotenv

load_dotenv()

config = {
    "api_key": os.getenv("API_KEY", ""),
    "api_base_url": os.getenv("API_BASE_URL", "http://127.0.0.1:5000/api_key/v1"),
    "timeout": int(os.getenv("TIMEOUT", "10")),
}
