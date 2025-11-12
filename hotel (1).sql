-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 07-11-2025 a las 00:03:14
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `hotel`
--

DELIMITER $$
--
-- Procedimientos
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_crear_anticipo` (IN `p_id_reserva` INT, IN `p_porcentaje` DECIMAL(5,2))   BEGIN
    DECLARE v_monto_total DECIMAL(10,2);
    DECLARE v_monto_anticipo DECIMAL(10,2);
    DECLARE v_monto_restante DECIMAL(10,2);
    
    SELECT monto INTO v_monto_total FROM reservas WHERE id = p_id_reserva;
    SET v_monto_anticipo = (v_monto_total * p_porcentaje) / 100;
    SET v_monto_restante = v_monto_total - v_monto_anticipo;
    
    INSERT INTO anticipos (id_reserva, monto_total, porcentaje_anticipo, monto_anticipo, monto_restante)
    VALUES (p_id_reserva, v_monto_total, p_porcentaje, v_monto_anticipo, v_monto_restante);
    
    UPDATE reservas 
    SET monto_anticipo = v_monto_anticipo, 
        porcentaje_anticipo = p_porcentaje
    WHERE id = p_id_reserva;
    
    SELECT v_monto_total as monto_total, v_monto_anticipo as monto_anticipo, v_monto_restante as monto_restante;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_estadisticas_anticipos` ()   BEGIN
    SELECT 
        COUNT(*) as total_reservas,
        SUM(monto) as total_facturado,
        SUM(COALESCE(monto_anticipo, 0)) as total_anticipos,
        SUM(monto - COALESCE(monto_anticipo, 0)) as total_pendiente,
        AVG(COALESCE(porcentaje_anticipo, 0)) as porcentaje_promedio
    FROM reservas 
    WHERE estado = 'confirmada';
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `acompanantes`
--

CREATE TABLE `acompanantes` (
  `id` int(11) NOT NULL,
  `id_reserva` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `dni` varchar(30) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `acompanantes`
--

INSERT INTO `acompanantes` (`id`, `id_reserva`, `nombre`, `dni`, `created_at`) VALUES
(1, 7, 'PEPITO', '23456767', '2025-10-21 14:10:29'),
(2, 7, 'MARIA', '2334567', '2025-10-21 14:10:29'),
(3, 9, 'Marisa', '45353634', '2025-10-22 00:16:04'),
(4, 14, 'PEPITO', '45353634', '2025-10-22 15:10:04'),
(5, 15, 'Marisa', '23456767', '2025-10-22 22:44:26'),
(6, 19, 'PEPITO', '45353634', '2025-10-23 13:40:06'),
(7, 19, 'MARIA', '2334567', '2025-10-23 13:40:06');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `admins`
--

CREATE TABLE `admins` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `admins`
--

INSERT INTO `admins` (`id`, `username`, `password`, `created_at`) VALUES
(1, 'EDUARDO RAMOS', '12345', '2025-09-19 00:04:03'),
(2, 'JUAN PUCHETA', '12345', '2025-09-19 00:04:03'),
(3, 'ADMIN', 'admin123', '2025-09-19 00:04:03');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `anticipos`
--

CREATE TABLE `anticipos` (
  `id` int(11) NOT NULL,
  `id_reserva` int(11) NOT NULL,
  `monto_total` decimal(10,2) NOT NULL,
  `porcentaje_anticipo` decimal(5,2) NOT NULL,
  `monto_anticipo` decimal(10,2) NOT NULL,
  `monto_restante` decimal(10,2) NOT NULL,
  `fecha_anticipo` timestamp NOT NULL DEFAULT current_timestamp(),
  `estado` enum('pendiente','pagado','parcial') DEFAULT 'pendiente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `anticipos`
--

INSERT INTO `anticipos` (`id`, `id_reserva`, `monto_total`, `porcentaje_anticipo`, `monto_anticipo`, `monto_restante`, `fecha_anticipo`, `estado`) VALUES
(4, 2, 75000.00, 30.00, 22500.00, 52500.00, '2025-09-19 00:21:47', 'pendiente'),
(5, 4, 35000.00, 30.00, 10500.00, 24500.00, '2025-09-19 00:35:55', 'pendiente'),
(6, 5, 135000.00, 30.00, 40500.00, 94500.00, '2025-10-07 23:46:16', 'pendiente'),
(7, 6, 50000.00, 50.00, 25000.00, 25000.00, '2025-10-08 23:10:08', 'pendiente'),
(8, 7, 150000.00, 30.00, 45000.00, 105000.00, '2025-10-21 14:09:45', 'pendiente'),
(9, 8, 45000.00, 30.00, 13500.00, 31500.00, '2025-10-21 14:12:36', 'pendiente'),
(10, 9, 45000.00, 30.00, 13500.00, 31500.00, '2025-10-22 00:15:43', 'pendiente'),
(11, 10, 25000.00, 30.00, 7500.00, 17500.00, '2025-10-22 00:40:36', 'pendiente'),
(12, 11, 40000.00, 0.00, 0.00, 40000.00, '2025-10-22 13:56:25', 'pendiente'),
(13, 12, 40000.00, 30.00, 12000.00, 28000.00, '2025-10-22 14:12:49', 'pendiente'),
(14, 13, 45000.00, 30.00, 13500.00, 31500.00, '2025-10-22 14:44:37', 'pendiente'),
(15, 14, 45000.00, 30.00, 13500.00, 31500.00, '2025-10-22 15:09:50', 'pendiente'),
(16, 15, 40000.00, 30.00, 12000.00, 28000.00, '2025-10-22 22:43:11', 'pendiente'),
(17, 16, 40000.00, 30.00, 12000.00, 28000.00, '2025-10-22 23:20:52', 'pendiente'),
(18, 17, 50000.00, 30.00, 15000.00, 35000.00, '2025-10-23 00:35:11', 'pendiente'),
(19, 18, 50000.00, 30.00, 15000.00, 35000.00, '2025-10-23 13:19:57', 'pendiente'),
(20, 19, 45000.00, 30.00, 13500.00, 31500.00, '2025-10-23 13:39:53', 'pendiente'),
(21, 20, 25000.00, 30.00, 7500.00, 17500.00, '2025-10-29 00:36:00', 'pendiente'),
(22, 21, 25000.00, 30.00, 7500.00, 17500.00, '2025-10-29 23:42:40', 'pendiente'),
(23, 22, 25000.00, 30.00, 7500.00, 17500.00, '2025-10-29 23:44:03', 'pendiente'),
(24, 23, 25000.00, 30.00, 7500.00, 17500.00, '2025-10-29 23:49:05', 'pendiente'),
(25, 24, 180000.00, 30.00, 54000.00, 126000.00, '2025-10-30 14:07:43', 'pendiente'),
(28, 27, 90000.00, 30.00, 27000.00, 63000.00, '2025-11-03 23:59:10', 'pendiente');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `id_cliente` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `apellido` varchar(50) NOT NULL,
  `dni_pasaporte_cpf` varchar(30) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `direccion` varchar(100) DEFAULT NULL,
  `fecha_registro` date DEFAULT curdate(),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `clientes`
--

INSERT INTO `clientes` (`id_cliente`, `nombre`, `apellido`, `dni_pasaporte_cpf`, `telefono`, `email`, `direccion`, `fecha_registro`, `created_at`) VALUES
(1, 'Eduardo A.', 'Ramos', '23456765', '3772651009', 'eduardor221193@gmail.com', 'Av Belgrano 2087', '2025-09-18', '2025-09-19 00:11:03'),
(2, 'Eduardo A.', 'Ramos', '56347623', '3772564312', 'eduardor221193@gmail.com', 'Av Belgrano 2087', '2025-09-18', '2025-09-19 00:20:55'),
(3, 'Eduardo A.', 'Ramos', '32543654', '3772400195', 'eduardor221193@gmail.com', 'Av Belgrano 2087', '2025-09-18', '2025-09-19 00:32:41'),
(4, 'Nacho', 'Piquet', '8798546535', '98687553453', 'nacho_1@gmail.com', 'barrio 100 mzn z casa 16', '2025-10-07', '2025-10-07 23:45:07'),
(5, 'Luciano', 'Gomez', '98768657656', '7687587648', 'eduardor221193@gmail.com', 'Barrio 255 mzn n casa 17', '2025-10-08', '2025-10-08 22:43:34'),
(6, 'Eduardo A.', 'Ramos', '6787654', '3772589812', 'eduardor221193@gmail.com', 'CHUBUT', '2025-10-08', '2025-10-08 23:08:54'),
(7, 'Nacho', 'Piquet', '7675845', '08459868', 'eduardor221193@gmail.com', 'Barrio 100 viv', '2025-10-16', '2025-10-16 20:44:02'),
(8, 'Eduardo A.', 'Ramos', '87592385793', '34537459', 'eduardor221193@gmail.com', 'Av Belgrano 2087', '2025-10-20', '2025-10-20 21:26:17'),
(9, 'Eduardo A.', 'Ramos', '8763456', '54667889', 'eduardor221193@gmail.com', 'Av Belgrano 2087', '2025-10-20', '2025-10-21 00:56:01'),
(10, 'Eduardo A.', 'Ramos', '5544336', '4564574574', 'eduardor221193@gmail.com', 'Av Belgrano 2087', '2025-10-20', '2025-10-21 01:06:26'),
(11, 'Jorge', 'Ramos', '4455667', '336678585685', 'dsgsdg@jhgasd', 'catamaraca', '2025-10-21', '2025-10-21 13:59:58'),
(12, 'Luciano', 'Gomez', '4433876', '665577843', 'hgsadh@cjhs', 'Chubut', '2025-10-21', '2025-10-22 00:14:40'),
(13, 'Eduardo A.', 'Ramos', '5566778', '66554433', 'eduardor221193@gmail.com', 'Av Belgrano 2087', '2025-10-21', '2025-10-22 00:56:42'),
(14, 'Graciela', 'Escobar', '4355675', '8793453', 'jksdfh@hsad', 'santa fe', '2025-10-22', '2025-10-22 13:55:50'),
(15, 'Nicolas', 'Percara', '36898765', '3772 439004', 'eduardor221193@gmail.com', 'barrio facundo quiroga', '2025-10-30', '2025-10-30 14:06:10');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `habitaciones`
--

CREATE TABLE `habitaciones` (
  `id` int(11) NOT NULL,
  `numero_habitacion` varchar(10) NOT NULL,
  `tipo` enum('individual','doble','suite') DEFAULT 'suite',
  `precio_por_noche` decimal(10,2) NOT NULL,
  `cantidad_camas` int(11) DEFAULT 1,
  `estado` enum('disponible','ocupada','mantenimiento') DEFAULT 'disponible',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ;

--
-- Volcado de datos para la tabla `habitaciones`
--

INSERT INTO `habitaciones` (`id`, `numero_habitacion`, `tipo`, `precio_por_noche`, `cantidad_camas`, `estado`, `created_at`) VALUES
(1, '01', 'suite', 25000.00, 1, 'ocupada', '2025-09-19 00:10:18'),
(2, '02', 'suite', 25000.00, 4, 'ocupada', '2025-09-19 00:10:18'),
(3, '03', 'suite', 35000.00, 5, 'ocupada', '2025-09-19 00:10:18'),
(4, '04', 'suite', 35000.00, 4, 'disponible', '2025-09-19 00:10:18'),
(5, '05', 'suite', 50000.00, 3, 'disponible', '2025-09-19 00:10:18'),
(6, '06', 'suite', 50000.00, 4, 'disponible', '2025-09-19 00:10:18'),
(7, '07', 'suite', 40000.00, 3, 'ocupada', '2025-09-19 00:10:18'),
(8, '08', 'suite', 40000.00, 4, 'disponible', '2025-09-19 00:10:18'),
(9, '09', 'suite', 45000.00, 3, 'ocupada', '2025-09-19 00:10:18'),
(10, '10', 'suite', 45000.00, 1, 'mantenimiento', '2025-09-19 00:10:18');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historial_reservas`
--

CREATE TABLE `historial_reservas` (
  `id` int(11) DEFAULT NULL,
  `fecha_entrada` datetime DEFAULT NULL,
  `fecha_salida` datetime DEFAULT NULL,
  `monto_total` decimal(10,2) DEFAULT NULL,
  `monto_anticipo` decimal(10,2) DEFAULT NULL,
  `porcentaje_anticipo` decimal(5,2) DEFAULT NULL,
  `monto_restante` decimal(11,2) DEFAULT NULL,
  `estado_reserva` enum('confirmada','cancelada','ocupada') DEFAULT NULL,
  `nombre` varchar(50) DEFAULT NULL,
  `apellido` varchar(50) DEFAULT NULL,
  `dni_pasaporte_cpf` varchar(30) DEFAULT NULL,
  `numero_habitacion` varchar(10) DEFAULT NULL,
  `tipo_habitacion` enum('individual','doble','suite') DEFAULT NULL,
  `dias_estadia` int(7) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pagos`
--

CREATE TABLE `pagos` (
  `id` int(11) NOT NULL,
  `id_reserva` int(11) DEFAULT NULL,
  `monto` decimal(10,2) DEFAULT NULL,
  `fecha_pago` date DEFAULT NULL,
  `metodo_pago` enum('efectivo','tarjeta','transferencia') DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pagos`
--

INSERT INTO `pagos` (`id`, `id_reserva`, `monto`, `fecha_pago`, `metodo_pago`, `created_at`) VALUES
(1, 11, 0.00, '2025-10-22', 'efectivo', '2025-10-22 13:56:25'),
(2, 12, 12000.00, '2025-10-22', 'tarjeta', '2025-10-22 14:12:49'),
(3, 13, 13500.00, '2025-10-22', 'tarjeta', '2025-10-22 14:44:37'),
(4, 14, 13500.00, '2025-10-22', 'efectivo', '2025-10-22 15:09:50'),
(5, 15, 12000.00, '2025-10-22', 'efectivo', '2025-10-22 22:43:11'),
(6, 16, 12000.00, '2025-10-22', 'efectivo', '2025-10-22 23:20:52'),
(7, 17, 15000.00, '2025-10-22', 'tarjeta', '2025-10-23 00:35:11'),
(8, 18, 15000.00, '2025-10-23', 'efectivo', '2025-10-23 13:19:57'),
(9, 19, 13500.00, '2025-10-23', 'efectivo', '2025-10-23 13:39:53'),
(10, 20, 7500.00, '2025-10-28', 'efectivo', '2025-10-29 00:36:00'),
(11, 21, 7500.00, '2025-10-29', 'efectivo', '2025-10-29 23:42:40'),
(12, 22, 7500.00, '2025-10-29', 'efectivo', '2025-10-29 23:44:03'),
(13, 23, 7500.00, '2025-10-29', 'efectivo', '2025-10-29 23:49:05'),
(14, 24, 54000.00, '2025-10-30', 'transferencia', '2025-10-30 14:07:43'),
(17, 27, 27000.00, '2025-11-03', 'efectivo', '2025-11-03 23:59:10');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reservas`
--

CREATE TABLE `reservas` (
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

--
-- Volcado de datos para la tabla `reservas`
--

INSERT INTO `reservas` (`id`, `id_cliente`, `id_habitacion`, `fecha_entrada`, `fecha_salida`, `monto`, `monto_anticipo`, `porcentaje_anticipo`, `estado`, `created_at`) VALUES
(1, 1, 5, '2025-09-19 10:00:00', '2025-09-21 10:00:00', 100000.00, NULL, NULL, 'cancelada', '2025-09-19 00:13:01'),
(2, 2, 2, '2025-09-18 22:30:00', '2025-09-21 22:30:00', 75000.00, 22500.00, 30.00, 'cancelada', '2025-09-19 00:21:47'),
(3, 3, 3, '2025-09-18 21:34:00', '2025-09-19 21:34:00', 35000.00, NULL, NULL, 'cancelada', '2025-09-19 00:33:18'),
(4, 3, 4, '2025-09-18 21:37:00', '2025-09-19 21:40:00', 35000.00, 10500.00, 30.00, 'cancelada', '2025-09-19 00:35:55'),
(5, 4, 10, '2025-10-07 22:00:00', '2025-10-10 22:00:00', 135000.00, 40500.00, 30.00, 'cancelada', '2025-10-07 23:46:16'),
(6, 6, 1, '2025-10-08 22:08:00', '2025-10-10 22:09:00', 50000.00, 25000.00, 50.00, 'cancelada', '2025-10-08 23:10:08'),
(7, 1, 6, '2025-10-21 12:00:00', '2025-10-24 12:00:00', 150000.00, 45000.00, 30.00, 'cancelada', '2025-10-21 14:09:44'),
(8, 11, 10, '2025-10-21 11:15:00', '2025-10-21 11:20:00', 45000.00, 13500.00, 30.00, 'cancelada', '2025-10-21 14:12:36'),
(9, 12, 9, '2025-10-21 23:00:00', '2025-10-22 23:30:00', 45000.00, 13500.00, 30.00, 'cancelada', '2025-10-22 00:15:43'),
(10, 1, 1, '2025-10-22 21:34:00', '2025-10-23 21:34:00', 25000.00, 7500.00, 30.00, 'cancelada', '2025-10-22 00:40:36'),
(11, 14, 7, '2025-10-22 12:55:00', '2025-10-23 12:55:00', 40000.00, 0.00, 0.00, 'cancelada', '2025-10-22 13:56:25'),
(12, 1, 8, '2025-10-22 14:12:00', '2025-10-23 14:12:00', 40000.00, 12000.00, 30.00, 'cancelada', '2025-10-22 14:12:49'),
(13, 1, 10, '2025-10-22 12:44:00', '2025-10-23 12:44:00', 45000.00, 13500.00, 30.00, 'cancelada', '2025-10-22 14:44:37'),
(14, 2, 9, '2025-10-23 12:09:00', '2025-10-23 14:09:00', 45000.00, 13500.00, 30.00, 'cancelada', '2025-10-22 15:09:50'),
(15, 7, 7, '2025-10-22 20:42:00', '2025-10-23 20:42:00', 40000.00, 12000.00, 30.00, 'cancelada', '2025-10-22 22:43:11'),
(16, 12, 8, '2025-10-22 22:20:00', '2025-10-23 22:20:00', 40000.00, 12000.00, 30.00, 'cancelada', '2025-10-22 23:20:52'),
(17, 1, 6, '2025-10-22 23:34:00', '2025-10-23 23:34:00', 50000.00, 15000.00, 30.00, 'cancelada', '2025-10-23 00:35:11'),
(18, 4, 6, '2025-10-23 12:19:00', '2025-10-24 12:19:00', 50000.00, 15000.00, 30.00, 'cancelada', '2025-10-23 13:19:57'),
(19, 5, 10, '2025-10-23 10:41:00', '2025-10-23 10:42:00', 45000.00, 13500.00, 30.00, 'cancelada', '2025-10-23 13:39:53'),
(20, 4, 2, '2025-10-28 21:40:00', '2025-10-29 12:00:00', 25000.00, 7500.00, 30.00, 'cancelada', '2025-10-29 00:36:00'),
(21, 4, 1, '2025-10-29 20:50:00', '2025-10-29 22:30:00', 25000.00, 7500.00, 30.00, '', '2025-10-29 23:42:40'),
(22, 5, 2, '2025-10-29 23:30:00', '2025-10-30 08:30:00', 25000.00, 7500.00, 30.00, '', '2025-10-29 23:44:03'),
(23, 1, 2, '2025-10-30 12:30:00', '2025-10-31 23:30:00', 25000.00, 7500.00, 30.00, '', '2025-10-29 23:49:05'),
(24, 15, 10, '2025-10-30 12:00:00', '2025-11-03 12:00:00', 180000.00, 54000.00, 30.00, '', '2025-10-30 14:07:43'),
(27, 5, 10, '2025-11-04 20:58:00', '2025-11-06 20:58:00', 90000.00, 27000.00, 30.00, 'ocupada', '2025-11-03 23:59:10');

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `v_reservas_con_anticipos`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `v_reservas_con_anticipos` (
`id` int(11)
,`fecha_entrada` datetime
,`fecha_salida` datetime
,`monto_total` decimal(10,2)
,`monto_anticipo` decimal(10,2)
,`porcentaje_anticipo` decimal(5,2)
,`monto_restante` decimal(11,2)
,`estado_reserva` enum('confirmada','cancelada','ocupada')
,`nombre` varchar(50)
,`apellido` varchar(50)
,`dni_pasaporte_cpf` varchar(30)
,`numero_habitacion` varchar(10)
,`tipo_habitacion` enum('individual','doble','suite')
,`dias_estadia` int(7)
);

-- --------------------------------------------------------

--
-- Estructura para la vista `v_reservas_con_anticipos`
--
DROP TABLE IF EXISTS `v_reservas_con_anticipos`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_reservas_con_anticipos`  AS SELECT `r`.`id` AS `id`, `r`.`fecha_entrada` AS `fecha_entrada`, `r`.`fecha_salida` AS `fecha_salida`, `r`.`monto` AS `monto_total`, `r`.`monto_anticipo` AS `monto_anticipo`, `r`.`porcentaje_anticipo` AS `porcentaje_anticipo`, `r`.`monto`- coalesce(`r`.`monto_anticipo`,0) AS `monto_restante`, `r`.`estado` AS `estado_reserva`, `c`.`nombre` AS `nombre`, `c`.`apellido` AS `apellido`, `c`.`dni_pasaporte_cpf` AS `dni_pasaporte_cpf`, `h`.`numero_habitacion` AS `numero_habitacion`, `h`.`tipo` AS `tipo_habitacion`, to_days(`r`.`fecha_salida`) - to_days(`r`.`fecha_entrada`) AS `dias_estadia` FROM ((`reservas` `r` join `clientes` `c` on(`r`.`id_cliente` = `c`.`id_cliente`)) join `habitaciones` `h` on(`r`.`id_habitacion` = `h`.`id`)) ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `acompanantes`
--
ALTER TABLE `acompanantes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_acomp_reserva` (`id_reserva`);

--
-- Indices de la tabla `admins`
--
ALTER TABLE `admins`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indices de la tabla `anticipos`
--
ALTER TABLE `anticipos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_reserva` (`id_reserva`);

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`id_cliente`),
  ADD UNIQUE KEY `dni_pasaporte_cpf` (`dni_pasaporte_cpf`);

--
-- Indices de la tabla `habitaciones`
--
ALTER TABLE `habitaciones`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `numero_habitacion` (`numero_habitacion`);

--
-- Indices de la tabla `pagos`
--
ALTER TABLE `pagos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_reserva` (`id_reserva`);

--
-- Indices de la tabla `reservas`
--
ALTER TABLE `reservas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_cliente` (`id_cliente`),
  ADD KEY `id_habitacion` (`id_habitacion`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `acompanantes`
--
ALTER TABLE `acompanantes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT de la tabla `admins`
--
ALTER TABLE `admins`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `anticipos`
--
ALTER TABLE `anticipos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT de la tabla `clientes`
--
ALTER TABLE `clientes`
  MODIFY `id_cliente` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT de la tabla `habitaciones`
--
ALTER TABLE `habitaciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `pagos`
--
ALTER TABLE `pagos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT de la tabla `reservas`
--
ALTER TABLE `reservas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `acompanantes`
--
ALTER TABLE `acompanantes`
  ADD CONSTRAINT `fk_acomp_reserva` FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `anticipos`
--
ALTER TABLE `anticipos`
  ADD CONSTRAINT `anticipos_ibfk_1` FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `pagos`
--
ALTER TABLE `pagos`
  ADD CONSTRAINT `pagos_ibfk_1` FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `reservas`
--
ALTER TABLE `reservas`
  ADD CONSTRAINT `reservas_ibfk_1` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`) ON DELETE CASCADE,
  ADD CONSTRAINT `reservas_ibfk_2` FOREIGN KEY (`id_habitacion`) REFERENCES `habitaciones` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
