"""
Alimentar Autoridades
"""

import csv
import sys
from pathlib import Path

import click
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from lib.safe_string import safe_clave, safe_string
from tauro.blueprints.autoridades.models import Autoridad
from tauro.blueprints.distritos.models import Distrito

AUTORIDADES_CSV = "seed/autoridades.csv"


def alimentar_autoridades():
    """Alimentar Autoridades"""
    ruta = Path(AUTORIDADES_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        sys.exit(1)
    try:
        distrito_nd = Distrito.query.filter_by(clave="ND").one()
    except (MultipleResultsFound, NoResultFound):
        click.echo("AVISO: No se encontró el distrito, materia y/o municipio 'ND'.")
        sys.exit(1)
    click.echo("Alimentando autoridades: ", nl=False)
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            # Si autoridad_id NO es consecutivo, se inserta una autoridad "NO EXISTE"
            contador += 1
            autoridad_id = int(row["autoridad_id"])
            if autoridad_id != contador:
                Autoridad(
                    distrito_id=distrito_nd.id,
                    clave=f"NE-{contador}",
                    descripcion="NO EXISTE",
                    descripcion_corta="NO EXISTE",
                    estatus="B",
                ).save()
                click.echo(click.style("!", fg="yellow"), nl=False)
                continue
            distrito_id = int(row["distrito_id"])
            clave = safe_clave(row["clave"])
            descripcion = safe_string(row["descripcion"], save_enie=True)
            descripcion_corta = safe_string(row["descripcion_corta"], save_enie=True)
            distrito = Distrito.query.get(distrito_id)
            if distrito is None:
                click.echo(click.style(f"  AVISO: distrito_id {distrito_id} no existe", fg="red"))
                sys.exit(1)
            Autoridad(
                distrito=distrito,
                clave=clave,
                descripcion=descripcion,
                descripcion_corta=descripcion_corta,
            ).save()
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} autoridades alimentadas.", fg="green"))
