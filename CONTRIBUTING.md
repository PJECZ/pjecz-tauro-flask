# 🚀 Guía de Contribución

¡Gracias por querer mejorar este proyecto! Para mantener el código limpio y organizado, utilizamos un flujo de trabajo basado en **Forks** y dos ramas principales: `main` (producción) y `dev` (desarrollo).

> [!info] Basado en plantilla v1.2.0 (2026-10-29)

## 🛠 Configuración Inicial

Antes de empezar, asegúrate de tener tu entorno listo:

1.  **Haz un _Fork_** del repositorio institucional a tu cuenta personal en **GitHub**.
2.  **Clona tu _Fork_** localmente (cambia `tu-usuario` por tu usuario de **GitHub**):

```bash
git clone https://github.com/tu-usuario/pjecz-tauro-flask.git
```

Este debe quedar como tu repositorio **remoto origin**.

3.  **Configura el repositorio institucional** como `upstream` para recibir actualizaciones de todos los contribuyentes:

```bash
git remote add upstream https://github.com/PJECZ/pjecz-tauro-flask.git
```

4.  **Prepara el entorno** (ver el [README](README.md) para el detalle):

```bash
cp .env.example .env      # edita con tus valores locales, nunca lo subas
uv sync                   # instala dependencias, incluidas las de desarrollo
uv run pre-commit install # activa isort, black y revisiones antes de cada commit
```

## 📈 Flujo de Trabajo (GitFlow – Simplificado)

### 1. Sincroniza tu rama `dev`

Antes de crear una nueva funcionalidad, asegúrate de tener lo último del proyecto principal:

```bash
# Cambia a la rama dev
git switch dev
# Baja cambios del proyecto principal y de tu rama dev
git pull upstream dev
```

### 2. Crea una rama para tu tarea

Usa nombres descriptivos como `mejora/nombre-mejora` o `fix/bug-sesion`:

```bash
git switch -c mejora/mi-nueva-mejora
```

> [!tip] Revisa la guía para nombrar ramas más abajo: [🌿Guía para nombres de ramas](CONTRIBUTING.md#🌿Guía%20para%20nombres%20de%20ramas)

### 3. Haz tus cambios y súbelos

> [!TIP] Cuando hagas un _commit_ utiliza la guía de _commit_ más abajo: [💬Guía para mensajes de _commit_](#💬Guía%20para%20mensajes%20de%20_commit_)

Luego, sube la rama a **tu Fork**:

```bash
git push origin mejora/mi-nueva-mejora
```

### 4. Abre un _Pull Request_ (PR)

Ve al repositorio `origin` (tu _Fork_) en **GitHub** y abre un nuevo _PR_.
Debes hacer un PR de `tu-rama -> dev (Institucional)`

- **Base:** `dev` (**¡Importante!** No envíes directamente a `main`).
- **Compare:** `tu-usuario:mejora/mi-nueva-mejora`.

## 🎨 Estilo de código

- Formato con **black** e **isort** (líneas de hasta 128 caracteres, configurado en `pyproject.toml`); `pre-commit` los aplica solo.
- Análisis con **pylint** (`uv run pylint tauro lib cli`).
- Nombres, comentarios y mensajes en **español**, igual que el resto del proyecto.
- Los módulos nuevos siguen la estructura de `tauro/blueprints/<módulo>/` (`models.py`, `views.py`, `forms.py`, `templates/`). Hay _snippets_ de VS Code en `.vscode/` para generarlos.

## 🔒 Seguridad

- **Nunca** subas `.env`, contraseñas, `SECRET_KEY`, `SALT`, API-Keys, IPs internas ni respaldos de la base de datos. Antes de cada _commit_ revisa con `git diff --staged`.
- Si una credencial se expone, avisa al equipo para rotarla; borrar el _commit_ no es suficiente.
- Para dependencias: si cambias `pyproject.toml`, ejecuta `uv lock` y **sube también `uv.lock`**.

## 📋 Reglas de Oro

- **No toques `main`:** Solo el equipo de despliegue hace _merges_ de `dev -> main`.
- **Tests:** Asegúrate de que tu código pasa los _tests_ locales (`uv run pytest`, necesitan la API en ejecución y las variables descritas en el README) antes de enviar el PR.
- **Documentación:** Si añades una funcionalidad nueva, actualiza el `CHANGELOG.md` para organizar los cambios añadidos, y de ser necesario el `README.md`. Si es algo que tiene que ver con la **lógica del negocio**, también actualiza la documentación en el directorio `docs/`.
- **Un PR por tarea:** No mezcles correcciones de errores con nuevas funcionalidades en el mismo PR.

## 🌿Guía para nombres de ramas

Buenas prácticas para nombrar las ramas de trabajo.
Recuerda que desde tu _fork_ debes hacer una nueva rama basada en la rama de desarrollo `dev`.
Debes nombrar la rama según se explica más abajo, dependiendo de lo que vayas a hacer, por ejemplo una mejora en el _login_ del sitio, la rama debe estar basada en `dev`, y se deberá llamar: `mejora/login`, y en los _commits_ ir añadiendo buenos mensajes de descripción, explicados más adelante.

| Abreviación                           | Descripción                                                                                          |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `feature/*`<br>`mejora/*`             | Nuevas funcionalidades o mejoras en algo.                                                            |
| `hotfix/*`                            | Arreglo crítico de algo, normalmente va directo a la rama `main` o de producción.                    |
| `bugfix/*`                            | Arreglo de un fallo menor, va en la rama `dev`.                                                      |
| `test/*`                              | Creación, modificación o mejora de un test.                                                          |
| `doc/*`                               | Creación, modificación o mejora en la documentación.                                                 |
| `refactor/*`                          | Código de mejora en legibilidad, funcionalidad o desempeño pero que no añade nuevas funcionalidades. |
| `design/*`<br>`style/*`<br>`diseno/*` | Mejoras en la interfaz de usuario, páginas de presentación.                                          |

Como observaras todas las abreviaciones para nombrar la rama van en **singular**, porque lo recomendable es que hagas una solo cosa para entregar.

## 💬Guía para mensajes de _commit_

Buenas prácticas para mensajes de _commit_ entendibles.

| Abreviación | Descripción                                        |
| ----------- | -------------------------------------------------- |
| `feat:`     | Nueva función o mejora.                            |
| `fix:`      | Arreglo de un _bug_.                               |
| `doc:`      | Añadido o corregida la documentación del proyecto. |
| `style:`    | Cambios en el estilo, formato, etc.                |
| `refactor:` | Refactorización del código                         |
| `test:`     | Añadido o modificado algún _test_.                 |
| `chore:`    | Tarea de mantenimiento.                            |
| `perf:`     | Mejora en el rendimiento.                          |
| `ci:`       | Cambios relacionados al CI/CD.                     |

> [!TIP] Un buen mensaje de _commit_ es corto, claro y descriptivo.

## 🚀 Despliegue a Producción

Una vez que las funciones en `dev (institucional)` son estables y han sido probadas, el administrador del proyecto realizará un _merge_ de `dev -> main` para el despliegue final.

```bash
git tag -a v1.0.0 -m "Lanzamiento versión 1.0"
git push origin v1.0.0
```

> [!Important] Para un _deploy_ en **GitHub** siga las instrucciones del documento: [DEPLOY](DEPLOY.md)

Después, en el servidor de producción se ejecuta `actualizar-proyecto-tauro` (ver [operación](docs/05-operacion-y-mantenimiento.md#-despliegue)).

---

© 2026 Poder Judicial del Estado de Coahuila de Zaragoza.
