#!/bin/sh
#
# Restablecer la ubicacion de los Usuarios
# Desactivar los turnos-tipos de los Usuarios
#
# Guardar archivo en: /home/pjecz-tauro/.local/bin/cli-turnos.sh
#
# Agregar con 'crontab -e' para ejecutar todos los días a las 01:15:00 AM
#   15 1 * * * /home/pjecz-tauro/.local/bin/cli-turnos.sh > /dev/null 2>&1
#

echo "Inicia cli-turnos.sh"

# Cambiar de directorio
cd $HOME/Documentos/GitHub/PJECZ/pjecz-tauro-flask

# Definir la variable de entorno PYTHONPATH
export PYTHONPATH=$(pwd)

# Cancelar turnos pasados
.venv/bin/python3 cli/app.py turnos cancelar-turnos-pasados

echo "Termina cli-turnos.sh"