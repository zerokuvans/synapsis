# SOLUCIÓN: Problemas de Cálculos en Servidor MySQL

## 📋 RESUMEN DEL PROBLEMA

El usuario reporta que los cálculos no funcionan cuando ejecuta la aplicación en un servidor con base de datos MySQL. Después de una investigación exhaustiva, se han identificado múltiples causas potenciales y soluciones.

## 🔍 CAUSAS IDENTIFICADAS

### 1. **TRIGGER FALTANTE (CRÍTICO)**
- ❌ **Problema**: El trigger `actualizar_stock_asignacion` no existe en la base de datos
- 🎯 **Impacto**: Las asignaciones se insertan pero el stock no se actualiza
- ✅ **Solución**: Crear el trigger en la base de datos del servidor

### 2. **DIFERENCIAS DE ZONA HORARIA**
- ❌ **Problema**: Diferencias entre zona horaria del servidor, MySQL y Python
- 🎯 **Impacto**: Cálculos de diferencia de días incorrectos
- ✅ **Solución**: Sincronizar zonas horarias o usar UTC

### 3. **CONFIGURACIÓN DE MYSQL**
- ❌ **Problema**: Diferencias en SQL_MODE, charset, collation entre entornos
- 🎯 **Impacto**: Comportamiento inconsistente en cálculos de fechas
- ✅ **Solución**: Estandarizar configuración MySQL

### 4. **VARIABLES DE ENTORNO**
- ❌ **Problema**: Variables MYSQL_* no configuradas correctamente en servidor
- 🎯 **Impacto**: Conexión fallida o configuración incorrecta
- ✅ **Solución**: Verificar archivo .env en servidor

### 5. **PERMISOS DE BASE DE DATOS**
- ❌ **Problema**: Usuario MySQL sin permisos suficientes
- 🎯 **Impacto**: Operaciones de SELECT/INSERT fallan
- ✅ **Solución**: Verificar y otorgar permisos necesarios

## 🛠️ SOLUCIONES IMPLEMENTADAS

### 1. Scripts de Diagnóstico

#### `diagnostico_mysql.py`
- Verifica configuración de MySQL
- Compara cálculos de fechas Python vs MySQL
- Valida variables de entorno
- Verifica permisos de base de datos

#### `debug_servidor_mysql.py`
- Debug completo del entorno
- Información detallada de MySQL
- Pruebas de funciones de fecha
- Recomendaciones específicas

#### `test_calculos_servidor.py`
- Simula exactamente el comportamiento de `registrar_ferretero`
- Reproduce los cálculos de límites
- Identifica puntos de falla

### 2. Parche de Logging

#### Archivos generados:
- `logging_code.py`: Código de logging detallado
- `patched_calculation_code.py`: Código de cálculos con logging
- `patch_installation_instructions.txt`: Instrucciones de instalación

## 🚀 PLAN DE ACCIÓN RECOMENDADO

### PASO 1: Verificación Inmediata en Servidor
```bash
# 1. Ejecutar scripts de diagnóstico en el servidor
python diagnostico_mysql.py
python debug_servidor_mysql.py
python test_calculos_servidor.py

# 2. Comparar resultados con entorno local
```

### PASO 2: Verificar Trigger Faltante
```sql
-- Verificar si existe el trigger
SHOW TRIGGERS LIKE 'actualizar_stock_asignacion';

-- Si no existe, crearlo (solicitar al DBA el código del trigger)
```

### PASO 3: Sincronizar Configuración
```sql
-- Verificar zona horaria MySQL
SELECT @@global.time_zone, @@session.time_zone;

-- Verificar configuración
SELECT @@sql_mode;
SHOW VARIABLES LIKE 'character_set%';
SHOW VARIABLES LIKE 'collation%';
```

### PASO 4: Aplicar Parche de Logging
```bash
# 1. Hacer backup
cp main.py main.py.backup.$(date +%Y%m%d_%H%M%S)

# 2. Aplicar parche siguiendo instrucciones
# 3. Reiniciar aplicación
# 4. Monitorear ferretero_debug.log
```

### PASO 5: Verificar Variables de Entorno
```bash
# Verificar archivo .env en servidor
cat .env

# Verificar permisos
ls -la .env
```

## 🔧 SOLUCIONES ESPECÍFICAS

### Para Problemas de Zona Horaria
```python
# Opción 1: Usar UTC en lugar de datetime.now()
fecha_actual = datetime.utcnow()

# Opción 2: Forzar zona horaria específica
import pytz
tz = pytz.timezone('America/Bogota')
fecha_actual = datetime.now(tz)
```

### Para Problemas de Trigger
```sql
-- Ejemplo de trigger que podría estar faltando
CREATE TRIGGER actualizar_stock_asignacion
AFTER INSERT ON ferretero
FOR EACH ROW
BEGIN
    -- Lógica para actualizar stock
    UPDATE stock_general 
    SET stock_actual = stock_actual - NEW.silicona
    WHERE material = 'Silicona';
    
    -- Más lógica según sea necesario
END;
```

### Para Problemas de Permisos
```sql
-- Otorgar permisos necesarios
GRANT SELECT, INSERT, UPDATE ON capired.ferretero TO 'usuario_app'@'%';
GRANT SELECT ON capired.recurso_operativo TO 'usuario_app'@'%';
GRANT SELECT, UPDATE ON capired.stock_general TO 'usuario_app'@'%';
FLUSH PRIVILEGES;
```

## 📊 MONITOREO Y VALIDACIÓN

### Logs a Monitorear
1. `ferretero_debug.log` - Logging detallado de cálculos
2. Logs de aplicación Flask
3. Logs de MySQL (error.log, slow.log)

### Métricas a Verificar
1. Tiempo de respuesta de cálculos
2. Errores en inserción de registros
3. Consistencia de stock
4. Diferencias en cálculos de fechas

## 🎯 RESULTADOS ESPERADOS

Después de aplicar estas soluciones:

✅ Los cálculos de límites funcionarán correctamente en el servidor
✅ Las asignaciones se insertarán y el stock se actualizará
✅ Los logs proporcionarán visibilidad completa del proceso
✅ Se identificará la causa raíz específica del problema

## 📞 SOPORTE ADICIONAL

Si el problema persiste después de aplicar estas soluciones:

1. **Revisar logs detallados** generados por el parche
2. **Comparar configuraciones** entre entorno local y servidor
3. **Verificar versiones** de Python, MySQL y dependencias
4. **Contactar al DBA** para verificar configuración de base de datos

---

**Fecha de creación**: $(date)
**Archivos relacionados**: 
- `main.py` (línea 3292 - función registrar_ferretero)
- `diagnostico_mysql.py`
- `debug_servidor_mysql.py` 
- `test_calculos_servidor.py`
- `patch_logging_ferretero.