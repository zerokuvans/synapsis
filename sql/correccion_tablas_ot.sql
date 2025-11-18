-- Correcciones de tablas para Órdenes de Trabajo (OT)
-- Objetivo:
-- 1) Eliminar columna duplicada/innecesaria `tecnicos` en `gestion_ot_tecnicos`
-- 2) Eliminar columna innecesaria `gestion_ot_tecnicos_historialcol` en `gestion_ot_tecnicos_historial`
-- 3) Corregir typo `descipcion` -> `descripcion` en `gestion_ot_tecnicos_historial`
-- 4) Agregar llaves foráneas apropiadas
-- 5) Ajustar tipos de datos y NOT NULL donde corresponda

-- NOTA: Ajusta el nombre del esquema/BD si es necesario antes de ejecutar.
-- Este script asume MySQL 8+.

-- =============================
-- Tabla: gestion_ot_tecnicos
-- =============================
ALTER TABLE `gestion_ot_tecnicos`
  DROP COLUMN `tecnicos`;

-- Asegurar tipos y restricciones clave
ALTER TABLE `gestion_ot_tecnicos`
  MODIFY COLUMN `ot` VARCHAR(7) NOT NULL,
  MODIFY COLUMN `cuenta` VARCHAR(8) NOT NULL,
  MODIFY COLUMN `servicio` VARCHAR(7) NOT NULL,
  MODIFY COLUMN `codigo` VARCHAR(50) NOT NULL,
  MODIFY COLUMN `tecnologia` VARCHAR(50) NOT NULL,
  MODIFY COLUMN `agrupacion` VARCHAR(50) NOT NULL,
  MODIFY COLUMN `nombre` VARCHAR(255) NOT NULL,
  MODIFY COLUMN `observacion` VARCHAR(255) NULL,
  MODIFY COLUMN `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  MODIFY COLUMN `id_codigo_consumidor` INT NOT NULL,
  MODIFY COLUMN `cantidad` INT NOT NULL DEFAULT 0,
  MODIFY COLUMN `valor` INT NOT NULL DEFAULT 0,
  MODIFY COLUMN `descripcion` VARCHAR(255) NOT NULL;

-- Índice para FK (si no existe)
CREATE INDEX `idx_got_codigo_consumidor` ON `gestion_ot_tecnicos` (`id_codigo_consumidor`);

-- Llave foránea hacia recurso_operativo
ALTER TABLE `gestion_ot_tecnicos`
  ADD CONSTRAINT `fk_got_recurso_operativo`
    FOREIGN KEY (`id_codigo_consumidor`)
    REFERENCES `recurso_operativo` (`id_codigo_consumidor`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT;

-- =============================
-- Tabla: gestion_ot_tecnicos_historial
-- =============================
ALTER TABLE `gestion_ot_tecnicos_historial`
  DROP COLUMN `gestion_ot_tecnicos_historialcol`;

-- Corregir nombre de columna con typo
ALTER TABLE `gestion_ot_tecnicos_historial`
  CHANGE COLUMN `descipcion` `descripcion` VARCHAR(255) NULL;

-- Asegurar tipos y restricciones clave en historial
ALTER TABLE `gestion_ot_tecnicos_historial`
  MODIFY COLUMN `ot` VARCHAR(7) NOT NULL,
  MODIFY COLUMN `cuenta` VARCHAR(8) NOT NULL,
  MODIFY COLUMN `servicio` VARCHAR(7) NOT NULL,
  MODIFY COLUMN `codigo` VARCHAR(50) NOT NULL,
  MODIFY COLUMN `tecnologia` VARCHAR(50) NOT NULL,
  MODIFY COLUMN `agrupacion` VARCHAR(50) NOT NULL,
  MODIFY COLUMN `nombre` VARCHAR(255) NOT NULL,
  MODIFY COLUMN `observacion` VARCHAR(255) NULL,
  MODIFY COLUMN `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  MODIFY COLUMN `id_codigo_consumidor` INT NOT NULL,
  MODIFY COLUMN `cantidad` INT NOT NULL DEFAULT 0,
  MODIFY COLUMN `valor` INT NOT NULL DEFAULT 0,
  MODIFY COLUMN `descripcion` VARCHAR(255) NULL;

-- Índice para FK (si no existe)
CREATE INDEX `idx_got_hist_codigo_consumidor` ON `gestion_ot_tecnicos_historial` (`id_codigo_consumidor`);

-- Llave foránea hacia recurso_operativo
ALTER TABLE `gestion_ot_tecnicos_historial`
  ADD CONSTRAINT `fk_got_hist_recurso_operativo`
    FOREIGN KEY (`id_codigo_consumidor`)
    REFERENCES `recurso_operativo` (`id_codigo_consumidor`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT;

-- Fin del script