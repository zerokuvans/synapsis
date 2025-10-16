# 📋 Documentación: Módulo "Turnos Analistas"

## 🎯 Objetivo
Desarrollar el submódulo "Turnos Analistas" dentro del módulo "Líder" para gestionar la asignación de turnos a analistas de manera eficiente y organizada.

## 📊 Análisis de Base de Datos

### 🗃️ Tablas Existentes Analizadas

#### 1. Tabla `turnos`
**Estructura:**
- `turnos_id` (int) - Clave primaria
- `turnos_horario` (varchar(45)) - Horario del turno (ej: "06:00-14:00")
- `turnos_almuerzo` (varchar(45)) - Horario de almuerzo
- `turnos_break` (varchar(45)) - Horario de descanso
- `turnos_horas_trabajadas` (int) - Total de horas trabajadas
- `turnos_dia_turno` (varchar(45)) - Día del turno
- `turnos_tipo_turno` (varchar(45)) - Tipo de turno

**Datos de ejemplo encontrados:**
- (1, '06:00-14:00', '11:00-12:00', '09:00-09:15', 8, 'Lunes a Viernes', 'Diurno')
- (2, '14:00-22:00', '18:00-19:00', '16:00-16:15', 8, 'Lunes a Viernes', 'Vespertino')
- (3, '22:00-06:00', '02:00-03:00', '00:00-00:15', 8, 'Lunes a Viernes', 'Nocturno')
- (4, '06:00-18:00', '12:00-13:00', '10:00-10:15', 12, 'Sábados', 'Extendido')
- (5, '08:00-17:00', '12:00-13:00', '15:00-15:15', 9, 'Domingos', 'Dominical')

#### 2. Tabla `analistas_turnos_base`
**Estructura:**
- `id_analistas_turnos` (int) - Clave primaria
- `analistas_turnos_fecha` (datetime) - Fecha de asignación del turno
- `analistas_turnos_analista` (varchar(85)) - Identificador del analista
- `analistas_turnos_turno` (varchar(45)) - Identificador del turno asignado
- `analistas_turnos_almuerzo` (varchar(45)) - Horario de almuerzo específico
- `analistas_turnos_break` (varchar(45)) - Horario de break específico
- `analistas_turnos_horas_trabajadas` (int) - Horas trabajadas en esa asignación
- `analistas_turnos_dia_turno` (varchar(45)) - Día específico del turno
- `analistas_turnos_tipo_turno` (varchar(45)) - Tipo de turno específico

**Estado actual:** Tabla vacía, lista para recibir asignaciones

#### 3. Tabla `recurso_operativo` (Usuarios/Analistas)
**Estructura relevante:**
- `id_codigo_consumidor` (int) - Clave primaria
- `recurso_operativo_cedula` (varchar(20)) - Cédula del empleado
- `nombre` (varchar(45)) - Nombre del empleado
- `cargo` (varchar(45)) - Cargo del empleado
- `estado` (varchar(45)) - Estado activo/inactivo

**Cargos disponibles para filtrar analistas:**
- ANALISTA LOGISTICA
- ANALISTA
- TECNICO
- SUPERVISORES
- DESARROLLADOR
- TECNICO CONDUCTOR
- TECNICO DE TELECOMUNICACIONES
- CONDUCTOR
- FTTH INSTALACIONES

## 🎨 Especificaciones de Diseño

### 📱 Interfaz de Usuario
- **Estilo:** Consistente con el módulo "Líder" (header amarillo, Bootstrap responsive)
- **Icono:** `fas fa-users-cog` (engranajes con usuarios)
- **Colores:** 
  - Header: Amarillo (#ffc107)
  - Botones: Bootstrap estándar (primary, success, warning, danger)
  - Cards: Fondo blanco con sombra sutil

### 🔧 Funcionalidades Principales

#### 1. **Vista Principal - Dashboard de Turnos**
- **Ruta:** `/lider/turnos-analistas`
- **Elementos:**
  - Calendario mensual con vista de turnos asignados
  - Filtros por fecha, analista, tipo de turno
  - Resumen estadístico (total analistas, turnos asignados, etc.)
  - Botones de acción rápida

#### 2. **Gestión de Asignaciones**
- **Crear nueva asignación:**
  - Selector de analista (filtrado por cargo "ANALISTA")
  - Selector de turno disponible
  - Selector de fecha
  - Validación de conflictos de horarios
  
- **Editar asignación existente:**
  - Modificar fecha, turno o analista
  - Historial de cambios
  
- **Eliminar asignación:**
  - Confirmación de eliminación
  - Registro de auditoría

#### 3. **Reportes y Consultas**
- **Reporte semanal:** Turnos por analista en la semana
- **Reporte mensual:** Distribución de turnos y horas trabajadas
- **Consulta por analista:** Historial de turnos asignados
- **Consulta por fecha:** Todos los turnos de un día específico

## 🔄 Flujo de Trabajo

### 📋 Proceso de Asignación de Turnos

1. **Selección de Analista**
   ```sql
   SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula 
   FROM recurso_operativo 
   WHERE cargo = 'ANALISTA' AND estado = 'activo'
   ```

2. **Selección de Turno**
   ```sql
   SELECT turnos_id, turnos_horario, turnos_tipo_turno 
   FROM turnos 
   ORDER BY turnos_id
   ```

3. **Validación de Conflictos**
   ```sql
   SELECT COUNT(*) FROM analistas_turnos_base 
   WHERE analistas_turnos_analista = ? 
   AND analistas_turnos_fecha = ?
   ```

4. **Inserción de Asignación**
   ```sql
   INSERT INTO analistas_turnos_base 
   (analistas_turnos_fecha, analistas_turnos_analista, analistas_turnos_turno, 
    analistas_turnos_almuerzo, analistas_turnos_break, analistas_turnos_horas_trabajadas,
    analistas_turnos_dia_turno, analistas_turnos_tipo_turno)
   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
   ```

## 📁 Estructura de Archivos

```
templates/modulos/lider/turnos-analistas/
├── dashboard.html              # Vista principal
├── asignar_turno.html         # Formulario de asignación
├── editar_asignacion.html     # Formulario de edición
├── reportes.html              # Vista de reportes
└── components/
    ├── calendario.html        # Componente calendario
    ├── filtros.html          # Componente filtros
    └── tabla_asignaciones.html # Tabla de asignaciones
```

## 🛠️ Implementación Técnica

### 🐍 Rutas de Flask (main.py)
```python
@app.route('/lider/turnos-analistas')
@login_required(role=['administrativo', 'lider'])
def turnos_analistas_dashboard():
    # Vista principal del módulo

@app.route('/lider/turnos-analistas/asignar', methods=['GET', 'POST'])
@login_required(role=['administrativo', 'lider'])
def asignar_turno():
    # Formulario de asignación de turnos

@app.route('/lider/turnos-analistas/editar/<int:id>', methods=['GET', 'POST'])
@login_required(role=['administrativo', 'lider'])
def editar_asignacion(id):
    # Editar asignación existente

@app.route('/lider/turnos-analistas/eliminar/<int:id>', methods=['POST'])
@login_required(role=['administrativo', 'lider'])
def eliminar_asignacion(id):
    # Eliminar asignación

@app.route('/lider/turnos-analistas/reportes')
@login_required(role=['administrativo', 'lider'])
def reportes_turnos():
    # Vista de reportes
```

### 📊 Consultas SQL Principales

#### Obtener Analistas Disponibles
```sql
SELECT 
    id_codigo_consumidor,
    nombre,
    recurso_operativo_cedula,
    cargo
FROM recurso_operativo 
WHERE cargo IN ('ANALISTA', 'ANALISTA LOGISTICA') 
AND estado = 'activo'
ORDER BY nombre
```

#### Obtener Turnos Disponibles
```sql
SELECT 
    turnos_id,
    turnos_horario,
    turnos_tipo_turno,
    turnos_horas_trabajadas,
    turnos_almuerzo,
    turnos_break
FROM turnos 
ORDER BY turnos_id
```

#### Consultar Asignaciones por Fecha
```sql
SELECT 
    atb.*,
    ro.nombre as nombre_analista,
    ro.recurso_operativo_cedula,
    t.turnos_horario,
    t.turnos_tipo_turno
FROM analistas_turnos_base atb
INNER JOIN recurso_operativo ro ON atb.analistas_turnos_analista = ro.id_codigo_consumidor
INNER JOIN turnos t ON atb.analistas_turnos_turno = t.turnos_id
WHERE DATE(atb.analistas_turnos_fecha) = ?
ORDER BY atb.analistas_turnos_fecha, t.turnos_horario
```

#### Reporte Mensual de Turnos
```sql
SELECT 
    ro.nombre,
    COUNT(*) as total_turnos,
    SUM(atb.analistas_turnos_horas_trabajadas) as total_horas,
    GROUP_CONCAT(DISTINCT t.turnos_tipo_turno) as tipos_turno
FROM analistas_turnos_base atb
INNER JOIN recurso_operativo ro ON atb.analistas_turnos_analista = ro.id_codigo_consumidor
INNER JOIN turnos t ON atb.analistas_turnos_turno = t.turnos_id
WHERE MONTH(atb.analistas_turnos_fecha) = ? 
AND YEAR(atb.analistas_turnos_fecha) = ?
GROUP BY ro.id_codigo_consumidor, ro.nombre
ORDER BY total_horas DESC
```

## 🔐 Seguridad y Validaciones

### ✅ Validaciones de Negocio
1. **Un analista no puede tener dos turnos el mismo día**
2. **Los turnos no pueden solaparse en horarios**
3. **Solo usuarios con rol 'administrativo' o 'lider' pueden gestionar turnos**
4. **Las fechas de asignación no pueden ser anteriores a hoy**
5. **Los analistas deben estar en estado 'activo'**

### 🛡️ Validaciones Técnicas
1. **Sanitización de inputs**
2. **Validación de tipos de datos**
3. **Protección contra SQL injection**
4. **Validación de permisos por rol**
5. **Logs de auditoría para cambios**

## 📈 Métricas y KPIs

### 📊 Indicadores Principales
- **Cobertura de turnos:** % de turnos asignados vs disponibles
- **Distribución equitativa:** Horas trabajadas por analista
- **Eficiencia de asignación:** Tiempo promedio de asignación
- **Conflictos resueltos:** Número de reasignaciones necesarias

## 🚀 Fases de Implementación

### Fase 1: Estructura Base ✅
- [x] Análisis de tablas existentes
- [x] Documentación técnica
- [ ] Creación de rutas básicas

### Fase 2: Funcionalidad Core
- [ ] Vista dashboard principal
- [ ] Formulario de asignación
- [ ] Validaciones de negocio
- [ ] CRUD completo

### Fase 3: Características Avanzadas
- [ ] Calendario interactivo
- [ ] Reportes y estadísticas
- [ ] Exportación de datos
- [ ] Notificaciones

### Fase 4: Optimización
- [ ] Performance tuning
- [ ] Interfaz responsive
- [ ] Testing completo
- [ ] Documentación de usuario

---

**Fecha de creación:** Enero 2025
**Versión:** 1.0
**Estado:** En desarrollo
**Responsable:** Sistema Synapsis - Módulo Líder