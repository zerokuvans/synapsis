# Plan de Implementación - Submódulo Turnos Analistas

## 1. Resumen Ejecutivo

Este documento detalla el plan de implementación para el submódulo "Turnos Analistas" dentro del módulo "Líder". La implementación se basa en las tablas existentes `turnos`, `analistas_turnos_base` y `recurso_operativo` en la base de datos `capired`.

## 2. Análisis de Tablas Existentes

### 2.1 Tabla `turnos` - ✅ VERIFICADA
- **Estado**: Tabla existente con 5 turnos predefinidos
- **Estructura**: Completa con horarios, breaks, almuerzo y horas trabajadas
- **Turnos Disponibles**:
  - Diurno (06:00-14:00, 8 horas)
  - Vespertino (14:00-22:00, 8 horas)
  - Nocturno (22:00-06:00, 8 horas)
  - Extendido (06:00-18:00, 12 horas)
  - Dominical (08:00-16:00, 8 horas)

### 2.2 Tabla `analistas_turnos_base` - ✅ VERIFICADA
- **Estado**: Tabla existente, actualmente vacía
- **Estructura**: Completa para asignaciones con campos personalizables
- **Campos Clave**:
  - `analistas_turnos_fecha`: Fecha de asignación
  - `analistas_turnos_analista`: Nombre del analista
  - `analistas_turnos_turno`: Nombre del turno
  - Campos de horarios personalizables (inicio, fin, almuerzo, breaks)

### 2.3 Tabla `recurso_operativo` - ✅ VERIFICADA
- **Estado**: Tabla existente con datos de personal
- **Filtros Identificados**:
  - Cargo: 'ANALISTA', 'ANALISTA LOGISTICA'
  - Estado: 'Activo'
- **Campos Utilizables**: nombre, cargo, estado

## 3. Fases de Implementación

### Fase 1: Backend - Rutas y APIs (Estimado: 2-3 horas)

#### 3.1 Crear Rutas en main.py
```python
# Ruta principal del submódulo
@app.route('/lider/turnos-analistas')
@login_required(role=['administrador', 'lider'])
def turnos_analistas():
    return render_template('modulos/lider/turnos_analistas.html')

# APIs para el submódulo
@app.route('/api/analistas-activos')
@login_required_api(role=['administrador', 'lider'])
def api_analistas_activos():
    # Implementar consulta a recurso_operativo

@app.route('/api/turnos-disponibles')
@login_required_api(role=['administrador', 'lider'])
def api_turnos_disponibles():
    # Implementar consulta a tabla turnos

@app.route('/api/asignar-turno', methods=['POST'])
@login_required_api(role=['administrador', 'lider'])
def api_asignar_turno():
    # Implementar inserción en analistas_turnos_base

@app.route('/api/turnos-semana')
@login_required_api(role=['administrador', 'lider'])
def api_turnos_semana():
    # Implementar consulta por rango de fechas
```

#### 3.2 Validaciones de Negocio
- Verificar que el analista esté activo
- Validar que no existan conflictos de horarios
- Verificar formato de fechas y horarios
- Validar permisos de usuario

### Fase 2: Frontend - Interfaz Principal (Estimado: 3-4 horas)

#### 2.1 Crear Template HTML
```html
<!-- templates/modulos/lider/turnos_analistas.html -->
- Header con título y navegación de semanas
- Calendario semanal (tabla 7 columnas)
- Panel lateral con lista de analistas
- Botón "Nuevo Turno" prominente
- Código de colores por analista
```

#### 2.2 Estilos CSS
```css
/* Estilos específicos para el calendario */
- Colores diferenciados por analista
- Hover effects para celdas
- Responsive design para móviles
- Consistencia con módulo líder existente
```

#### 2.3 JavaScript Base
```javascript
// Funcionalidades principales
- Cargar datos del calendario
- Navegación entre semanas
- Manejo de clicks en celdas
- Actualización dinámica de vista
```

### Fase 3: Modales y Funcionalidad Avanzada (Estimado: 4-5 horas)

#### 3.1 Modal de Asignación de Turnos
```html
<!-- Modal para crear nuevas asignaciones -->
- Dropdown de analistas (carga dinámica)
- Checkboxes para días de la semana
- Dropdown de turnos predefinidos
- Campos opcionales para horarios personalizados
- Validaciones en tiempo real
```

#### 3.2 Modal de Detalles del Día
```html
<!-- Modal para ver detalles completos -->
- Lista de analistas asignados al día
- Horarios completos (trabajo, almuerzo, breaks)
- Total de horas por analista
- Opción de editar/eliminar asignaciones
```

#### 3.3 JavaScript Avanzado
```javascript
// Funcionalidades de modales
- Carga dinámica de datos
- Validaciones de formularios
- Manejo de errores
- Confirmaciones de acciones
- Actualización automática del calendario
```

### Fase 4: Testing y Optimización (Estimado: 2-3 horas)

#### 4.1 Pruebas Funcionales
- Crear asignaciones de turnos
- Verificar guardado en base de datos
- Probar navegación entre semanas
- Validar modales y formularios
- Verificar responsive design

#### 4.2 Pruebas de Integración
- Verificar permisos de roles
- Probar con datos reales
- Validar consultas SQL
- Verificar rendimiento

#### 4.3 Optimizaciones
- Mejorar consultas SQL
- Optimizar carga de datos
- Ajustar estilos responsive
- Pulir experiencia de usuario

## 4. Estructura de Archivos a Crear

```
templates/modulos/lider/
├── turnos_analistas.html          # Página principal
└── components/
    ├── modal_asignar_turno.html    # Modal de asignación
    └── modal_detalles_dia.html     # Modal de detalles

static/css/
└── turnos_analistas.css           # Estilos específicos

static/js/
└── turnos_analistas.js            # JavaScript del módulo
```

## 5. Consultas SQL Requeridas

### 5.1 Consultas de Lectura
```sql
-- Obtener analistas activos
SELECT nombre, cargo FROM recurso_operativo 
WHERE cargo LIKE '%ANALISTA%' AND estado = 'Activo';

-- Obtener turnos disponibles
SELECT * FROM turnos ORDER BY turnos_inicio;

-- Obtener asignaciones por semana
SELECT * FROM analistas_turnos_base 
WHERE analistas_turnos_fecha BETWEEN ? AND ?;
```

### 5.2 Consultas de Escritura
```sql
-- Insertar nueva asignación
INSERT INTO analistas_turnos_base (...) VALUES (...);

-- Actualizar asignación existente
UPDATE analistas_turnos_base SET ... WHERE id = ?;

-- Eliminar asignación
DELETE FROM analistas_turnos_base WHERE id = ?;
```

## 6. Consideraciones de Seguridad

### 6.1 Validaciones Backend
- Verificar permisos de usuario en cada API
- Sanitizar datos de entrada
- Validar formato de fechas y horarios
- Prevenir inyección SQL

### 6.2 Validaciones Frontend
- Validar formularios antes del envío
- Mostrar mensajes de error claros
- Confirmar acciones destructivas
- Manejar errores de red

## 7. Métricas de Éxito

### 7.1 Funcionalidad
- ✅ Asignación exitosa de turnos
- ✅ Visualización correcta del calendario
- ✅ Modales funcionando correctamente
- ✅ Datos guardándose en base de datos

### 7.2 Usabilidad
- ✅ Interfaz intuitiva y fácil de usar
- ✅ Responsive en dispositivos móviles
- ✅ Tiempos de carga aceptables (<2 segundos)
- ✅ Consistencia visual con módulo líder

### 7.3 Rendimiento
- ✅ Consultas SQL optimizadas
- ✅ Carga eficiente de datos
- ✅ Manejo adecuado de errores
- ✅ Experiencia fluida del usuario

## 8. Cronograma Estimado

| Fase | Duración | Dependencias |
|------|----------|--------------|
| Fase 1: Backend | 2-3 horas | Acceso a base de datos |
| Fase 2: Frontend Base | 3-4 horas | Fase 1 completada |
| Fase 3: Modales | 4-5 horas | Fase 2 completada |
| Fase 4: Testing | 2-3 horas | Fases 1-3 completadas |
| **Total** | **11-15 horas** | - |

## 9. Próximos Pasos Inmediatos

1. **Implementar rutas backend** en `main.py`
2. **Crear template HTML** básico
3. **Desarrollar APIs** para datos
4. **Implementar modales** de funcionalidad
5. **Realizar testing** completo

¿Estás listo para comenzar con la implementación? ¿Por cuál fase te gustaría empezar?