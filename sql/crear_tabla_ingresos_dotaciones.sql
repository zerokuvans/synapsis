-- Script para crear tabla ingresos_dotaciones
-- Sistema de Gestión de Ingresos de Dotaciones
-- Fecha: 2024-01-24

-- Crear tabla para registrar ingresos de dotaciones
CREATE TABLE IF NOT EXISTS ingresos_dotaciones (
    id_ingreso INT AUTO_INCREMENT PRIMARY KEY,
    tipo_elemento VARCHAR(50) NOT NULL COMMENT 'Tipo de dotación (pantalon, camisetagris, etc.)',
    cantidad INT NOT NULL COMMENT 'Cantidad ingresada',
    talla VARCHAR(10) COMMENT 'Talla del elemento (XS, S, M, L, XL, XXL)',
    numero_calzado VARCHAR(5) COMMENT 'Número de calzado (35-45)',
    proveedor VARCHAR(100) COMMENT 'Nombre del proveedor',
    fecha_ingreso DATE NOT NULL COMMENT 'Fecha de ingreso a bodega',
    observaciones TEXT COMMENT 'Observaciones adicionales',
    usuario_registro VARCHAR(50) NOT NULL COMMENT 'Usuario que registra el ingreso',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tipo_elemento (tipo_elemento),
    INDEX idx_fecha_ingreso (fecha_ingreso),
    INDEX idx_usuario_registro (usuario_registro),
    INDEX idx_talla (talla),
    INDEX idx_numero_calzado (numero_calzado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Crear vista para cálculos de stock
CREATE OR REPLACE VIEW vista_stock_dotaciones AS
SELECT 
    'pantalon' as tipo_elemento,
    COALESCE(SUM(i.cantidad), 0) as cantidad_ingresada,
    COALESCE(SUM(d.pantalon), 0) as cantidad_entregada,
    COALESCE(SUM(i.cantidad), 0) - COALESCE(SUM(d.pantalon), 0) as saldo_disponible
FROM ingresos_dotaciones i
LEFT JOIN dotaciones d ON i.tipo_elemento = 'pantalon'
WHERE i.tipo_elemento = 'pantalon'
UNION ALL
SELECT 
    'camisetagris' as tipo_elemento,
    COALESCE(SUM(i.cantidad), 0) as cantidad_ingresada,
    COALESCE(SUM(d.camisetagris), 0) as cantidad_entregada,
    COALESCE(SUM(i.cantidad), 0) - COALESCE(SUM(d.camisetagris), 0) as saldo_disponible
FROM ingresos_dotaciones i
LEFT JOIN dotaciones d ON i.tipo_elemento = 'camisetagris'
WHERE i.tipo_elemento = 'camisetagris'
UNION ALL
SELECT 
    'guerrera' as tipo_elemento,
    COALESCE(SUM(i.cantidad), 0) as cantidad_ingresada,
    COALESCE(SUM(d.guerrera), 0) as cantidad_entregada,
    COALESCE(SUM(i.cantidad), 0) - COALESCE(SUM(d.guerrera), 0) as saldo_disponible
FROM ingresos_dotaciones i
LEFT JOIN dotaciones d ON i.tipo_elemento = 'guerrera'
WHERE i.tipo_elemento = 'guerrera'
UNION ALL
SELECT 
    'camisetapolo' as tipo_elemento,
    COALESCE(SUM(i.cantidad), 0) as cantidad_ingresada,
    COALESCE(SUM(d.camisetapolo), 0) as cantidad_entregada,
    COALESCE(SUM(i.cantidad), 0) - COALESCE(SUM(d.camisetapolo), 0) as saldo_disponible
FROM ingresos_dotaciones i
LEFT JOIN dotaciones d ON i.tipo_elemento = 'camisetapolo'
WHERE i.tipo_elemento = 'camisetapolo'
UNION ALL
SELECT 
    'guantes_nitrilo' as tipo_elemento,
    COALESCE(SUM(i.cantidad), 0) as cantidad_ingresada,
    COALESCE(SUM(d.guantes_nitrilo), 0) as cantidad_entregada,
    COALESCE(SUM(i.cantidad), 0) - COALESCE(SUM(d.guantes_nitrilo), 0) as saldo_disponible
FROM ingresos_dotaciones i
LEFT JOIN dotaciones d ON i.tipo_elemento = 'guantes_nitrilo'
WHERE i.tipo_elemento = 'guantes_nitrilo'
UNION ALL
SELECT 
    'guantes_carnaza' as tipo_elemento,
    COALESCE(SUM(i.cantidad), 0) as cantidad_ingresada,
    COALESCE(SUM(d.guantes_carnaza), 0) as cantidad_entregada,
    COALESCE(SUM(i.cantidad), 0) - COALESCE(SUM(d.guantes_carnaza), 0) as saldo_disponible
FROM ingresos_dotaciones i
LEFT JOIN dotaciones d ON i.tipo_elemento = 'guantes_carnaza'
WHERE i.tipo_elemento = 'guantes_carnaza'
UNION ALL
SELECT 
    'gafas' as tipo_elemento,
    COALESCE(SUM(i.cantidad), 0) as cantidad_ingresada,
    COALESCE(SUM(d.gafas), 0) as cantidad_entregada,
    COALESCE(SUM(i.cantidad), 0) - COALESCE(SUM(d.gafas), 0) as saldo_disponible
FROM ingresos_dotaciones i
LEFT JOIN dotaciones d ON i.tipo_elemento = 'gafas'
WHERE i.tipo_elemento = 'gafas'
UNION ALL
SELECT 
    'gorra' as tipo_elemento,
    COALESCE(SUM(i.cantidad), 0) as cantidad_ingresada,
    COALESCE(SUM(d.gorra), 0) as cantidad_entregada,
    COALESCE(SUM(i.cantidad), 0) - COALESCE(SUM(d.gorra), 0) as saldo_disponible
FROM ingresos_dotaciones i
LEFT JOIN dotaciones d ON i.tipo_elemento = 'gorra'
WHERE i.tipo_elemento = 'gorra'
UNION ALL
SELECT 
    'casco' as tipo_elemento,
    COALESCE(SUM(i.cantidad), 0) as cantidad_ingresada,
    COALESCE(SUM(d.casco), 0) as cantidad_entregada,
    COALESCE(SUM(i.cantidad), 0) - COALESCE(SUM(d.casco), 0) as saldo_disponible
FROM ingresos_dotaciones i
LEFT JOIN dotaciones d ON i.tipo_elemento = 'casco'
WHERE i.tipo_elemento = 'casco'
UNION ALL
SELECT 
    'botas' as tipo_elemento,
    COALESCE(SUM(i.cantidad), 0) as cantidad_ingresada,
    COALESCE(SUM(d.botas), 0) as cantidad_entregada,
    COALESCE(SUM(i.cantidad), 0) - COALESCE(SUM(d.botas), 0) as saldo_disponible
FROM ingresos_dotaciones i
LEFT JOIN dotaciones d ON i.tipo_elemento = 'botas'
WHERE i.tipo_elemento = 'botas';

-- Datos iniciales de ejemplo
INSERT INTO ingresos_dotaciones (tipo_elemento, cantidad, talla, numero_calzado, proveedor, fecha_ingreso, observaciones, usuario_registro) VALUES
('pantalon', 50, 'M', NULL, 'Proveedor Textil ABC', '2024-01-15', 'Pantalones talla M', 'admin_logistica'),
('pantalon', 50, 'L', NULL, 'Proveedor Textil ABC', '2024-01-15', 'Pantalones talla L', 'admin_logistica'),
('camisetagris', 50, 'S', NULL, 'Confecciones DEF', '2024-01-15', 'Camisetas grises talla S', 'admin_logistica'),
('camisetagris', 100, 'M', NULL, 'Confecciones DEF', '2024-01-15', 'Camisetas grises talla M', 'admin_logistica'),
('guerrera', 40, 'L', NULL, 'Uniformes GHI', '2024-01-16', 'Guerreras talla L', 'admin_logistica'),
('guerrera', 40, 'XL', NULL, 'Uniformes GHI', '2024-01-16', 'Guerreras talla XL', 'admin_logistica'),
('guantes_nitrilo', 200, NULL, NULL, 'Seguridad Industrial JKL', '2024-01-16', 'Talla única', 'admin_logistica'),
('botas', 30, NULL, '40', 'Calzado de Seguridad MNO', '2024-01-17', 'Botas número 40', 'admin_logistica'),
('botas', 30, NULL, '42', 'Calzado de Seguridad MNO', '2024-01-17', 'Botas número 42', 'admin_logistica');

-- Verificar que la tabla se creó correctamente
SELECT 'Tabla ingresos_dotaciones creada exitosamente' as mensaje;
SELECT COUNT(*) as total_registros FROM ingresos_dotaciones;
SELECT * FROM vista_stock_dotaciones LIMIT 5;