"""
Unit test crear_turno
"""

import unittest

import requests
from faker import Faker

from tests import config


class TestCrearTurno(unittest.TestCase):
    """Test crear_turno"""

    def test_post_crear_turno(self):
        """Test POST crear_turno, crear diez turnos aleatorios"""
        # Cargar los IDs de los turnos, unidades y usuarios desde la configuración
        turnos_tipos_ids = [int(id) for id in config["turnos_tipos_ids"]]
        unidades_ids = [int(id) for id in config["unidades_ids"]]
        usuarios_ids = [int(id) for id in config["usuarios_ids"]]
        # Inicializar Faker para generar datos aleatorios en español
        faker = Faker("es_ES")
        # Bucle
        for _ in range(10):
            comentario = faker.sentence(nb_words=6, variable_nb_words=True)
            payload = {
                "usuario_id": faker.random_element(usuarios_ids),
                "turno_tipo_id": faker.random_element(turnos_tipos_ids),
                "unidad_id": faker.random_element(unidades_ids),
                "comentarios": comentario,
            }
            response = requests.post(
                url=f"{config['api_base_url']}/crear_turno",
                headers={"X-Api-Key": config["api_key"]},
                json=payload,
                timeout=config["timeout"],
            )
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertTrue("success" in payload)
            self.assertTrue(payload["success"])
            self.assertTrue("message" in payload)
            self.assertTrue("data" in payload)


if __name__ == "__main__":
    unittest.main()
