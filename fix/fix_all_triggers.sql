USE capired;

-- Eliminar todos los triggers existentes
DROP TRIGGER IF EXISTS actualizar_stock_asignacion;
DROP TRIGGER IF EXISTS alerta_stock_bajo;
DROP TRIGGER IF EXISTS validar_asignacion;

-- =====================================================
-- TRIGGER 1: ACTUALIZAR_STOCK_ASIGNACION (CORREGIDO)
-- =====================================================

DELIMITER //

CREATE TRIGGER actualizar_stock_asignacion
AFTER INSERT ON ferretero
FOR EACH ROW
BEGIN
    -- Actualizar stock para cada material que tenga valor > 0
    
    -- Silicona
    IF NEW.silicona > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.silicona,
            fecha_actualizacion = NOW()
        WHERE codigo_material = 'silicona';
    END IF;
    
    -- Grapas blancas
    IF NEW.grapas_blancas > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.grapas_blancas,
            fecha_actualizacion = NOW()
        WHERE codigo_material = 'grapas_blancas';
    END IF;
    
    -- Grapas negras
    IF NEW.grapas_negras > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.grapas_negras,
            fecha_actualizacion = NOW()
        WHERE codigo_material = 'grapas_negras';
    END IF;
    
    -- Cinta aislante
    IF NEW.cinta_aislante > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.cinta_aislante,
            fecha_actualizacion = NOW()
        WHERE codigo_material = 'cinta_aislante';
    END IF;
    
    -- Amarres negros
    IF NEW.amarres_negros > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.amarres_negros,
            fecha_actualizacion = NOW()
        WHERE codigo_material = 'amarres_negros';
    END IF;
    
    -- Amarres blancos
    IF NEW.amarres_blancos > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.amarres_blancos,
            fecha_actualizacion = NOW()
        WHERE codigo_material = 'amarres_blancos';
    END IF;
    
END//

-- =====================================================
-- TRIGGER 2: VALIDAR_ASIGNACION (CORREGIDO)
-- =====================================================

CREATE TRIGGER validar_asignacion
BEFORE INSERT ON ferretero
FOR EACH ROW
BEGIN
    DECLARE stock_disponible INT;
    DECLARE mensaje_error VARCHAR(255);
    
    -- Validar silicona
    IF NEW.silicona > 0 THEN
        SELECT cantidad_disponible INTO stock_disponible 
        FROM stock_general 
        WHERE codigo_material = 'silicona';
        
        IF stock_disponible < NEW.silicona THEN
            SET mensaje_error = CONCAT('Stock insuficiente de silicona. Disponible: ', stock_disponible, ', Solicitado: ', NEW.silicona);
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = mensaje_error;
        END IF;
    END IF;
    
    -- Validar grapas blancas
    IF NEW.grapas_blancas > 0 THEN
        SELECT cantidad_disponible INTO stock_disponible 
        FROM stock_general 
        WHERE codigo_material = 'grapas_blancas';
        
        IF stock_disponible < NEW.grapas_blancas THEN
            SET mensaje_error = CONCAT('Stock insuficiente de grapas blancas. Disponible: ', stock_disponible, ', Solicitado: ', NEW.grapas_blancas);
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = mensaje_error;
        END IF;
    END IF;
    
    -- Validar grapas negras
    IF NEW.grapas_negras > 0 THEN
        SELECT cantidad_disponible INTO stock_disponible 
        FROM stock_general 
        WHERE codigo_material = 'grapas_negras';
        
        IF stock_disponible < NEW.grapas_negras THEN
            SET mensaje_error = CONCAT('Stock insuficiente de grapas negras. Disponible: ', stock_disponible, ', Solicitado: ', NEW.grapas_negras);
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = mensaje_error;
        END IF;
    END IF;
    
    -- Validar cinta aislante
    IF NEW.cinta_aislante > 0 THEN
        SELECT cantidad_disponible INTO stock_disponible 
        FROM stock_general 
        WHERE codigo_material = 'cinta_aislante';
        
        IF stock_disponible < NEW.cinta_aislante THEN
            SET mensaje_error = CONCAT('Stock insuficiente de cinta aislante. Disponible: ', stock_disponible, ', Solicitado: ', NEW.cinta_aislante);
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = mensaje_error;
        END IF;
    END IF;
    
    -- Validar amarres negros
    IF NEW.amarres_negros > 0 THEN
        SELECT cantidad_disponible INTO stock_disponible 
        FROM stock_general 
        WHERE codigo_material = 'amarres_negros';
        
        IF stock_disponible < NEW.amarres_negros THEN
            SET mensaje_error = CONCAT('Stock insuficiente de amarres negros. Disponible: ', stock_disponible, ', Solicitado: ', NEW.amarres_negros);
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = mensaje_error;
        END IF;
    END IF;
    
    -- Validar amarres blancos
    IF NEW.amarres_blancos > 0 THEN
        SELECT cantidad_disponible INTO stock_disponible 
        FROM stock_general 
        WHERE codigo_material = 'amarres_blancos';
        
        IF stock_disponible < NEW.amarres_blancos THEN
            SET mensaje_error = CONCAT('Stock insuficiente de amarres blancos. Disponible: ', stock_disponible, ', Solicitado: ', NEW.amarres_blancos);
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = mensaje_error;
        END IF;
    END IF;
    
END//

DELIMITER ;