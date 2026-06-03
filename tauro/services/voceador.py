"""
Servicio para conectar con la API del sistema voceador
"""

import json
import requests
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError
from typing import Tuple

from config.settings import Settings


class MyAnyError(Exception):
    """Base exception class"""


class MyRequestError(MyAnyError):
    """Excepción porque falló el request"""
