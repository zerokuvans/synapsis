# Sistema de Registro Preoperacional Mejorado - Documento de Requerimientos

## 1. Resumen Ejecutivo

El sistema de registro preoperacional actual requiere mejoras significativas para automatizar la captura de datos vehiculares y de licencias, reduciendo errores manuales y mejorando la eficiencia operativa. Este documento especifica los requerimientos para implementar un sistema automatizado que obtenga información desde las tablas existentes y valide datos críticos como el kilometraje.

## 2. Objetivos del Proyecto

- **Automatizar** la captura de datos vehiculares y de licencias desde las bases de datos existentes
- **Reducir errores** manuales en el registro preoperacional
- **Implementar validaciones** robustas para el kilometraje vehicular
- **Mejorar la experiencia** del técnico con formularios auto-completados
- **Mantener integridad** de datos históricos de kilometraje

## 3. Requerimientos Funcionales Detallados

### 3.1 Datos del Vehículo y Ubicación

#### 3.1.1 Ciudad
- **Fuente**: Tabla `recurso_operativo`, columna `ciudad`
- **Comportamiento**: Auto-completar basado en el técnico logueado
- **Validación**: Campo de solo lectura una vez cargado
- **Relación**: Vinculado a la cédula del técnico en sesión

#### 3.1.2 Placa del Vehículo
- **Fuente**: Tabla `mpa_vehiculos`, columna `placa`
- **Comportamiento**: Auto-completar según vehículo asignado al técnico
- **Validación**: Campo de solo lectura, clave para otras consultas
- **Relación**: Vehículo asignado al técnico logueado

#### 3.1.3 Modelo y Marca
- **Fuente**: Tabla `mpa_vehiculos`, columnas `modelo` y `marca`
- **Comportamiento**: Auto-completar basado en la placa obtenida
- **Validación**: Campos de solo lectura
- **Dependencia**: Requiere placa válida

### 3.2 Información de Licencia de Conducción

#### 3.2.1 Tipo de Licencia
- **Fuente**: Tabla `mpa_licencia_conducir`, columna `tipo_licencia`
- **Comportamiento**: Auto-completar según técnico logueado
- **Validación**: Campo de solo lectura
- **Formato**: Mostrar categoría completa (ej: "B1", "C1", etc.)

#### 3.2.2 Fecha de Vencimiento de Licencia
- **Fuente**: Tabla `mpa_licencia_conducir`, columna `fecha_vencimiento`
- **Comportamiento**: Auto-completar según técnico logueado
- **Validación**: 
  - Campo de solo lectura
  - Mostrar alerta si está próxima a vencer (30 días)
  - Bloquear registro si está vencida
- **Formato**: DD/MM/AAAA

### 3.3 Documentación Vehicular

#### 3.3.1 SOAT - Fecha de Vencimiento
- **Fuente**: Tabla `mpa_soat`, columna `fecha_vencimiento`
- **Comportamiento**: Auto-completar según placa del vehículo
- **Validación**:
  - Campo de solo lectura
  - Mostrar alerta si está próxima a vencer (30 días)
  - Bloquear registro si está vencida
- **Formato**: DD/MM/AAAA

#### 3.3.2 Técnico Mecánica - Fecha de Vencimiento
- **Fuente**: Tabla `mpa_tecnico_mecanica`, columna `fecha_vencimiento`
- **Comportamiento**: Auto-completar según placa del vehículo
- **Validación**:
  - Campo de solo lectura
  - Mostrar alerta si está próxima a vencer (30 días)
  - Bloquear registro si está vencida
- **Formato**: DD/MM/AAAA

### 3.4 Kilometraje Actual - Validación Crítica

#### 3.4.1 Campo de Entrada Manual
- **Tipo**: Campo numérico editable
- **Comportamiento**: Entrada manual obligatoria
- **Formato**: Números enteros, sin decimales
- **Placeholder**: "Ingrese kilometraje actual"

#### 3.4.2 Validación de Kilometraje
- **Regla Principal**: No puede ser menor al último registrado para esa placa
- **Fuente de Comparación**: Último registro en tabla `preoperacional` para la placa específica
- **Comportamiento de Validación**:
  - Validar en tiempo real (evento onBlur)
  - Mostrar último kilometraje registrado como referencia
  - Bloquear envío del formulario si es inválido
  - Mostrar mensaje de error específico

#### 3.4.3 Mensajes de Validación
- **Error**: "El kilometraje no puede ser menor al último registrado: [X] km en fecha [DD/MM/AAAA]"
- **Información**: "Último kilometraje registrado: [X] km"
- **Éxito**: "Kilometraje válido ✓"

## 4. Requerimientos Técnicos

### 4.1 Nuevos Endpoints API

#### 4.1.1 GET /api/preoperacional/datos-vehiculo
- **Propósito**: Obtener todos los datos del vehículo y licencia del técnico
- **Parámetros**: Cédula del técnico (desde sesión)
- **Respuesta**: JSON con todos los campos requeridos
- **Autenticación**: Requerida

#### 4.1.2 GET /api/preoperacional/ultimo-kilometraje/{placa}
- **Propósito**: Obtener último kilometraje registrado para una placa
- **Parámetros**: Placa del vehículo
- **Respuesta**: JSON con kilometraje y fecha
- **Autenticación**: Requerida

#### 4.1.3 POST /api/preoperacional/validar-kilometraje
- **Propósito**: Validar kilometraje antes del envío
- **Parámetros**: Placa y kilometraje propuesto
- **Respuesta**: JSON con resultado de validación
- **Autenticación**: Requerida

### 4.2 Modificaciones en Base de Datos

#### 4.2.1 Verificación de Relaciones
- Confirmar relaciones entre `mpa_vehiculos` y técnicos
- Verificar integridad referencial en `mpa_licencia_conducir`
- Validar estructura de `mpa_soat` y `mpa_tecnico_mecanica`

#### 4.2.2 Índices Requeridos
- Índice en `mpa_vehiculos.placa`
- Índice en `preoperacional.placa` para consultas de kilometraje
- Índice compuesto en `preoperacional(placa, fecha)` para optimización

### 4.3 Frontend - Modificaciones JavaScript

#### 4.3.1 Auto-completado de Formulario
- Función `cargarDatosVehiculo()` al cargar la página
- Poblar campos automáticamente desde API
- Deshabilitar campos auto-completados

#### 4.3.2 Validación de Kilometraje
- Función `validarKilometraje()` en evento onBlur
- Mostrar indicadores visuales de validación
- Prevenir envío si validación falla

#### 4.3.3 Manejo de Errores
- Mostrar mensajes de error claros
- Fallbacks para datos no encontrados
- Logging de errores para debugging

## 5. Flujo de Usuario Mejorado

### 5.1 Carga Inicial del Formulario
1. Usuario accede al formulario preoperacional
2. Sistema obtiene datos del técnico desde sesión
3. Auto-completa todos los campos desde las tablas correspondientes
4. Muestra último kilometraje como referencia
5. Habilita solo el campo de kilometraje para edición

### 5.2 Validación de Kilometraje
1. Usuario ingresa kilometraje actual
2. Sistema valida en tiempo real contra último registro
3. Muestra mensaje de validación (éxito/error)
4. Habilita/deshabilita botón de envío según validación

### 5.3 Envío del Formulario
1. Validación final de todos los campos
2. Verificación de documentos no vencidos
3. Confirmación de kilometraje válido
4. Envío a base de datos con todos los datos

## 6. Validaciones y Alertas

### 6.1 Documentos Próximos a Vencer (30 días)
- **Licencia de Conducción**: Alerta amarilla
- **SOAT**: Alerta amarilla
- **Técnico Mecánica**: Alerta amarilla

### 6.2 Documentos Vencidos
- **Cualquier documento vencido**: Bloqueo total del registro
- **Mensaje**: "No puede realizar el preoperacional. Documento [X] vencido desde [fecha]"

### 6.3 Kilometraje Inválido
- **Bloqueo de envío**: Botón deshabilitado
- **Mensaje claro**: Con último kilometraje registrado
- **Indicador visual**: Campo con borde rojo

## 7. Casos de Uso Especiales

### 7.1 Técnico Sin Vehículo Asignado
- **Comportamiento**: Mostrar mensaje informativo
- **Acción**: Contactar administrador para asignación
- **Bloqueo**: No permitir registro preoperacional

### 7.2 Datos Faltantes en Tablas
- **Licencia no encontrada**: Mostrar campos vacíos con alerta
- **SOAT no encontrado**: Mostrar alerta de documento faltante
- **Técnico mecánica no encontrado**: Mostrar alerta correspondiente

### 7.3 Primer Registro de Kilometraje
- **Comportamiento**: Permitir cualquier valor positivo
- **Validación**: Solo verificar que sea número positivo
- **Mensaje**: "Primer registro de kilometraje para este vehículo"

## 8. Criterios de Aceptación

### 8.1 Funcionalidad Básica
- ✅ Todos los campos se auto-completan correctamente
- ✅ Validación de kilometraje funciona en tiempo real
- ✅ Documentos vencidos bloquean el registro
- ✅ Formulario mantiene funcionalidad existente

### 8.2 Experiencia de Usuario
- ✅ Carga rápida de datos (< 2 segundos)
- ✅ Mensajes de error claros y específicos
- ✅ Indicadores visuales de validación
- ✅ Formulario intuitivo y fácil de usar

### 8.3 Integridad de Datos
- ✅ No se permite kilometraje menor al anterior
- ✅ Datos vehiculares correctos según asignación
- ✅ Fechas de vencimiento actualizadas
- ✅ Historial de kilometraje consistente

## 9. Plan de Implementación

### 9.1 Fase 1: Backend (APIs y Validaciones)
- Crear endpoints para datos vehiculares
- Implementar validación de kilometraje
- Configurar consultas optimizadas

### 9.2 Fase 2: Frontend (Auto-completado)
- Modificar formulario preoperacional
- Implementar carga automática de datos
- Agregar validaciones en tiempo real

### 9.3 Fase 3: Pruebas y Refinamiento
- Pruebas con diferentes escenarios
- Optimización de rendimiento
- Ajustes de UX según feedback

### 9.4 Fase 4: Despliegue y Monitoreo
- Despliegue en producción
- Monitoreo de errores
- Capacitación a usuarios

## 10. Riesgos y Mitigaciones

### 10.1 Datos Inconsistentes
- **Riesgo**: Información faltante en tablas MPA
- **Mitigación**: Validaciones robustas y mensajes informativos

### 10.2 Rendimiento
- **Riesgo**: Consultas lentas con múltiples JOINs
- **Mitigación**: Índices optimizados y consultas eficientes

### 10.3 Cambios en Asignaciones
- **Riesgo**: Técnico cambia de vehículo durante el día
- **Mitigación**: Validación en tiempo real de asignaciones

Este documento servirá como guía completa para la implementación del sistema de registro preoperacional mejorado, asegurando que todos los requerimientos sean cumplidos de manera eficiente y robusta.