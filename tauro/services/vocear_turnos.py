"""
Vocear-Turnos

Se encarga de la lógica de negocio, de cuándo, qué turnos vocear y
que mensaje transmitir al servicio de Voceador.
"""

from typing import Tuple

from config.settings import get_settings
from sqlalchemy import case

from tauro.services.voceador import Voceador, Mensaje

from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.unidades.models import Unidad


class VocearTurnos:
    """
    Clase que se encarga de la lógica de generar los mensajes de voceo
    """

    _voceador: Voceador

    def __init__(self):
        """Constructor: Inicializa variables"""
        self._voceador = Voceador(get_settings())

    def agregar_mensaje(self, turno: Turno) -> Tuple[bool, str]:
        """
        Agregar mensaje de turno a la lista del voceador
        """
        # Consultar Unidades
        unidades_sql = Unidad.query.all()
        unidades = {unidad.id: unidad for unidad in unidades_sql}

        # Validar si la unidad tiene activo el vocear
        unidad_turno = unidades[turno.unidad_id]
        if unidad_turno == 0 or unidad_turno is None or unidad_turno.es_voceable is False:
            return True, f"La unidad {unidad_turno.clave} no es voceable"

        # Construir mensaje voceable
        mensaje = ""
        if turno.numero_cubiculo == 0:
            mensaje = self.contruir_mensaje_turno(turno, unidad_turno)
        else:
            mensaje = self.construir_mensaje_cubiculo(turno, unidad_turno)

        try:
            respuesta, mensaje_resp = self._voceador.enviar_mensaje(mensaje)
        except Exception as e:
            return False, f"Ocurrió un error con el servicio de voceo: {e}"

        if respuesta is False:
            return False, f"Error con el servicio de voceador: {mensaje_resp}"

        return True, "Mensaje enviado al voceador exitosamente"

    def quitar_mensaje(self, turno: Turno) -> Tuple[bool, str]:
        """
        Quitar de la lista del voceado un turno
        """
        try:
            respuesta, mensaje_resp = self._voceador.quitar_mensaje(turno.id)
        except Exception as e:
            return False, f"Ocurrió un error con el servicio de voceo: {e}"

        if respuesta is False:
            return False, f"Error con el servicio de voceador: {mensaje_resp}"

        return True, "Mensaje eliminado del voceador exitosamente"

    def contruir_mensaje_turno(self, turno: Turno, unidad: Unidad) -> Mensaje:
        """Construye el mensaje para cada turno que pasen a una ubicación"""

        if unidad.pronunciacion:
            unidad_clave_deletreada = unidad.pronunciacion
        else:
            unidad_clave_deletreada = ".".join(unidad.clave)

        # Si no tiene ubicación mencionar la unidad
        texto = f"El Turrno {unidad_clave_deletreada} {turno.numero}."

        if turno.ubicacion.nombre == "NO DEFINIDO":
            texto = f" {texto} Pase a {unidad.nombre}"
        else:
            texto = f" {texto} Pase a la {turno.ubicacion.nombre} número {turno.ubicacion.numero}"

        mensaje = Mensaje(
            id=turno.id,
            mensaje=texto,
        )

        return mensaje

    def construir_mensaje_cubiculo(self, turno: Turno, unidad: Unidad) -> Mensaje:
        """Construye el mensaje para cada turno que son llamados a cubículos"""

        if unidad.pronunciacion:
            unidad_clave_deletreada = unidad.pronunciacion
        else:
            unidad_clave_deletreada = ".".join(unidad.clave)

        # Si no tiene ubicación mencionar la unidad
        texto = f"El Turrno {unidad_clave_deletreada} {turno.numero}."

        if turno.numero_cubiculo:
            texto = f" {texto} Pase al cubículo número {turno.numero_cubiculo}"
        else:
            texto = f" {texto} Pase al cubículo"

        mensaje = Mensaje(
            id=turno.id,
            mensaje=texto,
        )

        return mensaje
