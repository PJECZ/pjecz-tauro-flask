"""
Settings

Para desarrollo, debe crear un archivo .env con las variables de entorno:

- HOST
- SALT
- SECRET_KEY
- SQLALCHEMY_DATABASE_URI
"""

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID", "")  # Por defecto está vacío, esto significa estamos en modo local
SERVICE_PREFIX = os.getenv("SERVICE_PREFIX", "pjecz_tauro_flask")


class Settings(BaseSettings):
    """Settings"""

    HOST: str = ""
    SALT: str = ""
    SECRET_KEY: str = ""
    SQLALCHEMY_DATABASE_URI: str = ""
    TZ: str = "America/Mexico_City"

    class Config:
        """Load configuration"""

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            """Customise sources, first environment variables, then .env file, then google cloud secret manager"""
            return env_settings, file_secret_settings, init_settings


@lru_cache()
def get_settings() -> Settings:
    """Get Settings"""
    return Settings()
