-- 2026-07-08 Añadir campo nuevo 'es_voceable' en tabla de `unidades`
ALTER TABLE unidades ADD COLUMN es_voceable BOOLEAN NOT NULL DEFAULT FALSE;