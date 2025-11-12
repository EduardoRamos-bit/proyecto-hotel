-- Script para corregir errores en la base de datos hotel
-- Ejecutar este script después de importar hotel(1).sql

USE hotel;

-- 1. Agregar estado 'vencida' al enum de reservas
ALTER TABLE `reservas` 
MODIFY COLUMN `estado` ENUM('confirmada','cancelada','ocupada','vencida') DEFAULT 'confirmada';

-- 2. Corregir estructura de historial_reservas para que coincida con los inserts
DROP TABLE IF EXISTS `historial_reservas`;

CREATE TABLE `historial_reservas` (
  `id_historial` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `id_reserva` INT(11) DEFAULT NULL,
  `id_cliente` INT(11) DEFAULT NULL,
  `id_habitacion` INT(11) DEFAULT NULL,
  `fecha_entrada` DATETIME DEFAULT NULL,
  `fecha_salida` DATETIME DEFAULT NULL,
  `monto_total` DECIMAL(10,2) DEFAULT NULL,
  `monto_anticipo` DECIMAL(10,2) DEFAULT NULL,
  `porcentaje_anticipo` DECIMAL(5,2) DEFAULT NULL,
  `monto_restante` DECIMAL(10,2) DEFAULT NULL,
  `dias_estadia` INT(11) DEFAULT NULL,
  `estado` VARCHAR(50) DEFAULT NULL,
  `nombre` VARCHAR(50) DEFAULT NULL,
  `apellido` VARCHAR(50) DEFAULT NULL,
  `dni_pasaporte_cpf` VARCHAR(50) DEFAULT NULL,
  `numero_habitacion` VARCHAR(10) DEFAULT NULL,
  `tipo_habitacion` VARCHAR(50) DEFAULT NULL,
  `acompanantes_json` TEXT DEFAULT NULL,
  `fecha_registro` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY `idx_fecha_entrada` (`fecha_entrada`),
  KEY `idx_id_reserva` (`id_reserva`),
  KEY `idx_estado` (`estado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 3. Actualizar vista v_reservas_con_anticipos para incluir estado 'vencida' e IDs
DROP VIEW IF EXISTS `v_reservas_con_anticipos`;

CREATE VIEW `v_reservas_con_anticipos` AS 
SELECT 
    `r`.`id` AS `id`, 
    `r`.`id_cliente` AS `id_cliente`,
    `r`.`id_habitacion` AS `id_habitacion`,
    `r`.`fecha_entrada` AS `fecha_entrada`, 
    `r`.`fecha_salida` AS `fecha_salida`, 
    `r`.`monto` AS `monto_total`, 
    `r`.`monto_anticipo` AS `monto_anticipo`, 
    `r`.`porcentaje_anticipo` AS `porcentaje_anticipo`, 
    `r`.`monto` - COALESCE(`r`.`monto_anticipo`,0) AS `monto_restante`, 
    `r`.`estado` AS `estado_reserva`, 
    `c`.`nombre` AS `nombre`, 
    `c`.`apellido` AS `apellido`, 
    `c`.`dni_pasaporte_cpf` AS `dni_pasaporte_cpf`, 
    `h`.`numero_habitacion` AS `numero_habitacion`, 
    `h`.`tipo` AS `tipo_habitacion`, 
    DATEDIFF(`r`.`fecha_salida`, `r`.`fecha_entrada`) AS `dias_estadia` 
FROM ((`reservas` `r` 
    JOIN `clientes` `c` ON(`r`.`id_cliente` = `c`.`id_cliente`)) 
    JOIN `habitaciones` `h` ON(`r`.`id_habitacion` = `h`.`id`));

-- 4. Verificar que todas las reservas vacías tengan estado por defecto
UPDATE `reservas` 
SET `estado` = 'confirmada' 
WHERE `estado` IS NULL OR `estado` = '';

SELECT 'Base de datos corregida exitosamente' AS resultado;
