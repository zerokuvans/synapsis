#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla mpa_soat
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_mpa_soat_table():
    """Verificar la estructura de la tabla mpa_soat"""
    try:
        # Configuración de la base de datos (misma que app.py)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar si la tabla existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = 'mpa_soat'
            """, ('capired',))
            
            table_exists = cursor.fetchone()[0] > 0
            
            if table_exists:
                print("✅ La tabla mpa_soat existe")
                
                # Obtener estructura de la tabla
                cursor.execute("DESCRIBE mpa_soat")
                columns = cursor.fetchall()
                
                print("\n📋 Estructura de la tabla mpa_soat:")
                print("-" * 80)
                print(f"{'Campo':<25} {'Tipo':<20} {'Null':<8} {'Key':<8} {'Default':<15} {'Extra'}")
                print("-" * 80)
                
                for column in columns:
                    field, type_info, null, key, default, extra = column
                    print(f"{field:<25} {type_info:<20} {null:<8} {key:<8} {str(default):<15} {extra}")
                
                # Verificar datos existentes
                cursor.execute("SELECT COUNT(*) FROM mpa_soat")
                count = cursor.fetchone()[0]
                print(f"\n📊 Registros existentes: {count}")
                
                if count > 0:
                    cursor.execute("SELECT * FROM mpa_soat LIMIT 3")
                    sample_data = cursor.fetchall()
                    print("\n📝 Muestra de datos:")
                    for row in sample_data:
                        print(row)
                
            else:
                print("❌ La tabla mpa_soat NO existe")
                print("\n🔧 Creando tabla mpa_soat...")
                
                # Crear tabla mpa_soat
                create_table_sql = """
                CREATE TABLE mpa_soat (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    placa VARCHAR(10) NOT NULL,
                    numero_poliza VARCHAR(50) NOT NULL,
                    fecha_inicio DATE NOT NULL,
                    fecha_vencimiento DATE NOT NULL,
                    tecnico_asignado VARCHAR(20),
                    estado ENUM('vigente', 'proximo_vencer', 'vencido') DEFAULT 'vigente',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_placa (placa),
                    INDEX idx_fecha_vencimiento (fecha_vencimiento),
                    INDEX idx_estado (estado),
                    FOREIGN KEY (placa) REFERENCES mpa_vehiculos(placa) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                
                cursor.execute(create_table_sql)
                connection.commit()
                print("✅ Tabla mpa_soat creada exitosamente")
                
                # Crear trigger para actualizar estado automáticamente
                trigger_sql = """
                CREATE TRIGGER update_soat_estado 
                BEFORE INSERT ON mpa_soat
                FOR EACH ROW
                BEGIN
                    DECLARE dias_restantes INT;
                    SET dias_restantes = DATEDIFF(NEW.fecha_vencimiento, CURDATE());
                    
                    IF dias_restantes < 0 THEN
                        SET NEW.estado = 'vencido';
                    ELSEIF dias_restantes <= 30 THEN
                        SET NEW.estado = 'proximo_vencer';
                    ELSE
                        SET NEW.estado = 'vigente';
                    END IF;
                END
                """
                
                try:
                    cursor.execute(trigger_sql)
                    connection.commit()
                    print("✅ Trigger de estado creado exitosamente")
                except Error as e:
                    print(f"⚠️ Error creando trigger: {e}")
                
                # Crear trigger para actualización
                update_trigger_sql = """
                CREATE TRIGGER update_soat_estado_on_update
                BEFORE UPDATE ON mpa_soat
                FOR EACH ROW
                BEGIN
                    DECLARE dias_restantes INT;
                    SET dias_restantes = DATEDIFF(NEW.fecha_vencimiento, CURDATE());
                    
                    IF dias_restantes < 0 THEN
                        SET NEW.estado = 'vencido';
                    ELSEIF dias_restantes <= 30 THEN
                        SET NEW.estado = 'proximo_vencer';
                    ELSE
                        SET NEW.estado = 'vigente';
                    END IF;
                END
                """
                
                try:
                    cursor.execute(update_trigger_sql)
                    connection.commit()
                    print("✅ Trigger de actualización creado exitosamente")
                except Error as e:
                    print(f"⚠️ Error creando trigger de actualización: {e}")
            
            # Verificar relación con mpa_vehiculos
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = 'mpa_vehiculos'
            """, ('capired',))
            
            vehiculos_exists = cursor.fetchone()[0] > 0
            
            if vehiculos_exists:
                print("\n✅ Tabla mpa_vehiculos existe - relación disponible")
                
                # Verificar algunas placas de ejemplo
                cursor.execute("SELECT placa FROM mpa_vehiculos LIMIT 5")
                placas = cursor.fetchall()
                print(f"📋 Placas disponibles (muestra): {[p[0] for p in placas]}")
            else:
                print("\n❌ Tabla mpa_vehiculos NO existe - verificar dependencias")
            
    except Error as e:
        print(f"❌ Error conectando a la base de datos: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    print("🔍 Verificando estructura de tabla mpa_soat...")
    check_mpa_soat_table()