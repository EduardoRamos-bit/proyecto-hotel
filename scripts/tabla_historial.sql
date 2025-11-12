CREATE TABLE historial_reservas (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_reserva INT,
    id_cliente INT,
    id_habitacion INT,
    fecha_entrada DATETIME,
    fecha_salida DATETIME,
    estado VARCHAR(50),
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    numero_habitacion VARCHAR(20),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE `historial reservas` (
  `id` int(11) NOT NULL,
  `id_cliente` int(11) NOT NULL,
  `id_habitacion` int(11) NOT NULL,
  `fecha_entrada` datetime NOT NULL,
  `fecha_salida` datetime NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `monto_anticipo` decimal(10,2) DEFAULT NULL,
  `porcentaje_anticipo` decimal(5,2) DEFAULT NULL,
  `estado` enum('confirmada','cancelada','ocupada') DEFAULT 'confirmada',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;