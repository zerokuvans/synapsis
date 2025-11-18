-- Triggers corregidos para el sistema de gestión de vehículos
-- Fecha: 2025-01-20
-- Descripción: Triggers actualizados para coincidir con la estructura real de las tablas

-- =====================================================
-- TRIGGER 1: Historial automático de cambios en vehículos
-- =====================================================

DELIMITER //

CREATE TRIGGER tr_parque_automotor_historial_insert_v2
AFTER INSERT ON parque_automotor
FOR EACH ROW
BEGIN
    -- Registrar SOAT inicial
    IF NEW.soat_vencimiento IS NOT NULL THEN
        INSERT INTO historial_vencimientos (
            id_vehiculo,
            tipo_documento,
            fecha_vencimiento_anterior,
            fecha_vencimiento_nueva,
            fecha_renovacion,
            estado_documento,
            observaciones,
            usuario_actualizacion
        ) VALUES (
            NEW.id_parque_automotor,
            'soat',
            NULL,
            NEW.soat_vencimiento,
            CURDATE(),
            'vigente',
            CONCAT('Registro inicial del vehículo: ', NEW.placa),
            1
        );
    END IF;
    
    -- Registrar Tecnomecánica inicial
    IF NEW.tecnomecanica_vencimiento IS NOT NULL THEN
        INSERT INTO historial_vencimientos (
            id_vehiculo,
            tipo_documento,
            fecha_vencimiento_anterior,
            fecha_vencimiento_nueva,
            fecha_renovacion,
            estado_documento,
            observaciones,
            usuario_actualizacion
        ) VALUES (
            NEW.id_parque_automotor,
            'tecnomecanica',
            NULL,
            NEW.tecnomecanica_vencimiento,
            CURDATE(),
            'vigente',
            CONCAT('Registro inicial del vehículo: ', NEW.placa),
            1
        );
    END IF;
    
    -- Registrar kilometraje inicial
    IF NEW.kilometraje_actual IS NOT NULL AND NEW.kilometraje_actual > 0 THEN
        INSERT INTO kilometraje_vehiculos (
            id_vehiculo,
            kilometraje_actual,
            kilometraje_anterior,
            diferencia_km,
            fecha_registro,
            tipo_registro,
            usuario_registro,
            observaciones
        ) VALUES (
            NEW.id_parque_automotor,
            NEW.kilometraje_actual,
            0,
            NEW.kilometraje_actual,
            CURDATE(),
            'asignacion',
            1,
            CONCAT('Kilometraje inicial del vehículo: ', NEW.placa)
        );
    END IF;
END//

CREATE TRIGGER tr_parque_automotor_historial_update_v2
AFTER UPDATE ON parque_automotor
FOR EACH ROW
BEGIN
    -- Registrar cambios en SOAT
    IF (OLD.soat_vencimiento IS NULL AND NEW.soat_vencimiento IS NOT NULL) OR 
       (OLD.soat_vencimiento IS NOT NULL AND NEW.soat_vencimiento IS NOT NULL AND OLD.soat_vencimiento != NEW.soat_vencimiento) THEN
        INSERT INTO historial_vencimientos (
            id_vehiculo,
            tipo_documento,
            fecha_vencimiento_anterior,
            fecha_vencimiento_nueva,
            fecha_renovacion,
            estado_documento,
            observaciones,
            usuario_actualizacion
        ) VALUES (
            NEW.id_parque_automotor,
            'soat',
            OLD.soat_vencimiento,
            NEW.soat_vencimiento,
            CURDATE(),
            CASE 
                WHEN NEW.soat_vencimiento >= CURDATE() THEN 'vigente'
                ELSE 'vencido'
            END,
            'Actualización de fecha de vencimiento SOAT',
            1
        );
    END IF;
    
    -- Registrar cambios en Tecnomecánica
    IF (OLD.tecnomecanica_vencimiento IS NULL AND NEW.tecnomecanica_vencimiento IS NOT NULL) OR 
       (OLD.tecnomecanica_vencimiento IS NOT NULL AND NEW.tecnomecanica_vencimiento IS NOT NULL AND OLD.tecnomecanica_vencimiento != NEW.tecnomecanica_vencimiento) THEN
        INSERT INTO historial_vencimientos (
            id_vehiculo,
            tipo_documento,
            fecha_vencimiento_anterior,
            fecha_vencimiento_nueva,
            fecha_renovacion,
            estado_documento,
            observaciones,
            usuario_actualizacion
        ) VALUES (
            NEW.id_parque_automotor,
            'tecnomecanica',
            OLD.tecnomecanica_vencimiento,
            NEW.tecnomecanica_vencimiento,
            CURDATE(),
            CASE 
                WHEN NEW.tecnomecanica_vencimiento >= CURDATE() THEN 'vigente'
                ELSE 'vencido'
            END,
            'Actualización de fecha de vencimiento Tecnomecánica',
            1
        );
    END IF;
    
    -- Registrar cambios en kilometraje
    IF (OLD.kilometraje_actual IS NULL AND NEW.kilometraje_actual IS NOT NULL) OR 
       (OLD.kilometraje_actual IS NOT NULL AND NEW.kilometraje_actual IS NOT NULL AND OLD.kilometraje_actual != NEW.kilometraje_actual) THEN
        INSERT INTO kilometraje_vehiculos (
            id_vehiculo,
            kilometraje_actual,
            kilometraje_anterior,
            diferencia_km,
            fecha_registro,
            tipo_registro,
            usuario_registro,
            observaciones
        ) VALUES (
            NEW.id_parque_automotor,
            NEW.kilometraje_actual,
            COALESCE(OLD.kilometraje_actual, 0),
            NEW.kilometraje_actual - COALESCE(OLD.kilometraje_actual, 0),
            CURDATE(),
            'manual',
            1,
            'Actualización automática de kilometraje'
        );
    END IF;
END//

DELIMITER ;