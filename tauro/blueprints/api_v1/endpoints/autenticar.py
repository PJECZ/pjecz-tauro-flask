"""
API v1 Endpoint: Autenticar
"""

from datetime import datetime, timedelta
from functools import wraps

import jwt
import pytz
from flask import current_app, g, request
from flask_restful import Resource

from tauro.blueprints.api_v1.schemas import ResponseSchema, TokenSchema


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
                    message="Token is missing!",
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
                    message="Token has expired!",
                ).model_dump(),
                401,
            )
        except jwt.InvalidTokenError:
            return (
                ResponseSchema(
                    success=False,
                    message="Invalid token!",
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
        # Validar
        if username != "guillermo.valdes@pjecz.gob.mx" or password != "admin":
            return TokenSchema(
                success=False,
                message="Usuario o contraseña incorrectos",
            ).model_dump()
        # Generar token con PyJWT
        payload = {
            "sub": username,
            "iat": datetime.now(tz=pytz.UTC),
            "exp": datetime.now(tz=pytz.UTC) + timedelta(minutes=30),
        }
        access_token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
        # Entregar JSON
        return TokenSchema(
            success=True,
            message="Token generado",
            access_token=access_token,
            token_type="Bearer",
            expires_in=30 * 60,  # 30 minutos
            username=username,
        ).model_dump()
