#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear la tabla hora_preoperacional
Esta tabla almacenará la hora límite configurable para el preoperacional
"""

import mysql.connector
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def crear_tabla_hora_preoperacional():
    """Crear tabla hora_preoperacional para gestionar la hora límite"""
    try:
        # Configuración de la base de datos
        db_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DB', 'capired'),
            'port': int(os.getenv('MYSQL_PORT', 3306))
        }
        
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("🔧 Creando tabla hora_preoperacional...")
            
            # Crear tabla hora_preoperacional
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hora_preoperacional (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    hora_limite TIME NOT NULL DEFAULT '10:00:00',
                    descripcion VARCHAR(255) DEFAULT 'Hora límite para registro de preoperacional',
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    usuario_creacion VARCHAR(100) DEFAULT 'sistema',
                    usuario_actualizacion VARCHAR(100) DEFAULT 'sistema'
                )
            """)
            
            print("✅ Tabla hora_preoperacional creada exitosamente")
            
            # Verificar si ya existe un registro
            cursor.execute("SELECT COUNT(*) FROM hora_preoperacional")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Insertar registro por defecto
                cursor.execute("""
                    INSERT INTO hora_preoperacional (hora_limite, descripcion, activo, usuario_creacion)
                    VALUES ('10:00:00', 'Hora límite por defecto para registro de preoperacional', TRUE, 'sistema')
                """)
                print("✅ Registro por defecto insertado (10:00 AM)")
            else:
                print("ℹ️  Ya existe un registro en la tabla")
            
            # Confirmar cambios
            connection.commit()
            
            # Mostrar estructura de la tabla
            print("\n📋 Estructura de la tabla hora_preoperacional:")
            cursor.execute("DESCRIBE hora_preoperacional")
            columns = cursor.fetchall()
            
            for column in columns:
                print(f"  - {column[0]:<20} | {column[1]:<15} | NULL: {column[2]} | Key: {column[3]}")
            
            # Mostrar registro actual
            cursor.execute("SELECT * FROM hora_preoperacional LIMIT 1")
            registro = cursor.fetchone()
            if registro:
                print(f"\n⏰ Hora límite actual: {registro[1]} ({registro[2]})")
            
            print("\n🎉 Tabla hora_preoperacional configurada correctamente")
            
    except mysql.connector.Error as e:
        print(f"❌ Error de MySQL: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Conexión cerrada")

if __name__ == "__main__":
    crear_tabla_hora_preoperacional()