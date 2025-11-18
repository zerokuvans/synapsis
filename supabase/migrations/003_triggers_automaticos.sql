-- Triggers automáticos para el sistema de gestión de vehículos
-- Fecha: 2025-01-20
-- Descripción: Triggers para historial automático y generación de alertas

-- =====================================================
-- TRIGGER 1: Historial automático de cambios en vehículos
-- =====================================================

DELIMITER //

CREATE TRIGGER tr_parque_automotor_historial_insert
AFTER INSERT ON parque_automotor
FOR EACH ROW
BEGIN
    INSERT INTO historial_vencimientos (
        id_parque_automotor,
        tipo_documento,
        fecha_vencimiento_anterior,
        fecha_vencimiento_nueva,
        fecha_renovacion,
        observaciones,
        usuario_modificacion
    ) VALUES (
        NEW.id_parque_automotor,
        'SOAT',
        NULL,
        NEW.soat_vencimiento,
        NOW(),
        CONCAT('Registro inicial del vehículo: ', NEW.placa),
        'SISTEMA'
    );
    
    INSERT INTO historial_vencimientos (
        id_parque_automotor,
        tipo_documento,
        fecha_vencimiento_anterior,
        fecha_vencimiento_nueva,
        fecha_renovacion,
        observaciones,
        usuario_modificacion
    ) VALUES (
        NEW.id_parque_automotor,
        'Tecnomecánica',
        NULL,
        NEW.tecnomecanica_vencimiento,
        NOW(),
        CONCAT('Registro inicial del vehículo: ', NEW.placa),
        'SISTEMA'
    );
END//

CREATE TRIGGER tr_parque_automotor_historial_update
AFTER UPDATE ON parque_automotor
FOR EACH ROW
BEGIN
    -- Registrar cambios en SOAT
    IF OLD.soat_vencimiento != NEW.soat_vencimiento THEN
        INSERT INTO historial_vencimientos (
            id_parque_automotor,
            tipo_documento,
            fecha_vencimiento_anterior,
            fecha_vencimiento_nueva,
            fecha_renovacion,
            observaciones,
            usuario_modificacion
        ) VALUES (
            NEW.id_parque_automotor,
            'SOAT',
            OLD.soat_vencimiento,
            NEW.soat_vencimiento,
            NOW(),
            'Actualización de fecha de vencimiento SOAT',
            'SISTEMA'
        );
    END IF;
    
    -- Registrar cambios en Tecnomecánica
    IF OLD.tecnomecanica_vencimiento != NEW.tecnomecanica_vencimiento THEN
        INSERT INTO historial_vencimientos (
            id_parque_automotor,
            tipo_documento,
            fecha_vencimiento_anterior,
            fecha_vencimiento_nueva,
            fecha_renovacion,
            observaciones,
            usuario_modificacion
        ) VALUES (
            NEW.id_parque_automotor,
            'Tecnomecánica',
            OLD.tecnomecanica_vencimiento,
            NEW.tecnomecanica_vencimiento,
            NOW(),
            'Actualización de fecha de vencimiento Tecnomecánica',
            'SISTEMA'
        );
    END IF;
    
    -- Registrar cambios en kilometraje
    IF OLD.kilometraje_actual != NEW.kilometraje_actual THEN
        INSERT INTO kilometraje_vehiculos (
            id_parque_automotor,
            kilometraje_anterior,
            kilometraje_nuevo,
            fecha_actualizacion,
            diferencia_km,
            observaciones
        ) VALUES (
            NEW.id_parque_automotor,
            OLD.kilometraje_actual,
            NEW.kilometraje_actual,
            NOW(),
            NEW.kilometraje_actual - OLD.kilometraje_actual,
            'Actualización automática de kilometraje'
        );
    END IF;
END//

DELIMITER ;

-- =====================================================
-- TRIGGER 2: Generación automática de alertas
-- =====================================================

DELIMITER //

CREATE TRIGGER tr_generar_alertas_vencimiento
AFTER UPDATE ON parque_automotor
FOR EACH ROW
BEGIN
    DECLARE dias_soat INT DEFAULT 0;
    DECLARE dias_tecnomecanica INT DEFAULT 0;
    
    -- Calcular días hasta vencimiento
    IF NEW.soat_vencimiento IS NOT NULL THEN
        SET dias_soat = DATEDIFF(NEW.soat_vencimiento, CURDATE());
    END IF;
    
    IF NEW.tecnomecanica_vencimiento IS NOT NULL THEN
        SET dias_tecnomecanica = DATEDIFF(NEW.tecnomecanica_vencimiento, CURDATE());
    END IF;
    
    -- Generar alerta para SOAT (30 días antes o vencido)
    IF dias_soat <= 30 AND NEW.estado = 'Activo' THEN
        -- Verificar si ya existe una alerta activa para este documento
        IF NOT EXISTS (
            SELECT 1 FROM alertas_vencimiento 
            WHERE id_parque_automotor = NEW.id_parque_automotor 
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
                NEW.id_parque_automotor,
                'SOAT',
                NEW.soat_vencimiento,
                dias_soat,
                'Activa',
                NOW(),
                CASE 
                    WHEN dias_soat <= 0 THEN 'Alta'
                    WHEN dias_soat <= 7 THEN 'Media'
                    ELSE 'Baja'
                END,
                CASE 
                    WHEN dias_soat <= 0 THEN CONCAT('SOAT VENCIDO para vehículo ', NEW.placa)
                    ELSE CONCAT('SOAT vence en ', dias_soat, ' días para vehículo ', NEW.placa)
                END
            );
        END IF;
    END IF;
    
    -- Generar alerta para Tecnomecánica (30 días antes o vencido)
    IF dias_tecnomecanica <= 30 AND NEW.estado = 'Activo' THEN
        -- Verificar si ya existe una alerta activa para este documento
        IF NOT EXISTS (
            SELECT 1 FROM alertas_vencimiento 
            WHERE id_parque_automotor = NEW.id_parque_automotor 
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
                NEW.id_parque_automotor,
                'Tecnomecánica',
                NEW.tecnomecanica_vencimiento,
                dias_tecnomecanica,
                'Activa',
                NOW(),
                CASE 
                    WHEN dias_tecnomecanica <= 0 THEN 'Alta'
                    WHEN dias_tecnomecanica <= 7 THEN 'Media'
                    ELSE 'Baja'
                END,
                CASE 
                    WHEN dias_tecnomecanica <= 0 THEN CONCAT('Tecnomecánica VENCIDA para vehículo ', NEW.placa)
                    ELSE CONCAT('Tecnomecánica vence en ', dias_tecnomecanica, ' días para vehículo ', NEW.placa)
                END
            );
        END IF;
    END IF;
    
    -- Marcar alertas como resueltas si se renovaron los documentos
    IF OLD.soat_vencimiento != NEW.soat_vencimiento AND NEW.soat_vencimiento > CURDATE() THEN
        UPDATE alertas_vencimiento 
        SET estado_alerta = 'Resuelta', 
            fecha_resolucion = NOW(),
            observaciones_resolucion = 'Documento renovado'
        WHERE id_parque_automotor = NEW.id_parque_automotor 
        AND tipo_documento = 'SOAT' 
        AND estado_alerta = 'Activa';
    END IF;
    
    IF OLD.tecnomecanica_vencimiento != NEW.tecnomecanica_vencimiento AND NEW.tecnomecanica_vencimiento > CURDATE() THEN
        UPDATE alertas_vencimiento 
        SET estado_alerta = 'Resuelta', 
            fecha_resolucion = NOW(),
            observaciones_resolucion = 'Documento renovado'
        WHERE id_parque_automotor = NEW.id_parque_automotor 
        AND tipo_documento = 'Tecnomecánica' 
        AND estado_alerta = 'Activa';
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

-- Habilitar el programador de eventos
SET GLOBAL event_scheduler = ON;

-- Crear evento para generar alertas diariamente a las 8:00 AM
CREATE EVENT IF NOT EXISTS ev_generar_alertas_diarias
ON SCHEDULE EVERY 1 DAY
STARTS TIMESTAMP(CURDATE() + INTERVAL 1 DAY, '08:00:00')
DO
  CALL sp_generar_alertas_masivas();

-- =====================================================
-- ÍNDICES PARA OPTIMIZAR RENDIMIENTO
-- =====================================================

-- Índices para la tabla de alertas
CREATE INDEX IF NOT EXISTS idx_alertas_vehiculo_tipo ON alertas_vencimiento(id_parque_automotor, tipo_documento);
CREATE INDEX IF NOT EXISTS idx_alertas_estado ON alertas_vencimiento(estado_alerta);
CREATE INDEX IF NOT EXISTS idx_alertas_fecha_generacion ON alertas_vencimiento(fecha_generacion);
CREATE INDEX IF NOT EXISTS idx_alertas_prioridad ON alertas_vencimiento(prioridad);

-- Índices para la tabla de historial
CREATE INDEX IF NOT EXISTS idx_historial_vehiculo ON historial_vencimientos(id_parque_automotor);
CREATE INDEX IF NOT EXISTS idx_historial_tipo_documento ON historial_vencimientos(tipo_documento);
CREATE INDEX IF NOT EXISTS idx_historial_fecha_renovacion ON historial_vencimientos(fecha_renovacion);

-- Índices para la tabla de kilometraje
CREATE INDEX IF NOT EXISTS idx_kilometraje_vehiculo ON kilometraje_vehiculos(id_parque_automotor);
CREATE INDEX IF NOT EXISTS idx_kilometraje_fecha ON kilometraje_vehiculos(fecha_actualizacion);

-- Índices adicionales en parque_automotor para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_parque_soat_vencimiento ON parque_automotor(soat_vencimiento);
CREATE INDEX IF NOT EXISTS idx_parque_tecnomecanica_vencimiento ON parque_automotor(tecnomecanica_vencimiento);
CREATE INDEX IF NOT EXISTS idx_parque_estado ON parque_automotor(estado);

PRINT 'Triggers automáticos, procedimientos e índices creados exitosamente';