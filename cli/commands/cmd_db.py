"""
CLI Base de Datos
"""

import os
import sys

import click
from dotenv import load_dotenv

from cli.commands.alimentar_modulos import alimentar_modulos
from cli.commands.alimentar_permisos import alimentar_permisos
from cli.commands.alimentar_roles import alimentar_roles
from cli.commands.alimentar_usuarios import alimentar_usuarios
from cli.commands.alimentar_usuarios_roles import alimentar_usuarios_roles
from cli.commands.alimentar_turnos_estados import alimentar_turnos_estados
from cli.commands.alimentar_turnos_tipos import alimentar_turnos_tipos
from cli.commands.respaldar_modulos import respaldar_modulos
from cli.commands.respaldar_roles_permisos import respaldar_roles_permisos
from cli.commands.respaldar_usuarios_roles import respaldar_usuarios_roles
from cli.commands.respaldar_turnos_estados import respaldar_turnos_estados
from cli.commands.respaldar_turnos_tipos import respaldar_turnos_tipos
from tauro.app import create_app
from tauro.extensions import database

from tauro.blueprints.unidades.models import Unidad
from tauro.blueprints.ventanillas.models import Ventanilla

app = create_app()
app.app_context().push()
database.app = app

load_dotenv()  # Take environment variables from .env
DEPLOYMENT_ENVIRONMENT = os.environ.get("DEPLOYMENT_ENVIRONMENT", "develop").upper()


@click.group()
def cli():
    """Base de Datos"""


@click.command()
def inicializar():
    """Inicializar"""
    if DEPLOYMENT_ENVIRONMENT == "PRODUCTION":
        click.echo("PROHIBIDO: No se inicializa porque este es el servidor de producción.")
        sys.exit(1)
    database.drop_all()
    database.create_all()
    click.echo("Termina inicializar.")


@click.command()
def alimentar():
    """Alimentar"""
    if DEPLOYMENT_ENVIRONMENT == "PRODUCTION":
        click.echo("PROHIBIDO: No se alimenta porque este es el servidor de producción.")
        sys.exit(1)
    alimentar_modulos()
    alimentar_roles()
    alimentar_permisos()
    # Alimentar unidades y ventanillas NO DEFINIDO
    Unidad(clave="ND", nombre="NO DEFINIDO").save()
    Ventanilla(nombre="NO DEFINIDO").save()
    alimentar_usuarios()
    alimentar_usuarios_roles()
    alimentar_turnos_estados()
    alimentar_turnos_tipos()
    click.echo("Termina alimentar.")


@click.command()
@click.pass_context
def reiniciar(ctx):
    """Reiniciar ejecuta inicializar y alimentar"""
    ctx.invoke(inicializar)
    ctx.invoke(alimentar)


@click.command()
def respaldar():
    """Respaldar"""
    respaldar_modulos()
    respaldar_roles_permisos()
    respaldar_usuarios_roles()
    respaldar_turnos_estados()
    respaldar_turnos_tipos()
    click.echo("Termina respaldar.")


cli.add_command(inicializar)
cli.add_command(alimentar)
cli.add_command(reiniciar)
cli.add_command(respaldar)
