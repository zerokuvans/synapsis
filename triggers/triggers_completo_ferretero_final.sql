-- =====================================================
-- SISTEMA DE TRIGGERS PARA FERRETERO - VERSIÓN FINAL
-- =====================================================
-- Archivo: triggers_completo_ferretero_final.sql
-- Descripción: Sistema completo de triggers para gestión automática de stock
-- VERSIÓN FINAL: Incluye todas las correcciones con stock inicial de silicona mantenido
-- CAMBIOS PRINCIPALES:
--   1. Corregidas las referencias a columnas correctas
--   2. Stock inicial de silicona mantenido en 100 unidades
--   3. Triggers actualizados para usar entradas_ferretero correctamente
-- Fecha: 2024
-- Autor: Sistema Synapsis
--
-- INSTRUCCIONES DE INSTALACIÓN:
-- 1. Crear la base de datos: CREATE DATABASE IF NOT EXISTS capired;
-- 2. Usar la base de datos: USE capired;
-- 3. Ejecutar este archivo completo: mysql -u root -p capired < triggers_completo_ferretero_final.sql
-- =====================================================

USE capired;

-- =====================================================
-- CREACIÓN DE TABLAS
-- =====================================================

-- Tabla: stock_general
-- Descripción: Almacena el inventario general de materiales
-- COLUMNAS: id, codigo_material, descripcion, cantidad_disponible, cantidad_minima, fecha_actualizacion, activo
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

-- Tabla: entradas_ferretero
-- Descripción: Registra las entradas de materiales específicos para ferreteros
-- COLUMNAS: id, material_tipo, cantidad_entrada, fecha_entrada, observaciones
CREATE TABLE IF NOT EXISTS entradas_ferretero (
    id INT AUTO_INCREMENT PRIMARY KEY,
    material_tipo VARCHAR(50) NOT NULL,
    cantidad_entrada INT NOT NULL,
    fecha_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT
);

-- Tabla: entradas_stock
-- Descripción: Registra las entradas generales de stock al inventario
-- COLUMNAS: id, material, cantidad_ingresada, fecha_entrada, observaciones
CREATE TABLE IF NOT EXISTS entradas_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    material VARCHAR(50) NOT NULL,
    cantidad_ingresada INT NOT NULL,
    fecha_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT
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
    tipo VARCHAR(50) NOT NULL,
    mensaje TEXT NOT NULL,
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    datos_adicionales JSON
);

-- =====================================================
-- DATOS INICIALES
-- =====================================================

-- STOCK INICIAL: Silicona mantiene su stock inicial de 100 unidades
-- NOTA: El stock inicial de silicona se mantiene para preservar el inventario base
-- del sistema. Las entradas y salidas se registrarán adicionalmente a este stock base.

INSERT IGNORE INTO stock_general (codigo_material, descripcion, cantidad_disponible, cantidad_minima) VALUES
('silicona', 'Silicona para instalaciones', 100, 20),  -- MANTENIDO: Stock inicial de 100 unidades
('grapas_negras', 'Grapas negras para cable', 500, 50),
('grapas_blancas', 'Grapas blancas para cable', 300, 30),
('amarres_negros', 'Amarres negros plásticos', 200, 25),
('amarres_blancos', 'Amarres blancos plásticos', 150, 25),
('cinta_aislante', 'Cinta aislante eléctrica', 80, 15);

-- =====================================================
-- TRIGGERS DEL SISTEMA - VERSIÓN CORREGIDA
-- =====================================================

-- Eliminar triggers existentes si existen
DROP TRIGGER IF EXISTS actualizar_stock_entrada_ferretero;
DROP TRIGGER IF EXISTS actualizar_stock_entrada_general;
DROP TRIGGER IF EXISTS actualizar_stock_asignacion;
DROP TRIGGER IF EXISTS alerta_stock_bajo;
DROP TRIGGER IF EXISTS validar_asignacion;

DELIMITER //

-- =====================================================
-- TRIGGER 1: actualizar_stock_entrada_ferretero
-- Descripción: Actualiza el stock cuando se registra una entrada en entradas_ferretero
-- TABLA ORIGEN: entradas_ferretero (columna: cantidad_entrada)
-- TABLA DESTINO: stock_general (columna: cantidad_disponible)
-- =====================================================
CREATE TRIGGER actualizar_stock_entrada_ferretero
AFTER INSERT ON entradas_ferretero
FOR EACH ROW
BEGIN
    -- CORREGIDO: Usar NEW.cantidad_entrada de entradas_ferretero
    UPDATE stock_general 
    SET cantidad_disponible = cantidad_disponible + NEW.cantidad_entrada,
        fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE codigo_material = NEW.material_tipo;
    
    -- Registrar evento en el sistema
    INSERT INTO eventos_sistema (tipo, mensaje)
    VALUES (
        'ENTRADA_FERRETERO',
        CONCAT('Entrada ferretero: ', NEW.cantidad_entrada, ' unidades de ', NEW.material_tipo)
    );
END//

-- =====================================================
-- TRIGGER 2: actualizar_stock_entrada_general
-- Descripción: Actualiza el stock cuando se registra una entrada en entradas_stock
-- TABLA ORIGEN: entradas_stock (columna: cantidad_ingresada)
-- TABLA DESTINO: stock_general (columna: cantidad_disponible)
-- =====================================================
CREATE TRIGGER actualizar_stock_entrada_general
AFTER INSERT ON entradas_stock
FOR EACH ROW
BEGIN
    -- CORREGIDO: Usar NEW.cantidad_ingresada de entradas_stock
    UPDATE stock_general 
    SET cantidad_disponible = cantidad_disponible + NEW.cantidad_ingresada,
        fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE codigo_material = NEW.material;
    
    -- Registrar evento en el sistema
    INSERT INTO eventos_sistema (tipo, mensaje)
    VALUES (
        'ENTRADA_STOCK',
        CONCAT('Entrada stock: ', NEW.cantidad_ingresada, ' unidades de ', NEW.material)
    );
END//

-- =====================================================
-- TRIGGER 3: actualizar_stock_asignacion
-- Descripción: Actualiza el stock cuando se asignan materiales a ferreteros
-- TABLA ORIGEN: ferretero (columnas: silicona, grapas_negras, etc.)
-- TABLA DESTINO: stock_general (columna: cantidad_disponible)
-- =====================================================
CREATE TRIGGER actualizar_stock_asignacion
AFTER INSERT ON ferretero
FOR EACH ROW
BEGIN
    -- CORREGIDO: Usar cantidad_disponible de stock_general
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
    INSERT INTO eventos_sistema (tipo, mensaje)
    VALUES (
        'ASIGNACION_FERRETERO',
        CONCAT('Asignación a ferretero: ', NEW.codigo_ferretero, ' - Silicona:', NEW.silicona, ' Grapas N:', NEW.grapas_negras, ' Grapas B:', NEW.grapas_blancas)
    );
END//

-- =====================================================
-- TRIGGER 4: alerta_stock_bajo
-- Descripción: Genera alertas cuando el stock está por debajo del mínimo
-- TABLA: stock_general (usa cantidad_disponible y cantidad_minima)
-- =====================================================
CREATE TRIGGER alerta_stock_bajo
AFTER UPDATE ON stock_general
FOR EACH ROW
BEGIN
    -- CORREGIDO: Usar cantidad_disponible y cantidad_minima de stock_general
    IF NEW.cantidad_disponible < NEW.cantidad_minima AND NEW.cantidad_disponible != OLD.cantidad_disponible THEN
        -- Insertar alerta de stock bajo
        INSERT INTO alertas_stock (material, cantidad_actual, cantidad_minima)
        VALUES (NEW.codigo_material, NEW.cantidad_disponible, NEW.cantidad_minima);
        
        -- Registrar evento de alerta
        INSERT INTO eventos_sistema (tipo, mensaje)
        VALUES (
            'ALERTA_STOCK_BAJO',
            CONCAT('Stock bajo detectado para: ', NEW.codigo_material, ' (', NEW.cantidad_disponible, '/', NEW.cantidad_minima, ')')
        );
    END IF;
END//

-- =====================================================
-- TRIGGER 5: validar_asignacion
-- Descripción: Valida que hay suficiente stock antes de asignar
-- TABLA ORIGEN: ferretero (antes de insertar)
-- TABLA CONSULTA: stock_general (usa cantidad_disponible)
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
    
    -- CORREGIDO: Obtener cantidad_disponible de stock_general
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

-- Verificar estructura de stock_general
SELECT 'Estructura de stock_general:' AS status;
DESCRIBE stock_general;

-- Verificar estructura de entradas_ferretero
SELECT 'Estructura de entradas_ferretero:' AS status;
DESCRIBE entradas_ferretero;

-- Verificar estructura de entradas_stock
SELECT 'Estructura de entradas_stock:' AS status;
DESCRIBE entradas_stock;

-- Verificar que los triggers se crearon correctamente
SELECT 'Verificando triggers creados...' AS status;
SHOW TRIGGERS;

-- Mostrar stock inicial
SELECT 'Stock inicial configurado:' AS status;
SELECT codigo_material, descripcion, cantidad_disponible, cantidad_minima 
FROM stock_general ORDER BY codigo_material;

-- =====================================================
-- RESUMEN DE CAMBIOS REALIZADOS
-- =====================================================
/*
CAMBIOS PRINCIPALES EN ESTA VERSIÓN FINAL:

1. STOCK INICIAL DE SILICONA:
   - MANTENIDO: 100 unidades como stock base
   - RAZÓN: Preservar inventario inicial del sistema

2. TRIGGERS CORREGIDOS:
   - actualizar_stock_entrada_ferretero: Usa cantidad_entrada de entradas_ferretero
   - actualizar_stock_entrada_general: Usa cantidad_ingresada de entradas_stock
   - Todos los triggers usan cantidad_disponible en stock_general

3. TABLAS INCLUIDAS:
   - entradas_ferretero: Para registrar entradas específicas de ferreteros
   - entradas_stock: Para registrar entradas generales de stock
   - Estructura corregida de todas las tablas

4. FUNCIONAMIENTO DEL SISTEMA:
   - Stock inicial: 100 unidades de silicona como base
   - Entradas: Se suman al stock disponible
   - Asignaciones: Se restan del stock disponible
   - Stock final = Stock inicial + Entradas - Asignaciones
   - Sistema de alertas y validaciones funcionando correctamente
*/

-- =====================================================
-- FIN DEL ARCHIVO FINAL
-- =====================================================
SELECT 'Sistema de triggers final instalado correctamente!' AS mensaje_final;
SELECT 'Stock de silicona configurado con 100 unidades iniciales' AS nota_stock;