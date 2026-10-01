-- 2026-10-01 Añadir campo nuevo 'nombre' en tabla de `api_keys`
ALTER TABLE api_keys ADD COLUMN nombre VARCHAR(128) NOT NULL DEFAULT '';
