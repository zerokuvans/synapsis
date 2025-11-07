# Migración de técnico en mpa_mantenimientos

Objetivo: guardar nombres de técnico (no IDs) en `mpa_mantenimientos.tecnico` y crear triggers que lo garanticen en futuras inserciones/actualizaciones.

## Contenido
- SQL de migración y triggers: `sql/mpa_mantenimientos_tecnico_name_migration.sql`
- Runner Python: `migraciones/run_mpa_tecnico_migration.py`

## Ejecución
1. Asegura credenciales en variables de entorno (opcional) o usa las por defecto:
   - `MYSQL_HOST=localhost`
   - `MYSQL_USER=root`
   - `MYSQL_PASSWORD=732137A031E4b@`
   - `MYSQL_DB=capired`
2. Ejecuta el runner:
   - `python migraciones/run_mpa_tecnico_migration.py`

## Qué hace
- Normaliza históricos: si `mpa_mantenimientos.tecnico` contiene un número (UID), lo reemplaza por el `nombre` de `recurso_operativo`.
- Crea triggers `BEFORE INSERT` y `BEFORE UPDATE` para convertir cualquier UID entrante al `nombre` correspondiente.

## Verificación
- Confirmar triggers:
  - `SELECT TRIGGER_NAME, EVENT_MANIPULATION FROM INFORMATION_SCHEMA.TRIGGERS WHERE EVENT_OBJECT_TABLE = 'mpa_mantenimientos';`
- Validar datos recientes:
  - `SELECT id_mpa_mantenimientos, placa, tecnico FROM mpa_mantenimientos ORDER BY id_mpa_mantenimientos DESC LIMIT 10;`

## Notas
- Si un vehículo no tiene técnico asignado o el UID no existe en `recurso_operativo`, el valor original permanece.
- El frontend ya envía el `tecnico` como nombre tomado de la placa (`data-tecnico`). Los triggers actúan como salvaguarda adicional.