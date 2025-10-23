-- Script: normalizar_estados.sql
-- Objetivo: Normalizar estados de reservas al conjunto valido ('confirmada','cancelada','ocupada')
-- y liberar habitaciones sin reservas vigentes/activas.

START TRANSACTION;

-- 1) Mapear estados fuera del enum a valores validos
-- 'finalizada' -> 'cancelada'
UPDATE reservas
SET estado = 'cancelada'
WHERE estado = 'finalizada';

-- 'no confirmada' -> 'confirmada'
UPDATE reservas
SET estado = 'confirmada'
WHERE estado = 'no confirmada';

-- 2) Corregir estados vacios o nulos
UPDATE reservas
SET estado = 'confirmada'
WHERE estado IS NULL OR estado = '';

-- 3) Blindaje: cualquier otro valor no permitido pasa a 'confirmada'
UPDATE reservas
SET estado = 'confirmada'
WHERE estado NOT IN ('confirmada','cancelada','ocupada');

-- 4) Sincronizar habitaciones: liberar si no tienen reservas confirmadas u ocupadas vigentes
UPDATE habitaciones h
LEFT JOIN (
  SELECT DISTINCT id_habitacion
  FROM reservas
  WHERE estado IN ('confirmada','ocupada')
    AND fecha_salida >= NOW()
) r ON r.id_habitacion = h.id
SET h.estado = 'disponible'
WHERE r.id_habitacion IS NULL
  AND h.estado <> 'disponible';

COMMIT;

-- Verificacion
SELECT estado, COUNT(*) AS cantidad
FROM reservas
GROUP BY estado
ORDER BY estado;

SELECT estado, COUNT(*) AS cantidad
FROM habitaciones
GROUP BY estado
ORDER BY estado;
