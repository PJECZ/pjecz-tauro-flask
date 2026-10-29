#!/bin/sh
#
# Restablecer la ventanilla de los Usuarios
# Desactivar los turnos-tipos de los Usuarios
#
# Guardar archivo en: /home/pjecz-tauro/.local/bin/cli-turnos.sh
# Crea un directorio en: /home/pjecz-tauro/logs/
#
# Agregar con 'crontab -e' para ejecutar todos los días a las 01:15:00 AM
## Cancelar todos los turnos pasados que no fueron atentidos
# 15 01 * * * /home/pjecz-tauro/.local/bin/cli-turnos.sh >> /home/pjecz-tauro/logs/cli-turnos.log 2>&1
#

# Cambiar de directorio
cd $HOME/github/PJECZ/pjecz-tauro-flask

# Definir la variable de entorno PYTHONPATH
export PYTHONPATH=$(pwd)

# Ejecutar app para Cancelar turnos pasados
echo -n "[$(date "+%Y-%m-%d %H:%M:%S")] " && .venv/bin/python3 cli/app.py turnos cancelar-turnos-pasados