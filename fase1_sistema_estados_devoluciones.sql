-- =====================================================
-- FASE 1: SISTEMA DE GESTIÓN DE ESTADOS - DEVOLUCIONES
-- =====================================================

USE synapsis;

-- Crear tabla de auditoría de estados
CREATE TABLE IF NOT EXISTS auditoria_estados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    devolucion_id INT NOT NULL,
    estado_anterior ENUM('REGISTRADA', 'PROCESANDO', 'COMPLETADA', 'CANCELADA') NOT NULL,
    estado_nuevo ENUM('REGISTRADA', 'PROCESANDO', 'COMPLETADA', 'CANCELADA') NOT NULL,
    usuario_id INT NOT NULL,
    motivo_cambio TEXT NOT NULL,
    fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (devolucion_id) REFERENCES devoluciones_dotacion(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    INDEX idx_devolucion_fecha (devolucion_id, fecha_cambio DESC),
    INDEX idx_usuario_fecha (usuario_id, fecha_cambio DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Los índices ya están definidos en la tabla

-- =====================================================
-- 2. TABLA DE NOTIFICACIONES DE ESTADO
-- =====================================================

CREATE TABLE IF NOT EXISTS notificaciones_estado (
    id INT AUTO_INCREMENT PRIMARY KEY,
    devolucion_id INT NOT NULL,
    usuario_destinatario INT NOT NULL,
    tipo_notificacion ENUM('CAMBIO_ESTADO', 'APROBACION_REQUERIDA', 'PROCESO_COMPLETADO') NOT NULL,
    mensaje TEXT NOT NULL,
    leida BOOLEAN DEFAULT FALSE,
    fecha_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (devolucion_id) REFERENCES devoluciones_dotacion(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_destinatario) REFERENCES usuarios(id),
    INDEX idx_usuario_leida (usuario_destinatario, leida),
    INDEX idx_fecha_envio (fecha_envio DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 3. TABLA DE PERMISOS DE TRANSICIÓN
-- =====================================================

CREATE TABLE IF NOT EXISTS permisos_transicion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rol_id INT NOT NULL,
    estado_origen ENUM('REGISTRADA', 'PROCESANDO', 'COMPLETADA', 'CANCELADA') NOT NULL,
    estado_destino ENUM('REGISTRADA', 'PROCESANDO', 'COMPLETADA', 'CANCELADA') NOT NULL,
    permitido BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rol_id) REFERENCES roles(id),
    UNIQUE KEY unique_transicion (rol_id, estado_origen, estado_destino),
    INDEX idx_rol_origen (rol_id, estado_origen)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 4. ACTUALIZACIÓN DE TABLA PRINCIPAL
-- =====================================================

-- Agregar campos de auditoría a la tabla principal
-- Verificar si las columnas existen antes de agregarlas
SET @col_exists_updated_by = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                              WHERE TABLE_SCHEMA = 'synapsis' 
                              AND TABLE_NAME = 'devoluciones_dotacion' 
                              AND COLUMN_NAME = 'updated_by');

SET @col_exists_version = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                           WHERE TABLE_SCHEMA = 'synapsis' 
                           AND TABLE_NAME = 'devoluciones_dotacion' 
                           AND COLUMN_NAME = 'version');

SET @sql_updated_by = IF(@col_exists_updated_by = 0, 
    'ALTER TABLE devoluciones_dotacion ADD COLUMN updated_by INT NULL',
    'SELECT "Column updated_by already exists" as message');

SET @sql_version = IF(@col_exists_version = 0, 
    'ALTER TABLE devoluciones_dotacion ADD COLUMN version INT DEFAULT 1',
    'SELECT "Column version already exists" as message');

PREPARE stmt FROM @sql_updated_by;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

PREPARE stmt FROM @sql_version;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Agregar foreign key si no existe
SET @fk_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                  WHERE TABLE_SCHEMA = 'synapsis' 
                  AND TABLE_NAME = 'devoluciones_dotacion' 
                  AND COLUMN_NAME = 'updated_by' 
                  AND REFERENCED_TABLE_NAME = 'usuarios');

SET @sql = IF(@fk_exists = 0, 
    'ALTER TABLE devoluciones_dotacion ADD FOREIGN KEY (updated_by) REFERENCES usuarios(id)',
    'SELECT "Foreign key already exists" as message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- =====================================================
-- 5. TRIGGERS PARA AUDITORÍA AUTOMÁTICA
-- =====================================================

-- Eliminar trigger si existe
DROP TRIGGER IF EXISTS tr_devoluciones_version_update;

-- Crear trigger para actualizar version en cada cambio
DELIMITER //
CREATE TRIGGER tr_devoluciones_version_update
    BEFORE UPDATE ON devoluciones_dotacion
    FOR EACH ROW
BEGIN
    SET NEW.version = OLD.version + 1;
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END//
DELIMITER ;

-- Trigger para auditoría automática de cambios de estado
DROP TRIGGER IF EXISTS tr_auditoria_cambio_estado;

DELIMITER //
CREATE TRIGGER tr_auditoria_cambio_estado
    AFTER UPDATE ON devoluciones_dotacion
    FOR EACH ROW
BEGIN
    -- Solo registrar si cambió el estado
    IF OLD.estado != NEW.estado THEN
        INSERT INTO auditoria_estados (
            devolucion_id, 
            estado_anterior, 
            estado_nuevo, 
            usuario_id, 
            motivo_cambio
        ) VALUES (
            NEW.id,
            OLD.estado,
            NEW.estado,
            COALESCE(NEW.updated_by, 1), -- Usuario por defecto si no se especifica
            CONCAT('Cambio automático de estado de ', OLD.estado, ' a ', NEW.estado)
        );
    END IF;
END//
DELIMITER ;

-- =====================================================
-- 6. DATOS INICIALES DE PERMISOS
-- =====================================================

-- Limpiar datos existentes de permisos
DELETE FROM permisos_transicion;

-- Insertar permisos para Técnico Logística (rol_id = 3)
INSERT INTO permisos_transicion (rol_id, estado_origen, estado_destino, permitido) VALUES
(3, 'REGISTRADA', 'PROCESANDO', TRUE),
(3, 'REGISTRADA', 'CANCELADA', TRUE);

-- Insertar permisos para Supervisor Logística (rol_id = 4)
INSERT INTO permisos_transicion (rol_id, estado_origen, estado_destino, permitido) VALUES
(4, 'PROCESANDO', 'COMPLETADA', TRUE),
(4, 'PROCESANDO', 'CANCELADA', TRUE),
(4, 'REGISTRADA', 'PROCESANDO', TRUE),
(4, 'REGISTRADA', 'CANCELADA', TRUE);

-- Insertar permisos para Administrador Logística (rol_id = 5) - todos los permisos
INSERT INTO permisos_transicion (rol_id, estado_origen, estado_destino, permitido) VALUES
(5, 'REGISTRADA', 'PROCESANDO', TRUE),
(5, 'REGISTRADA', 'COMPLETADA', TRUE),
(5, 'REGISTRADA', 'CANCELADA', TRUE),
(5, 'PROCESANDO', 'COMPLETADA', TRUE),
(5, 'PROCESANDO', 'CANCELADA', TRUE),
(5, 'PROCESANDO', 'REGISTRADA', TRUE),
(5, 'COMPLETADA', 'REGISTRADA', TRUE),
(5, 'CANCELADA', 'REGISTRADA', TRUE);

-- =====================================================
-- 7. VERIFICACIÓN DE CREACIÓN
-- =====================================================

-- Mostrar resumen de tablas creadas
SELECT 
    'auditoria_estados' as tabla,
    COUNT(*) as registros
FROM auditoria_estados
UNION ALL
SELECT 
    'notificaciones_estado' as tabla,
    COUNT(*) as registros
FROM notificaciones_estado
UNION ALL
SELECT 
    'permisos_transicion' as tabla,
    COUNT(*) as registros
FROM permisos_transicion;

-- Mostrar permisos configurados
SELECT 
    r.nombre as rol,
    pt.estado_origen,
    pt.estado_destino,
    pt.permitido
FROM permisos_transicion pt
JOIN roles r ON pt.rol_id = r.id
ORDER BY r.nombre, pt.estado_origen, pt.estado_destino;

-- Verificar triggers creados
SHOW TRIGGERS LIKE 'devoluciones_dotacion';

SELECT 'Script de Fase 1 ejecutado exitosamente' as resultado;