-- Crear tabla de auditoría de estados de devolución
CREATE TABLE IF NOT EXISTS auditoria_estados_devolucion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    devolucion_id INT NOT NULL,
    estado_anterior VARCHAR(50),
    estado_nuevo VARCHAR(50) NOT NULL,
    usuario_id INT NOT NULL,
    fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
    motivo_cambio TEXT,
    observaciones TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    INDEX idx_devolucion_id (devolucion_id),
    INDEX idx_usuario_id (usuario_id),
    INDEX idx_fecha_cambio (fecha_cambio),
    INDEX idx_estado_nuevo (estado_nuevo)
);

-- Crear tabla de permisos del sistema
CREATE TABLE IF NOT EXISTS permisos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    modulo VARCHAR(50) NOT NULL,
    accion VARCHAR(50) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_modulo (modulo),
    INDEX idx_accion (accion)
);

-- Crear tabla de relación roles-permisos
CREATE TABLE IF NOT EXISTS roles_permisos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rol_id INT NOT NULL,
    permiso_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_rol_permiso (rol_id, permiso_id),
    INDEX idx_rol_id (rol_id),
    INDEX idx_permiso_id (permiso_id)
);

-- Insertar permisos básicos del sistema
INSERT IGNORE INTO permisos (nombre, descripcion, modulo, accion) VALUES
('ver_devoluciones', 'Ver listado de devoluciones', 'devoluciones', 'read'),
('crear_devolucion', 'Crear nueva devolución', 'devoluciones', 'create'),
('editar_devolucion', 'Editar devolución existente', 'devoluciones', 'update'),
('eliminar_devolucion', 'Eliminar devolución', 'devoluciones', 'delete'),
('cambiar_estado_devolucion', 'Cambiar estado de devolución', 'devoluciones', 'state_change'),
('ver_auditoria', 'Ver historial de auditoría', 'auditoria', 'read'),
('administrar_usuarios', 'Administrar usuarios del sistema', 'usuarios', 'admin'),
('administrar_roles', 'Administrar roles y permisos', 'roles', 'admin'),
('configurar_notificaciones', 'Configurar sistema de notificaciones', 'notificaciones', 'config'),
('ver_reportes', 'Ver reportes del sistema', 'reportes', 'read'),
('exportar_datos', 'Exportar datos del sistema', 'exportacion', 'export');

-- Actualizar tabla de devoluciones para incluir los nuevos estados
ALTER TABLE devoluciones_dotacion 
MODIFY COLUMN estado ENUM('REGISTRADA','PROCESANDO','COMPLETADA','CANCELADA') DEFAULT 'REGISTRADA';

-- Crear índices adicionales para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_estado_fecha ON devoluciones_dotacion(estado, fecha_devolucion);
CREATE INDEX IF NOT EXISTS idx_tecnico_estado ON devoluciones_dotacion(tecnico_id, estado);
CREATE INDEX IF NOT EXISTS idx_cliente_estado ON devoluciones_dotacion(cliente_id, estado);

-- Crear trigger para auditoría automática de cambios de estado
DELIMITER //
CREATE TRIGGER IF NOT EXISTS tr_auditoria_estado_devolucion
AFTER UPDATE ON devoluciones_dotacion
FOR EACH ROW
BEGIN
    IF OLD.estado != NEW.estado THEN
        INSERT INTO auditoria_estados_devolucion (
            devolucion_id, 
            estado_anterior, 
            estado_nuevo, 
            usuario_id, 
            motivo_cambio
        ) VALUES (
            NEW.id, 
            OLD.estado, 
            NEW.estado, 
            NEW.created_by, 
            'Cambio automático de estado'
        );
    END IF;
END//
DELIMITER ;