-- =====================================================
-- TABLA PARA ENTRADAS DE STOCK
-- =====================================================
-- Propósito: Registrar todas las entradas de material al inventario
-- Esta tabla almacena los ingresos de stock que luego actualizan
-- automáticamente la tabla stock_general mediante triggers

CREATE TABLE IF NOT EXISTS entradas_stock (
    id_entrada INT AUTO_INCREMENT PRIMARY KEY,
    material VARCHAR(50) NOT NULL,
    cantidad_ingresada INT NOT NULL CHECK (cantidad_ingresada > 0),
    precio_unitario DECIMAL(10,2) DEFAULT 0.00,
    proveedor VARCHAR(100),
    numero_factura VARCHAR(50),
    fecha_entrada DATETIME DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    usuario_registro VARCHAR(50),
    INDEX idx_material (material),
    INDEX idx_fecha_entrada (fecha_entrada)
);

-- =====================================================
-- TRIGGER 4: ACTUALIZAR_STOCK_ENTRADA
-- =====================================================
-- Propósito: Actualiza automáticamente el stock en stock_general
--           después de cada INSERT en la tabla entradas_stock
-- Activación: AFTER INSERT ON entradas_stock

DROP TRIGGER IF EXISTS actualizar_stock_entrada;

DELIMITER //

CREATE TRIGGER actualizar_stock_entrada
AFTER INSERT ON entradas_stock
FOR EACH ROW
BEGIN
    DECLARE stock_existe INT DEFAULT 0;
    
    -- Verificar si el material existe en stock_general
    SELECT COUNT(*) INTO stock_existe 
    FROM stock_general 
    WHERE material = NEW.material;
    
    -- Si el material existe, actualizar el stock
    IF stock_existe > 0 THEN
        UPDATE stock_general 
        SET stock_actual = stock_actual + NEW.cantidad_ingresada,
            fecha_ultima_actualizacion = NOW()
        WHERE material = NEW.material;
    ELSE
        -- Si el material no existe, crear un nuevo registro
        -- con stock mínimo por defecto de 10 unidades
        INSERT INTO stock_general (
            material, 
            stock_actual, 
            stock_minimo, 
            fecha_ultima_actualizacion
        ) VALUES (
            NEW.material,
            NEW.cantidad_ingresada,
            10, -- Stock mínimo por defecto
            NOW()
        );
    END IF;
    
    -- Log opcional de la operación
    -- INSERT INTO eventos_sistema (tipo, mensaje, fecha)
    -- VALUES ('ENTRADA_STOCK', CONCAT('Entrada de ', NEW.cantidad_ingresada, ' unidades de ', NEW.material), NOW());
    
END//

DELIMITER ;

-- =====================================================
-- TRIGGERS MYSQL PARA SISTEMA FERRETERO
-- =====================================================
-- Archivo: triggers_mysql_ferretero.sql
-- Descripción: Triggers necesarios para el funcionamiento del sistema ferretero
-- Fecha: 2025-01-17
-- =====================================================

-- INSTRUCCIONES DE INSTALACIÓN:
-- 1. Conectarse a MySQL como usuario con privilegios de CREATE TRIGGER
-- 2. Seleccionar la base de datos: USE nombre_de_tu_base_de_datos;
-- 3. Ejecutar este archivo completo: SOURCE triggers_mysql_ferretero.sql;
-- 4. Verificar la creación: SHOW TRIGGERS;

-- =====================================================
-- TRIGGER 1: ACTUALIZAR_STOCK_ASIGNACION
-- =====================================================
-- Propósito: Actualiza automáticamente el stock en stock_general
--           después de cada INSERT en la tabla ferretero
-- Activación: AFTER INSERT ON ferretero

DROP TRIGGER IF EXISTS actualizar_stock_asignacion;

DELIMITER //

CREATE TRIGGER actualizar_stock_asignacion
AFTER INSERT ON ferretero
FOR EACH ROW
BEGIN
    -- Variables para almacenar los valores de materiales
    DECLARE material_name VARCHAR(50);
    DECLARE cantidad_usada INT DEFAULT 0;
    
    -- Actualizar stock para cada material que tenga valor > 0
    
    -- Silicona
    IF NEW.silicona > 0 THEN
        UPDATE stock_general 
        SET stock_actual = stock_actual - NEW.silicona,
            fecha_ultima_actualizacion = NOW()
        WHERE material = 'silicona';
    END IF;
    
    -- Grapas blancas
    IF NEW.grapas_blancas > 0 THEN
        UPDATE stock_general 
        SET stock_actual = stock_actual - NEW.grapas_blancas,
            fecha_ultima_actualizacion = NOW()
        WHERE material = 'grapas_blancas';
    END IF;
    
    -- Grapas negras
    IF NEW.grapas_negras > 0 THEN
        UPDATE stock_general 
        SET stock_actual = stock_actual - NEW.grapas_negras,
            fecha_ultima_actualizacion = NOW()
        WHERE material = 'grapas_negras';
    END IF;
    
    -- Cinta aislante
     IF NEW.cinta_aislante > 0 THEN
         UPDATE stock_general 
         SET stock_actual = stock_actual - NEW.cinta_aislante,
             fecha_ultima_actualizacion = NOW()
         WHERE material = 'cinta_aislante';
     END IF;
    
    -- Amarres negros
    IF NEW.amarres_negros > 0 THEN
        UPDATE stock_general 
        SET stock_actual = stock_actual - NEW.amarres_negros,
            fecha_ultima_actualizacion = NOW()
        WHERE material = 'amarres_negros';
    END IF;
    
    -- Amarres blancos
    IF NEW.amarres_blancos > 0 THEN
        UPDATE stock_general 
        SET stock_actual = stock_actual - NEW.amarres_blancos,
            fecha_ultima_actualizacion = NOW()
        WHERE material = 'amarres_blancos';
    END IF;
    
    -- Registrar en log (opcional - requiere tabla de log)
    -- INSERT INTO stock_log (material, cantidad_anterior, cantidad_nueva, tipo_operacion, fecha, referencia)
    -- VALUES ('multiple', 0, 0, 'ASIGNACION', NOW(), CONCAT('ferretero_id:', NEW.id_ferretero));
    
END//

DELIMITER ;

-- =====================================================
-- TRIGGER 2: ALERTA_STOCK_BAJO
-- =====================================================
-- Propósito: Genera alertas cuando el stock de un material
--           está por debajo del mínimo establecido
-- Activación: AFTER UPDATE ON stock_general

DROP TRIGGER IF EXISTS alerta_stock_bajo;

DELIMITER //

CREATE TRIGGER alerta_stock_bajo
AFTER UPDATE ON stock_general
FOR EACH ROW
BEGIN
    -- Solo ejecutar si el stock actual cambió
    IF NEW.stock_actual != OLD.stock_actual THEN
        
        -- Verificar si el stock está por debajo del mínimo
        IF NEW.stock_actual < NEW.stock_minimo THEN
            
            -- Insertar alerta en tabla alertas_stock
            INSERT INTO alertas_stock (
                material, 
                stock_actual, 
                stock_minimo, 
                diferencia, 
                fecha_alerta, 
                estado
            ) VALUES (
                NEW.material,
                NEW.stock_actual,
                NEW.stock_minimo,
                (NEW.stock_minimo - NEW.stock_actual),
                NOW(),
                'PENDIENTE'
            );
            
            -- Log en tabla de eventos
            INSERT INTO eventos_sistema (tipo, mensaje, fecha)
            VALUES ('STOCK_BAJO', CONCAT('Material ', NEW.material, ' tiene stock bajo: ', NEW.stock_actual, ' (mínimo: ', NEW.stock_minimo, ')'), NOW());
            
        END IF;
        
        -- Verificar si el stock llegó a cero
        IF NEW.stock_actual <= 0 THEN
            
            -- Log de stock agotado
            INSERT INTO eventos_sistema (tipo, mensaje, fecha)
            VALUES ('STOCK_AGOTADO', CONCAT('Material ', NEW.material, ' AGOTADO. Stock actual: ', NEW.stock_actual), NOW());
            
        END IF;
        
    END IF;
    
END//

DELIMITER ;

-- =====================================================
-- TRIGGER 3: VALIDAR_ASIGNACION (OPCIONAL)
-- =====================================================
-- Propósito: Valida que haya suficiente stock antes de
--           permitir una asignación en ferretero
-- Activación: BEFORE INSERT ON ferretero

DROP TRIGGER IF EXISTS validar_asignacion;

DELIMITER //

CREATE TRIGGER validar_asignacion
BEFORE INSERT ON ferretero
FOR EACH ROW
BEGIN
    DECLARE stock_disponible INT;
    DECLARE mensaje_error VARCHAR(255);
    
    -- Validar silicona
    IF NEW.silicona > 0 THEN
        SELECT stock_actual INTO stock_disponible 
        FROM stock_general 
        WHERE material = 'silicona';
        
        IF stock_disponible < NEW.silicona THEN
            SET mensaje_error = CONCAT('Stock insuficiente de silicona. Disponible: ', stock_disponible, ', Solicitado: ', NEW.silicona);
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = mensaje_error;
        END IF;
    END IF;
    
    -- Validar grapas blancas
    IF NEW.grapas_blancas > 0 THEN
        SELECT stock_actual INTO stock_disponible 
        FROM stock_general 
        WHERE material = 'grapas_blancas';
        
        IF stock_disponible < NEW.grapas_blancas THEN
            SET mensaje_error = CONCAT('Stock insuficiente de grapas blancas. Disponible: ', stock_disponible, ', Solicitado: ', NEW.grapas_blancas);
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = mensaje_error;
        END IF;
    END IF;
    
    -- Validar grapas negras
    IF NEW.grapas_negras > 0 THEN
        SELECT stock_actual INTO stock_disponible 
        FROM stock_general 
        WHERE material = 'grapas_negras';
        
        IF stock_disponible < NEW.grapas_negras THEN
            SET mensaje_error = CONCAT('Stock insuficiente de grapas negras. Disponible: ', stock_disponible, ', Solicitado: ', NEW.grapas_negras);
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = mensaje_error;
        END IF;
    END IF;
    
    -- Validar cinta aislante
    IF NEW.cinta_aislante > 0 THEN
        SELECT stock_actual INTO stock_disponible 
        FROM stock_general 
        WHERE material = 'cinta_aislante';
        
        IF stock_disponible < NEW.cinta_aislante THEN
            SET mensaje_error = CONCAT('Stock insuficiente de cinta aislante. Disponible: ', stock_disponible, ', Solicitado: ', NEW.cinta_aislante);
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = mensaje_error;
        END IF;
    END IF;
    
    -- Validar amarres negros
    IF NEW.amarres_negros > 0 THEN
        SELECT stock_actual INTO stock_disponible 
        FROM stock_general 
        WHERE material = 'amarres_negros';
        
        IF stock_disponible < NEW.amarres_negros THEN
            SET mensaje_error = CONCAT('Stock insuficiente de amarres negros. Disponible: ', stock_disponible, ', Solicitado: ', NEW.amarres_negros);
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = mensaje_error;
        END IF;
    END IF;
    
    -- Validar amarres blancos
    IF NEW.amarres_blancos > 0 THEN
        SELECT stock_actual INTO stock_disponible 
        FROM stock_general 
        WHERE material = 'amarres_blancos';
        
        IF stock_disponible < NEW.amarres_blancos THEN
            SET mensaje_error = CONCAT('Stock insuficiente de amarres blancos. Disponible: ', stock_disponible, ', Solicitado: ', NEW.amarres_blancos);
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = mensaje_error;
        END IF;
    END IF;
    
END//

DELIMITER ;

-- =====================================================
-- COMANDOS DE VERIFICACIÓN
-- =====================================================

-- Verificar que los triggers se crearon correctamente
-- SHOW TRIGGERS;

-- Verificar triggers específicos
-- SHOW TRIGGERS WHERE `Trigger` LIKE '%stock%';

-- Ver detalles de un trigger específico
-- SHOW CREATE TRIGGER actualizar_stock_asignacion;

-- =====================================================
-- COMANDOS DE PRUEBA (OPCIONAL)
-- =====================================================

-- Probar el trigger con una inserción de prueba
/*
INSERT INTO ferretero (
    codigo_ferretero, 
    id_codigo_consumidor, 
    silicona, 
     grapas_blancas, 
     grapas_negras, 
     cinta_aislante, 
     amarres_negros, 
     amarres_blancos, 
    fecha_asignacion
) VALUES (
    'TEST001', 
    'CONSUMIDOR_TEST', 
    1, 1, 1, 1, 1, 1, 
    NOW()
);
*/

-- Verificar que el stock se actualizó
-- SELECT * FROM stock_general;

-- Limpiar datos de prueba
-- DELETE FROM ferretero WHERE codigo_ferretero = 'TEST001';

-- =====================================================
-- COMANDOS DE PRUEBA PARA ENTRADAS DE STOCK
-- =====================================================

-- Probar el trigger de entradas con una inserción de prueba
/*
INSERT INTO entradas_stock (
    material, 
    cantidad_ingresada, 
    precio_unitario, 
    proveedor, 
    numero_factura, 
    observaciones,
    usuario_registro
) VALUES (
    'silicona', 
    50, 
    2.50, 
    'Proveedor ABC', 
    'FAC-001', 
    'Entrada inicial de silicona',
    'admin'
);
*/

-- Probar entrada de un material nuevo
/*
INSERT INTO entradas_stock (
    material, 
    cantidad_ingresada, 
    precio_unitario, 
    proveedor, 
    observaciones,
    usuario_registro
) VALUES (
    'tornillos_phillips', 
    100, 
    0.15, 
    'Ferretería XYZ', 
    'Material nuevo en inventario',
    'admin'
);
*/

-- Verificar que el stock se actualizó correctamente
-- SELECT * FROM stock_general WHERE material IN ('silicona', 'tornillos_phillips');

-- Ver historial de entradas
-- SELECT * FROM entradas_stock ORDER BY fecha_entrada DESC;

-- Limpiar datos de prueba de entradas
-- DELETE FROM entradas_stock WHERE material IN ('silicona', 'tornillos_phillips');
-- DELETE FROM stock_general WHERE material = 'tornillos_phillips';

-- =====================================================
-- NOTAS IMPORTANTES:
-- =====================================================
-- 1. El trigger 'validar_asignacion' es opcional pero recomendado
--    para evitar asignaciones que excedan el stock disponible
--
-- 2. El trigger 'actualizar_stock_entrada' maneja automáticamente:
--    - Incremento de stock cuando se registran entradas
--    - Creación automática de nuevos materiales en stock_general
--    - Actualización de fechas de última modificación
--
-- 3. El sistema de alertas está HABILITADO y funcional:
--    - alertas_stock (almacena alertas de stock bajo)
--    - eventos_sistema (registra log de eventos)
--
-- 4. Las alertas se generan automáticamente cuando:
--    - Stock actual < Stock mínimo (alerta STOCK_BAJO)
--    - Stock actual <= 0 (alerta STOCK_AGOTADO)
--
-- 5. Los triggers se ejecutan automáticamente, no requieren
--    intervención manual una vez instalados
--
-- 6. Para desinstalar: DROP TRIGGER nombre_del_trigger;
--
-- 7. FLUJO COMPLETO DE STOCK:
--    - ENTRADAS: INSERT en entradas_stock → Incrementa stock_general
--    - SALIDAS: INSERT en ferretero → Decrementa stock_general
--    - VALIDACIÓN: Antes de salidas verifica stock disponible
--    - ALERTAS: Notifica cuando stock está bajo o agotado
--
-- =====================================================