USE capired;

DROP TRIGGER IF EXISTS alerta_stock_bajo;

DELIMITER //

CREATE TRIGGER alerta_stock_bajo
AFTER UPDATE ON stock_general
FOR EACH ROW
BEGIN
    -- Solo ejecutar si la cantidad disponible cambió
    IF NEW.cantidad_disponible != OLD.cantidad_disponible THEN
        
        -- Verificar si el stock está por debajo del mínimo
        IF NEW.cantidad_disponible < NEW.cantidad_minima THEN
            
            -- Insertar alerta en tabla alertas_stock
            INSERT INTO alertas_stock (
                material, 
                stock_actual, 
                stock_minimo, 
                diferencia, 
                fecha_alerta, 
                estado
            ) VALUES (
                NEW.codigo_material,
                NEW.cantidad_disponible,
                NEW.cantidad_minima,
                (NEW.cantidad_minima - NEW.cantidad_disponible),
                NOW(),
                'PENDIENTE'
            );
            
            -- Log en tabla de eventos
            INSERT INTO eventos_sistema (tipo, mensaje, fecha)
            VALUES ('STOCK_BAJO', CONCAT('Material ', NEW.codigo_material, ' tiene stock bajo: ', NEW.cantidad_disponible, ' (mínimo: ', NEW.cantidad_minima, ')'), NOW());
            
        END IF;
        
        -- Verificar si el stock llegó a cero
        IF NEW.cantidad_disponible <= 0 THEN
            
            -- Log de stock agotado
            INSERT INTO eventos_sistema (tipo, mensaje, fecha)
            VALUES ('STOCK_AGOTADO', CONCAT('Material ', NEW.codigo_material, ' AGOTADO. Stock actual: ', NEW.cantidad_disponible), NOW());
            
        END IF;
        
    END IF;
    
END//

DELIMITER ;