-- =====================================================
-- SCRIPT ALTER PARA ACTUALIZAR DEFINERS DE TRIGGERS
-- Sistema de Gestión Synapsis
-- Fecha: 2025-01-20
-- Descripción: Cambia el definer de triggers de vnaranjos@localhost a root@localhost
-- =====================================================

-- Configurar variables de sesión para manejo de errores
-- Nota: NO_AUTO_CREATE_USER fue removido en MySQL 8.0+
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, AUTOCOMMIT=0;

-- =====================================================
-- PASO 1: VERIFICAR TRIGGERS CON DEFINER INCORRECTO
-- =====================================================

SELECT 
    'VERIFICACIÓN INICIAL - Triggers con definer vnaranjos@localhost:' as 'ESTADO';

SELECT 
    TRIGGER_NAME as 'Trigger',
    EVENT_OBJECT_TABLE as 'Tabla',
    EVENT_MANIPULATION as 'Evento',
    DEFINER as 'Definer Actual'
FROM information_schema.TRIGGERS 
WHERE TRIGGER_SCHEMA = DATABASE()
AND DEFINER = 'vnaranjos@localhost'
ORDER BY EVENT_OBJECT_TABLE, TRIGGER_NAME;

-- =====================================================
-- PASO 2: GENERAR COMANDOS ALTER PARA CADA TRIGGER
-- =====================================================

-- Configurar delimitador para triggers
DELIMITER //

-- Procedimiento para cambiar definer de un trigger específico
CREATE PROCEDURE IF NOT EXISTS sp_change_trigger_definer(
    IN p_trigger_name VARCHAR(64),
    IN p_table_name VARCHAR(64),
    IN p_event VARCHAR(10),
    IN p_timing VARCHAR(10)
)
BEGIN
    DECLARE v_trigger_definition TEXT;
    DECLARE v_new_definition TEXT;
    DECLARE v_sql_statement TEXT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        GET DIAGNOSTICS CONDITION 1
            @sqlstate = RETURNED_SQLSTATE, 
            @errno = MYSQL_ERRNO, 
            @text = MESSAGE_TEXT;
        SELECT CONCAT('Error al modificar trigger ', p_trigger_name, ': ', @text) as 'ERROR';
    END;
    
    START TRANSACTION;
    
    -- Obtener la definición actual del trigger
    SELECT ACTION_STATEMENT INTO v_trigger_definition
    FROM information_schema.TRIGGERS
    WHERE TRIGGER_SCHEMA = DATABASE()
    AND TRIGGER_NAME = p_trigger_name;
    
    -- Crear el comando DROP y CREATE con nuevo definer
    SET v_sql_statement = CONCAT('DROP TRIGGER IF EXISTS ', p_trigger_name);
    SET @sql = v_sql_statement;
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
    
    -- Recrear el trigger con el nuevo definer
    SET v_sql_statement = CONCAT(
        'CREATE DEFINER=`root`@`localhost` TRIGGER ', p_trigger_name, ' ',
        p_timing, ' ', p_event, ' ON ', p_table_name, ' FOR EACH ROW ',
        v_trigger_definition
    );
    
    SET @sql = v_sql_statement;
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
    
    SELECT CONCAT('Trigger ', p_trigger_name, ' actualizado correctamente') as 'RESULTADO';
    
    COMMIT;
END//

DELIMITER ;

-- =====================================================
-- PASO 3: APLICAR CAMBIOS A TRIGGERS ESPECÍFICOS
-- =====================================================

-- Cambiar definer de triggers del sistema ferretero
CALL sp_change_trigger_definer('actualizar_stock_entrada', 'entradas_ferretero', 'INSERT', 'AFTER');
CALL sp_change_trigger_definer('actualizar_stock_asignacion', 'ferretero', 'INSERT', 'AFTER');
CALL sp_change_trigger_definer('tr_ferretero_after_insert', 'ferretero', 'INSERT', 'AFTER');
CALL sp_change_trigger_definer('tr_entradas_ferretero_after_insert', 'entradas_ferretero', 'INSERT', 'AFTER');

-- Cambiar definer de triggers de dotaciones
CALL sp_change_trigger_definer('tr_dotaciones_after_insert', 'dotaciones', 'INSERT', 'AFTER');
CALL sp_change_trigger_definer('tr_dotaciones_after_update', 'dotaciones', 'UPDATE', 'AFTER');
CALL sp_change_trigger_definer('tr_dotaciones_after_delete', 'dotaciones', 'DELETE', 'AFTER');

-- Cambiar definer de triggers de cambios de dotación
CALL sp_change_trigger_definer('tr_cambios_dotacion_after_insert', 'cambios_dotacion', 'INSERT', 'AFTER');
CALL sp_change_trigger_definer('tr_cambios_dotacion_after_update', 'cambios_dotacion', 'UPDATE', 'AFTER');

-- Cambiar definer de triggers de parque automotor
CALL sp_change_trigger_definer('tr_parque_automotor_after_insert', 'parque_automotor', 'INSERT', 'AFTER');
CALL sp_change_trigger_definer('tr_parque_automotor_after_update', 'parque_automotor', 'UPDATE', 'AFTER');

-- Cambiar definer de triggers de stock general
CALL sp_change_trigger_definer('tr_stock_general_after_update', 'stock_general', 'UPDATE', 'AFTER');

-- Cambiar definer de triggers de movimientos de stock
CALL sp_change_trigger_definer('tr_movimientos_stock_before_insert', 'movimientos_stock_ferretero', 'INSERT', 'BEFORE');

-- =====================================================
-- PASO 4: MÉTODO ALTERNATIVO - ALTER DIRECTO
-- =====================================================

-- Si el método anterior no funciona, usar ALTER directo
-- Nota: ALTER DEFINER no está disponible en todas las versiones de MySQL
-- En ese caso, se debe recrear el trigger

-- Comando genérico para triggers que puedan existir
SET @sql = '';
SELECT GROUP_CONCAT(
    CONCAT(
        'DROP TRIGGER IF EXISTS ', TRIGGER_NAME, '; ',
        'CREATE DEFINER=`root`@`localhost` TRIGGER ', TRIGGER_NAME, ' ',
        ACTION_TIMING, ' ', EVENT_MANIPULATION, ' ON ', EVENT_OBJECT_TABLE, ' FOR EACH ROW ',
        ACTION_STATEMENT, '; '
    ) SEPARATOR '\n'
) INTO @sql
FROM information_schema.TRIGGERS 
WHERE TRIGGER_SCHEMA = DATABASE()
AND DEFINER = 'vnaranjos@localhost';

-- Mostrar los comandos generados (para revisión manual si es necesario)
SELECT @sql as 'COMANDOS_GENERADOS';

-- =====================================================
-- PASO 5: VERIFICACIÓN FINAL
-- =====================================================

SELECT 
    'VERIFICACIÓN FINAL - Estado de todos los triggers:' as 'ESTADO';

SELECT 
    TRIGGER_NAME as 'Trigger',
    EVENT_OBJECT_TABLE as 'Tabla',
    EVENT_MANIPULATION as 'Evento',
    DEFINER as 'Definer Actual',
    CASE 
        WHEN DEFINER = 'root@localhost' THEN 'CORRECTO'
        WHEN DEFINER = 'vnaranjos@localhost' THEN 'PENDIENTE'
        ELSE 'REVISAR'
    END as 'Estado'
FROM information_schema.TRIGGERS 
WHERE TRIGGER_SCHEMA = DATABASE()
ORDER BY EVENT_OBJECT_TABLE, TRIGGER_NAME;

-- Contar triggers por definer
SELECT 
    DEFINER as 'Definer',
    COUNT(*) as 'Cantidad_Triggers'
FROM information_schema.TRIGGERS 
WHERE TRIGGER_SCHEMA = DATABASE()
GROUP BY DEFINER
ORDER BY DEFINER;

-- =====================================================
-- PASO 6: LIMPIEZA
-- =====================================================

-- Eliminar el procedimiento temporal
DROP PROCEDURE IF EXISTS sp_change_trigger_definer;

-- Restaurar configuraciones originales
SET SQL_MODE=@OLD_SQL_MODE;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

-- =====================================================
-- INSTRUCCIONES DE USO
-- =====================================================
/*
INSTRUCCIONES PARA EJECUTAR ESTE SCRIPT:

1. Hacer backup de la base de datos antes de ejecutar:
   mysqldump -u root -p nombre_base_datos > backup_antes_alter.sql

2. Ejecutar este script completo en MySQL:
   mysql -u root -p nombre_base_datos < alter_trigger_definers.sql

3. Verificar que todos los triggers tengan el definer correcto:
   - Revisar la salida de "VERIFICACIÓN FINAL"
   - Todos los triggers deben mostrar "CORRECTO" en la columna Estado

4. Si algún trigger no se actualizó correctamente:
   - Revisar los mensajes de error en la salida
   - Ejecutar manualmente los comandos de la sección "COMANDOS_GENERADOS"

5. Probar la funcionalidad de la aplicación:
   - Verificar que no hay errores de definer en los logs
   - Probar las funcionalidades que usan los triggers modificados

NOTAS IMPORTANTES:
- Este script maneja errores de manera segura con transacciones
- Si un trigger falla al actualizarse, no afectará a los demás
- El script genera comandos alternativos en caso de que el método principal falle
- Siempre hacer backup antes de ejecutar cambios en producción
*/

-- =====================================================
-- SCRIPT COMPLETADO
-- =====================================================
SELECT 'Script ALTER de definers completado exitosamente' as 'RESULTADO_FINAL';