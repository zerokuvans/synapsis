-- Triggers para actualización automática de stock ferretero

DELIMITER //

-- Trigger para actualizar stock cuando se registra una entrada
CREATE TRIGGER actualizar_stock_entrada
AFTER INSERT ON entradas_ferretero
FOR EACH ROW
BEGIN
    DECLARE stock_anterior INT DEFAULT 0;
    DECLARE stock_nuevo INT DEFAULT 0;
    
    -- Obtener stock anterior
    SELECT cantidad_disponible INTO stock_anterior 
    FROM stock_ferretero 
    WHERE material_tipo = NEW.material_tipo;
    
    -- Actualizar stock sumando la nueva entrada
    UPDATE stock_ferretero 
    SET cantidad_disponible = cantidad_disponible + NEW.cantidad_entrada,
        fecha_ultima_actualizacion = NOW()
    WHERE material_tipo = NEW.material_tipo;
    
    -- Obtener stock nuevo
    SELECT cantidad_disponible INTO stock_nuevo 
    FROM stock_ferretero 
    WHERE material_tipo = NEW.material_tipo;
    
    -- Registrar movimiento de entrada
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
        stock_nuevo,
        NEW.id_entrada,
        'entrada_ferretero',
        CONCAT('Entrada de material: ', NEW.observaciones),
        NEW.usuario_registro
    );
END//

-- Trigger para actualizar stock cuando se registra una asignación
CREATE TRIGGER actualizar_stock_asignacion
AFTER INSERT ON ferretero
FOR EACH ROW
BEGIN
    DECLARE stock_anterior_silicona INT DEFAULT 0;
    DECLARE stock_anterior_amarres_negros INT DEFAULT 0;
    DECLARE stock_anterior_amarres_blancos INT DEFAULT 0;
    DECLARE stock_anterior_cinta_aislante INT DEFAULT 0;
    DECLARE stock_anterior_grapas_blancas INT DEFAULT 0;
    DECLARE stock_anterior_grapas_negras INT DEFAULT 0;
    
    DECLARE stock_nuevo_silicona INT DEFAULT 0;
    DECLARE stock_nuevo_amarres_negros INT DEFAULT 0;
    DECLARE stock_nuevo_amarres_blancos INT DEFAULT 0;
    DECLARE stock_nuevo_cinta_aislante INT DEFAULT 0;
    DECLARE stock_nuevo_grapas_blancas INT DEFAULT 0;
    DECLARE stock_nuevo_grapas_negras INT DEFAULT 0;
    
    -- Obtener stocks anteriores
    SELECT cantidad_disponible INTO stock_anterior_silicona FROM stock_ferretero WHERE material_tipo = 'silicona';
    SELECT cantidad_disponible INTO stock_anterior_amarres_negros FROM stock_ferretero WHERE material_tipo = 'amarres_negros';
    SELECT cantidad_disponible INTO stock_anterior_amarres_blancos FROM stock_ferretero WHERE material_tipo = 'amarres_blancos';
    SELECT cantidad_disponible INTO stock_anterior_cinta_aislante FROM stock_ferretero WHERE material_tipo = 'cinta_aislante';
    SELECT cantidad_disponible INTO stock_anterior_grapas_blancas FROM stock_ferretero WHERE material_tipo = 'grapas_blancas';
    SELECT cantidad_disponible INTO stock_anterior_grapas_negras FROM stock_ferretero WHERE material_tipo = 'grapas_negras';
    
    -- Actualizar stocks restando las cantidades asignadas
    IF NEW.silicona > 0 THEN
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.silicona, fecha_ultima_actualizacion = NOW() WHERE material_tipo = 'silicona';
        SELECT cantidad_disponible INTO stock_nuevo_silicona FROM stock_ferretero WHERE material_tipo = 'silicona';
        
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('silicona', 'salida', NEW.silicona, stock_anterior_silicona, stock_nuevo_silicona, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
    END IF;
    
    IF NEW.amarres_negros > 0 THEN
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.amarres_negros, fecha_ultima_actualizacion = NOW() WHERE material_tipo = 'amarres_negros';
        SELECT cantidad_disponible INTO stock_nuevo_amarres_negros FROM stock_ferretero WHERE material_tipo = 'amarres_negros';
        
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('amarres_negros', 'salida', NEW.amarres_negros, stock_anterior_amarres_negros, stock_nuevo_amarres_negros, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
    END IF;
    
    IF NEW.amarres_blancos > 0 THEN
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.amarres_blancos, fecha_ultima_actualizacion = NOW() WHERE material_tipo = 'amarres_blancos';
        SELECT cantidad_disponible INTO stock_nuevo_amarres_blancos FROM stock_ferretero WHERE material_tipo = 'amarres_blancos';
        
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('amarres_blancos', 'salida', NEW.amarres_blancos, stock_anterior_amarres_blancos, stock_nuevo_amarres_blancos, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
    END IF;
    
    IF NEW.cinta_aislante > 0 THEN
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.cinta_aislante, fecha_ultima_actualizacion = NOW() WHERE material_tipo = 'cinta_aislante';
        SELECT cantidad_disponible INTO stock_nuevo_cinta_aislante FROM stock_ferretero WHERE material_tipo = 'cinta_aislante';
        
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('cinta_aislante', 'salida', NEW.cinta_aislante, stock_anterior_cinta_aislante, stock_nuevo_cinta_aislante, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
    END IF;
    
    IF NEW.grapas_blancas > 0 THEN
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.grapas_blancas, fecha_ultima_actualizacion = NOW() WHERE material_tipo = 'grapas_blancas';
        SELECT cantidad_disponible INTO stock_nuevo_grapas_blancas FROM stock_ferretero WHERE material_tipo = 'grapas_blancas';
        
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('grapas_blancas', 'salida', NEW.grapas_blancas, stock_anterior_grapas_blancas, stock_nuevo_grapas_blancas, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
    END IF;
    
    IF NEW.grapas_negras > 0 THEN
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.grapas_negras, fecha_ultima_actualizacion = NOW() WHERE material_tipo = 'grapas_negras';
        SELECT cantidad_disponible INTO stock_nuevo_grapas_negras FROM stock_ferretero WHERE material_tipo = 'grapas_negras';
        
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('grapas_negras', 'salida', NEW.grapas_negras, stock_anterior_grapas_negras, stock_nuevo_grapas_negras, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
    END IF;
END//

DELIMITER ;

-- Mostrar triggers creados
SHOW TRIGGERS LIKE '%ferretero%';