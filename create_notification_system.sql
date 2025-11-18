-- =====================================================
-- SISTEMA DE NOTIFICACIONES AUTOMÁTICAS - FASE 4
-- Creación de tablas para notificaciones por email/SMS
-- =====================================================

-- Tabla de configuración de notificaciones
CREATE TABLE IF NOT EXISTS configuracion_notificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_notificacion ENUM('EMAIL', 'SMS', 'AMBOS') NOT NULL DEFAULT 'EMAIL',
    evento_trigger ENUM('CAMBIO_ESTADO', 'VENCIMIENTO', 'RECORDATORIO') NOT NULL,
    estado_origen VARCHAR(20),
    estado_destino VARCHAR(20),
    activo BOOLEAN DEFAULT TRUE,
    destinatarios_roles JSON, -- Roles que reciben la notificación
    plantilla_email_id INT,
    plantilla_sms_id INT,
    delay_minutos INT DEFAULT 0, -- Retraso antes de enviar
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_evento_estado (evento_trigger, estado_origen, estado_destino),
    INDEX idx_activo (activo)
);

-- Tabla de plantillas de email
CREATE TABLE IF NOT EXISTS plantillas_email (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    asunto VARCHAR(200) NOT NULL,
    cuerpo_html TEXT NOT NULL,
    cuerpo_texto TEXT,
    variables_disponibles JSON, -- Variables que se pueden usar {devolucion_id}, {estado}, etc.
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_nombre (nombre),
    INDEX idx_activo (activo)
);

-- Tabla de plantillas de SMS
CREATE TABLE IF NOT EXISTS plantillas_sms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    mensaje TEXT NOT NULL,
    variables_disponibles JSON,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_nombre (nombre),
    INDEX idx_activo (activo)
);

-- Tabla de historial de notificaciones enviadas
CREATE TABLE IF NOT EXISTS historial_notificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    devolucion_id INT NOT NULL,
    tipo_notificacion ENUM('EMAIL', 'SMS') NOT NULL,
    destinatario VARCHAR(255) NOT NULL,
    asunto VARCHAR(200),
    mensaje TEXT,
    estado_envio ENUM('PENDIENTE', 'ENVIADO', 'FALLIDO', 'REINTENTANDO') DEFAULT 'PENDIENTE',
    intentos_envio INT DEFAULT 0,
    fecha_programada TIMESTAMP,
    fecha_enviado TIMESTAMP NULL,
    error_mensaje TEXT,
    configuracion_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (devolucion_id) REFERENCES devoluciones_dotacion(id) ON DELETE CASCADE,
    FOREIGN KEY (configuracion_id) REFERENCES configuracion_notificaciones(id),
    INDEX idx_devolucion (devolucion_id),
    INDEX idx_estado_envio (estado_envio),
    INDEX idx_fecha_programada (fecha_programada),
    INDEX idx_destinatario (destinatario)
);

-- Tabla de configuración SMTP/SMS
CREATE TABLE IF NOT EXISTS configuracion_servicios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    servicio ENUM('SMTP', 'SMS') NOT NULL,
    proveedor VARCHAR(50) NOT NULL, -- Gmail, Outlook, Twilio, etc.
    configuracion JSON NOT NULL, -- Configuración específica del proveedor
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_servicio_activo (servicio, activo),
    INDEX idx_servicio (servicio)
);

-- =====================================================
-- DATOS INICIALES
-- =====================================================

-- Plantillas de email por defecto
INSERT INTO plantillas_email (nombre, asunto, cuerpo_html, cuerpo_texto, variables_disponibles) VALUES
('cambio_estado_registrada', 
 'Devolución #{devolucion_id} - Estado: Registrada',
 '<h2>Devolución Registrada</h2><p>La devolución <strong>#{devolucion_id}</strong> ha sido registrada exitosamente.</p><p><strong>Cliente:</strong> {cliente_nombre}</p><p><strong>Fecha:</strong> {fecha_registro}</p><p><strong>Observaciones:</strong> {observaciones}</p>',
 'Devolución #{devolucion_id} registrada. Cliente: {cliente_nombre}. Fecha: {fecha_registro}',
 '["devolucion_id", "cliente_nombre", "fecha_registro", "observaciones"]'),

('cambio_estado_procesando',
 'Devolución #{devolucion_id} - En Proceso',
 '<h2>Devolución en Proceso</h2><p>La devolución <strong>#{devolucion_id}</strong> está siendo procesada.</p><p><strong>Cliente:</strong> {cliente_nombre}</p><p><strong>Procesado por:</strong> {usuario_proceso}</p>',
 'Devolución #{devolucion_id} en proceso. Cliente: {cliente_nombre}',
 '["devolucion_id", "cliente_nombre", "usuario_proceso"]'),

('cambio_estado_completada',
 'Devolución #{devolucion_id} - Completada',
 '<h2>Devolución Completada</h2><p>La devolución <strong>#{devolucion_id}</strong> ha sido completada exitosamente.</p><p><strong>Cliente:</strong> {cliente_nombre}</p><p><strong>Completado por:</strong> {usuario_completo}</p>',
 'Devolución #{devolucion_id} completada. Cliente: {cliente_nombre}',
 '["devolucion_id", "cliente_nombre", "usuario_completo"]'),

('cambio_estado_cancelada',
 'Devolución #{devolucion_id} - Cancelada',
 '<h2>Devolución Cancelada</h2><p>La devolución <strong>#{devolucion_id}</strong> ha sido cancelada.</p><p><strong>Cliente:</strong> {cliente_nombre}</p><p><strong>Motivo:</strong> {motivo_cancelacion}</p>',
 'Devolución #{devolucion_id} cancelada. Cliente: {cliente_nombre}',
 '["devolucion_id", "cliente_nombre", "motivo_cancelacion"]');

-- Plantillas de SMS por defecto
INSERT INTO plantillas_sms (nombre, mensaje, variables_disponibles) VALUES
('sms_registrada', 
 'Devolución #{devolucion_id} registrada. Cliente: {cliente_nombre}',
 '["devolucion_id", "cliente_nombre"]'),

('sms_procesando',
 'Devolución #{devolucion_id} en proceso. Cliente: {cliente_nombre}',
 '["devolucion_id", "cliente_nombre"]'),

('sms_completada',
 'Devolución #{devolucion_id} completada. Cliente: {cliente_nombre}',
 '["devolucion_id", "cliente_nombre"]'),

('sms_cancelada',
 'Devolución #{devolucion_id} cancelada. Cliente: {cliente_nombre}',
 '["devolucion_id", "cliente_nombre"]');

-- Configuración de notificaciones por defecto
INSERT INTO configuracion_notificaciones (tipo_notificacion, evento_trigger, estado_origen, estado_destino, destinatarios_roles, plantilla_email_id, plantilla_sms_id) VALUES
('EMAIL', 'CAMBIO_ESTADO', NULL, 'REGISTRADA', '["admin", "supervisor"]', 1, 1),
('EMAIL', 'CAMBIO_ESTADO', 'REGISTRADA', 'PROCESANDO', '["admin", "supervisor", "operador"]', 2, 2),
('EMAIL', 'CAMBIO_ESTADO', 'PROCESANDO', 'COMPLETADA', '["admin", "supervisor", "operador"]', 3, 3),
('EMAIL', 'CAMBIO_ESTADO', NULL, 'CANCELADA', '["admin", "supervisor"]', 4, 4);

-- Configuración SMTP por defecto (Gmail)
INSERT INTO configuracion_servicios (servicio, proveedor, configuracion) VALUES
('SMTP', 'Gmail', '{
  "host": "smtp.gmail.com",
  "port": 587,
  "secure": false,
  "auth": {
    "user": "tu-email@gmail.com",
    "pass": "tu-app-password"
  },
  "from": "Sistema Devoluciones <tu-email@gmail.com>"
}');

COMMIT;