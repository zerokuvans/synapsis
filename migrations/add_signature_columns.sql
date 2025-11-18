-- Migración para agregar columnas de firma digital a la tabla dotaciones
-- Fecha: 2025-01-27
-- Descripción: Agregar soporte para firma digital de dotaciones

USE capired;

-- Agregar columnas para funcionalidad de firma digital
ALTER TABLE dotaciones 
ADD COLUMN firmado TINYINT(1) DEFAULT 0 COMMENT 'Indica si la dotación ha sido firmada (0=No, 1=Sí)',
ADD COLUMN fecha_firma DATETIME NULL COMMENT 'Fecha y hora cuando se firmó la dotación',
ADD COLUMN firma_imagen LONGTEXT NULL COMMENT 'Imagen de la firma en formato base64',
ADD COLUMN usuario_firma INT NULL COMMENT 'ID del usuario que firmó la dotación';

-- Crear índice para mejorar consultas por estado de firma
CREATE INDEX idx_dotaciones_firmado ON dotaciones(firmado);

-- Crear índice para consultas por fecha de firma
CREATE INDEX idx_dotaciones_fecha_firma ON dotaciones(fecha_firma);

-- Verificar que las columnas se agregaron correctamente
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'capired' 
    AND TABLE_NAME = 'dotaciones' 
    AND COLUMN_NAME IN ('firmado', 'fecha_firma', 'firma_imagen', 'usuario_firma')
ORDER BY ORDINAL_POSITION;

-- Mostrar estadísticas después de la migración
SELECT 
    COUNT(*) as total_dotaciones,
    SUM(CASE WHEN firmado = 1 THEN 1 ELSE 0 END) as dotaciones_firmadas,
    SUM(CASE WHEN firmado = 0 OR firmado IS NULL THEN 1 ELSE 0 END) as dotaciones_sin_firmar
FROM dotaciones;