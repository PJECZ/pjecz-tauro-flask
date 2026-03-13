#
# Archivo de configuración para Gunicorn, optimizado para aplicaciones Flask con Socket.io
#
# Para usarlo, ejecuta:
#   uv run gunicorn -c config/gunicorn_config.py "tauro.app:create_app()""
#

# --- Conexión y Red ---
bind = "0.0.0.0:5020"
# El timeout debe ser largo para mantener los WebSockets vivos
timeout = 300
# Ayuda a mantener las conexiones HTTP persistentes
keepalive = 2
max_requests = 500     # Reinicia el worker después de 1000 peticiones
max_requests_jitter = 50 # Evita que todos los workers reinicien al mismo tiempo
graceful_timeout = 30   # Tiempo para cerrar conexiones limpiamente

# --- LA SOLUCIÓN AL ERROR DEL EVENT LOOP ---
# Desactiva el servidor de estadísticas interno que usa asyncio
bind_stats_server = None

# --- Configuración del Worker ---
# IMPORTANTE: Usamos el worker específico de gevent para websockets
# worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"
worker_class = "gthread"

# Para Socket.io sin un servidor de mensajes externo (como Redis), 
# DEBES usar solo 1 worker para que todos los clientes se vean entre sí.
workers = 1
threads = 4
# --- Rendimiento y Estabilidad ---
# Desactiva sendfile para evitar errores de memoria en algunos entornos WSL/Linux
sendfile = False
# Evita que el worker se bloquee si hay mucha carga
worker_connections = 1000

forwarded_allow_ips = '*' # Permite que proxies (como Nginx) le pasen tráfico
secure_scheme_headers = {
	'X-FORWARDED-PROTOCOL': 'ssl',
	'X-FORWARDED-PROTO': 'https',
	'X-FORWARDED-SCHEME': 'https',
	'X-FORWARDED-SSL': 'on'
}

preload_app = True # Carga la app antes de crear hilos

# --- Logs (Para ver qué pasa en tiempo real) ---
# '-' significa que los logs saldrán directamente en tu terminal
accesslog = "-"
errorlog = "-"
loglevel = "info"