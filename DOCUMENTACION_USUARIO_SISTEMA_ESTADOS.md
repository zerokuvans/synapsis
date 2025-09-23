# Documentación de Usuario - Sistema de Gestión de Estados de Devoluciones

## Tabla de Contenidos
1. [Introducción](#introducción)
2. [Conceptos Básicos](#conceptos-básicos)
3. [Estados de Devolución](#estados-de-devolución)
4. [Interfaz de Usuario](#interfaz-de-usuario)
5. [Gestión de Estados](#gestión-de-estados)
6. [Notificaciones](#notificaciones)
7. [Roles y Permisos](#roles-y-permisos)
8. [Auditoría y Trazabilidad](#auditoría-y-trazabilidad)
9. [Configuración del Sistema](#configuración-del-sistema)
10. [Solución de Problemas](#solución-de-problemas)
11. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Introducción

El Sistema de Gestión de Estados de Devoluciones es una herramienta integral que permite gestionar el ciclo completo de las devoluciones de dotación, desde su registro inicial hasta su finalización. El sistema proporciona:

- **Gestión completa del ciclo de vida** de las devoluciones
- **Trazabilidad completa** de todos los cambios de estado
- **Notificaciones automáticas** para mantener informados a los usuarios relevantes
- **Control de permisos** basado en roles
- **Auditoría detallada** de todas las acciones

### Beneficios Principales
- ✅ **Transparencia**: Visibilidad completa del estado de cada devolución
- ✅ **Eficiencia**: Automatización de procesos y notificaciones
- ✅ **Control**: Validaciones y permisos para garantizar la integridad
- ✅ **Trazabilidad**: Historial completo de cambios y responsables

---

## Conceptos Básicos

### ¿Qué es una Devolución?
Una devolución es el proceso mediante el cual un empleado retorna elementos de dotación a la empresa. Cada devolución tiene un estado que indica en qué fase del proceso se encuentra.

### ¿Qué es un Estado?
Un estado representa la situación actual de una devolución en su ciclo de vida. Los estados ayudan a:
- Conocer el progreso de la devolución
- Determinar qué acciones son posibles
- Asignar responsabilidades
- Generar reportes y estadísticas

### Transiciones de Estado
Las transiciones son los cambios permitidos entre estados. No todos los cambios de estado son válidos; el sistema controla qué transiciones son permitidas según:
- El estado actual
- El rol del usuario
- Las reglas de negocio

---

## Estados de Devolución

### 📝 REGISTRADA
**Descripción**: Estado inicial cuando se crea una nueva devolución.

**Características**:
- Es el estado por defecto al crear una devolución
- Indica que la devolución ha sido registrada en el sistema
- Permite realizar modificaciones en los datos

**Transiciones Permitidas**:
- ➡️ **PROCESANDO**: Cuando se inicia el procesamiento
- ➡️ **CANCELADA**: Si se decide cancelar antes de procesar

**Quién puede realizar transiciones**:
- Técnicos, Supervisores, Administradores

---

### ⚙️ PROCESANDO
**Descripción**: La devolución está siendo procesada activamente.

**Características**:
- Indica que el personal está trabajando en la devolución
- Se están verificando y procesando los elementos
- No se pueden realizar modificaciones mayores

**Transiciones Permitidas**:
- ➡️ **COMPLETADA**: Cuando el procesamiento termina exitosamente
- ➡️ **CANCELADA**: Si surge algún problema que impida continuar

**Quién puede realizar transiciones**:
- Técnicos, Supervisores, Administradores

---

### ✅ COMPLETADA
**Descripción**: La devolución ha sido procesada exitosamente.

**Características**:
- Estado final exitoso
- Todos los elementos han sido verificados y procesados
- La devolución está cerrada
- No se permiten más cambios

**Transiciones Permitidas**:
- Ninguna (estado final)

**Quién puede marcar como completada**:
- Supervisores, Administradores

---

### ❌ CANCELADA
**Descripción**: La devolución ha sido cancelada.

**Características**:
- Estado final de cancelación
- Puede ocurrir por diversos motivos (elementos no conformes, decisión administrativa, etc.)
- La devolución está cerrada
- Se requiere especificar el motivo de cancelación

**Transiciones Permitidas**:
- Ninguna (estado final)

**Quién puede cancelar**:
- Supervisores, Administradores

---

## Interfaz de Usuario

### Vista Principal de Devoluciones

La interfaz principal muestra:

1. **Lista de Devoluciones**
   - Tabla con todas las devoluciones
   - Filtros por estado, fecha, cliente
   - Indicadores visuales de estado

2. **Badges de Estado**
   - 🔵 **REGISTRADA**: Badge azul
   - 🟡 **PROCESANDO**: Badge amarillo
   - 🟢 **COMPLETADA**: Badge verde
   - 🔴 **CANCELADA**: Badge rojo

3. **Botones de Acción**
   - Solo se muestran las acciones permitidas según el estado actual
   - Los botones cambian dinámicamente según los permisos del usuario

### Detalle de Devolución

Al hacer clic en una devolución, se muestra:

1. **Información General**
   - Datos del cliente
   - Fecha de creación
   - Estado actual
   - Observaciones

2. **Panel de Gestión de Estados**
   - Estado actual destacado
   - Botones para transiciones disponibles
   - Formulario para cambio de estado

3. **Historial de Cambios**
   - Cronología completa de cambios
   - Usuario responsable de cada cambio
   - Motivos y observaciones
   - Timestamps precisos

---

## Gestión de Estados

### Cómo Cambiar el Estado de una Devolución

#### Paso 1: Acceder a la Devolución
1. Navegar a la lista de devoluciones
2. Hacer clic en la devolución deseada
3. Verificar que tiene permisos para realizar cambios

#### Paso 2: Seleccionar Nueva Estado
1. En el panel de gestión de estados, verá los botones disponibles
2. Solo aparecen las transiciones permitidas para su rol
3. Hacer clic en el botón del estado deseado

#### Paso 3: Completar Información
1. **Motivo** (obligatorio): Razón del cambio de estado
2. **Observaciones** (opcional): Detalles adicionales
3. Hacer clic en "Confirmar Cambio"

#### Paso 4: Confirmación
1. El sistema validará la transición
2. Se actualizará el estado en la base de datos
3. Se registrará en el historial de auditoría
4. Se enviarán notificaciones automáticas
5. Se mostrará un mensaje de confirmación

### Validaciones del Sistema

El sistema realiza las siguientes validaciones:

✅ **Transición Válida**: Verifica que el cambio de estado sea permitido
✅ **Permisos de Usuario**: Confirma que el usuario tenga autorización
✅ **Datos Requeridos**: Valida que se proporcionen motivo y observaciones
✅ **Estado Actual**: Verifica que el estado actual sea el esperado

### Mensajes de Error Comunes

- **"Transición no permitida"**: El cambio de estado solicitado no es válido
- **"Sin permisos suficientes"**: El usuario no tiene autorización para esta acción
- **"Motivo requerido"**: Debe proporcionar una razón para el cambio
- **"Estado ya actualizado"**: Otro usuario modificó el estado simultáneamente

---

## Notificaciones

### Tipos de Notificaciones

El sistema envía notificaciones automáticas en los siguientes casos:

1. **Cambios de Estado**
   - Cuando una devolución cambia de estado
   - Se notifica a los roles relevantes

2. **Asignaciones**
   - Cuando se asigna una devolución a un usuario
   - Notificación directa al usuario asignado

3. **Vencimientos**
   - Recordatorios de devoluciones pendientes
   - Alertas de tiempo límite

### Canales de Notificación

#### 📧 Email
- Notificaciones detalladas con información completa
- Enlaces directos a la devolución
- Plantillas personalizables

#### 📱 SMS
- Notificaciones breves para cambios críticos
- Ideal para notificaciones urgentes
- Configuración opcional

#### 🔔 Notificaciones en Sistema
- Alertas dentro de la aplicación
- Contador de notificaciones no leídas
- Historial de notificaciones

### Configuración de Notificaciones

Los usuarios pueden configurar:

- **Tipos de eventos** que desean recibir
- **Canales preferidos** (email, SMS, sistema)
- **Horarios** para recibir notificaciones
- **Frecuencia** de recordatorios

---

## Roles y Permisos

### Roles del Sistema

#### 👤 Técnico
**Permisos**:
- ✅ Ver devoluciones asignadas
- ✅ Cambiar estado: REGISTRADA → PROCESANDO
- ✅ Cambiar estado: PROCESANDO → COMPLETADA
- ✅ Agregar observaciones
- ❌ Cancelar devoluciones
- ❌ Configurar sistema

**Responsabilidades**:
- Procesar devoluciones asignadas
- Verificar elementos devueltos
- Actualizar estado según progreso

#### 👥 Supervisor
**Permisos**:
- ✅ Ver todas las devoluciones
- ✅ Realizar todas las transiciones de estado
- ✅ Cancelar devoluciones
- ✅ Asignar devoluciones a técnicos
- ✅ Generar reportes
- ❌ Configurar sistema

**Responsabilidades**:
- Supervisar el trabajo de los técnicos
- Aprobar completaciones
- Manejar casos especiales
- Generar reportes de gestión

#### 🔧 Administrador
**Permisos**:
- ✅ Acceso completo al sistema
- ✅ Configurar notificaciones
- ✅ Gestionar usuarios y roles
- ✅ Configurar plantillas
- ✅ Acceso a auditoría completa
- ✅ Configuración del sistema

**Responsabilidades**:
- Configurar y mantener el sistema
- Gestionar usuarios y permisos
- Configurar notificaciones
- Supervisar auditoría

### Matriz de Permisos

| Acción | Técnico | Supervisor | Administrador |
|--------|---------|------------|---------------|
| Ver devoluciones propias | ✅ | ✅ | ✅ |
| Ver todas las devoluciones | ❌ | ✅ | ✅ |
| REGISTRADA → PROCESANDO | ✅ | ✅ | ✅ |
| PROCESANDO → COMPLETADA | ✅ | ✅ | ✅ |
| Cancelar devoluciones | ❌ | ✅ | ✅ |
| Configurar notificaciones | ❌ | ❌ | ✅ |
| Gestionar usuarios | ❌ | ❌ | ✅ |
| Ver auditoría completa | ❌ | ✅ | ✅ |

---

## Auditoría y Trazabilidad

### Registro de Auditoría

Todos los cambios de estado se registran automáticamente con:

- **Timestamp**: Fecha y hora exacta del cambio
- **Usuario**: Quién realizó el cambio
- **Estado Anterior**: Estado antes del cambio
- **Estado Nuevo**: Estado después del cambio
- **Motivo**: Razón proporcionada para el cambio
- **Observaciones**: Detalles adicionales
- **IP Address**: Dirección IP desde donde se realizó el cambio

### Consulta de Historial

#### Desde la Interfaz Web
1. Acceder al detalle de la devolución
2. Hacer clic en "Ver Historial"
3. Se muestra cronología completa de cambios

#### Información Disponible
- **Línea de tiempo visual** con todos los cambios
- **Detalles de cada transición**
- **Usuario responsable** de cada cambio
- **Duración** en cada estado
- **Motivos y observaciones** completas

### Reportes de Auditoría

Los administradores pueden generar reportes que incluyen:

- **Actividad por usuario**: Qué cambios realizó cada usuario
- **Actividad por período**: Cambios en un rango de fechas
- **Estadísticas de estados**: Tiempo promedio en cada estado
- **Análisis de tendencias**: Patrones en los cambios de estado

---

## Configuración del Sistema

### Configuración de Notificaciones

#### Acceso a Configuración
1. Menú "Administración" → "Configuración de Notificaciones"
2. Solo disponible para administradores

#### Configuraciones Disponibles

**Por Evento**:
- Seleccionar qué cambios de estado generan notificaciones
- Configurar destinatarios por rol
- Establecer plantillas de mensaje

**Por Canal**:
- Configurar servidor SMTP para emails
- Configurar servicio SMS
- Personalizar plantillas

**Timing**:
- Notificaciones inmediatas
- Notificaciones con delay
- Recordatorios programados

### Gestión de Plantillas

#### Plantillas de Email
```html
Asunto: Devolución #{devolucion_id} - Estado actualizado a {nuevo_estado}

Estimado {usuario_nombre},

La devolución #{devolucion_id} ha cambiado de estado:
- Estado anterior: {estado_anterior}
- Estado nuevo: {nuevo_estado}
- Motivo: {motivo}
- Fecha: {fecha_cambio}

Puede ver los detalles en: {enlace_devolucion}

Saludos,
Sistema de Gestión de Devoluciones
```

#### Plantillas de SMS
```
Devolución #{devolucion_id}: {estado_anterior} → {nuevo_estado}
Motivo: {motivo}
Ver: {enlace_corto}
```

#### Variables Disponibles
- `{devolucion_id}`: ID de la devolución
- `{estado_anterior}`: Estado antes del cambio
- `{nuevo_estado}`: Estado después del cambio
- `{motivo}`: Motivo del cambio
- `{observaciones}`: Observaciones adicionales
- `{usuario_nombre}`: Nombre del usuario que realizó el cambio
- `{fecha_cambio}`: Fecha y hora del cambio
- `{cliente_nombre}`: Nombre del cliente
- `{enlace_devolucion}`: URL directa a la devolución

---

## Solución de Problemas

### Problemas Comunes

#### "No puedo cambiar el estado de una devolución"

**Posibles causas**:
1. **Permisos insuficientes**: Verificar que su rol permita la transición
2. **Transición inválida**: El cambio de estado no está permitido
3. **Devolución bloqueada**: Otro usuario está editando simultáneamente

**Soluciones**:
1. Contactar al supervisor para verificar permisos
2. Revisar el diagrama de estados permitidos
3. Esperar unos minutos e intentar nuevamente

#### "No recibo notificaciones"

**Posibles causas**:
1. **Configuración de usuario**: Notificaciones deshabilitadas
2. **Filtro de spam**: Emails bloqueados
3. **Configuración del sistema**: Problema en servidor SMTP

**Soluciones**:
1. Verificar configuración personal de notificaciones
2. Revisar carpeta de spam/correo no deseado
3. Contactar al administrador del sistema

#### "El historial no muestra cambios recientes"

**Posibles causas**:
1. **Cache del navegador**: Información desactualizada
2. **Sincronización**: Delay en la actualización

**Soluciones**:
1. Refrescar la página (F5 o Ctrl+R)
2. Limpiar cache del navegador
3. Esperar unos minutos para sincronización

### Contacto de Soporte

Para problemas no resueltos:

- **Email**: soporte@sistema-devoluciones.com
- **Teléfono**: +57 (1) 234-5678
- **Horario**: Lunes a Viernes, 8:00 AM - 6:00 PM

---

## Preguntas Frecuentes

### ❓ ¿Puedo cambiar una devolución de COMPLETADA a otro estado?
**Respuesta**: No. COMPLETADA y CANCELADA son estados finales. Una vez que una devolución alcanza estos estados, no puede ser modificada. Si necesita realizar cambios, debe crear una nueva devolución.

### ❓ ¿Qué pasa si me equivoco al cambiar un estado?
**Respuesta**: Todos los cambios quedan registrados en el historial de auditoría. Si realizó un cambio incorrecto, puede (si tiene permisos) realizar una nueva transición al estado correcto. El historial mostrará ambos cambios.

### ❓ ¿Puedo ver quién cambió el estado de una devolución?
**Respuesta**: Sí. En el detalle de la devolución, haga clic en "Ver Historial" para ver todos los cambios, incluyendo quién los realizó y cuándo.

### ❓ ¿Por qué no veo el botón para cambiar a cierto estado?
**Respuesta**: Los botones solo aparecen para transiciones válidas según su rol y el estado actual. Si no ve un botón, puede ser porque:
- No tiene permisos para esa transición
- La transición no es válida desde el estado actual
- La devolución está en un estado final

### ❓ ¿Cómo puedo configurar mis notificaciones?
**Respuesta**: Vaya a "Mi Perfil" → "Configuración de Notificaciones". Allí puede seleccionar qué eventos desea recibir y por qué canales.

### ❓ ¿Puedo cancelar una devolución en cualquier momento?
**Respuesta**: Depende de su rol. Los Supervisores y Administradores pueden cancelar devoluciones desde cualquier estado (excepto si ya están COMPLETADAS o CANCELADAS). Los Técnicos no pueden cancelar devoluciones.

### ❓ ¿Qué significa cada color en los badges de estado?
**Respuesta**:
- 🔵 **Azul (REGISTRADA)**: Devolución nueva, pendiente de procesar
- 🟡 **Amarillo (PROCESANDO)**: Devolución en proceso activo
- 🟢 **Verde (COMPLETADA)**: Devolución finalizada exitosamente
- 🔴 **Rojo (CANCELADA)**: Devolución cancelada

### ❓ ¿Cuánto tiempo se conserva el historial de auditoría?
**Respuesta**: El historial se conserva indefinidamente para cumplir con requisitos de auditoría y trazabilidad. Los administradores pueden configurar políticas de archivado para datos muy antiguos.

### ❓ ¿Puedo exportar el historial de una devolución?
**Respuesta**: Sí. En el detalle de la devolución, use el botón "Exportar Historial" para generar un PDF con toda la información de auditoría.

---

## Información de Contacto

**Equipo de Desarrollo**
- Email: desarrollo@capired.com
- Documentación: [Wiki Interno]

**Soporte Técnico**
- Email: soporte@capired.com
- Teléfono: +57 (1) 234-5678
- Horario: Lunes a Viernes, 8:00 AM - 6:00 PM

**Administración del Sistema**
- Email: admin@capired.com
- Para solicitudes de nuevos usuarios, cambios de permisos, y configuraciones especiales

---

*Última actualización: Diciembre 2024*
*Versión del documento: 1.0*
*Sistema de Gestión de Estados de Devoluciones v2.0*