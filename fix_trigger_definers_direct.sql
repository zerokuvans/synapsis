-- Script para corregir definers de triggers de 'vnaranjos@localhost' a 'root@localhost'
-- Generado automáticamente

-- Configurar sesión
SET SESSION sql_mode = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
SET SESSION foreign_key_checks = 0;
SET SESSION unique_checks = 0;

-- Verificación inicial
SELECT 'VERIFICACIÓN INICIAL - Triggers con definer incorrecto:' AS ESTADO;
SELECT TRIGGER_NAME, EVENT_OBJECT_TABLE, DEFINER 
FROM information_schema.TRIGGERS 
WHERE TRIGGER_SCHEMA = 'capired' AND DEFINER = 'vnaranjos@localhost'
ORDER BY EVENT_OBJECT_TABLE, TRIGGER_NAME;

-- Cambiar delimitador
DELIMITER $$

-- Iniciar transacción
START TRANSACTION$$

-- Corregir trigger: actualizar_stock_entrada_ferretero
DROP TRIGGER IF EXISTS actualizar_stock_entrada_ferretero$$
CREATE DEFINER=`root`@`localhost` TRIGGER actualizar_stock_entrada_ferretero
    AFTER INSERT ON entradas_ferretero
    FOR EACH ROW BEGIN
    UPDATE stock_general 
    SET cantidad_disponible = cantidad_disponible + NEW.cantidad_entrada,
        fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE codigo_material = NEW.material_tipo;
    
    INSERT INTO eventos_sistema (tipo, mensaje)
    VALUES (
        'ENTRADA_FERRETERO',
        CONCAT('Entrada ferretero: ', NEW.cantidad_entrada, ' unidades de ', NEW.material_tipo)
    );
END$$

-- Corregir trigger: actualizar_stock_entrada_general
DROP TRIGGER IF EXISTS actualizar_stock_entrada_general$$
CREATE DEFINER=`root`@`localhost` TRIGGER actualizar_stock_entrada_general
    AFTER INSERT ON entradas_stock
    FOR EACH ROW BEGIN
    UPDATE stock_general 
    SET cantidad_disponible = cantidad_disponible + NEW.cantidad_ingresada,
        fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE codigo_material = NEW.material;
    
    INSERT INTO eventos_sistema (tipo, mensaje)
    VALUES (
        'ENTRADA_STOCK',
        CONCAT('Entrada stock: ', NEW.cantidad_ingresada, ' unidades de ', NEW.material)
    );
END$$

-- Corregir trigger: actualizar_stock_asignacion
DROP TRIGGER IF EXISTS actualizar_stock_asignacion$$
CREATE DEFINER=`root`@`localhost` TRIGGER actualizar_stock_asignacion
    AFTER INSERT ON ferretero
    FOR EACH ROW BEGIN
    IF NEW.silicona > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.silicona,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE codigo_material = 'silicona';
    END IF;
    
    IF NEW.grapas_negras > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.grapas_negras,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE codigo_material = 'grapas_negras';
    END IF;
    
    IF NEW.grapas_blancas > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.grapas_blancas,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE codigo_material = 'grapas_blancas';
    END IF;
    
    IF NEW.amarres_negros > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.amarres_negros,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE codigo_material = 'amarres_negros';
    END IF;
    
    IF NEW.amarres_blancos > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.amarres_blancos,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE codigo_material = 'amarres_blancos';
    END IF;
    
    IF NEW.cinta_aislante > 0 THEN
        UPDATE stock_general 
        SET cantidad_disponible = cantidad_disponible - NEW.cinta_aislante,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE codigo_material = 'cinta_aislante';
    END IF;
END$$

-- Corregir trigger: tr_parque_automotor_historial_insert_v2
DROP TRIGGER IF EXISTS tr_parque_automotor_historial_insert_v2$$
CREATE DEFINER=`root`@`localhost` TRIGGER tr_parque_automotor_historial_insert_v2
    AFTER INSERT ON parque_automotor
    FOR EACH ROW BEGIN
    INSERT INTO parque_automotor_historial (
        id_parque_automotor,
        accion,
        campo_modificado,
        valor_anterior,
        valor_nuevo,
        fecha_modificacion,
        usuario_modificacion
    ) VALUES (
        NEW.id_parque_automotor,
        'INSERT',
        'REGISTRO_COMPLETO',
        NULL,
        CONCAT('Nuevo vehículo registrado: ', NEW.placa),
        NOW(),
        USER()
    );
END$$

-- Corregir trigger: tr_parque_automotor_historial_insert_v3
DROP TRIGGER IF EXISTS tr_parque_automotor_historial_insert_v3$$
CREATE DEFINER=`root`@`localhost` TRIGGER tr_parque_automotor_historial_insert_v3
    AFTER INSERT ON parque_automotor
    FOR EACH ROW BEGIN
    INSERT INTO parque_automotor_historial (
        id_parque_automotor,
        accion,
        campo_modificado,
        valor_anterior,
        valor_nuevo,
        fecha_modificacion,
        usuario_modificacion
    ) VALUES (
        NEW.id_parque_automotor,
        'INSERT',
        'REGISTRO_COMPLETO',
        NULL,
        CONCAT('Nuevo vehículo registrado: ', NEW.placa, ' - Marca: ', NEW.marca, ' - Modelo: ', NEW.modelo),
        NOW(),
        USER()
    );
END$$

-- Corregir trigger: tr_parque_automotor_historial_update_v2
DROP TRIGGER IF EXISTS tr_parque_automotor_historial_update_v2$$
CREATE DEFINER=`root`@`localhost` TRIGGER tr_parque_automotor_historial_update_v2
    AFTER UPDATE ON parque_automotor
    FOR EACH ROW BEGIN
    IF OLD.placa != NEW.placa THEN
        INSERT INTO parque_automotor_historial (id_parque_automotor, accion, campo_modificado, valor_anterior, valor_nuevo, fecha_modificacion, usuario_modificacion)
        VALUES (NEW.id_parque_automotor, 'UPDATE', 'placa', OLD.placa, NEW.placa, NOW(), USER());
    END IF;
    
    IF OLD.marca != NEW.marca THEN
        INSERT INTO parque_automotor_historial (id_parque_automotor, accion, campo_modificado, valor_anterior, valor_nuevo, fecha_modificacion, usuario_modificacion)
        VALUES (NEW.id_parque_automotor, 'UPDATE', 'marca', OLD.marca, NEW.marca, NOW(), USER());
    END IF;
    
    IF OLD.modelo != NEW.modelo THEN
        INSERT INTO parque_automotor_historial (id_parque_automotor, accion, campo_modificado, valor_anterior, valor_nuevo, fecha_modificacion, usuario_modificacion)
        VALUES (NEW.id_parque_automotor, 'UPDATE', 'modelo', OLD.modelo, NEW.modelo, NOW(), USER());
    END IF;
END$$

-- Corregir trigger: tr_generar_alertas_vencimiento
DROP TRIGGER IF EXISTS tr_generar_alertas_vencimiento$$
CREATE DEFINER=`root`@`localhost` TRIGGER tr_generar_alertas_vencimiento
    AFTER UPDATE ON parque_automotor
    FOR EACH ROW BEGIN
    DECLARE dias_soat INT DEFAULT 0;
    DECLARE dias_tecnomecanica INT DEFAULT 0;
    
    IF NEW.soat_vencimiento IS NOT NULL THEN
        SET dias_soat = DATEDIFF(NEW.soat_vencimiento, CURDATE());
    END IF;
    
    IF NEW.tecnomecanica_vencimiento IS NOT NULL THEN
        SET dias_tecnomecanica = DATEDIFF(NEW.tecnomecanica_vencimiento, CURDATE());
    END IF;
    
    IF dias_soat <= 30 AND NEW.estado = 'Activo' THEN
        IF NOT EXISTS (
            SELECT 1 FROM alertas_vencimiento 
            WHERE id_parque_automotor = NEW.id_parque_automotor 
            AND tipo_documento = 'SOAT' 
            AND estado_alerta = 'Activa'
        ) THEN
            INSERT INTO alertas_vencimiento (
                id_parque_automotor,
                tipo_documento,
                fecha_vencimiento,
                dias_anticipacion,
                estado_alerta,
                fecha_generacion,
                prioridad,
                mensaje
            ) VALUES (
                NEW.id_parque_automotor,
                'SOAT',
                NEW.soat_vencimiento,
                dias_soat,
                'Activa',
                NOW(),
                CASE 
                    WHEN dias_soat <= 0 THEN 'Alta'
                    WHEN dias_soat <= 7 THEN 'Media'
                    ELSE 'Baja'
                END,
                CASE 
                    WHEN dias_soat <= 0 THEN CONCAT('SOAT VENCIDO para vehículo ', NEW.placa)
                    ELSE CONCAT('SOAT vence en ', dias_soat, ' días para vehículo ', NEW.placa)
                END
            );
        END IF;
    END IF;
END$$

-- Corregir trigger: tr_parque_automotor_historial_update_v3
DROP TRIGGER IF EXISTS tr_parque_automotor_historial_update_v3$$
CREATE DEFINER=`root`@`localhost` TRIGGER tr_parque_automotor_historial_update_v3
    AFTER UPDATE ON parque_automotor
    FOR EACH ROW BEGIN
    IF OLD.placa != NEW.placa THEN
        INSERT INTO parque_automotor_historial (id_parque_automotor, accion, campo_modificado, valor_anterior, valor_nuevo, fecha_modificacion, usuario_modificacion)
        VALUES (NEW.id_parque_automotor, 'UPDATE', 'placa', OLD.placa, NEW.placa, NOW(), USER());
    END IF;
END$$

-- Corregir trigger: alerta_stock_bajo
DROP TRIGGER IF EXISTS alerta_stock_bajo$$
CREATE DEFINER=`root`@`localhost` TRIGGER alerta_stock_bajo
    AFTER UPDATE ON stock_general
    FOR EACH ROW BEGIN
    IF NEW.cantidad_disponible <= NEW.cantidad_minima AND OLD.cantidad_disponible > OLD.cantidad_minima THEN
        INSERT INTO eventos_sistema (tipo, mensaje)
        VALUES (
            'ALERTA_STOCK_BAJO',
            CONCAT('Stock bajo para material: ', NEW.codigo_material, ' - Cantidad: ', NEW.cantidad_disponible, ' - Mínimo: ', NEW.cantidad_minima)
        );
    END IF;
END$$

-- Restaurar delimitador
DELIMITER ;

-- Confirmar transacción
COMMIT;

-- Verificación final
SELECT 'VERIFICACIÓN FINAL - Estado de los triggers:' AS ESTADO;
SELECT TRIGGER_NAME, EVENT_OBJECT_TABLE, DEFINER 
FROM information_schema.TRIGGERS 
WHERE TRIGGER_SCHEMA = 'capired'
ORDER BY EVENT_OBJECT_TABLE, TRIGGER_NAME;

-- Restaurar configuración
SET SESSION foreign_key_checks = 1;
SET SESSION unique_checks = 1;

SELECT 'PROCESO COMPLETADO - Todos los triggers han sido actualizados con definer root@localhost' AS RESULTADO;
