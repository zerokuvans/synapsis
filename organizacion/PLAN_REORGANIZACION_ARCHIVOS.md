# Plan de Reorganización de Archivos

## Objetivo
Organizar los archivos del proyecto en directorios para reducir el desorden en la raíz, asegurando que ningún archivo crítico para el funcionamiento de la aplicación sea movido.

## Archivos Críticos (NO deben moverse)

Estos archivos DEBEN permanecer en la raíz del proyecto:

### Archivos Principales
- `app.py` - Aplicación Flask principal
- `main.py` - Punto de entrada principal del proyecto
- `main_fixed.py` - Versión corregida del main
- `temp_main.py` - Versión temporal del main

### Configuración
- `requirements.txt` - Dependencias del proyecto
- `.env.example` - Ejemplo de variables de entorno
- `README.md` - Documentación del proyecto

### Directorios del Sistema
- `templates/` - Plantillas HTML
- `static/` - Archivos estáticos (CSS, JS, imágenes)
- `migrations/` - Migraciones de base de datos
- `supabase/` - Configuración de Supabase
- `sql/` - Scripts SQL
- `backups/` - Respaldos
- `triggers/` - Triggers de base de datos

## Archivos a Organizar

### 1. Scripts de Prueba
**Patrón:** `test_*.py`
**Destino:** `test/`

Archivos identificados:
- `test_asistencia_endpoints.py`
- `test_frontend_camisetapolo_final.py`
- `test_sandra_hierarchy.py`

### 2. Scripts de Diagnóstico
**Patrón:** `diagnostico_*.py`
**Destino:** `diagnosticos/`

Archivos identificados:
- `diagnostico_problema_stock.py`
- `diagnostico_mysql.py`

### 3. Scripts de Verificación
**Patrón:** `verificar_*.py`
**Destino:** `verificar/`

Archivos identificados:
- `verificar_acceso_devoluciones.py`

### 4. Scripts de Corrección (Fix)
**Patrón:** `fix_*.py`
**Destino:** `fix/`

Archivos identificados:
- `fix_api.py`

### 5. Scripts de Depuración (Debug)
**Patrón:** `debug_*.py`
**Destino:** `debug/`

Archivos identificados:
- `debug_servidor_mysql.py`

### 6. Scripts de Utilidades Varias
**Patrón:** Otros scripts `.py` no críticos
**Destino:** `utilidades/`

Archivos identificados:
- `migration_triggers.py` - Migración de triggers
- `validar_sintaxis_triggers.py` - Validación de triggers
- `ejecutar_triggers_localhost.py` - Ejecución de triggers
- `patch_logging_ferretero.py` - Parche de logging
- `analizar_recurso_operativo.py` - Análisis de recursos
- `apply_corrected_triggers.py` - Aplicación de triggers corregidos

### 7. Archivos de Datos
**Patrón:** `*.json`, `*.csv`, `*.xlsx` (no críticos)
**Destino:** `data/`

### 8. Documentación Técnica
**Patrón:** `*.md` (excepto README.md)
**Destino:** `docs/tech/`

Archivos identificados:
- `DEPENDENCIAS_INSTALADAS.md`

### 9. Scripts de Reorganización (Meta)
**Destino:** `organizacion/`

Archivos:
- `reorganizar_archivos.py`
- `reorganizar_archivos_seguro.py`
- `verificar_despues_reorganizacion.py`
- `PLAN_REORGANIZACION_ARCHIVOS.md`

## Estructura Final Propuesta

```
synapsis/
├── app.py
├── main.py
├── main_fixed.py
├── temp_main.py
├── requirements.txt
├── .env.example
├── README.md
├── templates/
├── static/
├── migrations/
├── supabase/
├── sql/
├── backups/
├── triggers/
├── test/
│   ├── test_asistencia_endpoints.py
│   ├── test_frontend_camisetapolo_final.py
│   └── test_sandra_hierarchy.py
├── diagnosticos/
│   ├── diagnostico_problema_stock.py
│   └── diagnostico_mysql.py
├── verificar/
│   └── verificar_acceso_devoluciones.py
├── fix/
│   └── fix_api.py
├── debug/
│   └── debug_servidor_mysql.py
├── utilidades/
│   ├── migration_triggers.py
│   ├── validar_sintaxis_triggers.py
│   ├── ejecutar_triggers_localhost.py
│   ├── patch_logging_ferretero.py
│   ├── analizar_recurso_operativo.py
│   └── apply_corrected_triggers.py
├── data/
└── organizacion/
    ├── reorganizar_archivos.py
    ├── reorganizar_archivos_seguro.py
    ├── verificar_despues_reorganizacion.py
    └── PLAN_REORGANIZACION_ARCHIVOS.md
```

## Scripts de Reorganización

### 1. `reorganizar_archivos_seguro.py`
- **Propósito:** Reorganizar archivos de forma segura
- **Características:**
  - Análisis de dependencias antes de mover
  - Confirmación del usuario antes de ejecutar
  - Reporte detallado de cambios
  - Capacidad de deshacer cambios

### 2. `verificar_despues_reorganizacion.py`
- **Propósito:** Verificar que la aplicación funcione después de la reorganización
- **Verificaciones:**
  - Archivos críticos presentes
  - Importaciones Python funcionando
  - Dependencias instaladas
  - Sintaxis correcta
  - Estructura de directorios

## Pasos de Implementación

1. **Ejecutar el script de reorganización seguro:**
   ```bash
   python reorganizar_archivos_seguro.py
   ```

2. **Verificar la reorganización:**
   ```bash
   python verificar_despues_reorganizacion.py
   ```

3. **Probar la aplicación:**
   ```bash
   python main.py
   ```

## Consideraciones de Seguridad

- **Backup:** Se recomienda hacer un backup completo antes de ejecutar la reorganización
- **Git:** Si usas Git, asegúrate de tener un commit limpio antes de reorganizar
- **Testing:** Ejecuta las pruebas existentes después de la reorganización
- **Rollback:** Mantén los scripts de reorganización para poder deshacer cambios si es necesario

## Ventajas de esta Organización

1. **Raíz limpia:** Solo archivos críticos y directorios principales
2. **Fácil navegación:** Categorías claras por tipo de archivo
3. **Mantenimiento simplificado:** Archivos relacionados agrupados
4. **Escalabilidad:** Estructura preparada para crecimiento
5. **Seguridad:** Archivos críticos protegidos de movimientos accidentales

## Notas Adicionales

- Esta reorganización NO afecta el funcionamiento de la aplicación
- Los scripts de reorganización incluyen verificación de dependencias
- Se mantiene la compatibilidad con rutas existentes
- Los archivos movidos pueden ser accedidos mediante sus nuevas rutas relativas