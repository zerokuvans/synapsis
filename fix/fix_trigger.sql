USE capired;

DELIMITER //

CREATE TRIGGER alerta_stock_bajo
AFTER UPDATE ON stock_general
FOR EACH ROW
BEGIN
    IF NEW.cantidad_disponible < NEW.cantidad_minima AND NEW.cantidad_disponible != OLD.cantidad_disponible THEN
        INSERT INTO alertas_stock (material, stock_actual, stock_minimo)
        VALUES (NEW.codigo_material, NEW.cantidad_disponible, NEW.cantidad_minima);
        
        INSERT INTO eventos_sistema (tipo, mensaje)
        VALUES (
            'ALERTA_STOCK_BAJO',
            CONCAT('Stock bajo detectado para: ', NEW.codigo_material, ' (', NEW.cantidad_disponible, '/', NEW.cantidad_minima, ')')
        );
    END IF;
END//

DELIMITER ;