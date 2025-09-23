# APIs del Sistema de Gestión de Estados de Devoluciones

## Descripción General

Este documento describe las APIs implementadas para el sistema de gestión de estados de devoluciones, incluyendo endpoints para actualizar estados, consultar transiciones válidas y obtener historial de cambios.

## Autenticación y Permisos

Todas las APIs requieren:
- **Autenticación**: Usuario logueado con sesión válida
- **Autorización**: Rol de 'logistica' o superior
- **Headers**: `Content-Type: application/json` para requests con body JSON

## Endpoints Disponibles

### 1. Actualizar Estado de Devolución

**Endpoint**: `PUT /api/devoluciones/{id}/estado`

**Descripción**: Actualiza el estado de una devolución específica con validaciones de transición y auditoría automática.

**Parámetros de URL**:
- `id` (integer): ID de la devolución

**Body (JSON)**:
```json
{
  "nuevo_estado": "PROCESANDO",
  "motivo": "Iniciando proceso de revisión de elementos"
}
```

**Campos del Body**:
- `nuevo_estado` (string, obligatorio): Nuevo estado de la devolución
  - Valores válidos: `REGISTRADA`, `PROCESANDO`, `COMPLETADA`, `CANCELADA`
- `motivo` (string, obligatorio): Justificación del cambio de estado

**Respuesta Exitosa (200)**:
```json
{
  "success": true,
  "mensaje": "Estado actualizado exitosamente",
  "estado_anterior": "REGISTRADA",
  "estado_nuevo": "PROCESANDO",
  "devolucion_id": 123
}
```

**Respuestas de Error**:
- `400`: Datos faltantes o estado no válido
- `403`: Transición no permitida para el rol del usuario
- `404`: Devolución no encontrada
- `500`: Error interno del servidor

**Ejemplo de uso en JavaScript**:
```javascript
async function actualizarEstadoDevolucion(devolucionId, nuevoEstado, motivo) {
  try {
    const response = await fetch(`/api/devoluciones/${devolucionId}/estado`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        nuevo_estado: nuevoEstado,
        motivo: motivo
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('Estado actualizado:', data);
      // Actualizar UI
      actualizarInterfazEstado(data.estado_nuevo);
    } else {
      console.error('Error:', data.error);
      mostrarError(data.error);
    }
  } catch (error) {
    console.error('Error de red:', error);
  }
}
```

### 2. Obtener Transiciones Válidas

**Endpoint**: `GET /api/devoluciones/{id}/transiciones`

**Descripción**: Obtiene las transiciones de estado válidas para una devolución específica según el rol del usuario.

**Parámetros de URL**:
- `id` (integer): ID de la devolución

**Respuesta Exitosa (200)**:
```json
{
  "success": true,
  "devolucion_id": 123,
  "estado_actual": "REGISTRADA",
  "transiciones_validas": [
    {
      "estado_destino": "PROCESANDO",
      "descripcion": "Iniciar procesamiento",
      "requiere_motivo": true
    },
    {
      "estado_destino": "CANCELADA",
      "descripcion": "Cancelar devolución",
      "requiere_motivo": true
    }
  ],
  "rol_usuario": "logistica"
}
```

**Ejemplo de uso en JavaScript**:
```javascript
async function obtenerTransicionesValidas(devolucionId) {
  try {
    const response = await fetch(`/api/devoluciones/${devolucionId}/transiciones`);
    const data = await response.json();
    
    if (data.success) {
      // Generar botones de acción según transiciones válidas
      generarBotonesTransicion(data.transiciones_validas, devolucionId);
    }
  } catch (error) {
    console.error('Error al obtener transiciones:', error);
  }
}

function generarBotonesTransicion(transiciones, devolucionId) {
  const container = document.getElementById('acciones-estado');
  container.innerHTML = '';
  
  transiciones.forEach(transicion => {
    const button = document.createElement('button');
    button.className = `btn btn-${getButtonClass(transicion.estado_destino)}`;
    button.textContent = transicion.descripcion;
    button.onclick = () => {
      const motivo = prompt('Ingrese el motivo del cambio:');
      if (motivo) {
        actualizarEstadoDevolucion(devolucionId, transicion.estado_destino, motivo);
      }
    };
    container.appendChild(button);
  });
}

function getButtonClass(estado) {
  const classes = {
    'PROCESANDO': 'warning',
    'COMPLETADA': 'success',
    'CANCELADA': 'danger'
  };
  return classes[estado] || 'secondary';
}
```

### 3. Obtener Historial de Estados

**Endpoint**: `GET /api/devoluciones/{id}/historial`

**Descripción**: Consulta el historial completo de cambios de estado de una devolución.

**Parámetros de URL**:
- `id` (integer): ID de la devolución

**Respuesta Exitosa (200)**:
```json
{
  "success": true,
  "devolucion_id": 123,
  "estado_actual": "PROCESANDO",
  "total_cambios": 2,
  "historial": [
    {
      "id": 45,
      "estado_anterior": "REGISTRADA",
      "estado_nuevo": "PROCESANDO",
      "motivo_cambio": "Iniciando proceso de revisión",
      "fecha_cambio": "2024-01-15T10:30:00",
      "usuario_nombre": "Juan Pérez",
      "rol_usuario": "logistica"
    },
    {
      "id": 44,
      "estado_anterior": null,
      "estado_nuevo": "REGISTRADA",
      "motivo_cambio": "Registro inicial",
      "fecha_cambio": "2024-01-15T09:15:00",
      "usuario_nombre": "María García",
      "rol_usuario": "operario"
    }
  ]
}
```

**Ejemplo de uso en JavaScript**:
```javascript
async function mostrarHistorialEstados(devolucionId) {
  try {
    const response = await fetch(`/api/devoluciones/${devolucionId}/historial`);
    const data = await response.json();
    
    if (data.success) {
      generarTablaHistorial(data.historial);
    }
  } catch (error) {
    console.error('Error al obtener historial:', error);
  }
}

function generarTablaHistorial(historial) {
  const tbody = document.getElementById('historial-tbody');
  tbody.innerHTML = '';
  
  historial.forEach(registro => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${formatearFecha(registro.fecha_cambio)}</td>
      <td>
        <span class="badge bg-secondary">${registro.estado_anterior || 'Inicial'}</span>
        <i class="fas fa-arrow-right mx-2"></i>
        <span class="badge bg-${getBadgeClass(registro.estado_nuevo)}">${registro.estado_nuevo}</span>
      </td>
      <td>${registro.motivo_cambio}</td>
      <td>${registro.usuario_nombre} <small class="text-muted">(${registro.rol_usuario})</small></td>
    `;
    tbody.appendChild(row);
  });
}

function formatearFecha(fechaISO) {
  return new Date(fechaISO).toLocaleString('es-ES');
}

function getBadgeClass(estado) {
  const classes = {
    'REGISTRADA': 'primary',
    'PROCESANDO': 'warning',
    'COMPLETADA': 'success',
    'CANCELADA': 'danger'
  };
  return classes[estado] || 'secondary';
}
```

### 4. Validar Transición de Estado

**Endpoint**: `POST /api/estados/validar-transicion`

**Descripción**: Valida si una transición de estado específica es permitida para el usuario actual.

**Body (JSON)**:
```json
{
  "estado_actual": "REGISTRADA",
  "estado_nuevo": "PROCESANDO"
}
```

**Respuesta Exitosa (200)**:
```json
{
  "success": true,
  "validacion": {
    "valida": true,
    "mensaje": "Transición permitida",
    "rol_usuario": "logistica"
  }
}
```

**Ejemplo de uso en JavaScript**:
```javascript
async function validarTransicion(estadoActual, estadoNuevo) {
  try {
    const response = await fetch('/api/estados/validar-transicion', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        estado_actual: estadoActual,
        estado_nuevo: estadoNuevo
      })
    });
    
    const data = await response.json();
    return data.validacion;
  } catch (error) {
    console.error('Error al validar transición:', error);
    return { valida: false, mensaje: 'Error de conexión' };
  }
}
```

## Integración en el Frontend

### 1. Actualización de la Interfaz de Devoluciones

Para integrar estas APIs en la página de devoluciones existente:

```javascript
// Agregar al archivo devoluciones_dotacion.html

// Función para cargar acciones disponibles
function cargarAccionesEstado(devolucionId, estadoActual) {
  obtenerTransicionesValidas(devolucionId).then(data => {
    if (data && data.success) {
      const container = document.getElementById(`acciones-${devolucionId}`);
      if (container) {
        generarBotonesTransicion(data.transiciones_validas, devolucionId);
      }
    }
  });
}

// Función para mostrar modal de historial
function mostrarModalHistorial(devolucionId) {
  mostrarHistorialEstados(devolucionId).then(() => {
    $('#modalHistorial').modal('show');
  });
}

// Agregar botones de acción a cada fila de la tabla
function agregarBotonesAccion(devolucionId, estadoActual) {
  return `
    <div class="btn-group" role="group">
      <button type="button" class="btn btn-sm btn-outline-primary" 
              onclick="cargarAccionesEstado(${devolucionId}, '${estadoActual}')">
        <i class="fas fa-edit"></i> Cambiar Estado
      </button>
      <button type="button" class="btn btn-sm btn-outline-info" 
              onclick="mostrarModalHistorial(${devolucionId})">
        <i class="fas fa-history"></i> Historial
      </button>
    </div>
  `;
}
```

### 2. Modal para Historial de Estados

Agregar al HTML:

```html
<!-- Modal para Historial de Estados -->
<div class="modal fade" id="modalHistorial" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Historial de Estados</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Cambio de Estado</th>
              <th>Motivo</th>
              <th>Usuario</th>
            </tr>
          </thead>
          <tbody id="historial-tbody">
            <!-- Contenido dinámico -->
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
```

### 3. Estilos CSS Adicionales

```css
/* Estilos para badges de estado */
.badge-estado {
  font-size: 0.75rem;
  padding: 0.375rem 0.75rem;
}

.estado-REGISTRADA { background-color: #0d6efd; }
.estado-PROCESANDO { background-color: #fd7e14; }
.estado-COMPLETADA { background-color: #198754; }
.estado-CANCELADA { background-color: #dc3545; }

/* Animación para transiciones */
.estado-transition {
  transition: all 0.3s ease;
}

/* Estilos para historial */
.historial-item {
  border-left: 3px solid #dee2e6;
  padding-left: 1rem;
  margin-bottom: 1rem;
}

.historial-item.completada {
  border-left-color: #198754;
}

.historial-item.cancelada {
  border-left-color: #dc3545;
}
```

## Manejo de Errores

### Códigos de Error Comunes

- **400 Bad Request**: Datos faltantes o formato incorrecto
- **401 Unauthorized**: Usuario no autenticado
- **403 Forbidden**: Permisos insuficientes o transición no válida
- **404 Not Found**: Devolución no encontrada
- **500 Internal Server Error**: Error del servidor

### Función de Manejo de Errores

```javascript
function manejarErrorAPI(error, contexto = '') {
  console.error(`Error en ${contexto}:`, error);
  
  let mensaje = 'Ha ocurrido un error inesperado';
  
  if (error.error) {
    mensaje = error.error;
  } else if (error.message) {
    mensaje = error.message;
  }
  
  // Mostrar notificación de error
  mostrarNotificacion(mensaje, 'error');
}

function mostrarNotificacion(mensaje, tipo = 'info') {
  // Implementar según el sistema de notificaciones usado
  // Ejemplo con toast de Bootstrap
  const toast = document.createElement('div');
  toast.className = `toast align-items-center text-white bg-${tipo === 'error' ? 'danger' : 'success'}`;
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${mensaje}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  `;
  
  document.getElementById('toast-container').appendChild(toast);
  new bootstrap.Toast(toast).show();
}
```

## Consideraciones de Seguridad

1. **Validación del lado del servidor**: Todas las validaciones se realizan en el backend
2. **Control de permisos**: Verificación de roles en cada endpoint
3. **Auditoría**: Registro automático de todos los cambios
4. **Sanitización**: Escape de datos en las respuestas JSON

## Testing

Para probar las APIs, ejecutar:

```bash
python test_estado_apis.py
```

Este script ejecutará pruebas automatizadas de todos los endpoints y generará un reporte detallado.

---

**Nota**: Asegúrate de que las tablas de auditoría, notificaciones y permisos estén creadas antes de usar estas APIs. Consulta la documentación de arquitectura para más detalles sobre la estructura de la base de datos.