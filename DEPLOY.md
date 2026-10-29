# 📄 Procedimiento para hacer un _deploy_

> [!info] Basado en plantilla v1.1.2 (2026-10-29)

> [!TIP] NOTA:
> Recuerda que debes utilizar el **número de versión** último de entrega y la **fecha** en que se está haciendo esta entrega. En los ejemplos se utiliza la versión `v1.5.0` y una fecha ficticia del `2026-10-28`.

## 01. Comenzando el _deploy_ 🚚

1. Abre tu proyecto de desarrollo en tu rama `dev` y crea una rama llamada `deploy/v1.5.0` para indicar la última entrega a la rama. El número de versión, es el número que vas a entregar.
2. Ve al archivo `CHANGELOG` y coloca la **fecha de publicación** después del número de versión más actual. La fecha debería estar en formato: `YYYY-MM-DD`.
   **Ejemplo**: `## [1.5.0] - 2026-10-28`.
   1. Haz un búsqueda dentro del proyecto para ver si la fecha de publicación de la última versión se muestra en otra parte del proyecto, si es así también cámbiala.
3. Haz tu _commit_ con el mensaje: `subida de versión a v1.5.0`
4. Haz el **Pull Request** a la rama `dev (institucional)`. Como **título** escribe: `deploy v1.5.0` y dejo a tu críterio añadir **descripción**.
5. Haz el _merge_ del **Pull Request** enviado: `(Tu-Fork)/deploy/v1.5.0 -> (PJECZ)/dev`.

> [!Danger] No debes hacer el _PR_ a la rama `main`.

## 02. Hacer _merge_ del _deploy_ 🧶

1. Ve a la **cuenta institucional** y haz un nuevo **Pull Request** de la rama `dev -> main`.
2. Igual que antes haz el **Pull Request** de la rama `dev (institucional)`. Como **título** escribe: `deploy v1.5.0` y cómo **descripción** puede ser opcional. La entrega debe ser desde y para el **repositorio institucional** `dev -> main`.
3. Al hacer el _merge_ cambia el **título** por: `deploy v1.5.0` y cómo **descripción** añade todo el apartado del archivo `CHANGELOG` de la versión a entregar. Esto hará que en el historial GIT aparezcan los cambios efectuados en esta entrega.

## 03. Actualizar rama `dev` ♻️

Ahora la rama `main (institucional)` se encontrará adelantada de la rama `dev (institucional)`, vamos a actualizar la rama `dev`.

1. Haz un nuevo **Pull Request** dentro del **repositorio institucional** ahora de `main -> dev`. Esto hará que se actualice `dev` con los últimos cambios de `main` . Cómo **título** puedes poner: `Actualización de último deploy`. Así tu rama `dev` siempre estará más adelantada y contendrá todo lo de la rama `main`.

## 04. Añadir _tag_ de versión 🏷️

Es buena práctica tener identificados los _commits_ o _merges_ que se hicieron para generar un cambio de versión, para eso sirven los _tags_.

1. En **GitHub** en la **cuenta institucional**. En el apartado de **Code**, con la rama `main` activa. Presiona sobre la etiqueta **Tags**. _Se encuentra a la derecha del selector de ramas_.
2. En la página de **Tags** presiona sobre el botón de **Releases**, está arriba a la izquierda. Y una vez ahí, presiona el botón **Draft a new release** que se encuentra cargado a la derecha.
3. En la página de **New release**, en el _select tag_ tienes que abrirlo y presionar sobre el botón interno que está abajo para crea un **Create new tag**. Utiliza como **nombre del _tag_**: `v1.5.0`. En el _Select Target_ elige la rama `main`. Ahora como título **Release title** coloca: `v1.5.0 (2026-10-28)` y en **Release notes** pega todo el apartado del archivo `CHANGELOG` de la versión a entregar, **exceptuando el título de número de versión y fecha** (`## [1.5.0] - 2026-10-28`). Esto hará que **GitHub** lleve un registro de versiones del proyecto.
4. Ahora actualizar tus _Forks_ tanto de las ramas `main` y `dev`.
5. Baja cambios en tu equipo local.

> [!Note] NOTA:
> Si tienes instalada la extensión **Git Graph** en **VSCode** podrás ver de forma visual el _tag_ en el historial de _GIT_.

## 05. Actualizar proyecto en servidor de PRODUCCION 🤖

1. Baja cambios en el servidor de producción y efectúa las migraciones indicadas si las hay en el archivo `CHANGELOG`.
2. En el servidor de producción debes ejecutar el comando: `actualizar-proyecto-tauro` (ver [operación](docs/05-operacion-y-mantenimiento.md#-despliegue)).
3. Verifica que todo esté bien.
4. Ahora puedes comunicar al equipo que pueden bajar cambios, que actualicen sus _Forks_ en sus dos ramas `main` y `dev`.

> [!Note] NOTA:
> Si algún miembro del equipo no ve los _Tags_, puede ser que no tenga añadido el _repositorio remoto upstream_ que debe apuntar a la cuenta institucional.

---

© 2026 Poder Judicial del Estado de Coahuila de Zaragoza.
