"""
Autenticar API Key v1 Endpoints

This module provides the endpoints for authenticating users via API keys.

- Take the api key from the request header X-Api-Key
- Validate the API key against the database, querying the APIKey model.
- With a decorator, check if the API key is valid and active.
"""

from functools import wraps

from flask import g, request

from tauro.blueprints.api_v1.schemas import ResponseSchema
from tauro.blueprints.api_keys.models import APIKey


def api_key_required(f):
    """
    Checks for 'X-Api-Key' in request headers, validates it against the
    APIKey model, and ensures the key is active.
    If valid, stores the APIKey object in flask.g.api_key.
    Otherwise, returns a ResponseSchema object with the error details.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        # Get the API key from the request header
        api_key_value = request.headers.get("X-Api-Key")
        if not api_key_value:
            return (ResponseSchema(success=False, message="Falta el API key", status_code=401).model_dump(), 401)

        # Validates it against the APIKey model
        api_key = APIKey.query.filter_by(api_key=api_key_value).filter_by(estatus="A").first()
        if api_key is None:
            return (
                ResponseSchema(success=False, message="El API key no es válido o no existe", status_code=401).model_dump(),
                401,
            )

        # Si el API key esta deshabilitado
        if not api_key.es_activo:
            return (ResponseSchema(success=False, message="El API key está deshabilitado", status_code=403).model_dump(), 403)

        # Store the APIKey object for use in the endpoint
        g.api_key = api_key
        return f(*args, **kwargs)

    return decorated
