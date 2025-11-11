# Uso del Sistema de Votaciones

Este documento explica cómo crear y gestionar votaciones (encuestas de tipo "votación") y cómo los usuarios participan y consultan resultados.

## Para Administradores
- Crear encuesta base: en `Líder > Encuestas`, botón `Crear encuesta`. Complete título, descripción y estado `Activa`.
- Convertir a votación: edite la encuesta y seleccione `Tipo = Votación`.
- Configurar opciones:
  - `Mostrar resultados`: habilita que los usuarios vean resultados parciales.
  - `Fecha inicio/fin de votación`: acota el periodo para votar.
  - `Dirigida a`: defina la audiencia (todos, técnicos, analistas, supervisores). Para técnicos, puede filtrar por carpetas/supervisores/técnicos.
- Gestionar candidatos: use `Gestionar candidatos` para agregar nombre, descripción, foto y orden. Los candidatos se crean vía API (`/api/votaciones/<encuesta_id>/candidatos`).
- Validaciones clave:
  - Las votaciones requieren `tipo_encuesta = votacion`.
  - Un usuario solo puede votar una vez por encuesta (`UNIQUE (id_encuesta, id_usuario)`).
  - Solo se muestran resultados si `mostrar_resultados = true`.

## Para Usuarios
- Visualización: al iniciar sesión, si hay votaciones activas dirigidas a usted, aparece el modal `Votaciones activas` en el header.
- Votar: seleccione un candidato y confirme. Si el periodo no ha iniciado o ya finalizó, el botón aparecerá deshabilitado.
- Resultados: si la votación permite mostrar resultados, verá gráficos y conteos parciales (Chart.js integrado en `header.html`).

## APIs Relevantes
- `POST /api/encuestas`: crea una encuesta.
- `PATCH /api/encuestas/<id>`: actualiza campos, incluido `tipo_encuesta`, `mostrar_resultados`, `fecha_inicio_votacion`, `fecha_fin_votacion`.
- `POST /api/votaciones/<id>/candidatos`: crea candidato.
- `GET /api/votaciones/<id>/candidatos`: lista candidatos.
- `DELETE /api/votaciones/<id>/candidatos/<id_candidato>`: elimina candidato.
- `POST /api/votaciones/<id>/votar`: registra voto del usuario autenticado.
- `GET /api/votaciones/<id>/resultados`: retorna conteo por candidato (solo si `mostrar_resultados = true`).

## Solución de Problemas Comunes
- No aparecen votaciones en el header:
  - Verifique que la encuesta esté `activa` y en ventana de fechas.
  - Confirme `dirigida_a` y filtros aplicados; que el usuario pertenezca a la audiencia.
  - Revise terminal del servidor por errores en `/api/encuestas/activas/para-mi`.
- Error al votar: "Ya existe un voto para este usuario":
  - La restricción única impide votos múltiples. Verifique si ya votó o si el usuario de prueba está repetido.
- No se muestran resultados:
  - Habilite `mostrar_resultados` y asegure que existan candidatos y al menos un voto.
  - Revise el endpoint `/api/votaciones/<id>/resultados` y la consola del navegador.

## Verificación Automatizada
- Ejecute `python verificar/verificacion_sistema_votaciones.py` con el servidor activo.
- Variables de entorno útiles: `BASE_URL`, `ADMIN_USER`, `ADMIN_PASS`, `USER_USER`, `USER_PASS`.
- El script valida el esquema, crea una votación, añade candidatos, registra un voto y consulta resultados.

## Notas
- Chart.js se integra en `templates/header.html` para visualización de resultados.
- Las migraciones iniciales están en `migraciones/migration_votaciones_init.py` y verificación en `verificar/verificar_votaciones_schema.py`.