"""
Alimentar Unidades
"""

import csv
import sys
from pathlib import Path

import click

from lib.safe_string import safe_string, safe_clave
from tauro.blueprints.unidades.models import Unidad

UNIDADES_CSV = "seed/unidades.csv"


def alimentar_unidades():
    """Alimentar unidades"""
    ruta_csv = Path(UNIDADES_CSV)
    if not ruta_csv.exists():
        click.echo(f"AVISO: {ruta_csv.name} no se encontró.")
        sys.exit(1)
    if not ruta_csv.is_file():
        click.echo(f"AVISO: {ruta_csv.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando unidades: ", nl=False)
    contador = 0
    with open(ruta_csv, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            unidad_id = int(row["unidad_id"])
            clave = safe_clave(row["clave"])
            nombre = safe_string(row["nombre"], save_enie=True)
            es_activo = row["es_activo"] == "1"
            estatus = row["estatus"]
            if unidad_id != contador + 1:
                click.echo(click.style(f"  AVISO: unidad_id {unidad_id} no es consecutivo", fg="red"))
                sys.exit(1)
            Unidad(
                nombre=nombre,
                clave=clave,
                es_activo=es_activo,
                estatus=estatus,
            ).save()
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} unidades alimentadas.", fg="green"))
