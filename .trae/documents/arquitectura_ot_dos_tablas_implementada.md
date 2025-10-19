# Arquitectura de Órdenes de Trabajo - Dos Tablas (Implementada)

## Resumen

Se ha implementado una arquitectura de dos tablas para gestionar las órdenes de trabajo (OT) de técnicos, separando los datos principales de los detalles de códigos.

## Estructura de Tablas

### 1. Tabla Principal: `gestion_ot_tecnicos`
- **Propósito**: Almacena un resumen por OT con datos agregados
- **Unicidad**: Una fila por OT y técnico
- **Campos principales**:
  - `id`: Identificador único (PK)
  - `ot`: Número de orden de trabajo
  - `cuenta`: Cuenta del cliente
  - `servicio`: Servicio asociado
  - `tecnico_id`: ID del técnico
  - `tecnico_nombre`: Nombre del técnico
  - `total_valor`: Suma total de todos los códigos
  - `tecnologia`: Tecnología utilizada
  - `categoria`: Categoría de la OT
  - `fecha_creacion`: Fecha de creación
  - `fecha_actualizacion`: Última actualización

### 2. Tabla de Historial: `gestion_ot_tecnicos_historial`
- **Propósito**: Almacena cada código individual con sus detalles
- **Relación**: Múltiples filas por OT (relacionadas con tabla principal)
- **Campos principales**:
  - `id`: Identificador único (PK)
  - `ot_id`: ID de la tabla principal (FK lógica)
  - `ot`: Número de orden de trabajo (para referencia)
  - `codigo`: Código del material/servicio
  - `nombre`: Nombre corto del código
  - `descripcion`: Descripción detallada
  - `cantidad`: Cantidad del código
  - `valor_unitario`: Valor unitario
  - `valor_total`: Valor total (cantidad × valor_unitario)
  - `fecha_creacion`: Fecha de creación del registro

## Endpoints Backend Implementados

### 1. Listar Órdenes (GET /tecnicos/ordenes)
- **Función**: `api_tecnicos_list_ordenes`
- **Descripción**: Obtiene todas las OT del técnico autenticado desde la tabla principal
- **Respuesta**: Array de objetos con resumen de cada OT incluyendo cantidad de códigos

### 2. Ver Detalles de OT (GET /tecnicos/ordenes/detalle/{ot})
- **Función**: `api_tecnicos_get_orden_detalle`
- **Descripción**: Obtiene todos los códigos de una OT específica desde la tabla historial
- **Respuesta**: Objeto con información general de la OT y array de códigos

### 3. Crear Nueva Orden (POST /tecnicos/ordenes)
- **Función**: `api_tecnicos_create_orden`
- **Descripción**: 
  - Inserta/actualiza resumen en tabla principal
  - Inserta cada código individual en tabla historial
  - Calcula totales automáticamente
- **Flujo**:
  1. Verifica si existe OT para el técnico
  2. Si existe: actualiza totales
  3. Si no existe: crea nuevo registro
  4. Inserta cada código en historial con referencia al ID principal

## Frontend Actualizado

### Funciones JavaScript Modificadas

#### 1. actualizarTabla()
- Ahora muestra una sola fila por OT
- Muestra "Activa" como estado por defecto
- Usa `verDetallesOTById()` en lugar de `verDetallesOT()`

#### 2. verDetallesOTById(id)
- Nueva función para cargar detalles usando el ID de la tabla principal
- Obtiene la OT desde la lista local y luego carga detalles

#### 3. cargarDetallesOTById(id)
- Busca la OT en la lista local usando el ID
- Llama al endpoint de detalles con el número de OT
- Muestra todos los códigos en el modal de detalles

## Ventajas de la Arquitectura

1. **Separación de Responsabilidades**:
   - Tabla principal: Datos agregados y resumen
   - Tabla historial: Detalles individuales

2. **Rendimiento**:
   - Listado rápido sin cálculos complejos
   - Detalles solo cuando se necesitan

3. **Escalabilidad**:
   - Fácil agregar nuevos campos a either tabla
   - Índices optimizados por función

4. **Integridad**:
   - Relación lógica clara entre tablas
   - Actualización atómica en ambas tablas

5. **Flexibilidad**:
   - Fácil agregar más metadata a la OT principal
   - Historial completo de todos los códigos

## Flujo de Datos Completo

```
1. Crear OT:
   Frontend → POST /tecnicos/ordenes → Backend
   Backend: 
   - Inserta/Actualiza gestion_ot_tecnicos
   - Inserta múltiples registros en gestion_ot_tecnicos_historial
   - Retorna confirmación

2. Listar OTs:
   Frontend → GET /tecnicos/ordenes → Backend
   Backend:
   - Lee gestion_ot_tecnicos (resúmenes)
   - Cuenta códigos en gestion_ot_tecnicos_historial
   - Retorna array de OTs

3. Ver Detalles:
   Frontend → GET /tecnicos/ordenes/detalle/{ot} → Backend
   Backend:
   - Lee gestion_ot_tecnicos (info general)
   - Lee gestion_ot_tecnicos_historial (códigos)
   - Retorna OT completa con todos los códigos
```

## Estado Actual

✅ **Implementado y Funcional**:
- Backend: Todas las funciones modificadas
- Frontend: Tabla principal y detalles actualizados
- Base de datos: Ambas tablas existentes
- Flujo completo: Crear → Listar → Ver detalles

## Próximos Pasos Recomendados

1. **Optimización de Consultas**:
   - Agregar índices en campos frecuentemente consultados
   - Considerar vistas materializadas para reportes

2. **Funcionalidades Adicionales**:
   - Editar OT existente
   - Eliminar OT (cascada a historial)
   - Exportar detalles a PDF/Excel

3. **Mejoras de UI**:
   - Paginación en detalles si hay muchos códigos
   - Búsqueda y filtros en detalles
   - Resumen de totales por categoría

4. **Validaciones**:
   - Verificar duplicados en historial
   - Validar límites de caracteres
   - Control de concurrencia