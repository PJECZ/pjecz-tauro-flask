#!/bin/sh
#
# Restablecer la ventanilla de los Usuarios
# Desactivar los turnos-tipos de los Usuarios
#
# Guardar archivo en: /home/pjecz-tauro/.local/bin/cli-usuarios.sh
#
# Agregar con 'crontab -e' para ejecutar todos los días a las 01:10:00 AM
#   10 1 * * * /home/pjecz-tauro/.local/bin/cli-usuarios.sh > /dev/null 2>&1
#

# Cambiar de directorio
cd $HOME/github/PJECZ/pjecz-tauro-flask

# Definir la variable de entorno PYTHONPATH
export PYTHONPATH=$(pwd)

# Restablecer asignaciones de los usuarios
echo -n "[$(date "+%Y-%m-%d %H:%M:%S")] " && .venv/bin/python3 cli/app.py usuarios restablecer-turnos-tipos
echo -n "[$(date "+%Y-%m-%d %H:%M:%S")] " && .venv/bin/python3 cli/app.py usuarios restablecer-ventanilla
