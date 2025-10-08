# Plan de Reorganización de Archivos

## Archivos Críticos que DEBEN permanecer en la raíz

Estos archivos son esenciales para el funcionamiento de la aplicación:

### Archivos Principales de la Aplicación
- `app.py` - Aplicación Flask principal
- `main.py` - Servidor principal (importa app.py)
- `main_fixed.py` - Versión corregida de main.py
- `temp_main.py` - Versión temporal de main.py

### Configuración y Dependencias
- `requirements.txt` - Dependencias de Python
- `.env.example` - Ejemplo de variables de entorno
- `.env` - Variables de entorno (si existe)

### Documentación Principal
- `README.md` - Documentación principal del proyecto
- `RESUMEN_FASE_4_FINAL.md` - Resumen de la fase 4
- `DEPENDENCIAS_INSTALADAS.md` - Estado de dependencias

### Directorios del Sistema
- `templates/` - Plantillas HTML
- `static/` - Archivos estáticos (CSS, JS, imágenes)
- `migrations/` - Migraciones de base de datos
- `supabase/` - Configuración de Supabase
- `sql/` - Scripts SQL
- `backups/` - Respaldos de base de datos
- `triggers/` - Triggers de base de datos
- `utils/` - Utilidades
- `scripts/` - Scripts varios
- `docs/` - Documentación
- `diagnosticos/` - Scripts de diagnóstico
- `test/` - Pruebas
- `check/` - Verificaciones
- `fix/` - Scripts de corrección
- `debug/` - Scripts de depuración
- `verificar/` - Scripts de verificación

## Archivos que pueden ser ORGANIZADOS

### Scripts de Prueba y Testing (mover a `test/`)
```
test_*.py → test/
verificar_*.py → test/
```

**Archivos específicos:**
- `test_simple.py`
- `test_endpoint_final.py`
- `test_historial_auth.py`
- `test_sistema_completo.py`
- `test_frontend_real.py`
- `test_asistencia_endpoints.py`
- `test_stock_unificado.py`
- `test_validacion_stock.py`
- `test_endpoint_query.py`
- `test_mysql_fix.py`
- `test_integration_estado_management.py`
- `test_manual_save_functionality.py`
- `test_attendance_fix.py`
- `test_bloqueo_campos.py`
- `test_camisetapolo_estado.py`
- `test_camisetapolo_valorado.py`
- `test_devoluciones_api.py`
- `test_dotacion_con_estado.py`
- `test_endpoint_analista_espitia.py`
- `test_endpoint_analistas_corregido.py`
- `test_endpoint_con_usuario_logistica.py`
- `test_endpoint_directo.py`
- `test_endpoint_directo_logistica.py`
- `test_endpoint_final_corregido.py`
- `test_endpoint_mysql.py`
- `test_endpoint_sin_datos.py`
- `test_endpoint_sin_duplicados.py`
- `test_endpoint_stock.py`
- `test_endpoint_vencimientos.py`
- `test_endpoint_with_auth.py`
- `test_estado_apis.py`
- `test_final_vencimientos.py`
- `test_formulario_cambios.py`
- `test_frontend_api.py`
- `test_frontend_camisetapolo_final.py`
- `test_frontend_complete.py`
- `test_frontend_completo.py`
- `test_frontend_data.html`
- `test_frontend_endpoint.py`
- `test_graficos_endpoint.py`
- `test_guardado_analistas.py`
- `test_historial_completo.py`
- `test_historial_debug.py`
- `test_historial_endpoint.py`
- `test_inicio_operacion_endpoints.py`
- `test_modulo_analistas_completo.py`
- `test_modulo_analistas_final.py`
- `test_mysql_fix.py`
- `test_novedad_fix.py`
- `test_pantalon_30_fix.py`
- `test_produccion_endpoint.py`
- `test_registro_5992_fix.py`
- `test_resumen_agrupado_debug.py`
- `test_resumen_agrupado_fix.py`
- `test_resumen_endpoint.py`
- `test_sandra_hierarchy.py`
- `test_sandra_tecnicos.py`
- `test_simple_vencimientos.py`
- `test_solucion_final.py`
- `test_sql_grupos_validos.py`
- `test_sql_vencimientos.py`
- `test_step_by_step.py`
- `test_stock_no_valorado.py`
- `test_supervisores_endpoint.py`
- `test_temp.py`
- `test_validacion_ambas_variantes.py`
- `test_validacion_fechas.py`
- `test_validacion_stock_ambas_variantes.py`
- `test_validacion_stock_estado.py`
- `test_vencimientos_auth.py`
- `test_vencimientos_completo.py`
- `test_vencimientos_endpoint.py`

### Scripts de Diagnóstico (mover a `diagnosticos/`)
```
diagnostico_*.py → diagnosticos/
```

**Archivos específicos:**
- `diagnostico_problema_stock.py`
- `diagnostico_simple.py`

### Scripts de Verificación (mover a `verificar/`)
```
verificar_*.py → verificar/
```

**Archivos específicos:**
- `verificar_acceso_devoluciones.py`
- `verificar_asistencia_completa.py`
- `verificar_cambios_dotacion.py`
- `verificar_cedula_prueba.py`
- `verificar_cedulas.py`
- `verificar_correccion_final.py`
- `verificar_credenciales_analista.py`
- `verificar_datos_bd.py`
- `verificar_datos_finales.py`
- `verificar_datos_vencimientos.py`
- `verificar_devoluciones.py`
- `verificar_entregas_pantalones.py`
- `verificar_estado_usuario.py`
- `verificar_estructura_actual.py`
- `verificar_estructura_db.py`
- `verificar_estructura_produccion.py`
- `verificar_estructura_stock.py`
- `verificar_inventario_dotaciones.py`
- `verificar_pantalones.py`
- `verificar_password.py`
- `verificar_permisos.py`
- `verificar_produccion.py`
- `verificar_resultado.py`
- `verificar_roles_db.py`
- `verificar_stock_corregido.py`
- `verificar_stock_no_valorado.py`
- `verificar_stock_real.py`
- `verificar_stock_simple.py`
- `verificar_tabla_devoluciones.py`
- `verificar_tablas_asistencia.py`
- `verificar_tablas_auditoria.py`
- `verificar_tablas_causas_cierre.py`
- `verificar_tablas_db.py`
- `verificar_tablas_mysql.py`
- `verificar_tablas_stock.py`
- `verificar_tecnico_11.py`
- `verificar_tecnicos.py`
- `verificar_todos_usuarios.py`
- `verificar_usuario_logistica.py`
- `verificar_usuarios_db.py`
- `verificar_usuarios_logistica_real.py`
- `verificar_usuarios_mysql.py`
- `verificar_usuarios_recurso_operativo.py`
- `verificar_vencimientos_completo.py`
- `verificar_vencimientos_db.py`

### Scripts de Corrección (mover a `fix/`)
```
fix_*.py → fix/
corregir_*.py → fix/
```

**Archivos específicos:**
- `fix_vista_stock.py`
- `corregir_rol_usuario.py`

### Scripts de Depuración (mover a `debug/`)
```
debug_*.py → debug/
```

**Archivos específicos:**
- `debug_api.py`
- `debug_carga_datos.py`
- `debug_current_user.py`
- `debug_endpoint.py`
- `debug_firma_completo.py`
- `debug_firma_issue.py`
- `debug_registro_5992.py`
- `debug_servidor_mysql.py`
- `debug_stock_camisetagris.py`
- `debug_stock_final.py`
- `debug_tecnico.py`
- `debug_update_issue.py`

### Scripts de Utilidades (mover a `utils/`)
```
crear_*.py → utils/
actualizar_*.py → utils/
agregar_*.py → utils/
ajustar_*.py → utils/
analizar_*.py → utils/
backup_*.py → utils/
buscar_*.py → utils/
check_*.py → utils/
consultar_*.py → utils/
create_*.py → utils/
ejectuar_*.py → utils/
generate_*.py → utils/
get_*.py → utils/
import_*.py → utils/
insertar_*.py → utils/
migrar_*.py → utils/
populate_*.py → utils/
reset_*.py → utils/
setup_*.py → utils/
```

**Archivos específicos:**
- `crear_usuario_prueba.py`
- `crear_user.py`
- `crear_user_80833959.py`
- `actualizar_stock.py`
- `agregar_rol_sstt.py`
- `ajustar_stock_botas.py`
- `analizar_dotaciones.py`
- `analizar_recurso_operativo.py`
- `backup_database.py`
- `buscar_stock_faltante.py`
- `buscar_usuarios.py`
- `check_config.py`
- `check_firmas.py`
- `check_passwords.py`
- `check_roles.py`
- `check_roles_db.py`
- `check_stock.py`
- `check_table_structure.py`
- `check_tables.py`
- `check_tecnicos.py`
- `check_users.py`
- `check_vencimientos.py`
- `check_vista.py`
- `consultar_usuarios.py`
- `create_logistica_user.py`
- `create_test_user.py`
- `ejecutar_sql.py`
- `execute_migrations.py`
- `find_bogota_time.py`
- `find_technicians.py`
- `generate_trigger_fix.py`
- `get_operativo_users.py`
- `import_users.py`
- `insertar_datos_prueba_asistencia.py`
- `migrar_ferretero.py`
- `modo_prueba_truncate.py`
- `populate_config.py`
- `reset_password.py`
- `setup_database.py`
- `setup_sstt_database.py`

### Archivos de Datos y Configuración (mover a `data/`)
```
*.csv → data/
*.json → data/
*.txt → data/
```

**Archivos específicos:**
- `AUTOMOTOR.csv`
- `herramienta tabla.csv`
- `preoperacional.csv`
- `usuarios.csv`
- `cedulas_results.txt`
- `test_results.txt`
- `api_output.json`
- `api_response.json`
- `endpoint_corregido.txt`
- `patch_installation_instructions.txt`

### Archivos de Documentación Técnica (mover a `docs/tech/`)
```
*.md → docs/ (excepto README.md y RESUMEN_FASE_4_FINAL.md)
```

**Archivos específicos:**
- `SOLUCION_CALCULOS_MYSQL.md`
- `SOLUCION_ERROR_HISTORIAL.md`
- `instrucciones_instalacion.md`
- `validacion_formulario_cambios_dotacion.md`

### Scripts de Triggers (ya están en `triggers/`)
Los archivos en `triggers/` ya están bien organizados.

### Scripts de Migración (ya están en `migrations/`)
Los archivos en `migrations/` ya están bien organizados.

## Estructura Propuesta Final

```
synapsis/
├── app.py                          # CRÍTICO - App Flask
├── main.py                         # CRÍTICO - Servidor principal
├── main_fixed.py                   # CRÍTICO - Versión corregida
├── temp_main.py                    # CRÍTICO - Versión temporal
├── requirements.txt                # CRÍTICO - Dependencias
├── .env.example                    # CRÍTICO - Config example
├── .env                           # CRÍTICO - Config (si existe)
├── README.md                      # CRÍTICO - Documentación
├── RESUMEN_FASE_4_FINAL.md        # CRÍTICO - Resumen
├── DEPENDENCIAS_INSTALADAS.md     # CRÍTICO - Estado deps
│
├── templates/                     # CRÍTICO - Plantillas HTML
├── static/                        # CRÍTICO - Archivos estáticos
├── migrations/                    # CRÍTICO - Migraciones DB
├── supabase/                      # CRÍTICO - Config Supabase
├── sql/                          # CRÍTICO - Scripts SQL
├── backups/                      # CRÍTICO - Respaldos
├── triggers/                     # CRÍTICO - Triggers DB
├── utils/                        # ORGANIZADO - Utilidades
├── test/                         # ORGANIZADO - Pruebas
├── diagnosticos/                 # ORGANIZADO - Diagnósticos
├── verificar/                    # ORGANIZADO - Verificaciones
├── fix/                          # ORGANIZADO - Correcciones
├── debug/                        # ORGANIZADO - Depuración
├── data/                         # ORGANIZADO - Datos
└── docs/                         # ORGANIZADO - Documentación
```

## Pasos de Implementación

1. **Primero**: Crear los directorios que no existan
2. **Segundo**: Mover los archivos por categorías
3. **Tercero**: Verificar que la aplicación siga funcionando
4. **Cuarto**: Actualizar cualquier referencia a rutas si es necesario

## Notas Importantes

- **No mover** archivos que estén siendo importados directamente por `app.py` o `main.py`
- **No mover** archivos que sean ejecutados directamente por el sistema
- **Verificar** que los scripts que usan rutas relativas sigan funcionando después del cambio
- **Hacer backup** antes de mover archivos críticos

## Archivos a Verificar Especialmente

Antes de mover, verificar estos archivos que podrían tener dependencias:
- `logging_code.py` - Usado por patch_logging_ferretero.py
- `validacion_stock_por_estado.py` - Importado por varios scripts
- `mecanismo_stock_unificado.py` - Importado por integracion_dotaciones_validadas.py
- `validacion_dotaciones_unificada.py` - Importado por integracion_dotaciones_validadas.py

¿Deseas que proceda con la reorganización siguiendo este plan?