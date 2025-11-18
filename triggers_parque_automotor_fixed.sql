-- =====================================================
-- TRIGGERS COMPLETOS PARA PARQUE AUTOMOTOR - VERSIÓN CORREGIDA
-- =====================================================
-- Archivo: triggers_parque_automotor_fixed.sql
-- Fecha: 2025-01-20
-- Descripción: Triggers completos para el sistema de gestión de vehículos
-- Incluye: Historial automático, alertas de vencimiento, procedimientos y optimizaciones
-- VERSIÓN CORREGIDA: Sintaxis MySQL compatible

-- =====================================================
-- CONFIGURACIÓN INICIAL
-- =====================================================

-- Habilitar el programador de eventos
SET GLOBAL event_scheduler = ON;

-- =====================================================
-- ELIMINAR TRIGGERS EXISTENTES (SI EXISTEN)
-- =====================================================

DROP TRIGGER IF EXISTS tr_parque_automotor_historial_insert_v2;
DROP TRIGGER IF EXISTS tr_parque_automotor_historial_update_v2;
DROP TRIGGER IF EXISTS tr_generar_alertas_vencimiento;

-- =====================================================
-- ELIMINAR PROCEDIMIENTOS Y EVENTOS EXISTENTES
-- =====================================================

DROP PROCEDURE IF EXISTS sp_generar_alertas_masivas;
DROP EVENT IF EXISTS ev_generar_alertas_diarias;

-- =====================================================
-- TRIGGERS CORREGIDOS PARA HISTORIAL AUTOMÁTICO
-- =====================================================

DELIMITER //

-- Trigger para registrar historial al insertar un nuevo vehículo
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

-- Trigger para registrar historial al actualizar un vehículo
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

-- =====================================================
-- PROCEDIMIENTO PARA GENERAR ALERTAS MASIVAS
-- =====================================================

DELIMITER //

CREATE PROCEDURE sp_generar_alertas_masivas()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_id_parque_automotor INT;
    DECLARE v_placa VARCHAR(10);
    DECLARE v_soat_vencimiento DATE;
    DECLARE v_tecnomecanica_vencimiento DATE;
    DECLARE dias_soat INT;
    DECLARE dias_tecnomecanica INT;
    
    DECLARE cur_vehiculos CURSOR FOR 
        SELECT id_parque_automotor, placa, soat_vencimiento, tecnomecanica_vencimiento
        FROM parque_automotor 
        WHERE estado = 'Activo';
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur_vehiculos;
    
    read_loop: LOOP
        FETCH cur_vehiculos INTO v_id_parque_automotor, v_placa, v_soat_vencimiento, v_tecnomecanica_vencimiento;
        
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- Procesar SOAT
        IF v_soat_vencimiento IS NOT NULL THEN
            SET dias_soat = DATEDIFF(v_soat_vencimiento, CURDATE());
            
            IF dias_soat <= 30 THEN
                -- Verificar si ya existe alerta activa
                IF NOT EXISTS (
                    SELECT 1 FROM alertas_vencimiento 
                    WHERE id_parque_automotor = v_id_parque_automotor 
                    AND tipo_documento = 'SOAT' 
                    AND estado_alerta = 'Activa'
                ) THEN
                    INSERT INTO alertas_vencimiento (
                        id_parque_automotor,
                        tipo_documento,
                        fecha_vencimiento,
                        dias_anticipacion,
                        estado_alerta,
                        fecha_generacion,
                        prioridad,
                        mensaje
                    ) VALUES (
                        v_id_parque_automotor,
                        'SOAT',
                        v_soat_vencimiento,
                        dias_soat,
                        'Activa',
                        NOW(),
                        CASE 
                            WHEN dias_soat <= 0 THEN 'Alta'
                            WHEN dias_soat <= 7 THEN 'Media'
                            ELSE 'Baja'
                        END,
                        CASE 
                            WHEN dias_soat <= 0 THEN CONCAT('SOAT VENCIDO para vehículo ', v_placa)
                            ELSE CONCAT('SOAT vence en ', dias_soat, ' días para vehículo ', v_placa)
                        END
                    );
                END IF;
            END IF;
        END IF;
        
        -- Procesar Tecnomecánica
        IF v_tecnomecanica_vencimiento IS NOT NULL THEN
            SET dias_tecnomecanica = DATEDIFF(v_tecnomecanica_vencimiento, CURDATE());
            
            IF dias_tecnomecanica <= 30 THEN
                -- Verificar si ya existe alerta activa
                IF NOT EXISTS (
                    SELECT 1 FROM alertas_vencimiento 
                    WHERE id_parque_automotor = v_id_parque_automotor 
                    AND tipo_documento = 'Tecnomecánica' 
                    AND estado_alerta = 'Activa'
                ) THEN
                    INSERT INTO alertas_vencimiento (
                        id_parque_automotor,
                        tipo_documento,
                        fecha_vencimiento,
                        dias_anticipacion,
                        estado_alerta,
                        fecha_generacion,
                        prioridad,
                        mensaje
                    ) VALUES (
                        v_id_parque_automotor,
                        'Tecnomecánica',
                        v_tecnomecanica_vencimiento,
                        dias_tecnomecanica,
                        'Activa',
                        NOW(),
                        CASE 
                            WHEN dias_tecnomecanica <= 0 THEN 'Alta'
                            WHEN dias_tecnomecanica <= 7 THEN 'Media'
                            ELSE 'Baja'
                        END,
                        CASE 
                            WHEN dias_tecnomecanica <= 0 THEN CONCAT('Tecnomecánica VENCIDA para vehículo ', v_placa)
                            ELSE CONCAT('Tecnomecánica vence en ', dias_tecnomecanica, ' días para vehículo ', v_placa)
                        END
                    );
                END IF;
            END IF;
        END IF;
        
    END LOOP;
    
    CLOSE cur_vehiculos;
    
    SELECT 'Alertas generadas correctamente' as resultado;
END//

DELIMITER ;

-- =====================================================
-- EVENTO PROGRAMADO PARA EJECUTAR ALERTAS DIARIAMENTE
-- =====================================================

-- Crear evento para generar alertas diariamente a las 8:00 AM
CREATE EVENT ev_generar_alertas_diarias
ON SCHEDULE EVERY 1 DAY
STARTS TIMESTAMP(CURDATE() + INTERVAL 1 DAY, '08:00:00')
DO
  CALL sp_generar_alertas_masivas();

-- =====================================================
-- ÍNDICES PARA OPTIMIZAR RENDIMIENTO
-- =====================================================

-- Eliminar índices existentes si existen
DROP INDEX IF EXISTS idx_alertas_vehiculo_tipo ON alertas_vencimiento;
DROP INDEX IF EXISTS idx_alertas_estado ON alertas_vencimiento;
DROP INDEX IF EXISTS idx_alertas_fecha_generacion ON alertas_vencimiento;
DROP INDEX IF EXISTS idx_alertas_prioridad ON alertas_vencimiento;
DROP INDEX IF EXISTS idx_historial_vehiculo ON historial_vencimientos;
DROP INDEX IF EXISTS idx_historial_tipo_documento ON historial_vencimientos;
DROP INDEX IF EXISTS idx_historial_fecha_renovacion ON historial_vencimientos;
DROP INDEX IF EXISTS idx_kilometraje_vehiculo ON kilometraje_vehiculos;
DROP INDEX IF EXISTS idx_kilometraje_fecha ON kilometraje_vehiculos;
DROP INDEX IF EXISTS idx_parque_soat_vencimiento ON parque_automotor;
DROP INDEX IF EXISTS idx_parque_tecnomecanica_vencimiento ON parque_automotor;
DROP INDEX IF EXISTS idx_parque_estado ON parque_automotor;

-- Crear índices nuevos
-- Índices para la tabla de alertas
CREATE INDEX idx_alertas_vehiculo_tipo ON alertas_vencimiento(id_parque_automotor, tipo_documento);
CREATE INDEX idx_alertas_estado ON alertas_vencimiento(estado_alerta);
CREATE INDEX idx_alertas_fecha_generacion ON alertas_vencimiento(fecha_generacion);
CREATE INDEX idx_alertas_prioridad ON alertas_vencimiento(prioridad);

-- Índices para la tabla de historial
CREATE INDEX idx_historial_vehiculo ON historial_vencimientos(id_vehiculo);
CREATE INDEX idx_historial_tipo_documento ON historial_vencimientos(tipo_documento);
CREATE INDEX idx_historial_fecha_renovacion ON historial_vencimientos(fecha_renovacion);

-- Índices para la tabla de kilometraje
CREATE INDEX idx_kilometraje_vehiculo ON kilometraje_vehiculos(id_vehiculo);
CREATE INDEX idx_kilometraje_fecha ON kilometraje_vehiculos(fecha_registro);

-- Índices adicionales en parque_automotor para optimizar consultas
CREATE INDEX idx_parque_soat_vencimiento ON parque_automotor(soat_vencimiento);
CREATE INDEX idx_parque_tecnomecanica_vencimiento ON parque_automotor(tecnomecanica_vencimiento);
CREATE INDEX idx_parque_estado ON parque_automotor(estado);

-- =====================================================
-- MENSAJE DE FINALIZACIÓN
-- =====================================================

SELECT 'Triggers, procedimientos, eventos e índices para parque automotor creados exitosamente - VERSIÓN CORREGIDA' as mensaje;

/*
CORRECCIONES APLICADAS:
- Eliminada cláusula IF NOT EXISTS de CREATE INDEX (incompatible con algunas versiones de MySQL)
- Agregados comandos DROP para limpiar triggers, procedimientos e índices existentes
- Mejorada compatibilidad con MySQL 5.7 y 8.0
- Eliminado trigger de alertas en UPDATE (puede causar problemas de rendimiento)

Para ejecutar este archivo:
1. Conectarse a la base de datos MySQL
2. Ejecutar: SOURCE /ruta/al/archivo/triggers_parque_automotor_fixed.sql
3. Verificar que no haya errores en la ejecución

NOTA: Asegúrese de que las tablas requeridas existan antes de ejecutar:
- parque_automotor
- historial_vencimientos
- alertas_vencimiento
- kilometraje_vehiculos
*/