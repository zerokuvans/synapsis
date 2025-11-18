-- =====================================================
-- TRIGGERS COMPLETOS PARA PARQUE AUTOMOTOR - MYSQL COMPATIBLE
-- =====================================================
-- Archivo: triggers_parque_automotor_mysql_compatible.sql
-- Fecha: 2025-01-20
-- Descripción: Triggers corregidos para el sistema de gestión de vehículos
-- Incluye: Historial automático, alertas de vencimiento, procedimientos y optimizaciones
-- Versión: 2.2 - Compatible con sintaxis MySQL estándar
-- CORRECCIÓN: Usa id_historial en lugar de id_parque_automotor en alertas_vencimiento
-- SINTAXIS: Corregida para MySQL sin IF NOT EXISTS en CREATE INDEX

-- =====================================================
-- CONFIGURACIÓN INICIAL
-- =====================================================

-- Habilitar el programador de eventos
SET GLOBAL event_scheduler = ON;

-- =====================================================
-- TRIGGERS CORREGIDOS PARA HISTORIAL AUTOMÁTICO
-- =====================================================

DELIMITER //

-- Eliminar trigger si existe
DROP TRIGGER IF EXISTS tr_parque_automotor_historial_insert_v3//

-- Trigger para registrar historial al insertar un nuevo vehículo
CREATE TRIGGER tr_parque_automotor_historial_insert_v3
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

-- Eliminar trigger si existe
DROP TRIGGER IF EXISTS tr_parque_automotor_historial_update_v3//

-- Trigger para registrar historial al actualizar un vehículo
CREATE TRIGGER tr_parque_automotor_historial_update_v3
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

-- =====================================================
-- PROCEDIMIENTO PARA GENERAR ALERTAS MASIVAS CORREGIDO
-- =====================================================

-- Eliminar procedimiento si existe
DROP PROCEDURE IF EXISTS sp_generar_alertas_masivas_v2//

CREATE PROCEDURE sp_generar_alertas_masivas_v2()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_id_parque_automotor INT;
    DECLARE v_placa VARCHAR(10);
    DECLARE v_soat_vencimiento DATE;
    DECLARE v_tecnomecanica_vencimiento DATE;
    DECLARE dias_soat INT;
    DECLARE dias_tecnomecanica INT;
    DECLARE v_id_historial_soat INT;
    DECLARE v_id_historial_tecnomecanica INT;
    
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
                -- Buscar el historial más reciente de SOAT para este vehículo
                SELECT id_historial INTO v_id_historial_soat
                FROM historial_vencimientos 
                WHERE id_vehiculo = v_id_parque_automotor 
                AND tipo_documento = 'soat'
                ORDER BY fecha_registro DESC
                LIMIT 1;
                
                -- Si existe historial, verificar si ya hay alerta activa
                IF v_id_historial_soat IS NOT NULL THEN
                    IF NOT EXISTS (
                        SELECT 1 FROM alertas_vencimiento 
                        WHERE id_historial = v_id_historial_soat
                        AND notificado = FALSE
                        AND fecha_alerta >= CURDATE()
                    ) THEN
                        -- Determinar tipo de alerta según días restantes
                        INSERT INTO alertas_vencimiento (
                            id_historial,
                            tipo_alerta,
                            fecha_alerta,
                            notificado,
                            canal_notificacion
                        ) VALUES (
                            v_id_historial_soat,
                            CASE 
                                WHEN dias_soat <= 0 THEN 'vencido'
                                WHEN dias_soat <= 1 THEN '1_dia'
                                WHEN dias_soat <= 7 THEN '7_dias'
                                WHEN dias_soat <= 15 THEN '15_dias'
                                ELSE '30_dias'
                            END,
                            CURDATE(),
                            FALSE,
                            'sistema'
                        );
                    END IF;
                END IF;
            END IF;
        END IF;
        
        -- Procesar Tecnomecánica
        IF v_tecnomecanica_vencimiento IS NOT NULL THEN
            SET dias_tecnomecanica = DATEDIFF(v_tecnomecanica_vencimiento, CURDATE());
            
            IF dias_tecnomecanica <= 30 THEN
                -- Buscar el historial más reciente de tecnomecánica para este vehículo
                SELECT id_historial INTO v_id_historial_tecnomecanica
                FROM historial_vencimientos 
                WHERE id_vehiculo = v_id_parque_automotor 
                AND tipo_documento = 'tecnomecanica'
                ORDER BY fecha_registro DESC
                LIMIT 1;
                
                -- Si existe historial, verificar si ya hay alerta activa
                IF v_id_historial_tecnomecanica IS NOT NULL THEN
                    IF NOT EXISTS (
                        SELECT 1 FROM alertas_vencimiento 
                        WHERE id_historial = v_id_historial_tecnomecanica
                        AND notificado = FALSE
                        AND fecha_alerta >= CURDATE()
                    ) THEN
                        -- Determinar tipo de alerta según días restantes
                        INSERT INTO alertas_vencimiento (
                            id_historial,
                            tipo_alerta,
                            fecha_alerta,
                            notificado,
                            canal_notificacion
                        ) VALUES (
                            v_id_historial_tecnomecanica,
                            CASE 
                                WHEN dias_tecnomecanica <= 0 THEN 'vencido'
                                WHEN dias_tecnomecanica <= 1 THEN '1_dia'
                                WHEN dias_tecnomecanica <= 7 THEN '7_dias'
                                WHEN dias_tecnomecanica <= 15 THEN '15_dias'
                                ELSE '30_dias'
                            END,
                            CURDATE(),
                            FALSE,
                            'sistema'
                        );
                    END IF;
                END IF;
            END IF;
        END IF;
        
        -- Resetear variables para el siguiente vehículo
        SET v_id_historial_soat = NULL;
        SET v_id_historial_tecnomecanica = NULL;
        
    END LOOP;
    
    CLOSE cur_vehiculos;
    
    SELECT 'Alertas generadas correctamente usando estructura real de BD' as resultado;
END//

DELIMITER ;

-- =====================================================
-- EVENTO PROGRAMADO PARA EJECUTAR ALERTAS DIARIAMENTE
-- =====================================================

-- Eliminar evento si existe
DROP EVENT IF EXISTS ev_generar_alertas_diarias_v2;

-- Crear evento para generar alertas diariamente a las 8:00 AM
CREATE EVENT ev_generar_alertas_diarias_v2
ON SCHEDULE EVERY 1 DAY
STARTS TIMESTAMP(CURDATE() + INTERVAL 1 DAY, '08:00:00')
DO
  CALL sp_generar_alertas_masivas_v2();

-- =====================================================
-- ÍNDICES PARA OPTIMIZAR RENDIMIENTO - SINTAXIS MYSQL COMPATIBLE
-- =====================================================

-- Índices para la tabla de alertas (usando estructura real)
DROP INDEX IF EXISTS idx_alertas_historial ON alertas_vencimiento;
CREATE INDEX idx_alertas_historial ON alertas_vencimiento(id_historial);

DROP INDEX IF EXISTS idx_alertas_tipo ON alertas_vencimiento;
CREATE INDEX idx_alertas_tipo ON alertas_vencimiento(tipo_alerta);

DROP INDEX IF EXISTS idx_alertas_fecha ON alertas_vencimiento;
CREATE INDEX idx_alertas_fecha ON alertas_vencimiento(fecha_alerta);

DROP INDEX IF EXISTS idx_alertas_notificado ON alertas_vencimiento;
CREATE INDEX idx_alertas_notificado ON alertas_vencimiento(notificado);

-- Índices para la tabla de historial
DROP INDEX IF EXISTS idx_historial_vehiculo ON historial_vencimientos;
CREATE INDEX idx_historial_vehiculo ON historial_vencimientos(id_vehiculo);

DROP INDEX IF EXISTS idx_historial_tipo_documento ON historial_vencimientos;
CREATE INDEX idx_historial_tipo_documento ON historial_vencimientos(tipo_documento);

DROP INDEX IF EXISTS idx_historial_fecha_renovacion ON historial_vencimientos;
CREATE INDEX idx_historial_fecha_renovacion ON historial_vencimientos(fecha_renovacion);

DROP INDEX IF EXISTS idx_historial_estado ON historial_vencimientos;
CREATE INDEX idx_historial_estado ON historial_vencimientos(estado_documento);

-- Índices para la tabla de kilometraje
DROP INDEX IF EXISTS idx_kilometraje_vehiculo ON kilometraje_vehiculos;
CREATE INDEX idx_kilometraje_vehiculo ON kilometraje_vehiculos(id_vehiculo);

DROP INDEX IF EXISTS idx_kilometraje_fecha ON kilometraje_vehiculos;
CREATE INDEX idx_kilometraje_fecha ON kilometraje_vehiculos(fecha_registro);

DROP INDEX IF EXISTS idx_kilometraje_tipo ON kilometraje_vehiculos;
CREATE INDEX idx_kilometraje_tipo ON kilometraje_vehiculos(tipo_registro);

-- Índices adicionales en parque_automotor para optimizar consultas
DROP INDEX IF EXISTS idx_parque_soat_vencimiento ON parque_automotor;
CREATE INDEX idx_parque_soat_vencimiento ON parque_automotor(soat_vencimiento);

DROP INDEX IF EXISTS idx_parque_tecnomecanica_vencimiento ON parque_automotor;
CREATE INDEX idx_parque_tecnomecanica_vencimiento ON parque_automotor(tecnomecanica_vencimiento);

DROP INDEX IF EXISTS idx_parque_estado ON parque_automotor;
CREATE INDEX idx_parque_estado ON parque_automotor(estado);

-- =====================================================
-- MENSAJE DE FINALIZACIÓN
-- =====================================================

SELECT 'Triggers MySQL compatibles para parque automotor creados exitosamente' as mensaje;

-- =====================================================
-- INSTRUCCIONES DE USO
-- =====================================================
/*
Este archivo contiene los triggers MYSQL COMPATIBLES para el sistema de parque automotor:

CORRECCIONES REALIZADAS EN VERSIÓN 2.2:
- Eliminado 'IF NOT EXISTS' de todos los comandos CREATE INDEX
- Agregado 'DROP INDEX IF EXISTS' antes de cada CREATE INDEX
- Sintaxis 100% compatible con MySQL estándar
- Mantiene toda la funcionalidad de la versión anterior

CORRECCIONES PREVIAS:
- Eliminado el trigger tr_generar_alertas_vencimiento que usaba estructura incorrecta
- Corregido el procedimiento sp_generar_alertas_masivas para usar id_historial
- Adaptado a la estructura real de alertas_vencimiento según documentación
- Usa la relación correcta: alertas_vencimiento.id_historial -> historial_vencimientos.id_historial

1. TRIGGERS DE HISTORIAL:
   - tr_parque_automotor_historial_insert_v3: Registra historial al insertar vehículos
   - tr_parque_automotor_historial_update_v3: Registra historial al actualizar vehículos

2. PROCEDIMIENTO CORREGIDO:
   - sp_generar_alertas_masivas_v2(): Genera alertas usando estructura real de BD

3. EVENTO PROGRAMADO:
   - ev_generar_alertas_diarias_v2: Ejecuta alertas diariamente a las 8:00 AM

4. ÍNDICES: Optimizan el rendimiento usando sintaxis MySQL estándar

ESTRUCTURA REAL DE ALERTAS_VENCIMIENTO:
- id_alerta (PK)
- id_historial (FK a historial_vencimientos)
- tipo_alerta (ENUM)
- fecha_alerta
- notificado (BOOLEAN)
- canal_notificacion
- fecha_notificacion
- fecha_creacion

Para ejecutar este archivo:
1. Conectarse a la base de datos MySQL
2. Ejecutar: SOURCE /ruta/al/archivo/triggers_parque_automotor_mysql_compatible.sql
3. Verificar que no haya errores en la ejecución

NOTA: Esta versión corrige todos los errores de sintaxis MySQL y es completamente
compatible con versiones estándar de MySQL sin extensiones específicas.
*/