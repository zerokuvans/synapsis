#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT'))
}

def crear_triggers_ferretero():
    """Crear triggers para actualización automática de stock ferretero"""
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        print("=== Creando triggers para stock ferretero ===")
        
        # Leer el archivo SQL con los triggers
        sql_file_path = os.path.join(os.path.dirname(__file__), '..', 'sql', 'triggers_ferretero.sql')
        
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Dividir el contenido por declaraciones individuales
        # Primero eliminar triggers existentes si los hay
        print("\n1. Eliminando triggers existentes...")
        try:
            cursor.execute("DROP TRIGGER IF EXISTS actualizar_stock_entrada")
            cursor.execute("DROP TRIGGER IF EXISTS actualizar_stock_asignacion")
            print("   ✓ Triggers anteriores eliminados")
        except Error as e:
            print(f"   ⚠ No había triggers anteriores: {e}")
        
        # Crear trigger para entradas
        print("\n2. Creando trigger para entradas...")
        trigger_entrada = """
CREATE TRIGGER actualizar_stock_entrada
AFTER INSERT ON entradas_ferretero
FOR EACH ROW
BEGIN
    -- Obtener stock anterior
    DECLARE stock_anterior INT DEFAULT 0;
    SELECT cantidad_disponible INTO stock_anterior FROM stock_ferretero WHERE material_tipo = NEW.material_tipo;
    
    -- Actualizar stock sumando la nueva entrada
    UPDATE stock_ferretero 
    SET cantidad_disponible = cantidad_disponible + NEW.cantidad_entrada,
        fecha_actualizacion = NOW()
    WHERE material_tipo = NEW.material_tipo;
    
    -- Registrar movimiento de entrada
    INSERT INTO movimientos_stock_ferretero (
        material_tipo, 
        tipo_movimiento, 
        cantidad, 
        cantidad_anterior,
        cantidad_nueva, 
        referencia_id, 
        referencia_tipo, 
        observaciones
    ) VALUES (
        NEW.material_tipo, 
        'entrada', 
        NEW.cantidad_entrada, 
        stock_anterior,
        stock_anterior + NEW.cantidad_entrada, 
        NEW.id_entrada, 
        'entrada_ferretero', 
        CONCAT('Entrada de material: ', NEW.observaciones)
    );
END
        """
        
        cursor.execute(trigger_entrada)
        print("   ✓ Trigger para entradas creado")
        
        # Crear trigger para asignaciones
        print("\n3. Creando trigger para asignaciones...")
        trigger_asignacion = """
CREATE TRIGGER actualizar_stock_asignacion
AFTER INSERT ON ferretero
FOR EACH ROW
BEGIN
    DECLARE stock_anterior_silicona INT DEFAULT 0;
    DECLARE stock_anterior_amarres_negros INT DEFAULT 0;
    DECLARE stock_anterior_amarres_blancos INT DEFAULT 0;
    DECLARE stock_anterior_cinta_aislante INT DEFAULT 0;
    DECLARE stock_anterior_grapas_blancas INT DEFAULT 0;
    DECLARE stock_anterior_grapas_negras INT DEFAULT 0;
    
    DECLARE stock_nuevo_silicona INT DEFAULT 0;
    DECLARE stock_nuevo_amarres_negros INT DEFAULT 0;
    DECLARE stock_nuevo_amarres_blancos INT DEFAULT 0;
    DECLARE stock_nuevo_cinta_aislante INT DEFAULT 0;
    DECLARE stock_nuevo_grapas_blancas INT DEFAULT 0;
    DECLARE stock_nuevo_grapas_negras INT DEFAULT 0;
    
    -- Obtener stocks anteriores
    SELECT cantidad_disponible INTO stock_anterior_silicona FROM stock_ferretero WHERE material_tipo = 'silicona';
    SELECT cantidad_disponible INTO stock_anterior_amarres_negros FROM stock_ferretero WHERE material_tipo = 'amarres_negros';
    SELECT cantidad_disponible INTO stock_anterior_amarres_blancos FROM stock_ferretero WHERE material_tipo = 'amarres_blancos';
    SELECT cantidad_disponible INTO stock_anterior_cinta_aislante FROM stock_ferretero WHERE material_tipo = 'cinta_aislante';
    SELECT cantidad_disponible INTO stock_anterior_grapas_blancas FROM stock_ferretero WHERE material_tipo = 'grapas_blancas';
    SELECT cantidad_disponible INTO stock_anterior_grapas_negras FROM stock_ferretero WHERE material_tipo = 'grapas_negras';
    
    -- Actualizar stocks restando las cantidades asignadas
    IF NEW.silicona > 0 THEN
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.silicona, fecha_actualizacion = NOW() WHERE material_tipo = 'silicona';
        SELECT cantidad_disponible INTO stock_nuevo_silicona FROM stock_ferretero WHERE material_tipo = 'silicona';
        
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('silicona', 'salida', NEW.silicona, stock_anterior_silicona, stock_nuevo_silicona, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación de silicona', NEW.id_codigo_consumidor);
    END IF;
    
    IF NEW.amarres_negros > 0 THEN
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.amarres_negros, fecha_actualizacion = NOW() WHERE material_tipo = 'amarres_negros';
        SELECT cantidad_disponible INTO stock_nuevo_amarres_negros FROM stock_ferretero WHERE material_tipo = 'amarres_negros';
        
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('amarres_negros', 'salida', NEW.amarres_negros, stock_anterior_amarres_negros, stock_nuevo_amarres_negros, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación de amarres negros', NEW.id_codigo_consumidor);
    END IF;
    
    IF NEW.amarres_blancos > 0 THEN
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.amarres_blancos, fecha_actualizacion = NOW() WHERE material_tipo = 'amarres_blancos';
        SELECT cantidad_disponible INTO stock_nuevo_amarres_blancos FROM stock_ferretero WHERE material_tipo = 'amarres_blancos';
        
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('amarres_blancos', 'salida', NEW.amarres_blancos, stock_anterior_amarres_blancos, stock_nuevo_amarres_blancos, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación de amarres blancos', NEW.id_codigo_consumidor);
    END IF;
    
    IF NEW.cinta_aislante > 0 THEN
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.cinta_aislante, fecha_actualizacion = NOW() WHERE material_tipo = 'cinta_aislante';
        SELECT cantidad_disponible INTO stock_nuevo_cinta_aislante FROM stock_ferretero WHERE material_tipo = 'cinta_aislante';
        
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('cinta_aislante', 'salida', NEW.cinta_aislante, stock_anterior_cinta_aislante, stock_nuevo_cinta_aislante, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación de cinta aislante', NEW.id_codigo_consumidor);
    END IF;
    
    IF NEW.grapas_blancas > 0 THEN
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.grapas_blancas, fecha_actualizacion = NOW() WHERE material_tipo = 'grapas_blancas';
        SELECT cantidad_disponible INTO stock_nuevo_grapas_blancas FROM stock_ferretero WHERE material_tipo = 'grapas_blancas';
        
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('grapas_blancas', 'salida', NEW.grapas_blancas, stock_anterior_grapas_blancas, stock_nuevo_grapas_blancas, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación de grapas blancas', NEW.id_codigo_consumidor);
    END IF;
    
    IF NEW.grapas_negras > 0 THEN
        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.grapas_negras, fecha_actualizacion = NOW() WHERE material_tipo = 'grapas_negras';
        SELECT cantidad_disponible INTO stock_nuevo_grapas_negras FROM stock_ferretero WHERE material_tipo = 'grapas_negras';
        
        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
        VALUES ('grapas_negras', 'salida', NEW.grapas_negras, stock_anterior_grapas_negras, stock_nuevo_grapas_negras, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación de grapas negras', NEW.id_codigo_consumidor);
    END IF;
END
        """
        
        cursor.execute(trigger_asignacion)
        print("   ✓ Trigger para asignaciones creado")
        
        # Confirmar cambios
        connection.commit()
        
        # Verificar triggers creados
        print("\n4. Verificando triggers creados...")
        cursor.execute("SHOW TRIGGERS LIKE '%ferretero%'")
        triggers = cursor.fetchall()
        
        if triggers:
            print(f"   ✓ Se crearon {len(triggers)} triggers:")
            for trigger in triggers:
                print(f"     - {trigger[0]} ({trigger[1]} {trigger[2]})")
        else:
            print("   ❌ No se encontraron triggers")
        
        print("\n=== Triggers creados exitosamente ===")
        
    except Error as e:
        print(f"❌ Error al crear triggers: {e}")
        if connection:
            connection.rollback()
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    crear_triggers_ferretero()