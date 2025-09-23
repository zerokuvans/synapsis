# Solución al Error "Error al cargar historial"

## Problema Identificado
El error "Error al cargar historial" aparecía en el frontend al intentar cargar el historial de estados de las devoluciones.

## Causas Encontradas y Solucionadas

### 1. Tabla Incorrecta en la Base de Datos
**Problema**: El endpoint `/api/devoluciones/{id}/historial` estaba consultando la tabla `auditoria_estados` en lugar de `auditoria_estados_devolucion`.

**Solución**: Se corrigió la consulta SQL en `main.py` línea ~13370:
```sql
-- ANTES (incorrecto)
SELECT ae.*, u.nombre as usuario_nombre
FROM auditoria_estados ae
LEFT JOIN usuarios u ON ae.usuario_id = u.id

-- DESPUÉS (correcto)
SELECT aed.*, r.nombre_rol as usuario_nombre
FROM auditoria_estados_devolucion aed
LEFT JOIN recurso_operativo r ON aed.usuario_id = r.id_codigo_consumidor
```

### 2. Contraseña del Usuario de Prueba
**Problema**: El usuario de prueba (cédula: 12345678) tenía una contraseña incorrecta que impedía el login.

**Solución**: Se actualizó la contraseña del usuario a 'password123' con hash bcrypt correcto.

### 3. Rutas del Frontend
**Problema**: Las pruebas estaban usando rutas incorrectas para el login y las devoluciones.

**Solución**: 
- Login: Usar la ruta raíz `/` (no `/login`)
- Devoluciones: Usar `/logistica/devoluciones_dotacion` (no `/devoluciones`)

## Verificación de la Solución

### Pruebas Realizadas
1. ✅ Login con usuario de prueba (cédula: 12345678, password: password123)
2. ✅ Acceso a la página de devoluciones
3. ✅ Endpoint `/api/devoluciones/1/historial` retorna JSON válido
4. ✅ Manejo correcto de errores de autenticación
5. ✅ Sin errores en la consola del navegador

### Respuesta del Endpoint Corregido
```json
{
  "devolucion_id": 1,
  "estado_actual": "REGISTRADA",
  "historial": [],
  "success": true,
  "total_cambios": 0
}
```

## Archivos Modificados
1. `main.py` - Corrección de la consulta SQL del endpoint de historial
2. `recurso_operativo` (tabla) - Actualización de contraseña del usuario de prueba

## Scripts de Verificación Creados
1. `test_historial_completo.py` - Prueba específica del endpoint de historial
2. `test_frontend_completo.py` - Prueba completa del flujo frontend
3. `verificar_password_usuario.py` - Verificación y corrección de contraseñas

## Estado Final
✅ **PROBLEMA RESUELTO**: El error "Error al cargar historial" ya no aparece en el frontend. El sistema funciona correctamente con autenticación, acceso a devoluciones y carga de historial de estados.