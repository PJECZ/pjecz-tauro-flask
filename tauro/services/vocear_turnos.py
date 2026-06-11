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

    def vocear_turnos(self) -> Tuple[bool, str]:
        """
        Lógica de que mensajes enviar al servicio de voceador

        Vocear los turnos es estado de 'PASE A VENTANILLA'.
        """

        # Consultar los turnos a vocear
        turnos = (
            Turno.query.join(TurnoEstado)
            .join(TurnoTipo)
            .filter(TurnoEstado.nombre == "PASE A VENTANILLA")
            .filter(Turno.estatus == "A")
            .order_by(
                # 1. Prioridad por estado: PASE A VENTANILLA primero (valor 0), el resto después (valor 1)
                case((TurnoEstado.nombre == "PASE A VENTANILLA", 0), else_=1),
                # 2. Dentro de cada grupo, ordenar por número de turno
                Turno.numero,
            )
            .all()
        )

        # Si no se encuentran turnos
        if not turnos:
            return True, "No hay turnos que anunciar"

        # Consultar Unidades
        unidades_sql = Unidad.query.all()
        unidades = {unidad.id: unidad for unidad in unidades_sql}

        # Generar los mensajes
        for turno in turnos:
            mensaje = self.contruir_mensaje_turno(turno, unidades[turno.unidad_id])

            try:
                respuesta, mensaje_resp = self._voceador.enviar_mensaje(mensaje)
            except Exception as e:
                return False, f"Ocurrió un error con el servicio de voceo: {e}"

            if respuesta is False:
                return False, f"Error con el servicio de voceador: {mensaje_resp}"

        return True, "Mensaje enviado al voceador exitosamente"

    def agregar_mensaje(self, turno: Turno) -> Tuple[bool, str]:
        """
        Agregar mensaje de turno a la lista del voceador
        """
        # Consultar Unidades
        unidades_sql = Unidad.query.all()
        unidades = {unidad.id: unidad for unidad in unidades_sql}

        mensaje = ""
        if turno.numero_cubiculo == 0:
            mensaje = self.contruir_mensaje_turno(turno, unidades[turno.unidad_id])
        else:
            mensaje = self.construir_mensaje_cubiculo(turno, unidades[turno.unidad_id])

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

        unidad_clave_deletreada = ".".join(unidad.clave)

        # Si no tiene ubicación mencionar la unidad
        texto = f"El Turno {unidad_clave_deletreada} {turno.numero}"

        if turno.ubicacion.nombre == "NO DEFINIDO":
            texto = f" {texto} pase a {unidad.nombre}"
        else:
            texto = f" {texto} pase a la {turno.ubicacion.nombre} número {turno.ubicacion.numero}"

        mensaje = Mensaje(
            id=turno.id,
            mensaje=texto,
        )

        return mensaje

    def construir_mensaje_cubiculo(self, turno: Turno, unidad: Unidad) -> Mensaje:
        """Construye el mensaje para cada turno que son llamados a cubículos"""

        unidad_clave_deletreada = ".".join(unidad.clave)

        # Si no tiene ubicación mencionar la unidad
        texto = f"El Turno {unidad_clave_deletreada} {turno.numero}"

        if turno.numero_cubiculo == 0:
            texto = f" {texto} pase al cubículo número {turno.numero_cubiculo}"
        else:
            texto = f" {texto} pase al cubículo número {turno.numero_cubiculo}"

        mensaje = Mensaje(
            id=turno.id,
            mensaje=texto,
        )

        return mensaje
