-- Migration: Add initial configuration data
-- Date: 2024-01-20
-- Description: Adds sample configuration data for reporting module

-- Datos iniciales para configuraciones de ejemplo
INSERT INTO reportes_configuracion (usuario_id, nombre_reporte, configuracion_filtros, tipo_reporte) VALUES
(1, 'Reporte Mensual Preoperacionales', '{"periodo": "mensual", "incluir_graficos": true}', 'preoperacional'),
(1, 'Alertas de Vencimientos', '{"dias_anticipacion": 30, "tipos": ["licencia", "soat", "tecnomecanica"]}', 'vencimientos'),
(1, 'Estadísticas de Usuarios', '{"incluir_actividad": true, "agrupar_por_rol": true}', 'usuarios')
ON DUPLICATE KEY UPDATE nombre_reporte = VALUES(nombre_reporte);

-- Verificar que los datos se insertaron correctamente
SELECT 'Datos iniciales agregados exitosamente' as status;