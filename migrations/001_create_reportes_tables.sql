-- Migration: Create new tables for reporting module optimization
-- Date: 2024-01-20
-- Description: Creates reportes_configuracion, reportes_favoritos, reportes_programados tables
--              and optimizes existing preoperacional table with new indices

-- Crear tabla para configuraciones de reportes
CREATE TABLE IF NOT EXISTS reportes_configuracion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    nombre_reporte VARCHAR(255) NOT NULL,
    configuracion_filtros JSON,
    tipo_reporte ENUM('preoperacional', 'vencimientos', 'usuarios', 'consolidado') NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES recurso_operativo(id_codigo_consumidor)
);

-- Crear tabla para reportes favoritos
CREATE TABLE IF NOT EXISTS reportes_favoritos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    nombre_favorito VARCHAR(255) NOT NULL,
    parametros_filtro JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES recurso_operativo(id_codigo_consumidor)
);

-- Crear tabla para reportes programados
CREATE TABLE IF NOT EXISTS reportes_programados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    configuracion_id INT NOT NULL,
    frecuencia ENUM('diario', 'semanal', 'mensual', 'trimestral') NOT NULL,
    hora_ejecucion TIME NOT NULL,
    formato_salida ENUM('pdf', 'excel', 'csv') DEFAULT 'pdf',
    destinatarios_email TEXT,
    activo BOOLEAN DEFAULT TRUE,
    proxima_ejecucion TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (configuracion_id) REFERENCES reportes_configuracion(id)
);

-- Verificar que las tablas se crearon correctamente
SELECT 'Tablas creadas exitosamente' as status;