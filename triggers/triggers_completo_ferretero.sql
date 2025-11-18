-- =====================================================
-- SISTEMA DE TRIGGERS PARA FERRETERO - VERSIÓN COMPLETA
-- =====================================================
-- Archivo: triggers_completo_ferretero.sql
-- Descripción: Sistema completo de triggers para gestión automática de stock
-- Fecha: 2024
-- Autor: Sistema Synapsis
--
-- INSTRUCCIONES DE INSTALACIÓN:
-- 1. Crear la base de datos: CREATE DATABASE IF NOT EXISTS capired;
-- 2. Usar la base de datos: USE capired;
-- 3. Ejecutar este archivo completo: mysql -u root -p capired < triggers_completo_ferretero.sql
-- =====================================================

USE capired;

-- =====================================================
-- CREACIÓN DE TABLAS
-- =====================================================

-- Tabla: stock_general
-- Descripción: Almacena el inventario general de materiales
CREATE TABLE IF NOT EXISTS stock_general (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_material VARCHAR(50) UNIQUE NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    cantidad_disponible INT NOT NULL DEFAULT 0,
    cantidad_minima INT NOT NULL DEFAULT 10,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla: ferretero
-- Descripción: Registra las asignaciones de materiales a ferreteros
CREATE TABLE IF NOT EXISTS ferretero (
    id_ferretero INT AUTO_INCREMENT PRIMARY KEY,
    codigo_ferretero VARCHAR(50) NOT NULL,
    id_codigo_consumidor VARCHAR(50),
    silicona INT DEFAULT 0,
    grapas_negras INT DEFAULT 0,
    grapas_blancas INT DEFAULT 0,
    amarres_negros INT DEFAULT 0,
    amarres_blancos INT DEFAULT 0,
    cinta_aislante INT DEFAULT 0,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: entradas_stock
-- Descripción: Registra las entradas de stock al inventario
CREATE TABLE IF NOT EXISTS entradas_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_material VARCHAR(50) NOT NULL,
    cantidad_entrada INT NOT NULL,
    fecha_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    FOREIGN KEY (codigo_material) REFERENCES stock_general(codigo_material)
);

-- Tabla: alertas_stock
-- Descripción: Almacena alertas cuando el stock está bajo
CREATE TABLE IF NOT EXISTS alertas_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    material VARCHAR(50) NOT NULL,
    cantidad_actual INT NOT NULL,
    cantidad_minima INT NOT NULL,
    fecha_alerta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'PENDIENTE'
);

-- Tabla: eventos_sistema
-- Descripción: Registra eventos importantes del sistema
CREATE TABLE IF NOT EXISTS eventos_sistema (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_evento VARCHAR(50) NOT NULL,
    descripcion TEXT NOT NULL,
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    datos_adicionales JSON
);

-- =====================================================
-- DATOS INICIALES DE EJEMPLO
-- =====================================================

-- Insertar stock inicial
INSERT IGNORE INTO stock_general (codigo_material, descripcion, cantidad_disponible, cantidad_minima) VALUES
('silicona', 'Silicona para instalaciones', 100, 20),
('grapas_negras', 'Grapas negras para cable', 500, 50),
('grapas_blancas', 'Grapas blancas para cable', 300, 30),
('amarres_negros', 'Amarres negros plásticos', 200, 25),
('amarres_blancos', 'Amarres blancos plásticos', 150, 25),
('cinta_aislante', 'Cinta aislante eléctrica', 80, 15);

-- =====================================================
-- TRIGGERS DEL SISTEMA
-- =====================================================

-- Eliminar triggers existentes si existen
DROP TRIGGER IF EXISTS actualizar_stock_entrada;
DROP TRIGGER IF EXISTS actualizar_stock_asignacion;
DROP TRIGGER IF EXISTS alerta_stock_bajo;
DROP TRIGGER IF EXISTS validar_asignacion;

DELIMITER //

-- =====================================================
-- TRIGGER 1: actualizar_stock_entrada
-- Descripción: Actualiza el stock cuando se registra una entrada
-- =====================================================
CREATE TRIGGER actualizar_stock_entrada
AFTER INSERT ON entradas_stock
FOR EACH ROW
BEGIN
    -- Actualizar la cantidad disponible en stock_general
    UPDATE stock_general 
    SET cantidad_disponible = cantidad_disponible + NEW.cantidad_entrada,
        fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE codigo_material = NEW.codigo_material;
    
    -- Registrar evento en el sistema
    INSERT INTO eventos_sistema (tipo_evento, descripcion, datos_adicionales)
    VALUES (
        'ENTRADA_STOCK',
        CONCAT('Entrada de stock: ', NEW.cantidad_entrada, ' unidades de ', NEW.codigo_material),
        JSON_OBJECT(
            'material', NEW.codigo_material,
            'cantidad', NEW.cantidad_entrada,
            'fecha', NEW.fecha_entrada
        )
    );
END//

-- =====================================================
-- TRIGGER 2: actualizar_stock_asignacion
-- Descripción: Actualiza el stock cuando se asignan materiales a ferreteros
-- =====================================================
CREATE TRIGGER actualizar_stock_asignacion
AFTER INSERT ON ferretero
FOR EACH ROW
BEGIN
    -- Actualizar stock para silicona
    IF NEW.silicona > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.silicona,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE codigo_material = 'silicona';
    END IF;
    
    -- Actualizar stock para grapas negras
    IF NEW.grapas_negras > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.grapas_negras,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE codigo_material = 'grapas_negras';
    END IF;
    
    -- Actualizar stock para grapas blancas
    IF NEW.grapas_blancas > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.grapas_blancas,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE codigo_material = 'grapas_blancas';
    END IF;
    
    -- Actualizar stock para amarres negros
    IF NEW.amarres_negros > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.amarres_negros,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE codigo_material = 'amarres_negros';
    END IF;
    
    -- Actualizar stock para amarres blancos
    IF NEW.amarres_blancos > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.amarres_blancos,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE codigo_material = 'amarres_blancos';
    END IF;
    
    -- Actualizar stock para cinta aislante
    IF NEW.cinta_aislante > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.cinta_aislante,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE codigo_material = 'cinta_aislante';
    END IF;
    
    -- Registrar evento de asignación
    INSERT INTO eventos_sistema (tipo_evento, descripcion, datos_adicionales)
    VALUES (
        'ASIGNACION_FERRETERO',
        CONCAT('Asignación a ferretero: ', NEW.codigo_ferretero),
        JSON_OBJECT(
            'ferretero', NEW.codigo_ferretero,
            'silicona', NEW.silicona,
            'grapas_negras', NEW.grapas_negras,
            'grapas_blancas', NEW.grapas_blancas,
            'amarres_negros', NEW.amarres_negros,
            'amarres_blancos', NEW.amarres_blancos,
            'cinta_aislante', NEW.cinta_aislante,
            'fecha', NEW.fecha_asignacion
        )
    );
END//

-- =====================================================
-- TRIGGER 3: alerta_stock_bajo
-- Descripción: Genera alertas cuando el stock está por debajo del mínimo
-- =====================================================
CREATE TRIGGER alerta_stock_bajo
AFTER UPDATE ON stock_general
FOR EACH ROW
BEGIN
    -- Verificar si el stock está por debajo del mínimo
    IF NEW.cantidad_disponible < NEW.cantidad_minima AND NEW.cantidad_disponible != OLD.cantidad_disponible THEN
        -- Insertar alerta de stock bajo
        INSERT INTO alertas_stock (material, cantidad_actual, cantidad_minima)
        VALUES (NEW.codigo_material, NEW.cantidad_disponible, NEW.cantidad_minima);
        
        -- Registrar evento de alerta
        INSERT INTO eventos_sistema (tipo_evento, descripcion, datos_adicionales)
        VALUES (
            'ALERTA_STOCK_BAJO',
            CONCAT('Stock bajo detectado para: ', NEW.codigo_material, ' (', NEW.cantidad_disponible, '/', NEW.cantidad_minima, ')'),
            JSON_OBJECT(
                'material', NEW.codigo_material,
                'cantidad_actual', NEW.cantidad_disponible,
                'cantidad_minima', NEW.cantidad_minima,
                'diferencia', NEW.cantidad_minima - NEW.cantidad_disponible
            )
        );
    END IF;
END//

-- =====================================================
-- TRIGGER 4: validar_asignacion
-- Descripción: Valida que hay suficiente stock antes de asignar
-- =====================================================
CREATE TRIGGER validar_asignacion
BEFORE INSERT ON ferretero
FOR EACH ROW
BEGIN
    DECLARE stock_silicona INT DEFAULT 0;
    DECLARE stock_grapas_negras INT DEFAULT 0;
    DECLARE stock_grapas_blancas INT DEFAULT 0;
    DECLARE stock_amarres_negros INT DEFAULT 0;
    DECLARE stock_amarres_blancos INT DEFAULT 0;
    DECLARE stock_cinta_aislante INT DEFAULT 0;
    
    -- Obtener stock actual de cada material
    SELECT cantidad_disponible INTO stock_silicona 
    FROM stock_general WHERE codigo_material = 'silicona';
    
    SELECT cantidad_disponible INTO stock_grapas_negras 
    FROM stock_general WHERE codigo_material = 'grapas_negras';
    
    SELECT cantidad_disponible INTO stock_grapas_blancas 
    FROM stock_general WHERE codigo_material = 'grapas_blancas';
    
    SELECT cantidad_disponible INTO stock_amarres_negros 
    FROM stock_general WHERE codigo_material = 'amarres_negros';
    
    SELECT cantidad_disponible INTO stock_amarres_blancos 
    FROM stock_general WHERE codigo_material = 'amarres_blancos';
    
    SELECT cantidad_disponible INTO stock_cinta_aislante 
    FROM stock_general WHERE codigo_material = 'cinta_aislante';
    
    -- Validar stock suficiente para cada material
    IF NEW.silicona > stock_silicona THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuficiente de silicona';
    END IF;
    
    IF NEW.grapas_negras > stock_grapas_negras THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuficiente de grapas negras';
    END IF;
    
    IF NEW.grapas_blancas > stock_grapas_blancas THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuficiente de grapas blancas';
    END IF;
    
    IF NEW.amarres_negros > stock_amarres_negros THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuficiente de amarres negros';
    END IF;
    
    IF NEW.amarres_blancos > stock_amarres_blancos THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuficiente de amarres blancos';
    END IF;
    
    IF NEW.cinta_aislante > stock_cinta_aislante THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuficiente de cinta aislante';
    END IF;
END//

DELIMITER ;

-- =====================================================
-- COMANDOS DE VERIFICACIÓN
-- =====================================================

-- Verificar que las tablas se crearon correctamente
SELECT 'Verificando tablas creadas...' AS status;
SHOW TABLES;

-- Verificar que los triggers se crearon correctamente
SELECT 'Verificando triggers creados...' AS status;
SHOW TRIGGERS;

-- Mostrar stock inicial
SELECT 'Stock inicial cargado:' AS status;
SELECT codigo_material, descripcion, cantidad_disponible, cantidad_minima 
FROM stock_general ORDER BY codigo_material;

-- =====================================================
-- COMANDOS DE PRUEBA (OPCIONAL)
-- =====================================================

-- Para probar el sistema, ejecutar estos comandos:
/*
-- Prueba 1: Insertar entrada de stock
INSERT INTO entradas_stock (codigo_material, cantidad_entrada, observaciones) 
VALUES ('silicona', 50, 'Entrada de prueba');

-- Prueba 2: Asignar materiales a un ferretero
INSERT INTO ferretero (codigo_ferretero, id_codigo_consumidor, silicona, grapas_negras, cinta_aislante) 
VALUES ('F001', 'C001', 5, 10, 3);

-- Verificar stock después de las pruebas
SELECT codigo_material, cantidad_disponible, cantidad_minima 
FROM stock_general ORDER BY codigo_material;

-- Ver alertas generadas
SELECT * FROM alertas_stock ORDER BY fecha_alerta DESC;

-- Ver eventos del sistema
SELECT tipo_evento, descripcion, fecha_evento 
FROM eventos_sistema ORDER BY fecha_evento DESC LIMIT 10;
*/

-- =====================================================
-- FIN DEL ARCHIVO
-- =====================================================
SELECT 'Sistema de triggers instalado correctamente!' AS mensaje_final;