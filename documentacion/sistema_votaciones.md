# Sistema de Votaciones

## Objetivo
Permitir crear encuestas de tipo "votación", gestionar candidatos, registrar un voto por usuario y visualizar resultados parciales.

## Flujo para Administradores
- Crear encuesta: `Líder > Encuestas > Crear encuesta`.
- Convertir a votación: editar la encuesta y establecer `Tipo = Votación`.
- Configurar:
  - `Mostrar resultados`: habilita panel de resultados para usuarios.
  - `Fecha inicio/fin de votación`: ventana de votación.
  - `Dirigida a`: define audiencia; para técnicos, puede filtrar por carpetas/supervisores/técnicos.
- Gestionar candidatos: usar UI o API `/api/votaciones/<id>/candidatos`.

## Flujo para Usuarios
- Al iniciar sesión, si hay votaciones activas dirigidas a usted, aparece el modal `Votaciones activas` en el header.
- Puede votar por un candidato. Si ya votó, el sistema no permite votar de nuevo.
- Si `mostrar_resultados` está activo, ve el gráfico con conteos parciales en el modal.

## APIs Principales
- `POST /api/encuestas`: crea una encuesta.
- `PATCH /api/encuestas/<id>`: actualiza campos (incluye `tipo_encuesta`, `mostrar_resultados`, `fecha_inicio_votacion`, `fecha_fin_votacion`).
- `POST /api/votaciones/<id>/candidatos`: crea candidato.
- `GET /api/votaciones/<id>/candidatos`: lista candidatos.
- `DELETE /api/votaciones/<id>/candidatos/<id_candidato>`: elimina candidato.
- `POST /api/votaciones/<id>/votar`: registra voto (requiere usuario autenticado y FK en `usuarios`).
- `GET /api/votaciones/<id>/resultados`: resultados por candidato (solo si `mostrar_resultados` es verdadero).

## Validaciones y Reglas
- Único voto por usuario: `UNIQUE (id_encuesta, id_usuario)` en `votos`.
- Ventana de votación: respeta `fecha_inicio_votacion` y `fecha_fin_votacion`.
- Resultados visibles solo si `mostrar_resultados = true`.

## Pruebas Automatizadas
- Ejecutar `python test/test_votaciones_completo.py` con el servidor activo.
- Variables útiles: `BASE_URL`, `ADMIN_USER`, `ADMIN_PASS`, `USER_USER`, `USER_PASS`.
- El test crea encuesta, convierte a votación, añade candidatos, inicia sesión, vota y consulta resultados.

## Solución de Problemas
- No se puede votar: asegure que el usuario tenga fila en `usuarios` (`idusuarios` coincide con la sesión). El test crea una fila mínima si falta.
- PATCH devuelve "No hay campos para actualizar": use el fallback directo a DB (ya implementado en verificación) o verifique que el cuerpo incluye campos válidos.
- No aparecen votaciones en UI: revisar `/api/encuestas/activas/para-mi` y criterios de audiencia/fechas.

## Referencias
- Código: `encuestas_api.py` (endpoints), `templates/header.html` (UI votaciones).
- Migración: `migraciones/migration_votaciones_init.py`.
- Verificación: `verificar/verificacion_sistema_votaciones.py`.