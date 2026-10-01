-- 2026-10-01 Añadir campo nuevo 'nombre' en tabla de `api_keys`, con valores únicos para `nombre` y `api_key`

-- Añadir la columna permitiendo nulos mientras se llena
ALTER TABLE api_keys ADD COLUMN nombre VARCHAR(128);

-- Llenar los registros existentes con 'SIN NOMBRE 01', 'SIN NOMBRE 02', etc.
UPDATE api_keys
SET nombre = 'SIN NOMBRE ' || LPAD(numerados.numero::TEXT, 2, '0')
FROM (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS numero
    FROM api_keys
) AS numerados
WHERE api_keys.id = numerados.id;

-- Ya con todos llenos, volverla obligatoria
ALTER TABLE api_keys ALTER COLUMN nombre SET NOT NULL;

-- Que `nombre` y `api_key` no se repitan
-- (si falla por duplicados en `api_key`, corregir esos registros y volver a ejecutar solo esta parte)
ALTER TABLE api_keys ADD CONSTRAINT uq_api_keys_nombre UNIQUE (nombre);
ALTER TABLE api_keys ADD CONSTRAINT uq_api_keys_api_key UNIQUE (api_key);
