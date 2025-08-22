#!/usr/bin/env python3
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

def setup_stock_ferretero_tables():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("Creando tablas para gestión de stock de material ferretero...")
            
            # Crear tabla stock_ferretero
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_ferretero (
                    id_stock INT AUTO_INCREMENT PRIMARY KEY,
                    material_tipo ENUM('silicona', 'amarres_negros', 'amarres_blancos', 'cinta_aislante', 'grapas_blancas', 'grapas_negras') NOT NULL,
                    cantidad_disponible INT NOT NULL DEFAULT 0,
                    cantidad_minima INT NOT NULL DEFAULT 10,
                    cantidad_maxima INT NOT NULL DEFAULT 1000,
                    unidad_medida VARCHAR(20) DEFAULT 'unidades',
                    descripcion TEXT,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_material (material_tipo)
                )
            """)
            print("✓ Tabla stock_ferretero creada")
            
            # Crear tabla entradas_ferretero
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entradas_ferretero (
                    id_entrada INT AUTO_INCREMENT PRIMARY KEY,
                    material_tipo ENUM('silicona', 'amarres_negros', 'amarres_blancos', 'cinta_aislante', 'grapas_blancas', 'grapas_negras') NOT NULL,
                    cantidad_entrada INT NOT NULL,
                    precio_unitario DECIMAL(10,2) DEFAULT 0.00,
                    precio_total DECIMAL(10,2) DEFAULT 0.00,
                    proveedor VARCHAR(255),
                    numero_factura VARCHAR(100),
                    fecha_entrada DATE NOT NULL,
                    fecha_vencimiento DATE,
                    observaciones TEXT,
                    usuario_registro INT,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_registro) REFERENCES recurso_operativo(id_codigo_consumidor),
                    INDEX idx_material_fecha (material_tipo, fecha_entrada),
                    INDEX idx_fecha_entrada (fecha_entrada)
                )
            """)
            print("✓ Tabla entradas_ferretero creada")
            
            # Crear tabla movimientos_stock_ferretero
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movimientos_stock_ferretero (
                    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
                    material_tipo ENUM('silicona', 'amarres_negros', 'amarres_blancos', 'cinta_aislante', 'grapas_blancas', 'grapas_negras') NOT NULL,
                    tipo_movimiento ENUM('entrada', 'salida', 'ajuste') NOT NULL,
                    cantidad INT NOT NULL,
                    cantidad_anterior INT NOT NULL,
                    cantidad_nueva INT NOT NULL,
                    referencia_id INT,
                    referencia_tipo ENUM('entrada_ferretero', 'asignacion_ferretero', 'ajuste_manual') NOT NULL,
                    observaciones TEXT,
                    usuario_movimiento INT,
                    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_movimiento) REFERENCES recurso_operativo(id_codigo_consumidor),
                    INDEX idx_material_fecha (material_tipo, fecha_movimiento),
                    INDEX idx_tipo_movimiento (tipo_movimiento),
                    INDEX idx_referencia (referencia_tipo, referencia_id)
                )
            """)
            print("✓ Tabla movimientos_stock_ferretero creada")
            
            # Insertar datos iniciales para el stock
            cursor.execute("""
                INSERT IGNORE INTO stock_ferretero (material_tipo, cantidad_disponible, cantidad_minima, cantidad_maxima, descripcion) VALUES
                ('silicona', 0, 10, 1000, 'Silicona para instalaciones'),
                ('amarres_negros', 0, 50, 5000, 'Amarres de color negro'),
                ('amarres_blancos', 0, 50, 5000, 'Amarres de color blanco'),
                ('cinta_aislante', 0, 20, 2000, 'Cinta aislante para instalaciones'),
                ('grapas_blancas', 0, 100, 10000, 'Grapas de color blanco'),
                ('grapas_negras', 0, 100, 10000, 'Grapas de color negro')
            """)
            print("✓ Datos iniciales de stock insertados")
            
            # Crear trigger para actualizar stock en entradas
            cursor.execute("DROP TRIGGER IF EXISTS actualizar_stock_entrada")
            cursor.execute("""
                CREATE TRIGGER actualizar_stock_entrada
                AFTER INSERT ON entradas_ferretero
                FOR EACH ROW
                BEGIN
                    DECLARE stock_anterior INT DEFAULT 0;
                    
                    SELECT cantidad_disponible INTO stock_anterior 
                    FROM stock_ferretero 
                    WHERE material_tipo = NEW.material_tipo;
                    
                    UPDATE stock_ferretero 
                    SET cantidad_disponible = cantidad_disponible + NEW.cantidad_entrada
                    WHERE material_tipo = NEW.material_tipo;
                    
                    INSERT INTO movimientos_stock_ferretero (
                        material_tipo, 
                        tipo_movimiento, 
                        cantidad, 
                        cantidad_anterior, 
                        cantidad_nueva, 
                        referencia_id, 
                        referencia_tipo, 
                        observaciones, 
                        usuario_movimiento
                    ) VALUES (
                        NEW.material_tipo,
                        'entrada',
                        NEW.cantidad_entrada,
                        stock_anterior,
                        stock_anterior + NEW.cantidad_entrada,
                        NEW.id_entrada,
                        'entrada_ferretero',
                        CONCAT('Entrada de material - Factura: ', IFNULL(NEW.numero_factura, 'N/A')),
                        NEW.usuario_registro
                    );
                END
            """)
            print("✓ Trigger actualizar_stock_entrada creado")
            
            # Crear trigger para actualizar stock en asignaciones
            cursor.execute("DROP TRIGGER IF EXISTS actualizar_stock_asignacion")
            cursor.execute("""
                CREATE TRIGGER actualizar_stock_asignacion
                AFTER INSERT ON ferretero
                FOR EACH ROW
                BEGIN
                    DECLARE stock_anterior INT DEFAULT 0;
                    
                    IF NEW.silicona > 0 THEN
                        SELECT cantidad_disponible INTO stock_anterior FROM stock_ferretero WHERE material_tipo = 'silicona';
                        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.silicona WHERE material_tipo = 'silicona';
                        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
                        VALUES ('silicona', 'salida', NEW.silicona, stock_anterior, stock_anterior - NEW.silicona, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
                    END IF;
                    
                    IF NEW.amarres_negros > 0 THEN
                        SELECT cantidad_disponible INTO stock_anterior FROM stock_ferretero WHERE material_tipo = 'amarres_negros';
                        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.amarres_negros WHERE material_tipo = 'amarres_negros';
                        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
                        VALUES ('amarres_negros', 'salida', NEW.amarres_negros, stock_anterior, stock_anterior - NEW.amarres_negros, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
                    END IF;
                    
                    IF NEW.amarres_blancos > 0 THEN
                        SELECT cantidad_disponible INTO stock_anterior FROM stock_ferretero WHERE material_tipo = 'amarres_blancos';
                        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.amarres_blancos WHERE material_tipo = 'amarres_blancos';
                        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
                        VALUES ('amarres_blancos', 'salida', NEW.amarres_blancos, stock_anterior, stock_anterior - NEW.amarres_blancos, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
                    END IF;
                    
                    IF NEW.cinta_aislante > 0 THEN
                        SELECT cantidad_disponible INTO stock_anterior FROM stock_ferretero WHERE material_tipo = 'cinta_aislante';
                        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.cinta_aislante WHERE material_tipo = 'cinta_aislante';
                        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
                        VALUES ('cinta_aislante', 'salida', NEW.cinta_aislante, stock_anterior, stock_anterior - NEW.cinta_aislante, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
                    END IF;
                    
                    IF NEW.grapas_blancas > 0 THEN
                        SELECT cantidad_disponible INTO stock_anterior FROM stock_ferretero WHERE material_tipo = 'grapas_blancas';
                        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.grapas_blancas WHERE material_tipo = 'grapas_blancas';
                        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
                        VALUES ('grapas_blancas', 'salida', NEW.grapas_blancas, stock_anterior, stock_anterior - NEW.grapas_blancas, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
                    END IF;
                    
                    IF NEW.grapas_negras > 0 THEN
                        SELECT cantidad_disponible INTO stock_anterior FROM stock_ferretero WHERE material_tipo = 'grapas_negras';
                        UPDATE stock_ferretero SET cantidad_disponible = cantidad_disponible - NEW.grapas_negras WHERE material_tipo = 'grapas_negras';
                        INSERT INTO movimientos_stock_ferretero (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, referencia_tipo, observaciones, usuario_movimiento)
                        VALUES ('grapas_negras', 'salida', NEW.grapas_negras, stock_anterior, stock_anterior - NEW.grapas_negras, NEW.id_ferretero, 'asignacion_ferretero', 'Asignación a técnico', NEW.id_codigo_consumidor);
                    END IF;
                END
            """)
            print("✓ Trigger actualizar_stock_asignacion creado")
            
            connection.commit()
            print("\n✅ Todas las tablas y triggers para gestión de stock de material ferretero han sido creados exitosamente")
            
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión cerrada")

if __name__ == "__main__":
    setup_stock_ferretero_tables()