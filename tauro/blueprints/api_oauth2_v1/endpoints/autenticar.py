"""
API v1 Endpoint: Autenticar
"""

import re
from datetime import datetime, timedelta
from functools import wraps

import jwt
from pytz import timezone
from email_validator import EmailNotValidError, validate_email
from flask import current_app, g, request
from flask_restful import Resource

from tauro.blueprints.api_v1.schemas import ResponseSchema
from tauro.blueprints.api_oauth2_v1.schemas import RolOut, TokenSchema, UnidadOut, UbicacionOut
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.usuarios_roles.models import UsuarioRol

CONTRASENA_REGEXP = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"  # Contraseña con al menos 8 caracteres, una letra y un número


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        if not token:
            return (
                ResponseSchema(
                    success=False,
                    message="No hay token en esta solicitud",
                ).model_dump(),
                401,
            )
        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            g.current_user = data["sub"]
        except jwt.ExpiredSignatureError:
            return (
                ResponseSchema(
                    success=False,
                    message="El token ha expirado!",
                ).model_dump(),
                200,
            )
        except jwt.InvalidTokenError:
            return (
                ResponseSchema(
                    success=False,
                    message="No es válido el token!",
                ).model_dump(),
                401,
            )
        return f(*args, **kwargs)

    return decorated


class Authenticate(Resource):
    """Autenticarse recibiendo el username y el password por request form, entregar el Token"""

    def post(self) -> TokenSchema:
        """Autenticarse recibiendo el username y el password por request form, entregar el Token"""
        username = request.form.get("username")
        password = request.form.get("password")

        print(username, ":", password)
        # Si username es None y password es None, entonces recibir por JSON
        if username is None and password is None:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

        # Si aun asi username es None y password es None, entonces error
        if username is None or password is None:
            return TokenSchema(
                success=False,
                message="Username y password son requeridos",
            ).model_dump()

        # Validar que username sea un correo electrónico
        try:
            validate_email(username)
        except EmailNotValidError as error:
            return TokenSchema(
                success=False,
                message=f"Email no válido: {str(error)}",
            ).model_dump()

        # Validar que password cumpla con la expresión regular
        if not re.match(CONTRASENA_REGEXP, password):
            return TokenSchema(
                success=False,
                message="La contraseña debe tener al menos 8 caracteres, una letra y un número",
            ).model_dump()

        # Consultar el usuario
        usuario = Usuario.find_by_identity(username)

        # Si no existe el usuario
        if not usuario:
            return TokenSchema(
                success=False,
                message="Usuario no encontrado",
            ).model_dump()

        # Si la contraseña no es correcta
        if not usuario.authenticated(with_password=True, password=password):
            return TokenSchema(
                success=False,
                message="Contraseña incorrecta",
            ).model_dump()

        # Verificar si el usuario tiene acceso al front-end
        if not usuario.es_acceso_frontend:
            return TokenSchema(
                success=False,
                message="El usuario no tiene acceso al front-end",
            ).model_dump()

        # Extraer un único rol
        usuarios_roles = UsuarioRol.query.filter_by(usuario_id=usuario.id).filter_by(estatus="A").first()
        if usuarios_roles is None:
            return TokenSchema(
                success=False,
                message="El usuario no tiene un rol asignado",
            ).model_dump()
        rol = usuarios_roles.rol

        # Generar token con PyJWT
        payload = {
            "sub": username,
            "iat": datetime.now(tz=timezone(current_app.config["TZ"])),
            "exp": datetime.now(tz=timezone(current_app.config["TZ"])) + timedelta(hours=1),
        }
        access_token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

        # Entregar JSON
        return TokenSchema(
            success=True,
            message="Token generado",
            access_token=access_token,
            token_type="Bearer",
            expires_in=current_app.config["TOKEN_OAUTH2_EXPIRES_IN_SEG"],
            username=username,
            usuario_nombre_completo=usuario.nombre,
            rol=RolOut(
                id=rol.id,
                nombre=rol.nombre,
            ),
            unidad=UnidadOut(
                id=usuario.unidad_id,
                nombre=usuario.unidad.nombre,
                clave=usuario.unidad.clave,
            ),
            ubicacion=UbicacionOut(
                id=usuario.ubicacion_id,
                nombre=usuario.ubicacion.nombre,
                numero=usuario.ubicacion.numero,
            ),
        ).model_dump()


class ValidarToken(Resource):
    """Validar token"""

    def get(self):
        """Validar token"""

        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        if not token:
            return (
                ResponseSchema(
                    success=False,
                    message="No hay token en esta solicitud",
                ).model_dump(),
                200,
            )
        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            g.current_user = data["sub"]
        except jwt.ExpiredSignatureError:
            return (
                ResponseSchema(
                    success=False,
                    message="El token ha expirado!",
                ).model_dump(),
                200,
            )
        except jwt.InvalidTokenError:
            return (
                ResponseSchema(
                    success=False,
                    message="No es válido el token!",
                ).model_dump(),
                200,
            )
        # Entrega de resultado Favorable
        return (
            ResponseSchema(
                success=True,
                message="Token válido!",
            ).model_dump(),
            200,
        )
