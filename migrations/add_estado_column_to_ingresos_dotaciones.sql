-- Agregar columna estado a la tabla ingresos_dotaciones
-- Fecha: 2025-01-15
-- Descripción: Agregar campo de estado con valores VALORADO y NO VALORADO

ALTER TABLE ingresos_dotaciones 
ADD COLUMN estado ENUM('VALORADO', 'NO VALORADO') NOT NULL DEFAULT 'NO VALORADO' 
COMMENT 'Estado de valoración del ingreso de dotación'
AFTER proveedor;

-- Crear índice para mejorar consultas por estado
CREATE INDEX idx_estado ON ingresos_dotaciones(estado);

-- Comentario de la migración
-- Esta migración agrega el campo estado a la tabla ingresos_dotaciones
-- para permitir el seguimiento del estado de valoración de cada ingreso