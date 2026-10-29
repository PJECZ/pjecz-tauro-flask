#!/bin/bash
# Automatización de descarga de actualizaciones de todos los proyectos pertenecientes a Tauro:
# pjecz-tauro-flask y pjecz-tauro-reactjs

# Definición de colores
AZUL='\e[1;34m'
AZUL_SUBRAYADO='\e[4;34m'
AMARILLO='\e[1;33m'
VERDE='\e[1;32m'
ROJO='\e[1;31m'
RESET='\e[0m'

actualizar-proyecto-tauro() {
	# Guardamos el directorio actual para regresar a él al terminar
	local DIR_INICIAL
	DIR_INICIAL=$(pwd)

	local ERRORES=()

	# Lista de proyectos a actualizar: "ruta|nombre|comando_post_pull"
	local PROYECTOS=(
		"/home/pjecz-tauro/github/pjecz/pjecz-tauro-flask|pjecz-tauro-flask|sudo systemctl restart pjecz-tauro.service"
		"/home/pjecz-tauro/github/pjecz/pjecz-tauro-reactjs|pjecz-tauro-reactjs|npm run build"
	)

	local ENTRADA
	for ENTRADA in "${PROYECTOS[@]}"; do
		local RUTA NOMBRE COMANDO_POST
		IFS='|' read -r RUTA NOMBRE COMANDO_POST <<< "$ENTRADA"

		echo -e "\n${AMARILLO}--- Actualizando $NOMBRE ---${RESET}"

		cd "$RUTA" || {
			echo -e "${ROJO}>> ERROR: no se pudo entrar al directorio $RUTA${RESET}"
			ERRORES+=("$NOMBRE (directorio no encontrado)")
			continue
		}

		# Capturamos salida y código de salida por separado
		local SALIDA_PULL CODIGO_PULL
		SALIDA_PULL=$(git pull 2>&1)
		CODIGO_PULL=$?
		echo "$SALIDA_PULL"

		if [[ $CODIGO_PULL -ne 0 ]]; then
			echo -e "${ROJO}>> ERROR: git pull falló en $NOMBRE${RESET}"
			echo -e "${ROJO}>> Es probable que existan cambios locales sin confirmar. Revisa con 'git status'${RESET}"
			ERRORES+=("$NOMBRE (git pull falló)")
			continue
		fi
		
		# Aunque git pull haya salido con código 0, puede quedar un archivo con
		# cambios locales sin confirmar que el pull no tocó (porque ese archivo
		# específico no cambió en el commit remoto). Lo detectamos revisando si
		# el directorio de trabajo sigue "sucio" después del pull.
		local ESTADO_LOCAL
		ESTADO_LOCAL=$(git status --porcelain)
		if [[ -n "$ESTADO_LOCAL" ]]; then
			echo -e "${ROJO}>> ERROR: quedaron cambios locales sin confirmar en $NOMBRE después del pull${RESET}"
			echo -e "${ROJO}>> Es probable que alguien haya editado un archivo directamente en el servidor. Revisa con 'git status'${RESET}"
			ERRORES+=("$NOMBRE (cambios locales sin confirmar tras el pull)")
			continue
		fi
		

		if [[ "$SALIDA_PULL" != *"Already up to date."* ]]; then
			echo ">> Cambios detectados en proyecto ($NOMBRE)"
			if [[ -n "$COMANDO_POST" ]]; then
				echo ">> Ejecutando: $COMANDO_POST"
				eval "$COMANDO_POST"
				if [[ $? -ne 0 ]]; then
					echo -e "${ROJO}>> ERROR: falló el comando posterior al pull en $NOMBRE${RESET}"
					ERRORES+=("$NOMBRE (falló $COMANDO_POST)")
				fi
			fi
		else
			echo ">> Sin cambios en $NOMBRE"
		fi
	done

	# Regresamos siempre al directorio desde donde se invocó la función
	cd "$DIR_INICIAL"

	echo ""
	if [[ ${#ERRORES[@]} -eq 0 ]]; then
		echo -e "${VERDE}¡Proceso finalizado sin errores!${RESET}"
	else
		echo -e "${ROJO}¡Proceso finalizado CON ERRORES en los siguientes proyectos!${RESET}"
		local ERROR
		for ERROR in "${ERRORES[@]}"; do
			echo -e "${ROJO}  - $ERROR${RESET}"
		done
		return 1
	fi
}