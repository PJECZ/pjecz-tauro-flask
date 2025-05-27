"""
CLI Usuarios

- mostrar_api_key: Mostrar la API Key de un usuario
- nueva_api_key: Nueva API Key
- nueva_contrasena: Nueva contraseña
"""

import sys
from datetime import datetime, timedelta

import click

from lib.pwgen import generar_api_key
from tauro.app import create_app
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.ventanillas.models import Ventanilla
from tauro.blueprints.usuarios_turnos_tipos.models import UsuarioTurnoTipo
from tauro.extensions import database, pwd_context

app = create_app()
app.app_context().push()
database.app = app


@click.group()
def cli():
    """Usuarios"""


@click.command()
@click.argument("email", type=str)
def mostrar_api_key(email):
    """Mostrar la API Key de un usuario"""
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario is None:
        click.echo(f"ERROR: No existe el e-mail {email} en usuarios")
        sys.exit(1)
    click.echo(f"Usuario: {usuario.email}")
    click.echo(f"API key: {usuario.api_key}")
    click.echo(f"Expira:  {usuario.api_key_expiracion.strftime('%Y-%m-%d')}")


@click.command()
@click.argument("email", type=str)
@click.option("--dias", default=90, help="Cantidad de días para expirar la API Key")
def nueva_api_key(email, dias):
    """Nueva API Key"""
    usuario = Usuario.find_by_identity(email)
    if usuario is None:
        click.echo(f"No existe el e-mail {email} en usuarios")
        return
    api_key = generar_api_key(usuario.id, usuario.email)
    api_key_expiracion = datetime.now() + timedelta(days=dias)
    usuario.api_key = api_key
    usuario.api_key_expiracion = api_key_expiracion
    usuario.save()
    click.echo("Nueva API key")
    click.echo(f"Usuario: {usuario.email}")
    click.echo(f"API key: {usuario.api_key}")
    click.echo(f"Expira:  {usuario.api_key_expiracion.strftime('%Y-%m-%d')}")


@click.command()
@click.argument("email", type=str)
def nueva_contrasena(email):
    """Nueva contraseña"""
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario is None:
        click.echo(f"ERROR: No existe el e-mail {email} en usuarios")
        sys.exit(1)
    contrasena_1 = input("Contraseña: ")
    contrasena_2 = input("De nuevo la misma contraseña: ")
    if contrasena_1 != contrasena_2:
        click.echo("ERROR: No son iguales las contraseñas. Por favor intente de nuevo.")
        sys.exit(1)
    usuario.contrasena = pwd_context.hash(contrasena_1.strip())
    usuario.save()
    click.echo(f"Se ha cambiado la contraseña de {email} en usuarios")


@click.command()
def restablecer_ventanilla():
    """Asignar la Ventanilla NO DEFINIDO a todos los usuarios"""

    # Consultar cual es la ventanilla NO DEFINIDO
    ventanilla_nd = Ventanilla.query.filter_by(nombre="NO DEFINIDO").first()
    if ventanilla_nd is None:
        click.echo("ERROR: No existe la ventanilla NO DEFINIDO")
        sys.exit(1)

    # Contador
    contador = 0

    # Consultar todos los usuarios
    usuarios = Usuario.query.all()
    for usuario in usuarios:
        if usuario.ventanilla_id != ventanilla_nd.id:
            usuario.ventanilla_id = ventanilla_nd.id
            usuario.save()
            contador += 1

    # Mensaje de resultado
    click.echo(f"Se han restablecido las ventanillas de {contador} usuarios")


@click.command()
def restablecer_turnos_tipos():
    """Se desactivan todos los turnos_tipos que tengan los usuarios"""

    # Contador
    contador = 0

    # Consultar todos los usuarios-turnos_tipos
    usuarios_turnos_tipos = UsuarioTurnoTipo.query.filter_by(es_activo=True).all()
    for usuario_turnos_tipos in usuarios_turnos_tipos:
        usuario_turnos_tipos.es_activo = False
        usuario_turnos_tipos.save()
        contador += 1

    # Mensaje de resultado
    click.echo(f"Se han desactivado los tipos de turnos que atienden {contador} usuarios")


cli.add_command(mostrar_api_key)
cli.add_command(nueva_api_key)
cli.add_command(nueva_contrasena)
cli.add_command(restablecer_ventanilla)
cli.add_command(restablecer_turnos_tipos)
