"""
Servicio para conectar con la API del sistema voceador
"""

import requests
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError
from typing import Tuple, Any
from pydantic import BaseModel

from config.settings import Settings


class Mensaje(BaseModel):
    """
    Esquema para el payload del servicio de voceo.

    id: Id del turno que sirve como identificador del id del voceador
    texto: Texto que quieres que se vocee.
    minutos: Tiempo de vida del mensaje, una vez sobrepasado se elimina del voceador.
    """

    id: int
    texto: str
    minutos: int | None = 10


class MyAnyError(Exception):
    """Base exception class"""


class MyRequestError(MyAnyError):
    """Excepción porque falló el request"""


class Voceador:
    """Voceador"""

    _settings: Settings

    def __init__(self, setting: Settings):
        """Inicializa el servicio de voceo"""

        self._settings = setting
        self._last_response_data: dict[str, Any] | None = None

    def enviar_mensaje(self, mensaje: Mensaje) -> Tuple[bool, str]:
        """
        Enviar un mensaje para vocear.
        :param mensaje: Un objeto Mensaje con los datos a enviar.
        :return: Una tupla con el estado de éxito (bool) y un mensaje (str).
        """

        url = f"{self._settings.VOCEADOR_API_KEY_URL}/vocear"
        headers = {
            "X-API-KEY": self._settings.VOCEADOR_API_KEY,
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(url, headers=headers, data=mensaje.model_dump_json(), timeout=5)
            response.raise_for_status()

            try:
                data = response.json()
                self._last_response_data = data.get("data")
                if "success" in data and "message" in data:
                    return data["success"], data["message"]
                return False, "Respuesta JSON inválida desde el servidor de voceo."

            except JSONDecodeError:
                return False, "No se pudo decodificar la respuesta JSON del servidor de voceo."

        except RequestException as e:
            return False, f"Error de conexión con el sistema de voceo: {e}"
        except Exception as e:
            return False, f"Ocurrió un error inesperado: {e}"

    def quitar_mensaje(self, id: int) -> Tuple[bool, str]:
        """
        Quita un mensaje para dejar de vocearlo.
        :param id: El id identificador del turno que equivale al id del mensaje enviado previamente.
        :return: Una tupla con el estado de éxito (bool) y un mensaje (str).
        """

        url = f"{self._settings.VOCEADOR_API_KEY_URL}/quitar_mensaje"
        headers = {
            "X-API-KEY": self._settings.VOCEADOR_API_KEY,
        }

        try:
            response = requests.post(url, headers=headers, params=id, timeout=5)
            response.raise_for_status()

            try:
                data = response.json()
                self._last_response_data = data.get("data")
                if "success" in data and "message" in data:
                    return data["success"], data["message"]
                return False, "Respuesta JSON inválida desde el servidor de voceo."

            except JSONDecodeError:
                return False, "No se pudo decodificar la respuesta JSON del servidor de voceo."

        except RequestException as e:
            return False, f"Error de conexión con el sistema de voceo: {e}"
        except Exception as e:
            return False, f"Ocurrió un error inesperado: {e}"
