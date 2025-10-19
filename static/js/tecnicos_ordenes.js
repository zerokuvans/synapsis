// Variables globales
let ordenesTrabajo = [];
let codigosDisponibles = [];
let codigosSeleccionados = [];
let tecnologias = [];
let categorias = [];
let paginaActual = 1;
const registrosPorPagina = 10;

// Configuración de API
const API_BASE_URL = '/tecnicos';

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    inicializarEventos();
    cargarTecnologias();
    cargarOrdenesTrabajo();
});

// Función para inicializar eventos
function inicializarEventos() {
    // Botones principales
    document.getElementById('btnNuevaOT').addEventListener('click', abrirModalNuevaOT);
    document.getElementById('btnAplicarFiltros').addEventListener('click', aplicarFiltros);
    document.getElementById('btnLimpiarFiltros').addEventListener('click', limpiarFiltros);
    
    // Botones de vista
    document.getElementById('btnVistaTabla').addEventListener('click', cambiarVistaTabla);
    document.getElementById('btnVistaTarjetas').addEventListener('click', cambiarVistaTarjetas);
    
    // Filtros en cascada (solo si existen en la vista)
    const filtroTecnologiaEl = document.getElementById('filtroTecnologia');
    const filtroCategoriaEl = document.getElementById('filtroCategoria');
    if (filtroTecnologiaEl && filtroCategoriaEl) {
        filtroTecnologiaEl.addEventListener('change', function() {
            if (this.value) {
                cargarCategorias(this.value, 'filtroCategoria');
            } else {
                limpiarSelect('filtroCategoria', 'Seleccione tecnología primero', true);
            }
        });
    }
    
    // Filtros del modal
    document.getElementById('selectTecnologia').addEventListener('change', function() {
        if (this.value) {
            cargarCategorias(this.value, 'selectCategoria');
            cargarCodigosPorTecnologiaCategoria(this.value, '');
        } else {
            limpiarSelect('selectCategoria', 'Seleccione tecnología primero', true);
            limpiarTablaCodigosDisponibles();
        }
    });
    
    document.getElementById('selectCategoria').addEventListener('change', function() {
        const tecnologia = document.getElementById('selectTecnologia').value;
        if (tecnologia && this.value) {
            cargarCodigosPorTecnologiaCategoria(tecnologia, this.value);
        } else if (tecnologia) {
            cargarCodigosPorTecnologiaCategoria(tecnologia, '');
        }
    });
    
    // Validación de campos numéricos en tiempo real
    document.getElementById('inputOT').addEventListener('input', function() {
        validarCampoNumerico(this, 7);
    });
    
    document.getElementById('inputCuenta').addEventListener('input', function() {
        validarCampoNumerico(this, 8);
    });
    
    document.getElementById('inputServicio').addEventListener('input', function() {
        validarCampoNumerico(this, 7);
    });
    
    // Botón guardar OT
    document.getElementById('btnGuardarOT').addEventListener('click', guardarOT);
    
    // Validación del formulario
    document.getElementById('formNuevaOT').addEventListener('input', validarFormularioOT);
}

// Funciones de carga de datos
async function cargarOrdenesTrabajo() {
    try {
        mostrarCargandoTabla();
        
        const response = await fetch(`${API_BASE_URL}/ordenes`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        ordenesTrabajo = data.ordenes || data;
        
        actualizarTabla();
        actualizarTotalRegistros();
        
    } catch (error) {
        console.error('Error al cargar órdenes de trabajo:', error);
        mostrarErrorTabla('Error al cargar las órdenes de trabajo');
    }
}

async function cargarTecnologias() {
    try {
        const response = await fetch(`${API_BASE_URL}/tecnologias`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        tecnologias = data.tecnologias || data;
        
        // Llenar selects de tecnología
        const filtroEl = document.getElementById('filtroTecnologia');
        if (filtroEl) {
            llenarSelect('filtroTecnologia', tecnologias, 'Seleccione tecnología');
        }
        // Mantener el modal
        llenarSelect('selectTecnologia', tecnologias, 'Seleccione tecnología');
        
    } catch (error) {
        console.error('Error al cargar tecnologías:', error);
    }
}

async function cargarCategorias(tecnologia, selectId) {
    try {
        const response = await fetch(`${API_BASE_URL}/categorias/${tecnologia}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        categorias = data.categorias || data;
        
        // Habilitar select y llenar opciones
        const select = document.getElementById(selectId);
        select.disabled = false;
        llenarSelect(selectId, categorias, 'Seleccione categoría');
        
    } catch (error) {
        console.error('Error al cargar categorías:', error);
        limpiarSelect(selectId, 'Error al cargar categorías', true);
    }
}

async function cargarCodigosPorTecnologiaCategoria(tecnologia, categoria) {
    try {
        let url = `${API_BASE_URL}/codigos/tecnologia/${tecnologia}`;
        if (categoria) {
            url += `/categoria/${categoria}`;
        }
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        codigosDisponibles = data.codigos || data;
        
        actualizarTablaCodigosDisponibles();
        
    } catch (error) {
        console.error('Error al cargar códigos:', error);
        limpiarTablaCodigosDisponibles();
    }
}

// Funciones de UI
function actualizarTabla() {
    const cuerpoTabla = document.getElementById('cuerpoTabla');
    const inicio = (paginaActual - 1) * registrosPorPagina;
    const fin = inicio + registrosPorPagina;
    const ordenesPagina = ordenesTrabajo.slice(inicio, fin);
    
    if (ordenesPagina.length === 0) {
        cuerpoTabla.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted">
                    <i class="fas fa-inbox me-2"></i>No hay órdenes de trabajo registradas
                </td>
            </tr>
        `;
        return;
    }
    
    cuerpoTabla.innerHTML = ordenesPagina.map(orden => `
        <tr>
            <td><strong>${orden.ot || 'N/A'}</strong></td>
            <td>${orden.cuenta || 'N/A'}</td>
            <td>${orden.servicio || 'N/A'}</td>
            <td><span class="badge bg-info">${orden.cantidad_codigos || 0} códigos</span></td>
            <td><strong>$${formatoMoneda(orden.total_valor || 0)}</strong></td>
            <td>
                <span class="badge bg-${getEstadoColor('activa')}">
                    Activa
                </span>
            </td>
            <td>
                <div class="btn-group" role="group">
                    <button class="btn btn-sm btn-outline-primary" onclick="verDetallesOT('${orden.ot}')" title="Ver detalles">
                        <i class="fas fa-eye"></i> Ver
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    actualizarPaginacion();
}

function actualizarVistaTarjetas() {
    const contenedor = document.getElementById('vistaTarjetas');
    const inicio = (paginaActual - 1) * registrosPorPagina;
    const fin = inicio + registrosPorPagina;
    const ordenesPagina = ordenesTrabajo.slice(inicio, fin);
    
    if (ordenesPagina.length === 0) {
        contenedor.innerHTML = `
            <div class="col-12">
                <div class="text-center text-muted py-5">
                    <i class="fas fa-inbox fa-3x mb-3"></i>
                    <h5>No hay órdenes de trabajo registradas</h5>
                </div>
            </div>
        `;
        return;
    }
    
    contenedor.innerHTML = ordenesPagina.map(orden => `
        <div class="col-md-6 col-lg-4 mb-3">
            <div class="card h-100">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">OT: ${orden.ot || 'N/A'}</h6>
                    <span class="badge bg-${getEstadoColor(orden.estado)}">${orden.estado || 'Pendiente'}</span>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-6">
                            <small class="text-muted">Cuenta:</small>
                            <div>${orden.cuenta || 'N/A'}</div>
                        </div>
                        <div class="col-6">
                            <small class="text-muted">Servicio:</small>
                            <div>${orden.servicio || 'N/A'}</div>
                        </div>
                    </div>
                    <hr>
                    <div class="row">
                        <div class="col-6">
                            <small class="text-muted">Código:</small>
                            <div>${orden.codigo || 'N/A'}</div>
                        </div>
                        <div class="col-6">
                            <small class="text-muted">Nombre:</small>
                            <div>${orden.nombre || 'N/A'}</div>
                        </div>
                    </div>
                    <hr>
                    <div class="text-end">
                        <h5 class="text-primary">$${formatoMoneda(orden.valor_total || 0)}</h5>
                    </div>
                </div>
                <div class="card-footer">
                    <div class="btn-group w-100" role="group">
                        <button class="btn btn-sm btn-outline-primary" onclick="verDetallesOT('${orden.ot}')">
                            <i class="fas fa-eye"></i> Ver
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    actualizarPaginacion();
}

function actualizarPaginacion() {
    const totalPaginas = Math.ceil(ordenesTrabajo.length / registrosPorPagina);
    const paginacion = document.getElementById('paginacion');
    
    if (totalPaginas <= 1) {
        paginacion.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Botón anterior
    html += `
        <li class="page-item ${paginaActual === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="cambiarPagina(${paginaActual - 1}); return false;">
                <i class="fas fa-chevron-left"></i>
            </a>
        </li>
    `;
    
    // Números de página
    for (let i = 1; i <= totalPaginas; i++) {
        if (i === 1 || i === totalPaginas || (i >= paginaActual - 1 && i <= paginaActual + 1)) {
            html += `
                <li class="page-item ${i === paginaActual ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="cambiarPagina(${i}); return false;">${i}</a>
                </li>
            `;
        } else if (i === paginaActual - 2 || i === paginaActual + 2) {
            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }
    
    // Botón siguiente
    html += `
        <li class="page-item ${paginaActual === totalPaginas ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="cambiarPagina(${paginaActual + 1}); return false;">
                <i class="fas fa-chevron-right"></i>
            </a>
        </li>
    `;
    
    paginacion.innerHTML = html;
}

function cambiarPagina(nuevaPagina) {
    const totalPaginas = Math.ceil(ordenesTrabajo.length / registrosPorPagina);
    if (nuevaPagina >= 1 && nuevaPagina <= totalPaginas) {
        paginaActual = nuevaPagina;
        if (document.getElementById('vistaTabla').style.display !== 'none') {
            actualizarTabla();
        } else {
            actualizarVistaTarjetas();
        }
    }
}

function cambiarVistaTabla() {
    document.getElementById('vistaTabla').style.display = 'block';
    document.getElementById('vistaTarjetas').style.display = 'none';
    document.getElementById('btnVistaTabla').classList.add('active');
    document.getElementById('btnVistaTarjetas').classList.remove('active');
    actualizarTabla();
}

function cambiarVistaTarjetas() {
    document.getElementById('vistaTabla').style.display = 'none';
    document.getElementById('vistaTarjetas').style.display = 'block';
    document.getElementById('btnVistaTarjetas').classList.add('active');
    document.getElementById('btnVistaTabla').classList.remove('active');
    actualizarVistaTarjetas();
}

// Funciones del modal
function abrirModalNuevaOT() {
    limpiarFormularioOT();
    const modal = new bootstrap.Modal(document.getElementById('modalNuevaOT'));
    modal.show();
}

function limpiarFormularioOT() {
    document.getElementById('formNuevaOT').reset();
    codigosSeleccionados = [];
    limpiarTablaCodigosDisponibles();
    limpiarTablaCodigosSeleccionados();
    actualizarValorTotal();
    document.getElementById('btnGuardarOT').disabled = true;
}

function validarCampoNumerico(input, longitud) {
    // Remover caracteres no numéricos
    input.value = input.value.replace(/\D/g, '');
    
    // Limitar longitud
    if (input.value.length > longitud) {
        input.value = input.value.slice(0, longitud);
    }
    
    // Validar longitud exacta
    if (input.value.length !== longitud) {
        input.classList.add('is-invalid');
    } else {
        input.classList.remove('is-invalid');
    }
    
    validarFormularioOT();
}

function validarFormularioOT() {
    const ot = document.getElementById('inputOT');
    const cuenta = document.getElementById('inputCuenta');
    const servicio = document.getElementById('inputServicio');
    const tecnologia = document.getElementById('selectTecnologia');
    const categoria = document.getElementById('selectCategoria');
    
    const esValido = 
        ot.value.length === 7 &&
        cuenta.value.length === 8 &&
        servicio.value.length === 7 &&
        tecnologia.value &&
        categoria.value &&
        codigosSeleccionados.length > 0;
    
    document.getElementById('btnGuardarOT').disabled = !esValido;
}

function actualizarTablaCodigosDisponibles() {
    const tbody = document.querySelector('#tablaCodigosDisponibles tbody');
    
    if (codigosDisponibles.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    <i class="fas fa-info-circle me-2"></i>No hay códigos disponibles para esta selección
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = codigosDisponibles.map(codigo => `
        <tr>
            <td><strong>${codigo.codigo || codigo.codigo_codigos_facturacion}</strong></td>
            <td>${codigo.descripcion || codigo.nombre_codigos_facturacion}</td>
            <td>$${formatoMoneda(codigo.valor || 0)}</td>
            <td>
                <input type="number" 
                       class="form-control form-control-sm" 
                       min="1" 
                       max="999" 
                       value="1"
                       onchange="actualizarCantidadDisponible('${codigo.id || codigo.id_base_codigos_facturacion}', this.value)">
            </td>
            <td>$${formatoMoneda((codigo.valor || 0) * 1)}</td>
            <td>
                <button type="button" class="btn btn-sm btn-success" onclick="agregarCodigoSeleccionado(event, '${codigo.id || codigo.id_base_codigos_facturacion}')">
                    <i class="fas fa-plus"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function limpiarTablaCodigosDisponibles() {
    const tbody = document.querySelector('#tablaCodigosDisponibles tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="6" class="text-center text-muted">
                <i class="fas fa-info-circle me-2"></i>Seleccione tecnología y categoría para ver códigos disponibles
            </td>
        </tr>
    `;
}

function actualizarTablaCodigosSeleccionados() {
    const tbody = document.querySelector('#tablaCodigosSeleccionados tbody');
    console.log('[actualizarTablaCodigosSeleccionados] render', { seleccionadosLen: codigosSeleccionados.length, codigosSeleccionados });
    
    if (codigosSeleccionados.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    <i class="fas fa-shopping-cart me-2"></i>No hay códigos seleccionados
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = codigosSeleccionados.map(codigo => `
        <tr>
            <td><strong>${codigo.codigo || codigo.codigo_codigos_facturacion}</strong></td>
            <td>${codigo.descripcion || codigo.nombre_codigos_facturacion}</td>
            <td>$${formatoMoneda(codigo.valor || 0)}</td>
            <td>
                <input type="number" 
                       class="form-control form-control-sm" 
                       min="1" 
                       max="999" 
                       value="${codigo.cantidad || 1}"
                       onchange="actualizarCantidadSeleccionado('${codigo.id || codigo.id_base_codigos_facturacion}', this.value)">
            </td>
            <td>$${formatoMoneda((codigo.valor || 0) * (codigo.cantidad || 1))}</td>
            <td>
                <button type="button" class="btn btn-sm btn-danger" onclick="eliminarCodigoSeleccionado(event, '${codigo.id || codigo.id_base_codigos_facturacion}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
    
    actualizarValorTotal();
    validarFormularioOT();
}

function limpiarTablaCodigosSeleccionados() {
    const tbody = document.querySelector('#tablaCodigosSeleccionados tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="6" class="text-center text-muted">
                <i class="fas fa-shopping-cart me-2"></i>No hay códigos seleccionados
            </td>
        </tr>
    `;
}

function agregarCodigoSeleccionado(evt, idCodigo) {
    if (evt) { evt.preventDefault(); evt.stopPropagation(); }
    const idNorm = String(idCodigo);
    console.log('[agregarCodigoSeleccionado] click', { idCodigo, idNorm, codigosDisponiblesLen: codigosDisponibles.length });
    const codigo = codigosDisponibles.find(c => String(c.id ?? c.id_base_codigos_facturacion) === idNorm);
    console.log('[agregarCodigoSeleccionado] encontrado?', codigo);
    if (!codigo) {
        console.warn('[agregarCodigoSeleccionado] Código no encontrado en codigosDisponibles', { idCodigo });
        return;
    }
    
    // Verificar si ya está seleccionado
    const yaSeleccionado = codigosSeleccionados.some(c => String(c.id ?? c.id_base_codigos_facturacion) === idNorm);
    console.log('[agregarCodigoSeleccionado] yaSeleccionado?', yaSeleccionado);
    if (yaSeleccionado) {
        return;
    }
    
    // Obtener cantidad del input
    const filaInput = document.querySelector(`input[onchange*="${idNorm}"]`);
    const cantidad = filaInput ? parseInt(filaInput.value) || 1 : 1;
    console.log('[agregarCodigoSeleccionado] cantidad', cantidad);
    
    const codigoConCantidad = {
        ...codigo,
        cantidad: cantidad
    };
    
    codigosSeleccionados.push(codigoConCantidad);
    console.log('[agregarCodigoSeleccionado] codigosSeleccionados', codigosSeleccionados);
    actualizarTablaCodigosSeleccionados();
}

function eliminarCodigoSeleccionado(evt, idCodigo) {
    if (evt) { evt.preventDefault(); evt.stopPropagation(); }
    codigosSeleccionados = codigosSeleccionados.filter(c => (c.id || c.id_base_codigos_facturacion) !== idCodigo);
    actualizarTablaCodigosSeleccionados();
}

function actualizarCantidadDisponible(idCodigo, cantidad) {
    // Actualizar cantidad en códigos disponibles
    const codigo = codigosDisponibles.find(c => (c.id || c.id_base_codigos_facturacion) === idCodigo);
    if (codigo) {
        const subtotal = (codigo.valor || 0) * parseInt(cantidad || 1);
        const fila = document.querySelector(`tr:has(input[onchange*="${idCodigo}"])`);
        if (fila) {
            fila.cells[4].textContent = `$${formatoMoneda(subtotal)}`;
        }
    }
}

function actualizarCantidadSeleccionado(idCodigo, cantidad) {
    const codigo = codigosSeleccionados.find(c => (c.id || c.id_base_codigos_facturacion) === idCodigo);
    if (codigo) {
        codigo.cantidad = parseInt(cantidad || 1);
        actualizarTablaCodigosSeleccionados();
    }
}

function actualizarValorTotal() {
    const total = codigosSeleccionados.reduce((sum, codigo) => {
        return sum + ((codigo.valor || 0) * (codigo.cantidad || 1));
    }, 0);
    
    document.getElementById('valorTotal').textContent = formatoMoneda(total);
}

// Funciones de filtros
function aplicarFiltros() {
    const filtroOT = document.getElementById('filtroOT').value;
    const filtroCuenta = document.getElementById('filtroCuenta').value;
    
    let ordenesFiltradas = [...ordenesTrabajo];
    
    if (filtroOT) {
        ordenesFiltradas = ordenesFiltradas.filter(orden => 
            orden.ot && orden.ot.toString().includes(filtroOT)
        );
    }
    
    if (filtroCuenta) {
        ordenesFiltradas = ordenesFiltradas.filter(orden => 
            orden.cuenta && orden.cuenta.toString().includes(filtroCuenta)
        );
    }
    
    // Actualizar datos y vista
    ordenesTrabajo = ordenesFiltradas;
    paginaActual = 1;
    actualizarTabla();
    actualizarTotalRegistros();
}

function limpiarFiltros() {
    const otInput = document.getElementById('filtroOT');
    const cuentaInput = document.getElementById('filtroCuenta');
    if (otInput) otInput.value = '';
    if (cuentaInput) cuentaInput.value = '';
    
    // Recargar datos originales
    cargarOrdenesTrabajo();
}

// Funciones de guardado
async function guardarOT() {
    if (!validarFormularioOTCompleto()) {
        return;
    }
    
    try {
        const formData = {
            ot: document.getElementById('inputOT').value,
            cuenta: document.getElementById('inputCuenta').value,
            servicio: document.getElementById('inputServicio').value,
            tecnologia: document.getElementById('selectTecnologia').value,
            categoria: document.getElementById('selectCategoria').value,
            codigos: codigosSeleccionados.map(codigo => ({
                id_codigo: codigo.id || codigo.id_base_codigos_facturacion,
                codigo: codigo.codigo || codigo.codigo_codigos_facturacion,
                descripcion: codigo.descripcion || codigo.nombre_codigos_facturacion,
                cantidad: codigo.cantidad,
                valor_unitario: codigo.valor,
                subtotal: (codigo.valor || 0) * (codigo.cantidad || 1)
            })),
            valor_total: codigosSeleccionados.reduce((sum, codigo) => {
                return sum + ((codigo.valor || 0) * (codigo.cantidad || 1));
            }, 0)
        };
        
        const response = await fetch(`${API_BASE_URL}/ordenes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            // Intentar leer mensaje del backend
            let backendMsg = null;
            try {
                const errJson = await response.json();
                backendMsg = errJson?.message || errJson?.error || null;
            } catch {}
            
            if (response.status === 409) {
                // OT ya creada por otro técnico: mostrar advertencia y no cerrar el modal
                mostrarMensaje('warning', backendMsg || 'La OT ya fue registrada por otro técnico y no puede duplicarse');
                return; // No continuar con cierre ni recarga
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Cerrar modal y recargar datos
        bootstrap.Modal.getInstance(document.getElementById('modalNuevaOT')).hide();
        
        // Mostrar mensaje de éxito
        mostrarMensaje('success', 'Orden de trabajo creada exitosamente');
        
        // Recargar órdenes
        cargarOrdenesTrabajo();
        
    } catch (error) {
        console.error('Error al guardar OT:', error);
        mostrarMensaje('error', 'Error al guardar la orden de trabajo');
    }
}

function validarFormularioOTCompleto() {
    const form = document.getElementById('formNuevaOT');
    
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return false;
    }
    
    if (codigosSeleccionados.length === 0) {
        mostrarMensaje('warning', 'Debe seleccionar al menos un código');
        return false;
    }
    
    return true;
}

// Funciones auxiliares
function llenarSelect(selectId, opciones, placeholder) {
    const select = document.getElementById(selectId);
    select.innerHTML = `<option value="">${placeholder}</option>`;
    
    opciones.forEach(opcion => {
        const valor = typeof opcion === 'string' ? opcion : opcion.tecnologia || opcion.categoria;
        select.innerHTML += `<option value="${valor}">${valor}</option>`;
    });
}

function limpiarSelect(selectId, mensaje, disabled = false) {
    const select = document.getElementById(selectId);
    select.innerHTML = `<option value="">${mensaje}</option>`;
    select.disabled = disabled;
}

function mostrarCargandoTabla() {
    const cuerpoTabla = document.getElementById('cuerpoTabla');
    cuerpoTabla.innerHTML = `
        <tr>
            <td colspan="8" class="text-center text-muted">
                <i class="fas fa-spinner fa-spin me-2"></i>Cargando órdenes...
            </td>
        </tr>
    `;
}

function mostrarErrorTabla(mensaje) {
    const cuerpoTabla = document.getElementById('cuerpoTabla');
    cuerpoTabla.innerHTML = `
        <tr>
            <td colspan="8" class="text-center text-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>${mensaje}
            </td>
        </tr>
    `;
}

function actualizarTotalRegistros() {
    const total = ordenesTrabajo.length;
    document.getElementById('totalRegistros').textContent = `${total} registro${total !== 1 ? 's' : ''}`;
}

function getEstadoColor(estado) {
    const colores = {
        'Pendiente': 'warning',
        'En Proceso': 'info',
        'Completado': 'success',
        'Cancelado': 'danger'
    };
    return colores[estado] || 'secondary';
}

function formatoMoneda(valor) {
    return new Intl.NumberFormat('es-CL', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(valor);
}

function mostrarMensaje(tipo, mensaje) {
    // Crear contenedor de mensajes si no existe
    let contenedor = document.getElementById('mensajes-container');
    if (!contenedor) {
        contenedor = document.createElement('div');
        contenedor.id = 'mensajes-container';
        contenedor.className = 'position-fixed top-0 end-0 p-3';
        contenedor.style.zIndex = '9999';
        document.body.appendChild(contenedor);
    }
    
    const idMensaje = `mensaje-${Date.now()}`;
    const iconos = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    };
    
    const html = `
        <div id="${idMensaje}" class="alert alert-${tipo} alert-dismissible fade show" role="alert">
            <i class="${iconos[tipo]} me-2"></i>${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    contenedor.insertAdjacentHTML('beforeend', html);
    
    // Auto-cerrar después de 5 segundos
    setTimeout(() => {
        const mensajeElement = document.getElementById(idMensaje);
        if (mensajeElement) {
            const alert = bootstrap.Alert.getInstance(mensajeElement);
            if (alert) {
                alert.close();
            }
        }
    }, 5000);
}

// Funciones de acciones sobre OT
function verDetallesOT(ot) {
    console.log('Ver detalles OT:', ot);
    cargarDetallesOT(ot);
}

function verDetallesOTById(id) {
    console.log('Ver detalles OT por ID (entrada):', id, typeof id);
    // Buscar orden por ID con comparación flexible en caso de desajuste de tipos
    const orden = ordenesTrabajo.find(o => o.id == id);
    console.log('Orden encontrada por ID:', orden);
    if (!orden) {
        console.error('OT no encontrada en la lista local para id:', id);
        const cuerpoTabla = document.getElementById('cuerpoTablaDetalles');
        cuerpoTabla.innerHTML = '<tr><td colspan="6" class="text-center text-danger"><i class="fas fa-exclamation-triangle me-2"></i>OT no encontrada en la lista local</td></tr>';
        const modalDetalles = bootstrap.Modal.getOrCreateInstance(document.getElementById('modalDetallesOT'));
        modalDetalles.show();
        return;
    }
    if (!orden.ot) {
        console.error('La orden encontrada no tiene OT válida:', orden);
        const cuerpoTabla = document.getElementById('cuerpoTablaDetalles');
        cuerpoTabla.innerHTML = '<tr><td colspan="6" class="text-center text-danger"><i class="fas fa-exclamation-triangle me-2"></i>OT no disponible para la orden seleccionada</td></tr>';
        const modalDetalles = bootstrap.Modal.getOrCreateInstance(document.getElementById('modalDetallesOT'));
        modalDetalles.show();
        return;
    }
    // Redirigir a la carga por OT directamente
    verDetallesOT(orden.ot);
}

async function cargarDetallesOT(ot) {
    try {
        console.log('Cargando detalles de OT:', ot);
        
        // Mostrar loading en el modal
        const cuerpoTabla = document.getElementById('cuerpoTablaDetalles');
        cuerpoTabla.innerHTML = '<tr><td colspan="6" class="text-center text-muted"><i class="fas fa-spinner fa-spin me-2"></i>Cargando códigos...</td></tr>';
        
        // Abrir modal de detalles mientras carga
        const modalDetalles = bootstrap.Modal.getOrCreateInstance(document.getElementById('modalDetallesOT'));
        modalDetalles.show();
        
        const response = await fetch(`/tecnicos/ordenes/detalle/${ot}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Datos recibidos:', data);
        
        if (data.success) {
            mostrarDetallesOT(data.data);
        } else {
            // Mostrar error en el modal
            cuerpoTabla.innerHTML = '<tr><td colspan="6" class="text-center text-danger"><i class="fas fa-exclamation-triangle me-2"></i>' + (data.error || 'Error al cargar detalles') + '</td></tr>';
        }
    } catch (error) {
        console.error('Error al cargar detalles de OT:', error);
        // Mostrar error en el modal
        const cuerpoTabla = document.getElementById('cuerpoTablaDetalles');
        cuerpoTabla.innerHTML = '<tr><td colspan="6" class="text-center text-danger"><i class="fas fa-exclamation-triangle me-2"></i>Error: ' + error.message + '</td></tr>';
    }
}

async function cargarDetallesOTById(id) {
    try {
        console.log('Cargando detalles de OT por ID:', id);
        
        // Mostrar loading en el modal
        const cuerpoTabla = document.getElementById('cuerpoTablaDetalles');
        cuerpoTabla.innerHTML = '<tr><td colspan="6" class="text-center text-muted"><i class="fas fa-spinner fa-spin me-2"></i>Cargando códigos...</td></tr>';
        
        // Abrir modal de detalles mientras carga
        const modalDetalles = bootstrap.Modal.getOrCreateInstance(document.getElementById('modalDetallesOT'));
        modalDetalles.show();
        
        // Primero obtener la OT desde la lista local
        const orden = ordenesTrabajo.find(o => o.id === id);
        if (!orden) {
            throw new Error('OT no encontrada en la lista local');
        }
        
        const response = await fetch(`/tecnicos/ordenes/detalle/${orden.ot}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Datos recibidos:', data);
        
        if (data.success) {
            mostrarDetallesOT(data.data);
        } else {
            // Mostrar error en el modal
            cuerpoTabla.innerHTML = '<tr><td colspan="6" class="text-center text-danger"><i class="fas fa-exclamation-triangle me-2"></i>' + (data.error || 'Error al cargar detalles') + '</td></tr>';
        }
    } catch (error) {
        console.error('Error al cargar detalles de OT por ID:', error);
        // Mostrar error en el modal
        const cuerpoTabla = document.getElementById('cuerpoTablaDetalles');
        cuerpoTabla.innerHTML = '<tr><td colspan="6" class="text-center text-danger"><i class="fas fa-exclamation-triangle me-2"></i>Error: ' + error.message + '</td></tr>';
    }
}

function mostrarDetallesOT(orden) {
    console.log('Mostrando detalles de OT:', orden);
    
    // Actualizar información general
    document.getElementById('modalDetallesOTLabel').textContent = `Detalles OT: ${orden.ot}`;
    document.getElementById('detalleOT').textContent = orden.ot || 'N/A';
    document.getElementById('detalleCuenta').textContent = orden.cuenta || 'N/A';
    document.getElementById('detalleServicio').textContent = orden.servicio || 'N/A';
    document.getElementById('detalleTecnico').textContent = orden.tecnico_nombre || 'N/A';
    document.getElementById('detalleTecnologia').textContent = orden.tecnologia || 'N/A';
    document.getElementById('detalleCategoria').textContent = orden.categoria || 'N/A';
    document.getElementById('detalleTotal').textContent = '$' + formatoMoneda(orden.total_valor || 0);
    document.getElementById('detalleFecha').textContent = orden.fecha_creacion || 'N/A';
    
    // Actualizar tabla de códigos
    const cuerpoTabla = document.getElementById('cuerpoTablaDetalles');
    
    if (orden.codigos && orden.codigos.length > 0) {
        cuerpoTabla.innerHTML = orden.codigos.map(codigo => `
            <tr>
                <td><strong>${codigo.codigo || ''}</strong></td>
                <td>${codigo.nombre || ''}</td>
                <td>${codigo.descripcion || ''}</td>
                <td class="text-center">${codigo.cantidad || 1}</td>
                <td class="text-end">$${formatoMoneda(codigo.valor_unitario || 0)}</td>
                <td class="text-end"><strong>$${formatoMoneda(codigo.valor_total || 0)}</strong></td>
            </tr>
        `).join('');
    } else {
        cuerpoTabla.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No hay códigos asociados a esta OT</td></tr>';
    }
}