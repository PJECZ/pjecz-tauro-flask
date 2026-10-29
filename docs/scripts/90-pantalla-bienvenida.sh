# === Pantalla de bienvenida ===
# Listado de variables y comandos personalizados cargados para la sesión
# Definición de colores
AZUL='\e[34m'
AZUL_SUBRAYADO='\e[4;34m'
AMARILLO='\e[33m'
VERDE='\e[32m'
ROJO='\e[31m'
RESET='\e[0m'

# Banner Titulo
# Degradado Azul para título de DESARROLLO
figlet -d ~/.figlet -f "ANSI Shadow" TAURO | awk '{printf "\033[38;2;%d;%d;%dm%s\033[0m\n", 170-NR*25, 210-NR*25, 255-NR*8, $0}'

# Desarrollo
echo -ne "${AZUL}"
echo -e "============================================"
echo -e "===                 💻                   ==="
echo -e "=== BIENVENIDO AL SISTEMA-TAURO (TURNOS) ==="
echo -e "===   EN CARRANZA (SERVIDOR-DESAROLLO)   ==="
echo -e "===                 💻                   ==="
echo -e "============================================"
echo -e "${RESET}"
# Producción
echo -ne "${ROJO}"
echo -e "============================================"
echo -e "===                ⚠️⚠️⚠️                ==="
echo -e "=== BIENVENIDO AL SISTEMA-TAURO (TURNOS) ==="
echo -e "===    EN VILLA (SERVIDOR-PRODUCCION)    ==="
echo -e "===                ⚠️⚠️⚠️                ==="
echo -e "============================================"
echo -e "${RESET}"

echo -e "${AZUL}===[ DATOS DE LA BD ]===${RESET}"
echo -e "${AMARILLO}Base de Datos:${RESET} $PGVERSION"
echo -e "${AMARILLO}Nombre de BD:${RESET} $PGDATABASE"

echo -e "\n${AZUL}===[ URL's DE ACCESO PÚBLICO ]===${RESET}"
echo -e "${AZUL_SUBRAYADO}https://turnos.pjecz.gob.mx${RESET} <- Frontend"
echo -e "${AZUL_SUBRAYADO}https://turnos.pjecz.gob.mx/admin/${RESET} <- Backend"
echo -e "${AZUL_SUBRAYADO}https://turnos.pjecz.gob.mx/pantalla/${RESET} <- Pantalla General"
echo -e "${AZUL_SUBRAYADO}https://turnos.pjecz.gob.mx/pantalla/2${RESET} <- Pantalla por unidad"

echo -e "\n${AZUL}===[ COMANDOS PERSONALIZADOS DE MANTENIMIENTO ]===${RESET}"
echo -e "> ${AMARILLO}actualizar-proyecto-tauro${RESET}: Baja cambios de GitHub y reinicia su ejecución"
echo -e "> ${AMARILLO}cargar-tauro-flask${RESET}: Te lleva al directorio del proyecto y te carga el entorno virtual"
echo -e "> ${AMARILLO}cargar-tauro-reactjs${RESET}: Te lleva al directorio del proyecto"
echo -e "> ${AMARILLO}comandos${RESET}: Vuelve a mostrar esta pantalla${RESET}"
echo -e "> ${AMARILLO}respaldar-bd.sh${RESET}: Crea un respaldo de la Base de Datos de este momento y lo guarda en un archivo dentro del directorio: ${VERDE}'${HOME}/respaldos_bd/'${RESET}"
echo -e "> ${AMARILLO}restaurar-bd-desde-respaldo.sh [archivo_bd_de_respaldo.backup]${RESET}: Restablece la Base de Datos desde un archivo de respaldo indicado.${RESET} El archivo de respaldo indicado se encuentra dentro del direcotorio: ${VERDE}'${HOME}/respaldos_bd/'${RESET}"


echo -e "\n${VERDE}===[ COMANDOS PERSONALIZADOS DE ACCIÓN PARA ESTE PROYECTO ]===${RESET}"
echo -e "> ${AMARILLO}cli-turnos${RESET}: Cancela todos los turnos pendientes de los días anterior a hoy"
echo -e "> ${AMARILLO}cli-usuarios${RESET}: Quita la asignación de ventanillas de los usuarios que atienden al público"

echo -e "${RESET}"