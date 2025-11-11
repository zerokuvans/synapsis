# Sistema de Votaciones - Documentación Técnica

## 1. Visión General

El sistema de votaciones es una extensión del módulo de encuestas que permite crear elecciones internas con candidatos, fotos y conteo de votos en tiempo real.

### Características principales:
- ✅ Crear votaciones con candidatos
- ✅ Subir fotos de candidatos
- ✅ Sistema de votación (una opción por usuario)
- ✅ Conteo en tiempo real
- ✅ Resultados con porcentajes y gráficos
- ✅ Prevención de doble voto

## 2. Arquitectura y Tecnología

### Stack Tecnológico:
- **Backend**: Flask + Python
- **Base de datos**: PostgreSQL (Supabase)
- **Frontend**: HTML + JavaScript + Bootstrap
- **Almacenamiento**: Supabase Storage (fotos candidatos)

## 3. Diseño de Base de Datos

### 3.1 Tabla `encuestas` (Modificada)
```sql
-- Agregar campo tipo_encuesta a la tabla existente
ALTER TABLE encuestas ADD COLUMN tipo_encuesta VARCHAR(20) DEFAULT 'encuesta' CHECK (tipo_encuesta IN ('encuesta', 'votacion'));

-- Índice para búsquedas por tipo
CREATE INDEX idx_encuestas_tipo ON encuestas(tipo_encuesta);
```

### 3.2 Tabla `candidatos` (Nueva)
```sql
CREATE TABLE candidatos (
    id_candidato SERIAL PRIMARY KEY,
    id_encuesta INTEGER NOT NULL REFERENCES encuestas(id_encuesta) ON DELETE CASCADE,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    foto_url VARCHAR(500),
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_candidatos_encuesta ON candidatos(id_encuesta);
CREATE INDEX idx_candidatos_activo ON candidatos(activo);
```

### 3.3 Tabla `votos` (Nueva)
```sql
CREATE TABLE votos (
    id_voto SERIAL PRIMARY KEY,
    id_encuesta INTEGER NOT NULL REFERENCES encuestas(id_encuesta) ON DELETE CASCADE,
    id_candidato INTEGER NOT NULL REFERENCES candidatos(id_candidato) ON DELETE CASCADE,
    usuario_id VARCHAR(100) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(id_encuesta, usuario_id) -- Un voto por usuario por encuesta
);

CREATE INDEX idx_votos_encuesta ON votos(id_encuesta);
CREATE INDEX idx_votos_candidato ON votos(id_candidato);
CREATE INDEX idx_votos_usuario ON votos(usuario_id);
```

## 4. APIs REST

### 4.1 Gestión de Candidatos

#### Crear candidato
```
POST /api/encuestas/{id_encuesta}/candidatos
Content-Type: multipart/form-data

Body:
- nombre (string, requerido): Nombre del candidato
- descripcion (string, opcional): Descripción/bio del candidato  
- foto (file, opcional): Imagen del candidato
- orden (integer, opcional): Orden de aparición

Response:
{
  "success": true,
  "candidato": {
    "id_candidato": 1,
    "nombre": "Juan Pérez",
    "descripcion": "Experto en...",
    "foto_url": "https://storage.supabase.com/...",
    "orden": 1
  }
}
```

#### Listar candidatos
```
GET /api/encuestas/{id_encuesta}/candidatos

Response:
{
  "success": true,
  "candidatos": [
    {
      "id_candidato": 1,
      "nombre": "Juan Pérez",
      "descripcion": "Experto en...",
      "foto_url": "https://...",
      "votos": 15,
      "porcentaje": 42.5
    }
  ]
}
```

#### Eliminar candidato
```
DELETE /api/encuestas/{id_encuesta}/candidatos/{id_candidato}

Response:
{
  "success": true,
  "message": "Candidato eliminado"
}
```

### 4.2 Sistema de Votación

#### Votar por candidato
```
POST /api/encuestas/{id_encuesta}/votar
Content-Type: application/json

Body:
{
  "id_candidato": 1
}

Headers:
- X-Usuario-Id: ID del usuario (o desde sesión)

Response:
{
  "success": true,
  "message": "Voto registrado exitosamente"
}
```

#### Verificar si usuario ya votó
```
GET /api/encuestas/{id_encuesta}/votado?usuario_id={usuario_id}

Response:
{
  "success": true,
  "votado": true,
  "id_candidato_votado": 1
}
```

### 4.3 Resultados

#### Obtener resultados de votación
```
GET /api/encuestas/{id_encuesta}/resultados

Response:
{
  "success": true,
  "resultados": {
    "total_votos": 35,
    "candidatos": [
      {
        "id_candidato": 1,
        "nombre": "Juan Pérez",
        "foto_url": "https://...",
        "votos": 15,
        "porcentaje": 42.86
      },
      {
        "id_candidato": 2,
        "nombre": "María García",
        "foto_url": "https://...",
        "votos": 20,
        "porcentaje": 57.14
      }
    ]
  }
}
```

## 5. Frontend - Interfaces

### 5.1 Crear/Editar Votación

**Ubicación**: Modal en `encuestas.html`

**Elementos adicionales para votaciones:**
```html
<!-- Selector de tipo -->
<div class="mb-3">
  <label class="form-label">Tipo de encuesta</label>
  <select id="tipo-encuesta" class="form-select">
    <option value="encuesta">Encuesta normal</option>
    <option value="votacion">Votación</option>
  </select>
</div>

<!-- Sección de candidatos (solo para votaciones) -->
<div id="seccion-candidatos" class="d-none">
  <h5>Candidatos</h5>
  <div id="lista-candidatos" class="mb-3"></div>
  <button type="button" class="btn btn-outline-primary" id="btn-agregar-candidato">
    <i class="fas fa-plus"></i> Agregar candidato
  </button>
</div>
```

### 5.2 Formulario de Candidato

**Modal**: `modal-candidato.html`

```html
<div class="modal fade" id="modal-candidato">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Agregar Candidato</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form id="form-candidato">
          <div class="mb-3">
            <label class="form-label">Nombre del candidato</label>
            <input type="text" class="form-control" id="candidato-nombre" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Descripción</label>
            <textarea class="form-control" id="candidato-descripcion" rows="3"></textarea>
          </div>
          <div class="mb-3">
            <label class="form-label">Foto del candidato</label>
            <input type="file" class="form-control" id="candidato-foto" accept="image/*">
            <div id="preview-foto" class="mt-2"></div>
          </div>
          <div class="mb-3">
            <label class="form-label">Orden</label>
            <input type="number" class="form-control" id="candidato-orden" value="0">
          </div>
        </form>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
        <button type="button" class="btn btn-primary" id="btn-guardar-candidato">Guardar</button>
      </div>
    </div>
  </div>
</div>
```

### 5.3 Vista de Votación para Usuarios

**Página**: `votacion.html`

```html
<div class="container mt-4">
  <div class="row">
    <div class="col-12">
      <h2 class="text-center mb-4">{{ titulo_votacion }}</h2>
      <p class="text-center text-muted mb-5">{{ descripcion_votacion }}</p>
    </div>
  </div>
  
  <div class="row justify-content-center">
    <div class="col-md-8">
      <form id="form-votacion">
        <div class="row">
          {% for candidato in candidatos %}
          <div class="col-md-6 mb-4">
            <div class="card candidato-card h-100" style="cursor: pointer;">
              <div class="card-body text-center">
                <img src="{{ candidato.foto_url }}" 
                     alt="{{ candidato.nombre }}" 
                     class="rounded-circle mb-3" 
                     style="width: 120px; height: 120px; object-fit: cover;">
                <h5 class="card-title">{{ candidato.nombre }}</h5>
                <p class="card-text">{{ candidato.descripcion }}</p>
                <div class="form-check">
                  <input class="form-check-input" type="radio" 
                         name="candidato" value="{{ candidato.id_candidato }}" 
                         id="candidato-{{ candidato.id_candidato }}">
                  <label class="form-check-label" for="candidato-{{ candidato.id_candidato }}">
                    Seleccionar
                  </label>
                </div>
              </div>
            </div>
          </div>
          {% endfor %}
        </div>
        
        <div class="text-center mt-4">
          <button type="submit" class="btn btn-primary btn-lg">
            <i class="fas fa-vote-yea"></i> Votar
          </button>
        </div>
      </form>
    </div>
  </div>
</div>
```

### 5.4 Panel de Resultados

**Componente**: `resultados-votacion.html`

```html
<div class="container mt-4">
  <div class="row">
    <div class="col-12">
      <h2 class="text-center mb-4">Resultados de la Votación</h2>
      <div class="text-center mb-4">
        <span class="badge bg-primary fs-5">Total de votos: <span id="total-votos">0</span></span>
      </div>
    </div>
  </div>
  
  <div class="row">
    <div class="col-md-8 mx-auto">
      <div id="resultados-container">
        <!-- Resultados dinámicos -->
      </div>
      
      <div class="mt-4">
        <canvas id="grafico-resultados"></canvas>
      </div>
    </div>
  </div>
</div>
```

## 6. JavaScript - Funcionalidad

### 6.1 Gestión de candidatos
```javascript
// Agregar candidato
async function agregarCandidato() {
  const formData = new FormData();
  formData.append('nombre', document.getElementById('candidato-nombre').value);
  formData.append('descripcion', document.getElementById('candidato-descripcion').value);
  formData.append('orden', document.getElementById('candidato-orden').value);
  
  const fotoInput = document.getElementById('candidato-foto');
  if (fotoInput.files[0]) {
    formData.append('foto', fotoInput.files[0]);
  }
  
  const response = await fetch(`/api/encuestas/${encuestaId}/candidatos`, {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  if (data.success) {
    // Actualizar lista de candidatos
    cargarCandidatos();
    cerrarModalCandidato();
  }
}

// Cargar candidatos
async function cargarCandidatos() {
  const response = await fetch(`/api/encuestas/${encuestaId}/candidatos`);
  const data = await response.json();
  
  if (data.success) {
    mostrarCandidatos(data.candidatos);
  }
}
```

### 6.2 Sistema de votación
```javascript
// Votar
async function votar(idCandidato) {
  try {
    const response = await fetch(`/api/encuestas/${encuestaId}/votar`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Usuario-Id': usuarioActual.id
      },
      body: JSON.stringify({ id_candidato: idCandidato })
    });
    
    const data = await response.json();
    if (data.success) {
      showToast('Éxito', 'Voto registrado exitosamente');
      // Redirigir a resultados o mostrar confirmación
      window.location.href = `/votacion/${encuestaId}/resultados`;
    } else {
      showToast('Error', data.message || 'No se pudo registrar el voto', 'error');
    }
  } catch (error) {
    console.error('Error al votar:', error);
    showToast('Error', 'Error al procesar el voto', 'error');
  }
}

// Verificar si ya votó
async function verificarVoto() {
  const response = await fetch(`/api/encuestas/${encuestaId}/votado?usuario_id=${usuarioActual.id}`);
  const data = await response.json();
  
  if (data.success && data.votado) {
    // Mostrar mensaje de que ya votó
    document.getElementById('mensaje-ya-voto').classList.remove('d-none');
    document.getElementById('form-votacion').classList.add('d-none');
  }
}
```

### 6.3 Resultados en tiempo real
```javascript
// Cargar resultados
async function cargarResultados() {
  try {
    const response = await fetch(`/api/encuestas/${encuestaId}/resultados`);
    const data = await response.json();
    
    if (data.success) {
      mostrarResultados(data.resultados);
      actualizarGrafico(data.resultados);
    }
  } catch (error) {
    console.error('Error al cargar resultados:', error);
  }
}

// Mostrar resultados
function mostrarResultados(resultados) {
  const container = document.getElementById('resultados-container');
  container.innerHTML = '';
  
  resultados.candidatos.forEach(candidato => {
    const card = document.createElement('div');
    card.className = 'card mb-3';
    card.innerHTML = `
      <div class="card-body">
        <div class="row align-items-center">
          <div class="col-auto">
            <img src="${candidato.foto_url}" alt="${candidato.nombre}" 
                 class="rounded-circle" style="width: 60px; height: 60px; object-fit: cover;">
          </div>
          <div class="col">
            <h6 class="mb-1">${candidato.nombre}</h6>
            <div class="progress mb-2" style="height: 25px;">
              <div class="progress-bar" role="progressbar" 
                   style="width: ${candidato.porcentaje}%"
                   aria-valuenow="${candidato.porcentaje}" 
                   aria-valuemin="0" aria-valuemax="100">
                ${candidato.porcentaje.toFixed(1)}%
              </div>
            </div>
            <small class="text-muted">${candidato.votos} votos</small>
          </div>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
  
  document.getElementById('total-votos').textContent = resultados.total_votos;
}

// Actualizar gráfico
function actualizarGrafico(resultados) {
  const ctx = document.getElementById('grafico-resultados').getContext('2d');
  
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: resultados.candidatos.map(c => c.nombre),
      datasets: [{
        data: resultados.candidatos.map(c => c.votos),
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF'
        ]
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'bottom',
        }
      }
    }
  });
}
```

## 7. Seguridad y Validaciones

### 7.1 Prevención de doble voto
- ✅ Constraint UNIQUE en tabla `votos` (usuario_id + id_encuesta)
- ✅ Verificación previa al votar
- ✅ Validación en backend antes de procesar voto

### 7.2 Validaciones de negocio
- Solo usuarios autenticados pueden votar
- Solo encuestas de tipo "votacion" aceptan candidatos
- Mínimo 2 candidatos para activar votación
- Solo encuestas en estado "activa" pueden recibir votos

### 7.3 Almacenamiento seguro
- Fotos en Supabase Storage con políticas de acceso
- URLs firmadas para acceso temporal
- Backup automático de resultados

## 8. Flujos de Usuario

### 8.1 Administrador crea votación
1. Click en "Nueva Encuesta"
2. Selecciona tipo "Votación"
3. Completa título y descripción
4. Agrega candidatos con fotos
5. Publica la votación

### 8.2 Usuario vota
1. Accede a la votación activa
2. Ve candidatos con fotos
3. Selecciona un candidato
4. Confirma su voto
5. Ve confirmación y acceso a resultados

### 8.3 Ver resultados
1. Accede a resultados de votación
2. Ve conteo por candidato
3. Ve porcentajes y gráfico
4. (Opcional) Actualización en tiempo real

## 9. Consideraciones Técnicas

### 9.1 Rendimiento
- Índices en tablas de votos para consultas rápidas
- Caché de resultados con TTL de 5 minutos
- Paginación si hay muchos candidatos

### 9.2 Escalabilidad
- Diseño preparado para múltiples votaciones simultáneas
- Proceso de conteo optimizado con queries SQL eficientes
- Posibilidad de agregar más tipos de votación en futuro

### 9.3 Mantenimiento
- Scripts de limpieza para votos de prueba
- Logs de auditoría para votaciones importantes
- Exportación de resultados a CSV/Excel

## 10. Próximos Pasos

1. ✅ Implementar backend (modelos y APIs)
2. ✅ Crear interfaces frontend
3. ✅ Integrar con sistema existente
4. ✅ Pruebas de seguridad
5. ✅ Validación con usuarios
6. ✅ Documentación de usuario final

¿Estás listo para comenzar la implementación? Podemos empezar por el backend (modelos y APIs) y luego continuar con el frontend.