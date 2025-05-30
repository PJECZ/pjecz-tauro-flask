"""
Unit test actualizar_usuario
"""

import unittest

import requests
from faker import Faker

from tests import config


class TestActualizarUsuario(unittest.TestCase):
    """Test actualizar_usuario"""

    def test_post_actualizar_usuario(self):
        """Test POST actualizar_usuario"""
        # Cargar los IDs de los turnos, unidades y usuarios desde la configuración
        turnos_tipos_ids = [int(id) for id in config["turnos_tipos_ids"]]
        usuarios_ids = [int(id) for id in config["usuarios_ids"]]
        ventanillas_ids = [int(id) for id in config["ventanillas_ids"]]
        # Inicializar Faker para generar datos aleatorios en español
        faker = Faker("es_ES")
        # Bucle
        for usuario_id in usuarios_ids:
            # Escoger de uno a todos los tipos de turnos de forma aleatoria
            turnos_tipos_ids = faker.random_elements(
                elements=turnos_tipos_ids, unique=True, length=faker.random_int(min=1, max=len(turnos_tipos_ids))
            )
            # Preparar el payload
            payload = {
                "usuario_id": usuario_id,
                "ventanilla_id": faker.random_element(ventanillas_ids),
                "turnos_tipos_ids": turnos_tipos_ids,
            }
            response = requests.post(
                url=f"{config['api_base_url']}/actualizar_usuario",
                headers={"X-Api-Key": config["api_key"]},
                json=payload,
                timeout=config["timeout"],
            )
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertTrue("success" in payload)
            # self.assertTrue(payload["success"])
            self.assertTrue(
                (
                    (payload["success"] is True and payload["message"] == "Usuario actualizado")
                    or (payload["success"] is False and payload["message"].startswith("Ventanilla ocupada por"))
                )
            )
            self.assertTrue("message" in payload)
            self.assertTrue("data" in payload)


if __name__ == "__main__":
    unittest.main()
