-- Migración: Normalizar técnico en mpa_mantenimientos y crear triggers para guardar nombres
-- Base de datos objetivo: capired

-- 1) Normalizar históricos: reemplazar IDs numéricos en mpa_mantenimientos.tecnico por nombres de recurso_operativo
UPDATE mpa_mantenimientos m
JOIN (
  SELECT id_mpa_mantenimientos AS id_mm, CAST(tecnico AS UNSIGNED) AS tecnico_uid
  FROM mpa_mantenimientos
  WHERE tecnico REGEXP '^[0-9]+$'
) mm ON mm.id_mm = m.id_mpa_mantenimientos
JOIN recurso_operativo ro
  ON CAST(ro.id_codigo_consumidor AS UNSIGNED) = mm.tecnico_uid
SET m.tecnico = ro.nombre;

-- 2) Asegurar que futuras inserciones/actualizaciones siempre guarden nombres
DROP TRIGGER IF EXISTS mpa_mantenimientos_bi_name;
DROP TRIGGER IF EXISTS mpa_mantenimientos_bu_name;

DELIMITER //
CREATE TRIGGER mpa_mantenimientos_bi_name
BEFORE INSERT ON mpa_mantenimientos
FOR EACH ROW
BEGIN
  DECLARE v_nombre VARCHAR(255);
  SET v_nombre = NULL;
  -- Si llega un UID numérico, convertir a nombre desde recurso_operativo
  IF NEW.tecnico REGEXP '^[0-9]+$' THEN
    SELECT ro.nombre INTO v_nombre
    FROM recurso_operativo ro
    WHERE CAST(ro.id_codigo_consumidor AS UNSIGNED) = CAST(NEW.tecnico AS UNSIGNED)
    LIMIT 1;
    IF v_nombre IS NOT NULL THEN
      SET NEW.tecnico = v_nombre;
    END IF;
  END IF;
END//

CREATE TRIGGER mpa_mantenimientos_bu_name
BEFORE UPDATE ON mpa_mantenimientos
FOR EACH ROW
BEGIN
  DECLARE v_nombreU VARCHAR(255);
  SET v_nombreU = NULL;
  -- Si llega un UID numérico, convertir a nombre desde recurso_operativo
  IF NEW.tecnico REGEXP '^[0-9]+$' THEN
    SELECT ro.nombre INTO v_nombreU
    FROM recurso_operativo ro
    WHERE CAST(ro.id_codigo_consumidor AS UNSIGNED) = CAST(NEW.tecnico AS UNSIGNED)
    LIMIT 1;
    IF v_nombreU IS NOT NULL THEN
      SET NEW.tecnico = v_nombreU;
    END IF;
  END IF;
END//
DELIMITER ;

-- 3) Validaciones rápidas (opcionales)
-- SELECT TRIGGER_NAME, EVENT_MANIPULATION FROM INFORMATION_SCHEMA.TRIGGERS WHERE EVENT_OBJECT_TABLE = 'mpa_mantenimientos';
-- SELECT id_mpa_mantenimientos, placa, tecnico FROM mpa_mantenimientos ORDER BY id_mpa_mantenimientos DESC LIMIT 10;