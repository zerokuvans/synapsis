# Resumen de Reorganización de Archivos

Este documento registra el resultado de la reorganización de archivos realizada en el proyecto. Sirve como referencia para entender qué se movió, qué estructura se creó y qué archivos críticos permanecen en la raíz.

## Objetivo
- Organizar scripts, diagnósticos, pruebas y utilidades en una estructura más clara.
- Mantener archivos críticos y directorios clave en la raíz para no afectar el arranque de la aplicación.

## Resultados
- Simulación: 310 archivos candidatos para mover.
- Ejecución real: 308 archivos movidos exitosamente.
- Incidencia: 1 archivo no encontrado durante el movimiento (`completar_migracion_poliza.py`).
- Se creó la carpeta `organizacion/` y se ubicaron allí los documentos y scripts relacionados al plan de reorganización.

## Estructura creada/normalizada
Se crearon y/o poblaron las siguientes carpetas, moviendo archivos según su propósito:
- `check/`: scripts de verificación y chequeos temporales.
- `data/`: datos, insumos y archivos de soporte.
- `debug/`: scripts y utilidades para depuración.
- `diagnosticos/`: diagnósticos de MySQL, formularios y procesos.
- `docs/`: documentación técnica y funcional (se contempla `docs/tech/` para documentos técnicos específicos).
- `fix/`: scripts de corrección y parches.
- `organizacion/`: documentos y scripts del plan de reorganización.
- `scripts/utils/`: utilidades y helpers.
- `test/`: pruebas automatizadas y scripts de test.
- `verificar/`: verificaciones finales y validaciones.

## Archivos críticos en la raíz
Se mantuvieron en la raíz para asegurar el correcto arranque y operación:
- `.env.example`
- `app.py`
- `main.py`
- `requirements.txt`
- `README.md`
- `templates/`
- `static/`
- `migrations/`
- `sql/`
- `supabase/`
- `triggers/`

Otros archivos funcionales (por ejemplo: `models.py`, `utils.py`, algunos scripts de integración y migración) también permanecen o fueron ubicados de forma segura para no romper dependencias.

## Documentos y scripts del plan de reorganización
Ubicados en `organizacion/`:
- `PLAN_REORGANIZACION_ARCHIVOS.md`
- `reorganizar_archivos.py`
- `reorganizar_archivos_seguro.py`

## Incidencias conocidas
- `completar_migracion_poliza.py` no se encontró al intentar moverlo; no existe en el repositorio.

## Recomendaciones posteriores
- Ejecutar `python main.py` para confirmar que el servidor Flask inicia correctamente.
- Correr pruebas desde `test/` para detectar posibles imports rotos.
- Si aparecen errores de importación, ajustar rutas relativas o `PYTHONPATH` según corresponda.

---
Última actualización: generada automáticamente tras la reorganización.