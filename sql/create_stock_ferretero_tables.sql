-- Crear tablas para gestión de stock de material ferretero

-- Tabla para el stock actual de material ferretero
CREATE TABLE IF NOT EXISTS stock_ferretero (
    id_stock INT AUTO_INCREMENT PRIMARY KEY,
    material_tipo ENUM('silicona', 'amarres_negros', 'amarres_blancos', 'cinta_aislante', 'grapas_blancas', 'grapas_negras') NOT NULL,
    cantidad_disponible INT NOT NULL DEFAULT 0,
    cantidad_minima INT NOT NULL DEFAULT 10,
    cantidad_maxima INT NOT NULL DEFAULT 1000,
    unidad_medida VARCHAR(20) DEFAULT 'unidades',
    descripcion TEXT,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_material (material_tipo)
);

-- Tabla para registrar entradas de material ferretero
CREATE TABLE IF NOT EXISTS entradas_ferretero (
    id_entrada INT AUTO_INCREMENT PRIMARY KEY,
    material_tipo ENUM('silicona', 'amarres_negros', 'amarres_blancos', 'cinta_aislante', 'grapas_blancas', 'grapas_negras') NOT NULL,
    cantidad_entrada INT NOT NULL,
    precio_unitario DECIMAL(10,2) DEFAULT 0.00,
    precio_total DECIMAL(10,2) DEFAULT 0.00,
    proveedor VARCHAR(255),
    numero_factura VARCHAR(100),
    fecha_entrada DATE NOT NULL,
    fecha_vencimiento DATE,
    observaciones TEXT,
    usuario_registro INT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_registro) REFERENCES recurso_operativo(id_codigo_consumidor),
    INDEX idx_material_fecha (material_tipo, fecha_entrada),
    INDEX idx_fecha_entrada (fecha_entrada)
);

-- Tabla para historial de movimientos de stock
CREATE TABLE IF NOT EXISTS movimientos_stock_ferretero (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    material_tipo ENUM('silicona', 'amarres_negros', 'amarres_blancos', 'cinta_aislante', 'grapas_blancas', 'grapas_negras') NOT NULL,
    tipo_movimiento ENUM('entrada', 'salida', 'ajuste') NOT NULL,
    cantidad INT NOT NULL,
    cantidad_anterior INT NOT NULL,
    cantidad_nueva INT NOT NULL,
    referencia_id INT, -- ID de la entrada o asignación relacionada
    referencia_tipo ENUM('entrada_ferretero', 'asignacion_ferretero', 'ajuste_manual') NOT NULL,
    observaciones TEXT,
    usuario_movimiento INT,
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_movimiento) REFERENCES recurso_operativo(id_codigo_consumidor),
    INDEX idx_material_fecha (material_tipo, fecha_movimiento),
    INDEX idx_tipo_movimiento (tipo_movimiento),
    INDEX idx_referencia (referencia_tipo, referencia_id)
);

-- Insertar datos iniciales para el stock (valores por defecto)
INSERT IGNORE INTO stock_ferretero (material_tipo, cantidad_disponible, cantidad_minima, cantidad_maxima, descripcion) VALUES
('silicona', 0, 10, 1000, 'Silicona para instalaciones'),
('amarres_negros', 0, 50, 5000, 'Amarres de color negro'),
('amarres_blancos', 0, 50, 5000, 'Amarres de color blanco'),
('cinta_aislante', 0, 20, 2000, 'Cinta aislante para instalaciones'),
('grapas_blancas', 0, 100, 10000, 'Grapas de color blanco'),
('grapas_negras', 0, 100, 10000, 'Grapas de color negro');

-- Crear trigger para actualizar stock automáticamente cuando se registre una entrada
DELIMITER //
CREATE TRIGGER IF NOT EXISTS actualizar_stock_entrada
AFTER INSERT ON entradas_ferretero
FOR EACH ROW
BEGIN
    DECLARE stock_anterior INT DEFAULT 0;
    
    -- Obtener stock anterior
    SELECT cantidad_disponible INTO stock_anterior 
    FROM stock_ferretero 
    WHERE material_tipo = NEW.material_tipo;
    
    -- Actualizar stock
    UPDATE stock_ferretero 
    SET cantidad_disponible = cantidad_disponible + NEW.cantidad_entrada
    WHERE material_tipo = NEW.material_tipo;
    
    -- Registrar movimiento
    INSERT INTO movimientos_stock_ferretero (
        material_tipo, 
        tipo_movimiento, 
        cantidad, 
        cantidad_anterior, 
        cantidad_nueva, 
        referencia_id, 
        referencia_tipo, 
        observaciones, 
        usuario_movimiento
    ) VALUES (
        NEW.material_tipo,
        'entrada',
        NEW.cantidad_entrada,
        stock_anterior,
        stock_anterior + NEW.cantidad_entrada,
        NEW.id_entrada,
        'entrada_ferretero',
        CONCAT('Entrada de material - Factura: ', IFNULL(NEW.numero_factura, 'N/A')),
        NEW.usuario_registro
    );
END//
DELIMITER ;

-- Crear trigger para actualizar stock automáticamente cuando se registre una asignación
DELIMITER //
CREATE TRIGGER IF NOT EXISTS actualizar_stock_asignacion
AFTER INSERT ON ferretero
FOR EACH ROW
BEGIN
    DECLARE stock_anterior_silicona INT DEFAULT 0;
    DECLARE stock_anterior_amarres_negros INT DEFAULT 0;
    DECLARE stock_anterior_amarres_blancos INT DEFAULT 0;
    DECLARE stock_anterior_cinta INT DEFAULT 0;
    DECLARE stock_anterior_grapas_blancas INT DEFAULT 0;
    DECLARE stock_anterior_grapas_negras INT DEFAULT 0;
    
    -- Actualizar stock para silicona
    IF NEW.silicona > 0 THEN
        SELECT cantidad_disponible INTO stock_anterior_silicona FROM stock_ferretero WHERE material_tipo = 'silicona';
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.silicona WHERE material_tipo = 'silicona';
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('silicona', 'salida', NEW.silicona, stock_anterior_silicona, stock_anterior_silicona - NEW.silicona, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
    END IF;
    
    -- Actualizar stock para amarres negros
    IF NEW.amarres_negros > 0 THEN
        SELECT cantidad_disponible INTO stock_anterior_amarres_negros FROM stock_ferretero WHERE material_tipo = 'amarres_negros';
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.amarres_negros WHERE material_tipo = 'amarres_negros';
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('amarres_negros', 'salida', NEW.amarres_negros, stock_anterior_amarres_negros, stock_anterior_amarres_negros - NEW.amarres_negros, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
    END IF;
    
    -- Actualizar stock para amarres blancos
    IF NEW.amarres_blancos > 0 THEN
        SELECT cantidad_disponible INTO stock_anterior_amarres_blancos FROM stock_ferretero WHERE material_tipo = 'amarres_blancos';
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.amarres_blancos WHERE material_tipo = 'amarres_blancos';
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('amarres_blancos', 'salida', NEW.amarres_blancos, stock_anterior_amarres_blancos, stock_anterior_amarres_blancos - NEW.amarres_blancos, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
    END IF;
    
    -- Actualizar stock para cinta aislante
    IF NEW.cinta_aislante > 0 THEN
        SELECT cantidad_disponible INTO stock_anterior_cinta FROM stock_ferretero WHERE material_tipo = 'cinta_aislante';
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.cinta_aislante WHERE material_tipo = 'cinta_aislante';
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('cinta_aislante', 'salida', NEW.cinta_aislante, stock_anterior_cinta, stock_anterior_cinta - NEW.cinta_aislante, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
    END IF;
    
    -- Actualizar stock para grapas blancas
    IF NEW.grapas_blancas > 0 THEN
        SELECT cantidad_disponible INTO stock_anterior_grapas_blancas FROM stock_ferretero WHERE material_tipo = 'grapas_blancas';
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.grapas_blancas WHERE material_tipo = 'grapas_blancas';
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('grapas_blancas', 'salida', NEW.grapas_blancas, stock_anterior_grapas_blancas, stock_anterior_grapas_blancas - NEW.grapas_blancas, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
    END IF;
    
    -- Actualizar stock para grapas negras
    IF NEW.grapas_negras > 0 THEN
        SELECT cantidad_disponible INTO stock_anterior_grapas_negras FROM stock_ferretero WHERE material_tipo = 'grapas_negras';
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.grapas_negras WHERE material_tipo = 'grapas_negras';
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('grapas_negras', 'salida', NEW.grapas_negras, stock_anterior_grapas_negras, stock_anterior_grapas_negras - NEW.grapas_negras, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
    END IF;
END//
DELIMITER ;