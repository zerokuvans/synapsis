/**
 * Módulo Analistas - Diccionario de Causas de Cierre IMM
 * Funcionalidades de búsqueda y filtrado
 */

class AnalistasModule {
    constructor() {
        this.datos = [];
        this.datosFiltrados = [];
        this.paginaActual = 1;
        this.registrosPorPagina = 20;
        this.vistaActual = 'tabla'; // 'tabla' o 'cards'
        this.gruposDisponibles = [];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.cargarDatos();
        this.cargarGrupos();
        this.cargarAgrupaciones();
    }
    
    setupEventListeners() {
        // Búsqueda en tiempo real
        document.getElementById('buscarTexto').addEventListener('input', 
            this.debounce(() => this.aplicarFiltros(), 300)
        );
        
        // Filtros
        document.getElementById('filtroTecnologia').addEventListener('change', () => {
            this.actualizarAgrupacionesPorTecnologia();
            this.aplicarFiltros();
        });
        document.getElementById('filtroAgrupacion').addEventListener('change', () => {
            this.actualizarGruposPorTecnologiaYAgrupacion();
            this.aplicarFiltros();
        });
        document.getElementById('filtroGrupo').addEventListener('change', () => this.aplicarFiltros());
        
        // Botones
        document.getElementById('btnBuscar').addEventListener('click', () => this.aplicarFiltros());
        document.getElementById('btnLimpiar').addEventListener('click', () => this.limpiarFiltros());
        document.getElementById('limpiarBusqueda').addEventListener('click', () => this.limpiarBusqueda());
        
        // Cambio de vista
        document.getElementById('vistaTabla').addEventListener('click', () => this.cambiarVista('tabla'));
        document.getElementById('vistaCards').addEventListener('click', () => this.cambiarVista('cards'));
    }
    
    async cargarDatos() {
        console.log('Iniciando carga de datos...');
        let timeoutId;
        
        try {
            this.mostrarLoading(true);
            
            // Timeout de seguridad para ocultar el loading después de 10 segundos
            timeoutId = setTimeout(() => {
                console.warn('Timeout alcanzado, ocultando loading por seguridad');
                this.mostrarLoading(false);
            }, 10000);
            
            const response = await fetch('/api/analistas/causas-cierre', { credentials: 'include' });
            if (response.status === 401 || response.status === 403 || response.redirected) {
                window.location.href = '/login';
                return;
            }
            if (!response.ok) {
                throw new Error('Error al cargar los datos');
            }
            
            this.datos = await response.json();
            this.datosFiltrados = [...this.datos];
            
            console.log(`Datos cargados: ${this.datos.length} registros`);
            
            this.actualizarContador();
            this.renderizarDatos();
            this.renderizarPaginacion();
            
        } catch (error) {
            console.error('Error:', error);
            this.mostrarError('Error al cargar los datos. Por favor, intente nuevamente.');
        } finally {
            if (timeoutId) {
                clearTimeout(timeoutId);
            }
            console.log('Finalizando carga de datos, ocultando loading...');
            this.mostrarLoading(false);
        }
    }
    
    async cargarGrupos(tecnologia = '', agrupacion = '') {
        try {
            let url = '/api/analistas/grupos';
            const params = new URLSearchParams();
            
            if (tecnologia) {
                params.append('tecnologia', tecnologia);
            }
            if (agrupacion) {
                params.append('agrupacion', agrupacion);
            }
            
            if (params.toString()) {
                url += '?' + params.toString();
            }
            
            const response = await fetch(url, { credentials: 'include' });
            if (response.status === 401 || response.status === 403 || response.redirected) { window.location.href = '/login'; return; }
            if (!response.ok) {
                throw new Error('Error al cargar los grupos');
            }
            
            this.gruposDisponibles = await response.json();
            this.renderizarOpcionesGrupos();
            
        } catch (error) {
            console.error('Error al cargar grupos:', error);
        }
    }
    
    async cargarAgrupaciones(tecnologia = '') {
        try {
            let url = '/api/analistas/agrupaciones';
            if (tecnologia) {
                url += `?tecnologia=${encodeURIComponent(tecnologia)}`;
            }
            
            const response = await fetch(url, { credentials: 'include' });
            if (response.status === 401 || response.status === 403 || response.redirected) { window.location.href = '/login'; return; }
            if (!response.ok) {
                throw new Error('Error al cargar las agrupaciones');
            }
            
            const agrupaciones = await response.json();
            this.renderizarOpcionesAgrupaciones(agrupaciones);
            
        } catch (error) {
            console.error('Error al cargar agrupaciones:', error);
        }
    }
    
    async actualizarAgrupacionesPorTecnologia() {
        const tecnologiaSeleccionada = document.getElementById('filtroTecnologia').value;
        
        // Limpiar las selecciones dependientes
        document.getElementById('filtroAgrupacion').value = '';
        document.getElementById('filtroGrupo').value = '';
        
        // Cargar agrupaciones filtradas por tecnología
        await this.cargarAgrupaciones(tecnologiaSeleccionada);
        
        // Cargar todos los grupos para la tecnología seleccionada
        await this.cargarGrupos(tecnologiaSeleccionada);
    }
    
    async actualizarGruposPorTecnologiaYAgrupacion() {
        const tecnologiaSeleccionada = document.getElementById('filtroTecnologia').value;
        const agrupacionSeleccionada = document.getElementById('filtroAgrupacion').value;
        
        // Limpiar la selección de grupo
        document.getElementById('filtroGrupo').value = '';
        
        // Cargar grupos filtrados por tecnología y agrupación
        await this.cargarGrupos(tecnologiaSeleccionada, agrupacionSeleccionada);
    }
    
    renderizarOpcionesGrupos() {
        const select = document.getElementById('filtroGrupo');
        
        // Limpiar opciones existentes (excepto la primera)
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        // Agregar nuevas opciones
        this.gruposDisponibles.forEach(grupo => {
            const option = document.createElement('option');
            option.value = grupo;
            option.textContent = grupo;
            select.appendChild(option);
        });
    }
    
    renderizarOpcionesAgrupaciones(agrupaciones) {
        const select = document.getElementById('filtroAgrupacion');
        
        // Limpiar opciones existentes (excepto la primera)
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        // Agregar nuevas opciones
        agrupaciones.forEach(agrupacion => {
            const option = document.createElement('option');
            option.value = agrupacion;
            option.textContent = agrupacion;
            select.appendChild(option);
        });
    }
    
    aplicarFiltros() {
        const textoBusqueda = document.getElementById('buscarTexto').value.toLowerCase().trim();
        const tecnologia = document.getElementById('filtroTecnologia').value;
        const agrupacion = document.getElementById('filtroAgrupacion').value;
        const grupo = document.getElementById('filtroGrupo').value;
        
        this.datosFiltrados = this.datos.filter(item => {
            // Filtro de texto
            const coincideTexto = !textoBusqueda || 
                (item.codigo_causas_cierre && item.codigo_causas_cierre.toLowerCase().includes(textoBusqueda)) ||
                (item.nombre_causas_cierre && item.nombre_causas_cierre.toLowerCase().includes(textoBusqueda)) ||
                (item.instrucciones_de_uso_causas_cierre && item.instrucciones_de_uso_causas_cierre.toLowerCase().includes(textoBusqueda));
            
            // Filtro de tecnología
            const coincideTecnologia = !tecnologia || item.tecnologia_causas_cierre === tecnologia;
            
            // Filtro de agrupación
            const coincideAgrupacion = !agrupacion || item.agrupaciones_causas_cierre === agrupacion;
            
            // Filtro de grupo
            const coincideGrupo = !grupo || item.todos_los_grupos_causas_cierre === grupo;
            
            return coincideTexto && coincideTecnologia && coincideAgrupacion && coincideGrupo;
        });
        
        this.paginaActual = 1;
        this.actualizarContador();
        this.renderizarDatos();
        this.renderizarPaginacion();
    }
    
    async limpiarFiltros() {
        document.getElementById('buscarTexto').value = '';
        document.getElementById('filtroTecnologia').value = '';
        document.getElementById('filtroAgrupacion').value = '';
        document.getElementById('filtroGrupo').value = '';
        
        // Recargar todas las opciones sin filtros
        await this.cargarAgrupaciones();
        await this.cargarGrupos();
        
        this.aplicarFiltros();
    }
    
    limpiarBusqueda() {
        document.getElementById('buscarTexto').value = '';
        this.aplicarFiltros();
    }
    
    cambiarVista(vista) {
        this.vistaActual = vista;
        
        // Actualizar botones
        document.getElementById('vistaTabla').classList.toggle('active', vista === 'tabla');
        document.getElementById('vistaCards').classList.toggle('active', vista === 'cards');
        
        // Mostrar/ocultar contenedores
        document.getElementById('vistaTablaContainer').style.display = vista === 'tabla' ? 'block' : 'none';
        document.getElementById('vistaCardsContainer').style.display = vista === 'cards' ? 'block' : 'none';
        
        this.renderizarDatos();
    }
    
    renderizarDatos() {
        if (this.vistaActual === 'tabla') {
            this.renderizarTabla();
        } else {
            this.renderizarCards();
        }
    }
    
    renderizarTabla() {
        const tbody = document.getElementById('tablaCausasBody');
        tbody.innerHTML = '';
        
        const inicio = (this.paginaActual - 1) * this.registrosPorPagina;
        const fin = inicio + this.registrosPorPagina;
        const datosPagina = this.datosFiltrados.slice(inicio, fin);
        
        if (datosPagina.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center py-4">
                        <i class="fas fa-search fa-2x text-muted mb-2"></i>
                        <p class="text-muted mb-0">No se encontraron resultados</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        datosPagina.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <span class="badge bg-primary codigo-badge">${item.codigo_causas_cierre || 'N/A'}</span>
                </td>
                <td>
                    <div class="fw-bold">${item.nombre_causas_cierre || 'Sin descripción'}</div>
                    <small class="text-muted">${item.tipo_causas_cierre || ''}</small>
                </td>
                <td>
                    <span class="badge ${this.getTecnologiaBadgeClass(item.tecnologia_causas_cierre)}">
                        ${item.tecnologia_causas_cierre || 'N/A'}
                    </span>
                </td>
                <td>
                    <small class="text-muted">${item.agrupaciones_causas_cierre || 'N/A'}</small>
                </td>
                <td>
                    <small class="text-muted">${item.todos_los_grupos_causas_cierre || 'N/A'}</small>
                </td>
                <td>
                    <span class="badge ${item.facturable_causas_cierre === 'NO ES FACTURABLE' ? 'bg-danger' : 'bg-success'}">
                        ${item.facturable_causas_cierre || 'N/A'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-info" onclick="analistasModule.mostrarDetalles(${item.idbase_causas_cierre})">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
    
    renderizarCards() {
        const container = document.getElementById('vistaCardsContainer');
        container.innerHTML = '';
        
        const inicio = (this.paginaActual - 1) * this.registrosPorPagina;
        const fin = inicio + this.registrosPorPagina;
        const datosPagina = this.datosFiltrados.slice(inicio, fin);
        
        if (datosPagina.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No se encontraron resultados</h5>
                    <p class="text-muted">Intente modificar los criterios de búsqueda</p>
                </div>
            `;
            return;
        }
        
        datosPagina.forEach(item => {
            const card = document.createElement('div');
            card.className = 'col-md-6 col-lg-4 mb-3';
            card.innerHTML = `
                <div class="card causa-card h-100">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <span class="badge bg-primary codigo-badge">${item.codigo_causas_cierre || 'N/A'}</span>
                        <span class="badge ${this.getTecnologiaBadgeClass(item.tecnologia_causas_cierre)}">
                            ${item.tecnologia_causas_cierre || 'N/A'}
                        </span>
                    </div>
                    <div class="card-body">
                        <h6 class="card-title text-truncate-2">${item.nombre_causas_cierre || 'Sin descripción'}</h6>
                        <p class="card-text">
                            <small class="text-muted">
                                <strong>Agrupación:</strong> ${item.agrupaciones_causas_cierre || 'N/A'}<br>
                                <strong>Grupo:</strong> ${item.todos_los_grupos_causas_cierre || 'N/A'}<br>
                                <strong>Facturable:</strong> <span class="badge ${item.facturable_causas_cierre === 'NO ES FACTURABLE' ? 'bg-danger' : 'bg-success'}">${item.facturable_causas_cierre || 'N/A'}</span>
                            </small>
                        </p>
                    </div>
                    <div class="card-footer">
                        <button class="btn btn-sm btn-outline-info w-100" onclick="analistasModule.mostrarDetalles(${item.idbase_causas_cierre})">
                            <i class="fas fa-eye me-1"></i>Ver Detalles
                        </button>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
    }
    
    getTecnologiaBadgeClass(tecnologia) {
        switch (tecnologia) {
            case 'HFC': return 'bg-success';
            case 'FTTH': return 'bg-info';
            case 'WTTH': return 'bg-warning';
            default: return 'bg-secondary';
        }
    }
    
    renderizarPaginacion() {
        const totalPaginas = Math.ceil(this.datosFiltrados.length / this.registrosPorPagina);
        const paginacion = document.getElementById('paginacion');
        paginacion.innerHTML = '';
        
        if (totalPaginas <= 1) return;
        
        // Botón anterior
        const anterior = document.createElement('li');
        anterior.className = `page-item ${this.paginaActual === 1 ? 'disabled' : ''}`;
        anterior.innerHTML = `
            <a class="page-link" href="#" onclick="analistasModule.irAPagina(${this.paginaActual - 1})">
                <i class="fas fa-chevron-left"></i>
            </a>
        `;
        paginacion.appendChild(anterior);
        
        // Páginas
        const inicio = Math.max(1, this.paginaActual - 2);
        const fin = Math.min(totalPaginas, this.paginaActual + 2);
        
        for (let i = inicio; i <= fin; i++) {
            const pagina = document.createElement('li');
            pagina.className = `page-item ${i === this.paginaActual ? 'active' : ''}`;
            pagina.innerHTML = `
                <a class="page-link" href="#" onclick="analistasModule.irAPagina(${i})">${i}</a>
            `;
            paginacion.appendChild(pagina);
        }
        
        // Botón siguiente
        const siguiente = document.createElement('li');
        siguiente.className = `page-item ${this.paginaActual === totalPaginas ? 'disabled' : ''}`;
        siguiente.innerHTML = `
            <a class="page-link" href="#" onclick="analistasModule.irAPagina(${this.paginaActual + 1})">
                <i class="fas fa-chevron-right"></i>
            </a>
        `;
        paginacion.appendChild(siguiente);
    }
    
    irAPagina(pagina) {
        const totalPaginas = Math.ceil(this.datosFiltrados.length / this.registrosPorPagina);
        if (pagina < 1 || pagina > totalPaginas) return;
        
        this.paginaActual = pagina;
        this.renderizarDatos();
        this.renderizarPaginacion();
        
        // Scroll al inicio de los resultados
        document.getElementById('areaResultados').scrollIntoView({ behavior: 'smooth' });
    }
    
    actualizarContador() {
        document.getElementById('contadorResultados').textContent = this.datosFiltrados.length;
    }
    
    async mostrarDetalles(id) {
        try {
            const item = this.datos.find(d => d.idbase_causas_cierre === id);
            if (!item) {
                this.mostrarError('No se encontraron los detalles del elemento');
                return;
            }
            
            const modalBody = document.getElementById('modalDetallesBody');
            modalBody.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6><i class="fas fa-code me-2"></i>Información General</h6>
                        <table class="table table-sm">
                            <tr>
                                <td class="fw-bold">Código:</td>
                                <td><span class="badge bg-primary codigo-badge">${item.codigo_causas_cierre || 'N/A'}</span></td>
                            </tr>
                            <tr>
                                <td class="fw-bold">Tipo:</td>
                                <td>${item.tipo_causas_cierre || 'N/A'}</td>
                            </tr>
                            <tr>
                                <td class="fw-bold">Tecnología:</td>
                                <td><span class="badge ${this.getTecnologiaBadgeClass(item.tecnologia_causas_cierre)}">${item.tecnologia_causas_cierre || 'N/A'}</span></td>
                            </tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6><i class="fas fa-layer-group me-2"></i>Clasificación</h6>
                        <table class="table table-sm">
                            <tr>
                                <td class="fw-bold">Agrupación:</td>
                                <td>${item.agrupaciones_causas_cierre || 'N/A'}</td>
                            </tr>
                            <tr>
                                <td class="fw-bold">Grupo:</td>
                                <td>${item.todos_los_grupos_causas_cierre || 'N/A'}</td>
                            </tr>
                            <tr>
                                <td class="fw-bold">Facturable:</td>
                                <td><span class="badge ${item.facturable_causas_cierre === 'NO ES FACTURABLE' ? 'bg-danger' : 'bg-success'}">${item.facturable_causas_cierre || 'N/A'}</span></td>
                            </tr>
                        </table>
                    </div>
                </div>
                <div class="row mt-3">
                    <div class="col-12">
                        <h6><i class="fas fa-file-alt me-2"></i>Descripción</h6>
                        <p class="border p-3 bg-light rounded">${item.nombre_causas_cierre || 'Sin descripción disponible'}</p>
                    </div>
                </div>
                <div class="row mt-3">
                    <div class="col-12">
                        <h6><i class="fas fa-info-circle me-2"></i>Instrucciones de Uso</h6>
                        <p class="border p-3 bg-light rounded">${item.instrucciones_de_uso_causas_cierre || 'Sin instrucciones disponibles'}</p>
                    </div>
                </div>
            `;
            
            const modal = new bootstrap.Modal(document.getElementById('modalDetalles'));
            modal.show();
            
        } catch (error) {
            console.error('Error al mostrar detalles:', error);
            this.mostrarError('Error al cargar los detalles');
        }
    }
    
    mostrarLoading(mostrar) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            if (mostrar) {
                overlay.style.display = 'flex';
                overlay.style.visibility = 'visible';
                overlay.classList.remove('d-none');
                overlay.classList.add('d-flex');
            } else {
                overlay.style.display = 'none';
                overlay.style.visibility = 'hidden';
                overlay.classList.remove('d-flex');
                overlay.classList.add('d-none');
            }
            console.log('Loading overlay:', mostrar ? 'mostrado' : 'ocultado');
        } else {
            console.error('No se encontró el elemento loadingOverlay');
        }
    }
    
    mostrarError(mensaje) {
        // Crear toast de error
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-danger border-0 position-fixed';
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 10000;';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-exclamation-triangle me-2"></i>${mensaje}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remover el toast después de que se oculte
        toast.addEventListener('hidden.bs.toast', () => {
            document.body.removeChild(toast);
        });
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Inicializar el módulo cuando se carga la página
let analistasModule;
document.addEventListener('DOMContentLoaded', function() {
    analistasModule = new AnalistasModule();
    
    // Función de seguridad para ocultar el loading después de 3 segundos
    setTimeout(() => {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay && (overlay.style.display === 'flex' || overlay.classList.contains('d-flex'))) {
            console.warn('Forzando ocultación del loading overlay por seguridad');
            overlay.style.display = 'none';
            overlay.style.visibility = 'hidden';
            overlay.classList.remove('d-flex');
            overlay.classList.add('d-none');
        }
    }, 3000);
});

// Prevenir el envío del formulario al presionar Enter
document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && e.target.id === 'buscarTexto') {
        e.preventDefault();
        analistasModule.aplicarFiltros();
    }
});
