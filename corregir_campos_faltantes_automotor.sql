-- =====================================================
-- CORRECCIÓN DE CAMPOS FALTANTES EN TABLA PARQUE_AUTOMOTOR
-- Fecha: 2025-09-01
-- Propósito: Agregar campos del formulario que faltan en la base de datos
-- =====================================================

USE capired;

-- Verificar estructura actual de la tabla
SELECT 'Estructura actual de parque_automotor:' as info;
DESCRIBE parque_automotor;

-- =====================================================
-- 1. AGREGAR CAMPOS FALTANTES IDENTIFICADOS
-- =====================================================

-- Campo: vehiculo_asistio_operacion
-- Descripción: Indica si el vehículo asistió a la operación
ALTER TABLE parque_automotor 
ADD COLUMN vehiculo_asistio_operacion VARCHAR(10) DEFAULT 'No' 
COMMENT 'Indica si el vehículo asistió a la operación (Sí/No)';

-- Campo: licencia_conduccion
-- Descripción: Número de licencia de conducción del conductor asignado
ALTER TABLE parque_automotor 
ADD COLUMN licencia_conduccion VARCHAR(20) 
COMMENT 'Número de licencia de conducción del conductor asignado';

-- Campo: vencimiento_licencia
-- Descripción: Fecha de vencimiento de la licencia de conducción
ALTER TABLE parque_automotor 
ADD COLUMN vencimiento_licencia DATE 
COMMENT 'Fecha de vencimiento de la licencia de conducción';

SELECT 'Campos faltantes agregados exitosamente' as resultado;

-- =====================================================
-- 2. CREAR ÍNDICES PARA OPTIMIZACIÓN
-- =====================================================

-- Índice para vehiculo_asistio_operacion (consultas de filtrado)
CREATE INDEX idx_vehiculo_asistio_operacion 
ON parque_automotor(vehiculo_asistio_operacion);

-- Índice para licencia_conduccion (búsquedas por licencia)
CREATE INDEX idx_licencia_conduccion 
ON parque_automotor(licencia_conduccion);

-- Índice para vencimiento_licencia (alertas de vencimiento)
CREATE INDEX idx_vencimiento_licencia 
ON parque_automotor(vencimiento_licencia);

-- Índice compuesto para consultas de vencimientos
CREATE INDEX idx_vencimientos_documentos 
ON parque_automotor(vencimiento_licencia, soat_vencimiento, tecnomecanica_vencimiento);

SELECT 'Índices de optimización creados exitosamente' as resultado;

-- =====================================================
-- 3. ACTUALIZAR DATOS EXISTENTES (SI ES NECESARIO)
-- =====================================================

-- Establecer valores por defecto para registros existentes
UPDATE parque_automotor 
SET vehiculo_asistio_operacion = 'No' 
WHERE vehiculo_asistio_operacion IS NULL;

SELECT 'Datos existentes actualizados' as resultado;

-- =====================================================
-- 4. VERIFICAR ESTRUCTURA FINAL
-- =====================================================

SELECT 'Estructura final de parque_automotor:' as info;
DESCRIBE parque_automotor;

-- Contar total de campos
SELECT COUNT(*) as total_campos 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'capired' 
AND TABLE_NAME = 'parque_automotor';

-- Verificar índices creados
SELECT 
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX
FROM INFORMATION_SCHEMA.STATISTICS 
WHERE TABLE_SCHEMA = 'capired' 
AND TABLE_NAME = 'parque_automotor'
AND INDEX_NAME LIKE 'idx_%'
ORDER BY INDEX_NAME, SEQ_IN_INDEX;

-- =====================================================
-- 5. VALIDAR CAMPOS CRÍTICOS
-- =====================================================

-- Verificar que los campos críticos existen
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'capired' 
AND TABLE_NAME = 'parque_automotor'
AND COLUMN_NAME IN (
    'vehiculo_asistio_operacion',
    'licencia_conduccion', 
    'vencimiento_licencia'
)
ORDER BY COLUMN_NAME;

-- =====================================================
-- 6. REPORTE FINAL
-- =====================================================

SELECT 
    '✅ CORRECCIÓN COMPLETADA' as estado,
    'Campos faltantes agregados exitosamente' as descripcion,
    NOW() as fecha_correccion;

SELECT 
    'CAMPOS AGREGADOS:' as categoria,
    'vehiculo_asistio_operacion, licencia_conduccion, vencimiento_licencia' as campos;

SELECT 
    'ÍNDICES CREADOS:' as categoria,
    'idx_vehiculo_asistio_operacion, idx_licencia_conduccion, idx_vencimiento_licencia, idx_vencimientos_documentos' as indices;

-- Verificar integridad final
SELECT 
    COUNT(*) as total_registros,
    COUNT(CASE WHEN vehiculo_asistio_operacion IS NOT NULL THEN 1 END) as con_asistio_operacion,
    COUNT(CASE WHEN licencia_conduccion IS NOT NULL THEN 1 END) as con_licencia,
    COUNT(CASE WHEN vencimiento_licencia IS NOT NULL THEN 1 END) as con_vencimiento_licencia
FROM parque_automotor;

SELECT '🎯 CORRECCIÓN FINALIZADA - FORMULARIO Y DB AHORA ESTÁN SINCRONIZADOS' as mensaje_final;