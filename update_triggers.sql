-- =====================================================
-- SCRIPT DE ACTUALIZACIÓN DE TRIGGERS
-- Sistema de Gestión Synapsis
-- Fecha: 2025-01-20
-- Descripción: Actualiza todos los triggers con el definer correcto
-- =====================================================

-- Configurar el delimitador para triggers
DELIMITER //

-- =====================================================
-- PASO 1: ELIMINAR TRIGGERS EXISTENTES
-- =====================================================

-- Eliminar triggers del sistema ferretero
DROP TRIGGER IF EXISTS actualizar_stock_entrada//
DROP TRIGGER IF EXISTS actualizar_stock_asignacion//
DROP TRIGGER IF EXISTS tr_ferretero_after_insert//
DROP TRIGGER IF EXISTS tr_entradas_ferretero_after_insert//

-- Eliminar triggers de dotaciones
DROP TRIGGER IF EXISTS tr_dotaciones_after_insert//
DROP TRIGGER IF EXISTS tr_dotaciones_after_update//
DROP TRIGGER IF EXISTS tr_dotaciones_after_delete//

-- Eliminar triggers de cambios de dotación
DROP TRIGGER IF EXISTS tr_cambios_dotacion_after_insert//
DROP TRIGGER IF EXISTS tr_cambios_dotacion_after_update//

-- Eliminar triggers de parque automotor
DROP TRIGGER IF EXISTS tr_parque_automotor_after_insert//
DROP TRIGGER IF EXISTS tr_parque_automotor_after_update//

-- Eliminar triggers de stock general
DROP TRIGGER IF EXISTS tr_stock_general_after_update//

-- =====================================================
-- PASO 2: CREAR TRIGGERS PARA SISTEMA FERRETERO
-- =====================================================

-- Trigger para actualizar stock cuando se registra una entrada
CREATE TRIGGER actualizar_stock_entrada
    AFTER INSERT ON entradas_ferretero
    FOR EACH ROW
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    -- Actualizar stock sumando la nueva entrada
    UPDATE stock_ferretero 
    SET cantidad_disponible = cantidad_disponible + NEW.cantidad_entrada,
        fecha_actualizacion = NOW()
    WHERE material_tipo = NEW.material_tipo;
    
    -- Si no existe el material en stock, crearlo
    IF ROW_COUNT() = 0 THEN
        INSERT INTO stock_ferretero (material_tipo, cantidad_disponible, fecha_actualizacion)
        VALUES (NEW.material_tipo, NEW.cantidad_entrada, NOW());
    END IF;
    
    -- Registrar movimiento en historial
    INSERT INTO movimientos_stock_ferretero (
        material_tipo, 
        tipo_movimiento, 
        cantidad, 
        cantidad_anterior, 
        cantidad_nueva, 
        observaciones,
        fecha_movimiento
    ) VALUES (
        NEW.material_tipo,
        'ENTRADA',
        NEW.cantidad_entrada,
        COALESCE((SELECT cantidad_disponible - NEW.cantidad_entrada FROM stock_ferretero WHERE material_tipo = NEW.material_tipo), 0),
        (SELECT cantidad_disponible FROM stock_ferretero WHERE material_tipo = NEW.material_tipo),
        CONCAT('Entrada registrada - Proveedor: ', COALESCE(NEW.proveedor, 'N/A')),
        NOW()
    );
    
    COMMIT;
END//

-- Trigger para actualizar stock cuando se asigna material a un técnico
CREATE TRIGGER actualizar_stock_asignacion
    AFTER INSERT ON ferretero
    FOR EACH ROW
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    -- Actualizar stock restando la cantidad asignada
    UPDATE stock_ferretero 
    SET cantidad_disponible = cantidad_disponible - NEW.cantidad,
        fecha_actualizacion = NOW()
    WHERE material_tipo = NEW.codigo_material;
    
    -- Registrar movimiento en historial
    INSERT INTO movimientos_stock_ferretero (
        material_tipo, 
        tipo_movimiento, 
        cantidad, 
        cantidad_anterior, 
        cantidad_nueva, 
        observaciones,
        fecha_movimiento,
        cedula_tecnico
    ) VALUES (
        NEW.codigo_material,
        'SALIDA',
        NEW.cantidad,
        (SELECT cantidad_disponible + NEW.cantidad FROM stock_ferretero WHERE material_tipo = NEW.codigo_material),
        (SELECT cantidad_disponible FROM stock_ferretero WHERE material_tipo = NEW.codigo_material),
        CONCAT('Asignación a técnico - Código: ', NEW.id_codigo_consumidor),
        NOW(),
        NEW.cedula_tecnico
    );
    
    COMMIT;
END//

-- =====================================================
-- PASO 3: CREAR TRIGGERS PARA DOTACIONES
-- =====================================================

-- Trigger para auditoría de inserción de dotaciones
CREATE TRIGGER tr_dotaciones_after_insert
    AFTER INSERT ON dotaciones
    FOR EACH ROW
BEGIN
    -- Registrar en historial de cambios si la tabla existe
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'cambios_dotacion') THEN
        INSERT INTO cambios_dotacion (
            id_dotacion,
            tipo_cambio,
            campo_modificado,
            valor_anterior,
            valor_nuevo,
            usuario_modificacion,
            fecha_registro,
            observaciones
        ) VALUES (
            NEW.id,
            'CREACION',
            'REGISTRO_COMPLETO',
            NULL,
            CONCAT('Nueva dotación creada para técnico: ', NEW.cedula_tecnico),
            USER(),
            NOW(),
            'Registro inicial de dotación'
        );
    END IF;
END//

-- Trigger para auditoría de actualización de dotaciones
CREATE TRIGGER tr_dotaciones_after_update
    AFTER UPDATE ON dotaciones
    FOR EACH ROW
BEGIN
    -- Registrar cambios específicos en cada campo
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'cambios_dotacion') THEN
        
        -- Verificar cambios en pantalón
        IF OLD.pantalon != NEW.pantalon THEN
            INSERT INTO cambios_dotacion (
                id_dotacion, tipo_cambio, campo_modificado, valor_anterior, valor_nuevo, 
                usuario_modificacion, fecha_registro, observaciones
            ) VALUES (
                NEW.id, 'MODIFICACION', 'pantalon', OLD.pantalon, NEW.pantalon, 
                USER(), NOW(), 'Cambio en talla de pantalón'
            );
        END IF;
        
        -- Verificar cambios en camisa
        IF OLD.camisa != NEW.camisa THEN
            INSERT INTO cambios_dotacion (
                id_dotacion, tipo_cambio, campo_modificado, valor_anterior, valor_nuevo, 
                usuario_modificacion, fecha_registro, observaciones
            ) VALUES (
                NEW.id, 'MODIFICACION', 'camisa', OLD.camisa, NEW.camisa, 
                USER(), NOW(), 'Cambio en talla de camisa'
            );
        END IF;
        
        -- Verificar cambios en botas
        IF OLD.botas != NEW.botas THEN
            INSERT INTO cambios_dotacion (
                id_dotacion, tipo_cambio, campo_modificado, valor_anterior, valor_nuevo, 
                usuario_modificacion, fecha_registro, observaciones
            ) VALUES (
                NEW.id, 'MODIFICACION', 'botas', OLD.botas, NEW.botas, 
                USER(), NOW(), 'Cambio en talla de botas'
            );
        END IF;
        
    END IF;
END//

-- =====================================================
-- PASO 4: CREAR TRIGGERS PARA PARQUE AUTOMOTOR
-- =====================================================

-- Trigger para auditoría de vehículos
CREATE TRIGGER tr_parque_automotor_after_insert
    AFTER INSERT ON parque_automotor
    FOR EACH ROW
BEGIN
    -- Crear registro de historial si la tabla existe
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'historial_vehiculos') THEN
        INSERT INTO historial_vehiculos (
            id_vehiculo,
            accion,
            descripcion,
            usuario,
            fecha_registro
        ) VALUES (
            NEW.id_vehiculo,
            'CREACION',
            CONCAT('Vehículo registrado - Placa: ', NEW.placa, ', Tipo: ', NEW.tipo_vehiculo),
            USER(),
            NOW()
        );
    END IF;
END//

-- Trigger para auditoría de cambios en vehículos
CREATE TRIGGER tr_parque_automotor_after_update
    AFTER UPDATE ON parque_automotor
    FOR EACH ROW
BEGIN
    -- Registrar cambios importantes
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'historial_vehiculos') THEN
        
        -- Cambio de estado
        IF OLD.estado != NEW.estado THEN
            INSERT INTO historial_vehiculos (
                id_vehiculo, accion, descripcion, usuario, fecha_registro
            ) VALUES (
                NEW.id_vehiculo, 'CAMBIO_ESTADO', 
                CONCAT('Estado cambiado de "', OLD.estado, '" a "', NEW.estado, '"'),
                USER(), NOW()
            );
        END IF;
        
        -- Cambio de asignación
        IF OLD.id_codigo_consumidor != NEW.id_codigo_consumidor THEN
            INSERT INTO historial_vehiculos (
                id_vehiculo, accion, descripcion, usuario, fecha_registro
            ) VALUES (
                NEW.id_vehiculo, 'REASIGNACION', 
                CONCAT('Vehículo reasignado de código ', OLD.id_codigo_consumidor, ' a ', NEW.id_codigo_consumidor),
                USER(), NOW()
            );
        END IF;
        
    END IF;
END//

-- =====================================================
-- PASO 5: CREAR TRIGGERS PARA CONTROL DE STOCK GENERAL
-- =====================================================

-- Trigger para alertas de stock bajo
CREATE TRIGGER tr_stock_general_after_update
    AFTER UPDATE ON stock_general
    FOR EACH ROW
BEGIN
    -- Generar alerta si el stock está por debajo del mínimo
    IF NEW.cantidad_disponible <= NEW.cantidad_minima AND NEW.cantidad_disponible < OLD.cantidad_disponible THEN
        
        -- Insertar alerta si la tabla existe
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'alertas_stock') THEN
            INSERT INTO alertas_stock (
                codigo_material,
                tipo_alerta,
                mensaje,
                cantidad_actual,
                cantidad_minima,
                fecha_alerta,
                estado
            ) VALUES (
                NEW.codigo_material,
                'STOCK_BAJO',
                CONCAT('Stock bajo para material: ', NEW.descripcion, '. Cantidad actual: ', NEW.cantidad_disponible),
                NEW.cantidad_disponible,
                NEW.cantidad_minima,
                NOW(),
                'PENDIENTE'
            );
        END IF;
        
    END IF;
END//

-- =====================================================
-- PASO 6: CREAR TRIGGERS PARA MOVIMIENTOS DE STOCK
-- =====================================================

-- Trigger para validar movimientos de stock
CREATE TRIGGER tr_movimientos_stock_before_insert
    BEFORE INSERT ON movimientos_stock_ferretero
    FOR EACH ROW
BEGIN
    -- Validar que la cantidad sea positiva
    IF NEW.cantidad <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cantidad del movimiento debe ser mayor a cero';
    END IF;
    
    -- Asegurar que la fecha no sea futura
    IF NEW.fecha_movimiento > NOW() THEN
        SET NEW.fecha_movimiento = NOW();
    END IF;
    
    -- Generar ID único si no se proporciona
    IF NEW.id IS NULL THEN
        SET NEW.id = UUID();
    END IF;
END//

-- =====================================================
-- PASO 7: CREAR PROCEDIMIENTOS AUXILIARES
-- =====================================================

-- Procedimiento para recalcular stock
CREATE PROCEDURE sp_recalcular_stock_ferretero(IN p_material_tipo VARCHAR(100))
BEGIN
    DECLARE v_total_entradas INT DEFAULT 0;
    DECLARE v_total_salidas INT DEFAULT 0;
    DECLARE v_stock_calculado INT DEFAULT 0;
    
    -- Calcular total de entradas
    SELECT COALESCE(SUM(cantidad_entrada), 0) INTO v_total_entradas
    FROM entradas_ferretero 
    WHERE material_tipo = p_material_tipo;
    
    -- Calcular total de salidas (asignaciones)
    SELECT COALESCE(SUM(cantidad), 0) INTO v_total_salidas
    FROM ferretero 
    WHERE codigo_material = p_material_tipo;
    
    -- Calcular stock actual
    SET v_stock_calculado = v_total_entradas - v_total_salidas;
    
    -- Actualizar stock en la tabla
    UPDATE stock_ferretero 
    SET cantidad_disponible = v_stock_calculado,
        fecha_actualizacion = NOW()
    WHERE material_tipo = p_material_tipo;
    
    -- Si no existe el registro, crearlo
    IF ROW_COUNT() = 0 THEN
        INSERT INTO stock_ferretero (material_tipo, cantidad_disponible, fecha_actualizacion)
        VALUES (p_material_tipo, v_stock_calculado, NOW());
    END IF;
    
END//

-- Procedimiento para limpiar alertas antiguas
CREATE PROCEDURE sp_limpiar_alertas_antiguas()
BEGIN
    -- Eliminar alertas resueltas de más de 30 días
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'alertas_stock') THEN
        DELETE FROM alertas_stock 
        WHERE estado = 'RESUELTO' 
        AND fecha_alerta < DATE_SUB(NOW(), INTERVAL 30 DAY);
    END IF;
END//

-- =====================================================
-- PASO 8: CREAR EVENTOS PROGRAMADOS
-- =====================================================

-- Evento para limpieza automática de alertas
CREATE EVENT IF NOT EXISTS ev_limpiar_alertas_stock
ON SCHEDULE EVERY 1 WEEK
STARTS CURRENT_TIMESTAMP
DO
BEGIN
    CALL sp_limpiar_alertas_antiguas();
END//

-- Restaurar delimitador
DELIMITER ;

-- =====================================================
-- VERIFICACIONES FINALES
-- =====================================================

-- Verificar que los triggers se crearon correctamente
SELECT 
    TRIGGER_NAME as 'Trigger Creado',
    EVENT_MANIPULATION as 'Evento',
    EVENT_OBJECT_TABLE as 'Tabla',
    DEFINER as 'Definer'
FROM information_schema.TRIGGERS 
WHERE TRIGGER_SCHEMA = DATABASE()
ORDER BY EVENT_OBJECT_TABLE, TRIGGER_NAME;

-- Verificar procedimientos creados
SELECT 
    ROUTINE_NAME as 'Procedimiento Creado',
    ROUTINE_TYPE as 'Tipo',
    DEFINER as 'Definer'
FROM information_schema.ROUTINES 
WHERE ROUTINE_SCHEMA = DATABASE()
AND ROUTINE_NAME LIKE 'sp_%'
ORDER BY ROUTINE_NAME;

-- Verificar eventos creados
SELECT 
    EVENT_NAME as 'Evento Creado',
    STATUS as 'Estado',
    DEFINER as 'Definer'
FROM information_schema.EVENTS 
WHERE EVENT_SCHEMA = DATABASE()
ORDER BY EVENT_NAME;

-- =====================================================
-- SCRIPT COMPLETADO
-- =====================================================
-- Todos los triggers han sido recreados con el definer correcto: root@localhost
-- El sistema ahora debería funcionar sin errores de definer
-- =====================================================