-- =====================================================
-- MIGRACIÓN DEL SISTEMA DE GESTIÓN DE VEHÍCULOS
-- Fecha: 2025-01-30
-- Descripción: Creación de nuevas tablas y mejoras al sistema existente
-- =====================================================

-- 1. MEJORAS A LA TABLA EXISTENTE parque_automotor
-- =====================================================

-- Agregar campos faltantes a la tabla existente (verificando si no existen)
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE table_name = 'parque_automotor' 
     AND table_schema = 'capired' 
     AND column_name = 'fecha_actualizacion') = 0,
    'ALTER TABLE parque_automotor ADD COLUMN fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP',
    'SELECT "Column fecha_actualizacion already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE table_name = 'parque_automotor' 
     AND table_schema = 'capired' 
     AND column_name = 'kilometraje_actual') = 0,
    'ALTER TABLE parque_automotor ADD COLUMN kilometraje_actual INT DEFAULT 0',
    'SELECT "Column kilometraje_actual already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE table_name = 'parque_automotor' 
     AND table_schema = 'capired' 
     AND column_name = 'proximo_mantenimiento_km') = 0,
    'ALTER TABLE parque_automotor ADD COLUMN proximo_mantenimiento_km INT',
    'SELECT "Column proximo_mantenimiento_km already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE table_name = 'parque_automotor' 
     AND table_schema = 'capired' 
     AND column_name = 'fecha_ultimo_mantenimiento') = 0,
    'ALTER TABLE parque_automotor ADD COLUMN fecha_ultimo_mantenimiento DATE',
    'SELECT "Column fecha_ultimo_mantenimiento already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Crear índices para optimización de consultas (verificando si no existen)
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE table_name = 'parque_automotor' 
     AND table_schema = 'capired' 
     AND index_name = 'idx_parque_automotor_placa') = 0,
    'CREATE INDEX idx_parque_automotor_placa ON parque_automotor(placa)',
    'SELECT "Index idx_parque_automotor_placa already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE table_name = 'parque_automotor' 
     AND table_schema = 'capired' 
     AND index_name = 'idx_parque_automotor_estado') = 0,
    'CREATE INDEX idx_parque_automotor_estado ON parque_automotor(estado)',
    'SELECT "Index idx_parque_automotor_estado already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE table_name = 'parque_automotor' 
     AND table_schema = 'capired' 
     AND index_name = 'idx_parque_automotor_soat_vencimiento') = 0,
    'CREATE INDEX idx_parque_automotor_soat_vencimiento ON parque_automotor(soat_vencimiento)',
    'SELECT "Index idx_parque_automotor_soat_vencimiento already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE table_name = 'parque_automotor' 
     AND table_schema = 'capired' 
     AND index_name = 'idx_parque_automotor_tecnomecanica_vencimiento') = 0,
    'CREATE INDEX idx_parque_automotor_tecnomecanica_vencimiento ON parque_automotor(tecnomecanica_vencimiento)',
    'SELECT "Index idx_parque_automotor_tecnomecanica_vencimiento already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE table_name = 'parque_automotor' 
     AND table_schema = 'capired' 
     AND index_name = 'idx_parque_automotor_asignacion') = 0,
    'CREATE INDEX idx_parque_automotor_asignacion ON parque_automotor(id_codigo_consumidor)',
    'SELECT "Index idx_parque_automotor_asignacion already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2. TABLA DE HISTORIAL DE VENCIMIENTOS
-- =====================================================

-- Eliminar tablas existentes si existen
DROP TABLE IF EXISTS alertas_vencimiento;
DROP TABLE IF EXISTS historial_vencimientos;
DROP TABLE IF EXISTS kilometraje_vehiculos;

CREATE TABLE historial_vencimientos (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_vehiculo INT NOT NULL,
    tipo_documento ENUM('soat', 'tecnomecanica', 'licencia_conduccion', 'poliza_todo_riesgo', 'revision_preventiva') NOT NULL,
    fecha_vencimiento_anterior DATE,
    fecha_vencimiento_nueva DATE NOT NULL,
    fecha_renovacion DATE NOT NULL,
    estado_documento ENUM('vigente', 'vencido', 'en_tramite', 'renovado') DEFAULT 'vigente',
    costo_renovacion DECIMAL(10,2),
    entidad_emisora VARCHAR(100),
    numero_documento VARCHAR(50),
    observaciones TEXT,
    usuario_actualizacion INT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_vehiculo) REFERENCES parque_automotor(id_parque_automotor) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizacion) REFERENCES recurso_operativo(id_codigo_consumidor)
);

-- Crear índices para historial
CREATE INDEX idx_historial_vehiculo ON historial_vencimientos(id_vehiculo);
CREATE INDEX idx_historial_tipo_documento ON historial_vencimientos(tipo_documento);
CREATE INDEX idx_historial_fecha_vencimiento ON historial_vencimientos(fecha_vencimiento_nueva);
CREATE INDEX idx_historial_estado ON historial_vencimientos(estado_documento);

-- 3. TABLA DE ALERTAS DE VENCIMIENTO
-- =====================================================

CREATE TABLE alertas_vencimiento (
    id_alerta INT AUTO_INCREMENT PRIMARY KEY,
    id_historial INT NOT NULL,
    tipo_alerta ENUM('30_dias', '15_dias', '7_dias', '1_dia', 'vencido') NOT NULL,
    fecha_alerta DATE NOT NULL,
    notificado BOOLEAN DEFAULT FALSE,
    canal_notificacion ENUM('email', 'sistema', 'sms') DEFAULT 'sistema',
    fecha_notificacion TIMESTAMP NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_historial) REFERENCES historial_vencimientos(id_historial) ON DELETE CASCADE
);

-- Crear índices para alertas
CREATE INDEX idx_alertas_fecha ON alertas_vencimiento(fecha_alerta);
CREATE INDEX idx_alertas_notificado ON alertas_vencimiento(notificado);
CREATE INDEX idx_alertas_tipo ON alertas_vencimiento(tipo_alerta);

-- 4. TABLA DE CONTROL DE KILOMETRAJE
-- =====================================================

CREATE TABLE kilometraje_vehiculos (
    id_kilometraje INT AUTO_INCREMENT PRIMARY KEY,
    id_vehiculo INT NOT NULL,
    kilometraje_actual INT NOT NULL,
    kilometraje_anterior INT DEFAULT 0,
    diferencia_km INT GENERATED ALWAYS AS (kilometraje_actual - kilometraje_anterior) STORED,
    fecha_registro DATE NOT NULL,
    tipo_registro ENUM('manual', 'mantenimiento', 'inspeccion', 'asignacion') DEFAULT 'manual',
    usuario_registro INT,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_vehiculo) REFERENCES parque_automotor(id_parque_automotor) ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro) REFERENCES recurso_operativo(id_codigo_consumidor)
);

-- Crear índices para kilometraje
CREATE INDEX idx_kilometraje_vehiculo ON kilometraje_vehiculos(id_vehiculo);
CREATE INDEX idx_kilometraje_fecha ON kilometraje_vehiculos(fecha_registro);
-- CREATE INDEX idx_kilometraje_tipo ON kilometraje_vehiculos(tipo_registro); -- Column doesn't exist

-- 5. TRIGGERS AUTOMÁTICOS
-- =====================================================

-- Trigger para actualizar fecha de modificación en parque_automotor
DROP TRIGGER IF EXISTS tr_parque_automotor_update;
DELIMITER //
CREATE TRIGGER tr_parque_automotor_update 
    BEFORE UPDATE ON parque_automotor
    FOR EACH ROW
BEGIN
    SET NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
END//
DELIMITER ;

-- Trigger para crear alertas automáticas cuando se registra un vencimiento
DROP TRIGGER IF EXISTS tr_crear_alertas_vencimiento;
DELIMITER //
CREATE TRIGGER tr_crear_alertas_vencimiento
    AFTER INSERT ON historial_vencimientos
    FOR EACH ROW
BEGIN
    -- Solo crear alertas si la fecha de vencimiento es futura
    IF NEW.fecha_vencimiento_nueva > CURDATE() THEN
        -- Alerta 30 días antes
        IF DATE_SUB(NEW.fecha_vencimiento_nueva, INTERVAL 30 DAY) >= CURDATE() THEN
            INSERT INTO alertas_vencimiento (id_historial, tipo_alerta, fecha_alerta)
            VALUES (NEW.id_historial, '30_dias', DATE_SUB(NEW.fecha_vencimiento_nueva, INTERVAL 30 DAY));
        END IF;
        
        -- Alerta 15 días antes
        IF DATE_SUB(NEW.fecha_vencimiento_nueva, INTERVAL 15 DAY) >= CURDATE() THEN
            INSERT INTO alertas_vencimiento (id_historial, tipo_alerta, fecha_alerta)
            VALUES (NEW.id_historial, '15_dias', DATE_SUB(NEW.fecha_vencimiento_nueva, INTERVAL 15 DAY));
        END IF;
        
        -- Alerta 7 días antes
        IF DATE_SUB(NEW.fecha_vencimiento_nueva, INTERVAL 7 DAY) >= CURDATE() THEN
            INSERT INTO alertas_vencimiento (id_historial, tipo_alerta, fecha_alerta)
            VALUES (NEW.id_historial, '7_dias', DATE_SUB(NEW.fecha_vencimiento_nueva, INTERVAL 7 DAY));
        END IF;
        
        -- Alerta 1 día antes
        IF DATE_SUB(NEW.fecha_vencimiento_nueva, INTERVAL 1 DAY) >= CURDATE() THEN
            INSERT INTO alertas_vencimiento (id_historial, tipo_alerta, fecha_alerta)
            VALUES (NEW.id_historial, '1_dia', DATE_SUB(NEW.fecha_vencimiento_nueva, INTERVAL 1 DAY));
        END IF;
    ELSE
        -- Si ya está vencido, crear alerta de vencido
        INSERT INTO alertas_vencimiento (id_historial, tipo_alerta, fecha_alerta)
        VALUES (NEW.id_historial, 'vencido', NEW.fecha_vencimiento_nueva);
    END IF;
END//
DELIMITER ;

-- Trigger para actualizar kilometraje en parque_automotor cuando se registra nuevo kilometraje
-- COMENTADO: Causa conflicto circular con la inserción de datos de prueba
-- DROP TRIGGER IF EXISTS tr_actualizar_kilometraje_vehiculo;
-- DELIMITER //
-- CREATE TRIGGER tr_actualizar_kilometraje_vehiculo
--     AFTER INSERT ON kilometraje_vehiculos
--     FOR EACH ROW
-- BEGIN
--     UPDATE parque_automotor 
--     SET kilometraje_actual = NEW.kilometraje_actual,
--         fecha_actualizacion = CURRENT_TIMESTAMP
--     WHERE id_parque_automotor = NEW.id_vehiculo;
-- END//
-- DELIMITER ;

-- 6. PROCEDIMIENTOS ALMACENADOS
-- =====================================================

-- Procedimiento para migrar datos existentes al historial
DROP PROCEDURE IF EXISTS MigrarDatosExistentesHistorial;
DELIMITER //
CREATE PROCEDURE MigrarDatosExistentesHistorial()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_id_vehiculo INT;
    DECLARE v_soat_vencimiento DATE;
    DECLARE v_tecnomecanica_vencimiento DATE;
    DECLARE v_fecha_asignacion DATE;

    
    -- Cursor para recorrer vehículos existentes
    DECLARE cur CURSOR FOR 
        SELECT id_parque_automotor, soat_vencimiento, tecnomecanica_vencimiento, fecha_asignacion
        FROM parque_automotor;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur;
    
    read_loop: LOOP
        FETCH cur INTO v_id_vehiculo, v_soat_vencimiento, v_tecnomecanica_vencimiento, v_fecha_asignacion;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- Migrar datos de SOAT si existen
        IF v_soat_vencimiento IS NOT NULL THEN
            INSERT IGNORE INTO historial_vencimientos 
            (id_vehiculo, tipo_documento, fecha_vencimiento_nueva, fecha_renovacion, estado_documento)
            VALUES (
                v_id_vehiculo,
                'soat',
                v_soat_vencimiento,
                CURDATE(),
                CASE 
                    WHEN v_soat_vencimiento < CURDATE() THEN 'vencido'
                    ELSE 'vigente'
                END
            );
        END IF;
        
        -- Migrar datos de tecnomecánica si existen
        IF v_tecnomecanica_vencimiento IS NOT NULL THEN
            INSERT IGNORE INTO historial_vencimientos 
            (id_vehiculo, tipo_documento, fecha_vencimiento_nueva, fecha_renovacion, estado_documento)
            VALUES (
                v_id_vehiculo,
                'tecnomecanica',
                v_tecnomecanica_vencimiento,
                CURDATE(),
                CASE 
                    WHEN v_tecnomecanica_vencimiento < CURDATE() THEN 'vencido'
                    ELSE 'vigente'
                END
            );
        END IF;
        
    END LOOP;
    
    CLOSE cur;
END//
DELIMITER ;

-- Procedimiento para obtener alertas de vencimiento
DROP PROCEDURE IF EXISTS ObtenerAlertasVencimiento;
DELIMITER //
CREATE PROCEDURE ObtenerAlertasVencimiento(
    IN p_dias_adelanto INT
)
BEGIN
    -- Set default value if parameter is NULL
    IF p_dias_adelanto IS NULL THEN
        SET p_dias_adelanto = 30;
    END IF;
    SELECT 
        pa.id_parque_automotor,
        pa.placa,
        hv.tipo_documento,
        hv.fecha_vencimiento_nueva,
        DATEDIFF(hv.fecha_vencimiento_nueva, CURDATE()) as dias_restantes,
        av.notificado,
        CASE 
            WHEN DATEDIFF(hv.fecha_vencimiento_nueva, CURDATE()) < 0 THEN 'critica'
            WHEN DATEDIFF(hv.fecha_vencimiento_nueva, CURDATE()) <= 7 THEN 'alta'
            WHEN DATEDIFF(hv.fecha_vencimiento_nueva, CURDATE()) <= 15 THEN 'media'
            ELSE 'baja'
        END as criticidad,
        ro.nombre as tecnico_asignado
    FROM parque_automotor pa
    INNER JOIN historial_vencimientos hv ON pa.id_parque_automotor = hv.id_vehiculo
    LEFT JOIN alertas_vencimiento av ON hv.id_historial = av.id_historial
    LEFT JOIN recurso_operativo ro ON pa.id_codigo_consumidor = ro.id_codigo_consumidor
    WHERE hv.fecha_vencimiento_nueva <= DATE_ADD(CURDATE(), INTERVAL p_dias_adelanto DAY)
    AND hv.estado_documento IN ('vigente', 'en_tramite')
    ORDER BY hv.fecha_vencimiento_nueva ASC, pa.placa ASC;
END//
DELIMITER ;

-- 7. EJECUTAR MIGRACIÓN DE DATOS EXISTENTES
-- =====================================================

-- Ejecutar la migración de datos existentes
CALL MigrarDatosExistentesHistorial();

-- 8. DATOS DE PRUEBA (OPCIONAL)
-- =====================================================

-- Insertar algunos datos de prueba para kilometraje si no existen registros
-- COMENTADO: Causa conflicto con el trigger de actualización
-- INSERT IGNORE INTO kilometraje_vehiculos (id_vehiculo, kilometraje_anterior, kilometraje_actual, fecha_registro, usuario_registro)
-- SELECT 
--     id_parque_automotor,
--     0,
--     COALESCE(kilometraje_actual, 0),
--     COALESCE(fecha_asignacion, CURRENT_DATE),
--     1
-- FROM parque_automotor 
-- WHERE id_parque_automotor NOT IN (SELECT DISTINCT id_vehiculo FROM kilometraje_vehiculos);

-- =====================================================
-- FIN DE LA MIGRACIÓN
-- =====================================================

SELECT 'Migración completada exitosamente' as resultado;
SELECT COUNT(*) as total_vehiculos FROM parque_automotor;
SELECT COUNT(*) as total_historial FROM historial_vencimientos;
SELECT COUNT(*) as total_alertas FROM alertas_vencimiento;
SELECT COUNT(*) as total_kilometraje FROM kilometraje_vehiculos;