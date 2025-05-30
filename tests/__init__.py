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
    "turnos_tipos_ids": os.getenv("TURNOS_TIPOS_IDS").split(","),
    "unidades_ids": os.getenv("UNIDADES_IDS").split(","),
    "usuarios_ids": os.getenv("USUARIOS_IDS").split(","),
    "ventanillas_ids": os.getenv("VENTANILLAS_IDS").split(","),
}
