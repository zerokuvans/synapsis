/* Debug de edición/eliminación de secciones en /lider/encuestas
Uso:
1) Asegúrate de incluir este archivo en la página de encuestas
   <script src="/static/js/debug_seccion_editar.js"></script>
2) En la consola del navegador, ejecuta:
   debugSecciones()
   - Muestra diagnóstico de botones y modal
   - Intercepta editarSeccion/eliminarSeccion para loguear actividad
3) Pruebas manuales desde consola:
   debugEditarSeccion(<id>)
   debugEliminarSeccion(<id>)
   debugPatchSeccion(<id>, { titulo: 'x', descripcion: 'y' })
*/
(function(){
  const log = (...args) => console.log('%c[DEBUG SECCIONES]', 'color:#0af;font-weight:bold;', ...args);
  const warn = (...args) => console.warn('%c[DEBUG SECCIONES]', 'color:#e67e22;font-weight:bold;', ...args);
  const error = (...args) => console.error('%c[DEBUG SECCIONES]', 'color:#e74c3c;font-weight:bold;', ...args);

  function getSectionButtons() {
    const edits = Array.from(document.querySelectorAll('button[onclick*="editarSeccion"], .btn[onclick*="editarSeccion"]'));
    const deletes = Array.from(document.querySelectorAll('button[onclick*="eliminarSeccion"], .btn[onclick*="eliminarSeccion"]'));
    return { edits, deletes };
  }

  function getSectionCards(){
    return Array.from(document.querySelectorAll('[data-seccion-id]'));
  }

  function parseOnclickId(btn){
    const attr = btn.getAttribute('onclick') || '';
    const m = attr.match(/\((\d+)\)/);
    return m ? Number(m[1]) : null;
  }

  function checkModal(){
    const modal = document.getElementById('modalEditarSeccion');
    const id = document.getElementById('editSeccionId');
    const titulo = document.getElementById('editSeccionTitulo');
    const desc = document.getElementById('editSeccionDescripcion');
    return { exists: !!modal, modal, idExists: !!id, tituloExists: !!titulo, descExists: !!desc };
  }

  async function safeJson(res){
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/json')) { return res.json(); }
    const txt = await res.text();
    return { success: false, nonJson: true, body: txt, status: res.status };
  }

  async function probeGetSeccion(id){
    log('GET /api/secciones/'+id);
    try {
      const res = await fetch('/api/secciones/'+id, { credentials: 'same-origin' });
      const data = await safeJson(res);
      log('GET status:', res.status, 'data:', data);
      if (res.status === 401 || res.status === 403) warn('Auth/CORS posible. Revisa sesión/CSRF.');
      if (res.status === 404) warn('Sección no encontrada. ¿ID correcto?');
      if (res.status >= 500) error('Error servidor. Revisa logs backend.');
      return { res, data };
    } catch (e){ error('GET fallo:', e); return { error: e }; }
  }

  async function probeDeleteSeccion(id){
    log('DELETE /api/secciones/'+id);
    try {
      const res = await fetch('/api/secciones/'+id, { method:'DELETE', headers:{'Content-Type':'application/json'}, credentials:'same-origin' });
      const data = await safeJson(res);
      log('DELETE status:', res.status, 'data:', data);
      return { res, data };
    } catch (e){ error('DELETE fallo:', e); return { error: e }; }
  }

  async function probePatchSeccion(id, payload){
    log('PATCH /api/secciones/'+id, payload);
    try {
      const res = await fetch('/api/secciones/'+id, { method:'PATCH', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload||{}), credentials:'same-origin' });
      const data = await safeJson(res);
      log('PATCH status:', res.status, 'data:', data);
      return { res, data };
    } catch (e){ error('PATCH fallo:', e); return { error: e }; }
  }

  function interceptFunctions(){
    try {
      const hasEditar = typeof window.editarSeccion === 'function';
      const hasEliminar = typeof window.eliminarSeccion === 'function';
      log('Funciones globales:', { editarSeccion: hasEditar, eliminarSeccion: hasEliminar });

      if (hasEditar && !window.__orig_editarSeccion){
        window.__orig_editarSeccion = window.editarSeccion;
        window.editarSeccion = async function(id){
          log('Intercept editarSeccion -> id:', id);
          try {
            const r = await probeGetSeccion(id);
            log('Pre-modal data:', r);
          } catch(e){ error('Intercept GET previo al modal falló:', e); }
          try {
            return await window.__orig_editarSeccion(id);
          } catch(e){ error('editarSeccion original arrojó error:', e); throw e; }
        };
      }

      if (hasEliminar && !window.__orig_eliminarSeccion){
        window.__orig_eliminarSeccion = window.eliminarSeccion;
        window.eliminarSeccion = async function(id){
          log('Intercept eliminarSeccion -> id:', id);
          try { await probeDeleteSeccion(id); } catch(e){ error('Probe DELETE falló:', e); }
          try { return await window.__orig_eliminarSeccion(id); } catch(e){ error('eliminarSeccion original arrojó error:', e); throw e; }
        };
      }
    } catch(e){ error('InterceptFunctions error:', e); }
  }

  function diagnose(){
    log('Iniciando diagnóstico de secciones...');
    const { edits, deletes } = getSectionButtons();
    const cards = getSectionCards();
    const modalInfo = checkModal();

    log('Botones editar:', edits.length, 'Botones eliminar:', deletes.length, 'Cards:', cards.length);
    if (!modalInfo.exists) warn('Modal #modalEditarSeccion NO existe en el DOM');
    if (!modalInfo.idExists || !modalInfo.tituloExists) warn('Inputs del modal faltan: {id,titulo,descripcion}', modalInfo);

    // Adjuntar listeners de prueba
    edits.forEach((btn, idx)=>{
      const id = parseOnclickId(btn);
      btn.addEventListener('click', ()=> log('Click EDIT (btn '+idx+') id=', id));
    });
    deletes.forEach((btn, idx)=>{
      const id = parseOnclickId(btn);
      btn.addEventListener('click', ()=> log('Click DELETE (btn '+idx+') id=', id));
    });

    interceptFunctions();
    log('Diagnóstico listo. Usa debugEditarSeccion(id) / debugEliminarSeccion(id) / debugPatchSeccion(id, payload).');
  }

  // API pública para consola
  window.debugSecciones = diagnose;
  window.debugEditarSeccion = probeGetSeccion;
  window.debugEliminarSeccion = probeDeleteSeccion;
  window.debugPatchSeccion = probePatchSeccion;
})();