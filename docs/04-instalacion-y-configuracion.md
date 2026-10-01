# ⚙️ Instalación y configuración

## Requisitos

- Debian 13 (servidor) o Linux/WSL (desarrollo)
- Python ≥ 3.14 (ver `pyproject.toml`) y [uv](https://docs.astral.sh/uv/)
- PostgreSQL 17
- nginx + Certbot (solo servidores con dominio público)
- Node.js/npm para construir el *frontend*

## 1. Usuario del sistema (servidor)

Se ejecuta con un usuario de pocos privilegios, sin contraseña y con acceso solo por llave SSH:

```bash
sudo adduser --disabled-password --gecos "" pjecz-tauro

sudo mkdir -p /home/pjecz-tauro/.ssh
sudo nano /home/pjecz-tauro/.ssh/authorized_keys   # pega las llaves públicas autorizadas
sudo chown -R pjecz-tauro:pjecz-tauro /home/pjecz-tauro/.ssh
sudo chmod 700 /home/pjecz-tauro/.ssh
sudo chmod 600 /home/pjecz-tauro/.ssh/authorized_keys
```

## 2. Base de datos

Crea la base y un usuario propietario en PostgreSQL. Guarda la contraseña en tu gestor de contraseñas, **no en el repositorio**.

```sql
CREATE DATABASE pjecz_tauro;
CREATE USER adminpjecztauro WITH PASSWORD '<contraseña-segura>';
GRANT ALL PRIVILEGES ON DATABASE pjecz_tauro TO adminpjecztauro;
```

Después inicializa las tablas y catálogos con el CLI (`cli/app.py db inicializar`, ver [operación](05-operacion-y-mantenimiento.md)).

## 3. Variables de entorno

Copia la plantilla y completa los valores:

```bash
cp .env.example .env
```

| Variable | Descripción |
|----------|-------------|
| `FLASK_APP` | `tauro.app` |
| `FLASK_DEBUG` | `1` solo en desarrollo |
| `SECRET_KEY` | Clave de sesión. Genérala con `openssl rand -hex 24` |
| `DB_*` | Datos de conexión (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS`) |
| `SQLALCHEMY_DATABASE_URI` | `postgresql+psycopg2://usuario:contraseña@host:5432/base` |
| `SALT` | Sal de HashIDs. **Debe ser igual en todas las instancias de la API**; cambiarla invalida los IDs cifrados ya emitidos |
| `HOST` | URL pública del sistema (se usa en CORS) |
| `CORS` | Origen permitido del *frontend* |
| `TZ` | Huso horario, `America/Mexico_City` |
| `LIMITE_DE_TURNOS_LISTADOS` | Máximo de turnos mostrados en el listado |
| `VOCEADOR_API_KEY`, `VOCEADOR_API_KEY_URL` | Credenciales y URL del sistema de voceo |
| `ENVIRONMENT` | `production` evita reiniciar la base de datos y activa el prefijo |
| `PREFIX` | Prefijo de rutas (`/admin`), solo con `ENVIRONMENT=production` |

> [!CAUTION]
> El archivo `.env` está en `.gitignore`. **Nunca** lo subas ni pegues su contenido en documentación, chats o *tickets*. Si una credencial se expone, rótala.

### Frontend (`pjecz-tauro-reactjs/.env`)

```bash
REACT_APP_URL_BASE=https://<dominio>/admin/
REACT_APP_URL_BASE_SOCKET=https://<dominio>
```

```bash
npm install
npm run build      # genera build/, que nginx sirve como sitio raíz
```

## 4. Instalar el *backend*

```bash
# Producción (sin dependencias de desarrollo)
uv sync --no-dev

# Desarrollo
uv sync

# Reinstalación limpia
rm -rf .venv uv.lock && uv sync
```

## 5. Ejecutar

> [!WARNING]
> `flask run` es el servidor de desarrollo. Para producción se prefiere gunicorn; al 2026-03-20 el servidor de producción **todavía usa** el comando de desarrollo (ver [`pjecz-tauro.service`](pjecz-tauro.service)).

| Modo | Comando |
|------|---------|
| Desarrollo | `uv run flask run --host=0.0.0.0 --port=5020` |
| gunicorn (recomendado) | `uv run gunicorn --bind 127.0.0.1:5020 --workers 1 --threads 4 --timeout 0 "appserver:gunicorn_app"` |
| gunicorn con archivo | `uv run gunicorn -c config/gunicorn_config.py "tauro.app:create_app()"` |
| uvicorn | `uv run uvicorn "appserver:gunicorn_app" --host 127.0.0.1 --port 5020 --workers 1 --proxy-headers --forwarded-allow-ips="*"` |

> [!IMPORTANT]
> Usa **un solo *worker*** (`--workers 1`) por Socket.IO; el paralelismo se logra con `--threads`.

## 6. Servicio systemd

Archivo de ejemplo: [pjecz-tauro.service](pjecz-tauro.service).

```bash
sudo nano /etc/systemd/system/pjecz-tauro.service
sudo systemctl daemon-reload
sudo systemctl enable --now pjecz-tauro
sudo systemctl status pjecz-tauro
```

Línea `ExecStart` recomendada para producción:

```ini
ExecStart=/home/pjecz-tauro/.local/bin/uv run gunicorn --bind 127.0.0.1:5020 --workers 1 --threads 8 --timeout 0 appserver:gunicorn_app
```

Tras cada cambio del `.service` ejecuta `daemon-reload` y `restart`.

## 7. nginx

Archivo de ejemplo: [tauro-turnos.nginx](tauro-turnos.nginx). Define:

- `/` → *frontend* estático (`pjecz-tauro-reactjs/build`)
- `/admin/` → Flask en `localhost:5020`
- `/socket.io/` → Flask, con *upgrade* de WebSocket y tiempos largos (86400 s)
- Redirección de HTTP (80) a HTTPS

```bash
sudo nginx -t && sudo systemctl restart nginx
```

El certificado SSL se emite con Certbot.

## 8. Tareas programadas

Ver [operación y mantenimiento](05-operacion-y-mantenimiento.md#-tareas-programadas-cron).

## 🧪 Desarrollo local rápido

```bash
git clone https://github.com/PJECZ/pjecz-tauro-flask.git
cd pjecz-tauro-flask
cp .env.example .env     # edita los valores
uv sync
uv run flask run --host=0.0.0.0 --port=5020
```

Las pruebas de API están en [`tests/`](../tests) (pytest y colección Bruno; la variable `api_key` de Bruno es secreta y no se guarda en el repositorio).
