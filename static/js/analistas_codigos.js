/**
 * Submódulo Analistas - Códigos de Facturación
 * Funcionalidades de búsqueda, filtrado y visualización
 */

class AnalistasCodigosModule {
    constructor() {
        this.datos = [];
        this.datosFiltrados = [];
        this.paginaActual = 1;
        this.registrosPorPagina = 20;
        this.vistaActual = 'tabla';
        this.gruposDisponibles = [];
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.cargarDatos();
        await this.cargarAgrupaciones();
        await this.cargarGrupos();
    }

    setupEventListeners() {
        const buscarInput = document.getElementById('buscarTexto');
        if (buscarInput) buscarInput.addEventListener('input', this.debounce(() => this.aplicarFiltros(), 300));

        const filtroTecnologia = document.getElementById('filtroTecnologia');
        const filtroAgrupacion = document.getElementById('filtroAgrupacion');
        const filtroGrupo = document.getElementById('filtroGrupo');

        if (filtroTecnologia) filtroTecnologia.addEventListener('change', async () => {
            await this.cargarAgrupaciones(filtroTecnologia.value);
            await this.cargarGrupos(filtroTecnologia.value, filtroAgrupacion?.value || '');
            this.aplicarFiltros();
        });
        if (filtroAgrupacion) filtroAgrupacion.addEventListener('change', async () => {
            await this.cargarGrupos(filtroTecnologia?.value || '', filtroAgrupacion.value);
            this.aplicarFiltros();
        });
        if (filtroGrupo) filtroGrupo.addEventListener('change', () => this.aplicarFiltros());

        const btnBuscar = document.getElementById('btnBuscar');
        const btnLimpiar = document.getElementById('btnLimpiar');
        const btnLimpiarBusqueda = document.getElementById('limpiarBusqueda');
        if (btnBuscar) btnBuscar.addEventListener('click', () => this.aplicarFiltros());
        if (btnLimpiar) btnLimpiar.addEventListener('click', () => this.limpiarFiltros());
        if (btnLimpiarBusqueda) btnLimpiarBusqueda.addEventListener('click', () => this.limpiarBusqueda());

        const btnVistaTabla = document.getElementById('vistaTabla');
        const btnVistaCards = document.getElementById('vistaCards');
        if (btnVistaTabla) btnVistaTabla.addEventListener('click', () => this.cambiarVista('tabla'));
        if (btnVistaCards) btnVistaCards.addEventListener('click', () => this.cambiarVista('cards'));
    }

    async cargarDatos() {
        try {
            const response = await fetch('/api/analistas/codigos', { credentials: 'include' });
            if (response.status === 401 || response.status === 403 || response.redirected) { window.location.href = '/login'; return; }
            if (!response.ok) throw new Error('Error al cargar los datos');
            this.datos = await response.json();
            this.datosFiltrados = [...this.datos];
            this.actualizarContador();
            this.renderizarDatos();
            this.renderizarPaginacion();
        } catch (error) {
            console.error('Error:', error);
            this.mostrarError('Error al cargar los códigos de facturación.');
        }
    }

    async cargarGrupos(tecnologia = '', agrupacion = '') {
        try {
            let url = '/api/analistas/codigos/grupos';
            const params = new URLSearchParams();
            if (tecnologia) params.append('tecnologia', tecnologia);
            if (agrupacion) params.append('agrupacion', agrupacion);
            if (params.toString()) url += `?${params.toString()}`;
            const response = await fetch(url, { credentials: 'include' });
            if (response.status === 401 || response.status === 403 || response.redirected) { window.location.href = '/login'; return; }
            if (!response.ok) throw new Error('Error al cargar grupos');
            this.gruposDisponibles = await response.json();
            this.renderizarOpcionesGrupos();
        } catch (error) {
            console.error('Error al cargar grupos:', error);
        }
    }

    async cargarAgrupaciones(tecnologia = '') {
        try {
            let url = '/api/analistas/codigos/agrupaciones';
            if (tecnologia) url += `?tecnologia=${encodeURIComponent(tecnologia)}`;
            const response = await fetch(url, { credentials: 'include' });
            if (response.status === 401 || response.status === 403 || response.redirected) { window.location.href = '/login'; return; }
            if (!response.ok) throw new Error('Error al cargar agrupaciones');
            const agrupaciones = await response.json();
            this.renderizarOpcionesAgrupaciones(agrupaciones);
        } catch (error) {
            console.error('Error al cargar agrupaciones:', error);
        }
    }

    renderizarOpcionesGrupos() {
        const select = document.getElementById('filtroGrupo');
        if (!select) return;
        while (select.children.length > 1) select.removeChild(select.lastChild);
        this.gruposDisponibles.forEach(grupo => {
            const option = document.createElement('option');
            option.value = grupo;
            option.textContent = grupo;
            select.appendChild(option);
        });
    }

    renderizarOpcionesAgrupaciones(agrupaciones) {
        const select = document.getElementById('filtroAgrupacion');
        if (!select) return;
        while (select.children.length > 1) select.removeChild(select.lastChild);
        agrupaciones.forEach(agrupacion => {
            const option = document.createElement('option');
            option.value = agrupacion;
            option.textContent = agrupacion;
            select.appendChild(option);
        });
    }

    aplicarFiltros() {
        const textoBusqueda = (document.getElementById('buscarTexto')?.value || '').toLowerCase().trim();
        const tecnologia = document.getElementById('filtroTecnologia')?.value || '';
        const agrupacion = document.getElementById('filtroAgrupacion')?.value || '';
        const grupo = document.getElementById('filtroGrupo')?.value || '';

        this.datosFiltrados = this.datos.filter(item => {
            const coincideTexto = !textoBusqueda ||
                (item.codigo_codigos_facturacion && item.codigo_codigos_facturacion.toLowerCase().includes(textoBusqueda)) ||
                (item.nombre_codigos_facturacion && item.nombre_codigos_facturacion.toLowerCase().includes(textoBusqueda)) ||
                (item.instrucciones_de_uso_codigos_facturacion && item.instrucciones_de_uso_codigos_facturacion.toLowerCase().includes(textoBusqueda));
            const coincideTecnologia = !tecnologia || item.tecnologia === tecnologia;
            const coincideAgrupacion = !agrupacion || item.categoria === agrupacion;
            const coincideGrupo = !grupo || item.nombre === grupo;
            return coincideTexto && coincideTecnologia && coincideAgrupacion && coincideGrupo;
        });

        this.paginaActual = 1;
        this.actualizarContador();
        this.renderizarDatos();
        this.renderizarPaginacion();
    }

    async limpiarFiltros() {
        const buscar = document.getElementById('buscarTexto');
        const tecnologia = document.getElementById('filtroTecnologia');
        const agrupacion = document.getElementById('filtroAgrupacion');
        const grupo = document.getElementById('filtroGrupo');
        if (buscar) buscar.value = '';
        if (tecnologia) tecnologia.value = '';
        if (agrupacion) agrupacion.value = '';
        if (grupo) grupo.value = '';
        await this.cargarAgrupaciones();
        await this.cargarGrupos();
        this.aplicarFiltros();
    }

    limpiarBusqueda() {
        const buscar = document.getElementById('buscarTexto');
        if (buscar) buscar.value = '';
        this.aplicarFiltros();
    }

    cambiarVista(vista) {
        this.vistaActual = vista;
        const btnTabla = document.getElementById('vistaTabla');
        const btnCards = document.getElementById('vistaCards');
        if (btnTabla) btnTabla.classList.toggle('active', vista === 'tabla');
        if (btnCards) btnCards.classList.toggle('active', vista === 'cards');
        const contTabla = document.getElementById('vistaTablaContainer');
        const contCards = document.getElementById('vistaCardsContainer');
        if (contTabla) contTabla.style.display = vista === 'tabla' ? 'block' : 'none';
        if (contCards) contCards.style.display = vista === 'cards' ? 'block' : 'none';
        this.renderizarDatos();
    }

    renderizarDatos() {
        if (this.vistaActual === 'tabla') this.renderizarTabla(); else this.renderizarCards();
    }

    renderizarTabla() {
        const tbody = document.getElementById('tablaCodigosBody');
        if (!tbody) return;
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
                <td><span class="badge bg-primary codigo-badge">${item.codigo_codigos_facturacion || 'N/A'}</span></td>
                <td>${item.nombre || 'N/A'}</td>
                <td><span class="badge ${this.getTecnologiaBadgeClass(item.tecnologia)}">${item.tecnologia || 'N/A'}</span></td>
                <td>${item.categoria || 'N/A'}</td>
                
                <td>
                    <div class="fw-bold">${item.nombre_codigos_facturacion || 'Sin descripción'}</div>
                    <small class="text-muted">${item.instrucciones_de_uso_codigos_facturacion || ''}</small>
                </td>
                <td>${item.facturable_codigos_facturacion ? '<i class="fas fa-check text-success"></i>' : '<i class="fas fa-times text-danger"></i>'}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="analistasCodigosModule.mostrarDetalles(${item.idbase_codigos_facturacion})"><i class="fas fa-eye"></i></button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderizarCards() {
        const container = document.getElementById('vistaCardsContainer');
        if (!container) return;
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
                        <span class="badge bg-primary codigo-badge">${item.codigo_codigos_facturacion || 'N/A'}</span>
                        <span class="badge ${this.getTecnologiaBadgeClass(item.tecnologia)}">${item.tecnologia || 'N/A'}</span>
                    </div>
                    <div class="card-body">
                        <h5 class="card-title text-truncate-2">${item.nombre_codigos_facturacion || 'Sin descripción'}</h5>
                        <p class="card-text text-truncate-2">${item.instrucciones_de_uso_codigos_facturacion || ''}</p>
                        <div class="d-flex justify-content-between">
                            <span class="badge bg-secondary">${item.categoria || 'N/A'}</span>
                            <span class="badge bg-dark">${item.nombre || 'N/A'}</span>
                        </div>
                    </div>
                    <div class="card-footer d-flex justify-content-between align-items-center">
                        <span>${item.facturable_codigos_facturacion ? '<i class="fas fa-check text-success me-1"></i>Facturable' : '<i class="fas fa-times text-danger me-1"></i>No facturable'}</span>
                        <button class="btn btn-sm btn-outline-primary" onclick="analistasCodigosModule.mostrarDetalles(${item.idbase_codigos_facturacion})"><i class="fas fa-eye me-1"></i>Ver detalles</button>
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
        if (!paginacion) return;
        paginacion.innerHTML = '';
        if (totalPaginas <= 1) return;
        const anterior = document.createElement('li');
        anterior.className = `page-item ${this.paginaActual === 1 ? 'disabled' : ''}`;
        anterior.innerHTML = `<a class="page-link" href="#" onclick="analistasCodigosModule.irAPagina(${this.paginaActual - 1})"><i class="fas fa-chevron-left"></i></a>`;
        paginacion.appendChild(anterior);
        const inicio = Math.max(1, this.paginaActual - 2);
        const fin = Math.min(totalPaginas, this.paginaActual + 2);
        for (let i = inicio; i <= fin; i++) {
            const pagina = document.createElement('li');
            pagina.className = `page-item ${i === this.paginaActual ? 'active' : ''}`;
            pagina.innerHTML = `<a class="page-link" href="#" onclick="analistasCodigosModule.irAPagina(${i})">${i}</a>`;
            paginacion.appendChild(pagina);
        }
        const siguiente = document.createElement('li');
        siguiente.className = `page-item ${this.paginaActual === totalPaginas ? 'disabled' : ''}`;
        siguiente.innerHTML = `<a class="page-link" href="#" onclick="analistasCodigosModule.irAPagina(${this.paginaActual + 1})"><i class="fas fa-chevron-right"></i></a>`;
        paginacion.appendChild(siguiente);
    }

    irAPagina(pagina) {
        const totalPaginas = Math.ceil(this.datosFiltrados.length / this.registrosPorPagina);
        if (pagina < 1 || pagina > totalPaginas) return;
        this.paginaActual = pagina;
        this.renderizarDatos();
        this.renderizarPaginacion();
        const area = document.getElementById('areaResultados');
        if (area) area.scrollIntoView({ behavior: 'smooth' });
    }

    actualizarContador() {
        const contador = document.getElementById('contadorResultados');
        if (contador) contador.textContent = this.datosFiltrados.length;
    }

    async mostrarDetalles(id) {
        try {
            const item = this.datos.find(d => d.idbase_codigos_facturacion === id);
            if (!item) {
                this.mostrarError('No se encontraron los detalles del código');
                return;
            }
            const modalBody = document.getElementById('modalDetallesBody');
            if (!modalBody) return;
            modalBody.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6><i class="fas fa-code me-2"></i>Información General</h6>
                        <table class="table table-sm">
                            <tr>
                                <td class="fw-bold">Código:</td>
                                <td><span class="badge bg-primary codigo-badge">${item.codigo_codigos_facturacion || 'N/A'}</span></td>
                            </tr>
                            <tr>
                                <td class="fw-bold">Grupo:</td>
                                <td>${item.nombre || 'N/A'}</td>
                            </tr>
                            <tr>
                                <td class="fw-bold">Tecnología:</td>
                                <td><span class="badge ${this.getTecnologiaBadgeClass(item.tecnologia)}">${item.tecnologia || 'N/A'}</span></td>
                            </tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6><i class="fas fa-layer-group me-2"></i>Agrupación y Grupo</h6>
                        <table class="table table-sm">
                            <tr>
                                <td class="fw-bold">Agrupación:</td>
                                <td>${item.categoria || 'N/A'}</td>
                            </tr>
                            
                            <tr>
                                <td class="fw-bold">Nombre:</td>
                                <td>${item.nombre_codigos_facturacion || 'N/A'}</td>
                            </tr>
                            <tr>
                                <td class="fw-bold">Facturable:</td>
                                <td>${item.facturable_codigos_facturacion ? '<span class="text-success">Sí</span>' : '<span class="text-danger">No</span>'}</td>
                            </tr>
                        </table>
                    </div>
                    <div class="col-12 mt-3">
                        <h6><i class="fas fa-info-circle me-2"></i>Instrucciones de Uso</h6>
                        <p class="border p-3 bg-light rounded">${item.instrucciones_de_uso_codigos_facturacion || 'Sin instrucciones disponibles'}</p>
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

    mostrarError(mensaje) { console.error(mensaje); }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => { clearTimeout(timeout); func(...args); };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

let analistasCodigosModule;
document.addEventListener('DOMContentLoaded', function() {
    analistasCodigosModule = new AnalistasCodigosModule();
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && e.target.id === 'buscarTexto') { e.preventDefault(); analistasCodigosModule.aplicarFiltros(); }
    });
});