"""
Alimentar Usuarios
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

import click
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from lib.pwgen import generar_contrasena
from lib.safe_string import safe_email, safe_string
from tauro.blueprints.usuarios.models import Usuario
from tauro.extensions import pwd_context

USUARIOS_CSV = "seed/usuarios_roles.csv"


def alimentar_usuarios():
    """Alimentar Usuarios"""
    ruta = Path(USUARIOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando usuarios: ", nl=False)
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            # Si usuario_id NO es consecutivo, se inserta un usuario "NO EXISTE"
            while True:
                contador += 1
                usuario_id = int(row["usuario_id"])
                if usuario_id == contador:
                    break
                Usuario(
                    email=f"no-existe-{contador}@server.com",
                    nombres="NO EXISTE",
                    apellido_paterno="",
                    apellido_materno="",
                    estatus="B",
                    contrasena=pwd_context.hash(generar_contrasena()),
                ).save()
                click.echo(click.style("0", fg="blue"), nl=False)
            email = safe_email(row["email"])
            nombres = safe_string(row["nombres"], save_enie=True)
            apellido_paterno = safe_string(row["apellido_paterno"], save_enie=True)
            apellido_materno = safe_string(row["apellido_materno"], save_enie=True)
            estatus = row["estatus"]
            Usuario(
                email=email,
                nombres=nombres,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                estatus=estatus,
                contrasena=pwd_context.hash(generar_contrasena()),
            ).save()
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} usuarios alimentados.", fg="green"))
