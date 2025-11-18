-- Recrear triggers del parque automotor con definer correcto
USE capired;

-- Eliminar triggers existentes y recrearlos
DROP TRIGGER IF EXISTS tr_parque_automotor_update;
DROP TRIGGER IF EXISTS tr_parque_automotor_historial_insert;
DROP TRIGGER IF EXISTS tr_parque_automotor_historial_update;
DROP TRIGGER IF EXISTS tr_generar_alertas_vencimiento;

-- Trigger básico para actualizar fecha de modificación en parque_automotor
DELIMITER //
CREATE TRIGGER tr_parque_automotor_update 
    BEFORE UPDATE ON parque_automotor
    FOR EACH ROW
BEGIN
    SET NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
END//
DELIMITER ;

-- Trigger para historial de inserciones en parque_automotor
DELIMITER //
CREATE TRIGGER tr_parque_automotor_historial_insert
    AFTER INSERT ON parque_automotor
    FOR EACH ROW
BEGIN
    -- Solo insertar si existe la tabla historial_vencimientos
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'capired' AND table_name = 'historial_vencimientos') THEN
        INSERT INTO historial_vencimientos (id_vehiculo, tipo_documento, fecha_vencimiento_nueva, fecha_renovacion, estado_documento)
        VALUES (NEW.id_parque_automotor, 'soat', NEW.soat_vencimiento, COALESCE(NEW.fecha_asignacion, NOW()), 'vigente');
    END IF;
END//
DELIMITER ;

-- Trigger para historial de actualizaciones en parque_automotor
DELIMITER //
CREATE TRIGGER tr_parque_automotor_historial_update
    AFTER UPDATE ON parque_automotor
    FOR EACH ROW
BEGIN
    -- Solo insertar si existe la tabla historial_vencimientos y cambió el SOAT
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'capired' AND table_name = 'historial_vencimientos') 
       AND (OLD.soat_vencimiento != NEW.soat_vencimiento OR (OLD.soat_vencimiento IS NULL AND NEW.soat_vencimiento IS NOT NULL)) THEN
        INSERT INTO historial_vencimientos (id_vehiculo, tipo_documento, fecha_vencimiento_anterior, fecha_vencimiento_nueva, fecha_renovacion, estado_documento)
        VALUES (NEW.id_parque_automotor, 'soat', OLD.soat_vencimiento, NEW.soat_vencimiento, CURRENT_DATE, 'vigente');
    END IF;
END//
DELIMITER ;

-- Trigger básico para generar alertas de vencimiento
DELIMITER //
CREATE TRIGGER tr_generar_alertas_vencimiento
    AFTER INSERT ON parque_automotor
    FOR EACH ROW
BEGIN
    -- Generar alerta si el SOAT vence en menos de 30 días
    IF NEW.soat_vencimiento IS NOT NULL AND NEW.soat_vencimiento <= DATE_ADD(CURRENT_DATE, INTERVAL 30 DAY) THEN
        INSERT INTO eventos_sistema (tipo_evento, descripcion, fecha_evento, tabla_afectada, id_registro)
        VALUES ('alerta_vencimiento', CONCAT('SOAT del vehículo ', NEW.placa, ' vence el ', NEW.soat_vencimiento), NOW(), 'parque_automotor', NEW.id_parque_automotor);
    END IF;
END//
DELIMITER ;