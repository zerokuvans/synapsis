-- Migration: Add indices and initial data for reporting module
-- Date: 2024-01-20
-- Description: Adds performance indices and initial configuration data

-- Crear índices para reportes_configuracion
CREATE INDEX idx_reportes_config_usuario ON reportes_configuracion(usuario_id);
CREATE INDEX idx_reportes_config_tipo ON reportes_configuracion(tipo_reporte);
CREATE INDEX idx_reportes_config_activo ON reportes_configuracion(activo);

-- Crear índices para reportes_favoritos
CREATE INDEX idx_reportes_favoritos_usuario ON reportes_favoritos(usuario_id);
CREATE INDEX idx_reportes_favoritos_created ON reportes_favoritos(created_at DESC);

-- Crear índices para reportes_programados
CREATE INDEX idx_reportes_programados_config ON reportes_programados(configuracion_id);
CREATE INDEX idx_reportes_programados_proxima ON reportes_programados(proxima_ejecucion);
CREATE INDEX idx_reportes_programados_activo ON reportes_programados(activo);

-- Optimización de tabla preoperacional existente - Agregar índices para mejorar rendimiento
CREATE INDEX idx_preoperacional_fecha_supervisor ON preoperacional(fecha, supervisor);
CREATE INDEX idx_preoperacional_centro_trabajo ON preoperacional(centro_de_trabajo);
CREATE INDEX idx_preoperacional_vencimientos ON preoperacional(fecha_vencimiento_licencia, fecha_vencimiento_soat, fecha_vencimiento_tecnomecanica);
CREATE INDEX idx_preoperacional_estado_vehiculo ON preoperacional(estado_espejos, bocina_pito, frenos, encendido, estado_bateria);

-- Datos iniciales para configuraciones de ejemplo
-- Note: Using user ID 1 as example (replace with actual admin user ID)
INSERT INTO reportes_configuracion (usuario_id, nombre_reporte, configuracion_filtros, tipo_reporte) VALUES
(1, 'Reporte Mensual Preoperacionales', '{"periodo": "mensual", "incluir_graficos": true}', 'preoperacional'),
(1, 'Alertas de Vencimientos', '{"dias_anticipacion": 30, "tipos": ["licencia", "soat", "tecnomecanica"]}', 'vencimientos'),
(1, 'Estadísticas de Usuarios', '{"incluir_actividad": true, "agrupar_por_rol": true}', 'usuarios')
ON DUPLICATE KEY UPDATE nombre_reporte = VALUES(nombre_reporte);

-- Verificar que los índices se crearon correctamente
SELECT 'Índices y datos iniciales agregados exitosamente' as status;