#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar si las tablas de mantenimientos existen
"""

import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def check_tables():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Verificar si existe mpa_mantenimientos
        cursor.execute("SHOW TABLES LIKE 'mpa_mantenimientos'")
        mpa_mantenimientos_exists = cursor.fetchone() is not None
        
        # Verificar si existe mpa_categoria_mantenimiento
        cursor.execute("SHOW TABLES LIKE 'mpa_categoria_mantenimiento'")
        mpa_categoria_exists = cursor.fetchone() is not None
        
        print("=== VERIFICACIÓN DE TABLAS DE MANTENIMIENTOS ===")
        print(f"mpa_mantenimientos: {'✅ Existe' if mpa_mantenimientos_exists else '❌ No existe'}")
        print(f"mpa_categoria_mantenimiento: {'✅ Existe' if mpa_categoria_exists else '❌ No existe'}")
        
        if not mpa_mantenimientos_exists or not mpa_categoria_exists:
            print("\n=== CREANDO TABLAS FALTANTES ===")
            
            if not mpa_categoria_exists:
                print("Creando tabla mpa_categoria_mantenimiento...")
                cursor.execute("""
                CREATE TABLE mpa_categoria_mantenimiento (
                    id_categoria_mantenimiento INT AUTO_INCREMENT PRIMARY KEY,
                    categoria VARCHAR(50) NOT NULL,
                    tipo_vehiculo VARCHAR(50) NOT NULL,
                    tipo_mantenimiento VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # Insertar datos iniciales
                cursor.execute("""
                INSERT INTO mpa_categoria_mantenimiento (categoria, tipo_vehiculo, tipo_mantenimiento) VALUES
                ('Preventivo', 'Moto', 'Cambio de aceite'),
                ('Preventivo', 'Moto', 'Revisión de frenos'),
                ('Preventivo', 'Moto', 'Ajuste de cadena'),
                ('Preventivo', 'Moto', 'Revisión de luces'),
                ('Correctivo', 'Moto', 'Reparación de motor'),
                ('Correctivo', 'Moto', 'Cambio de llantas'),
                ('Correctivo', 'Moto', 'Reparación eléctrica'),
                ('Correctivo', 'Moto', 'Reparación de frenos'),
                ('Preventivo', 'Camioneta', 'Cambio de aceite'),
                ('Preventivo', 'Camioneta', 'Revisión de frenos'),
                ('Preventivo', 'Camioneta', 'Alineación'),
                ('Preventivo', 'Camioneta', 'Balanceo'),
                ('Preventivo', 'Camioneta', 'Revisión de suspensión'),
                ('Correctivo', 'Camioneta', 'Reparación de motor'),
                ('Correctivo', 'Camioneta', 'Cambio de llantas'),
                ('Correctivo', 'Camioneta', 'Reparación eléctrica'),
                ('Correctivo', 'Camioneta', 'Reparación de transmisión')
                """)
                print("✅ Tabla mpa_categoria_mantenimiento creada con datos iniciales")
            
            if not mpa_mantenimientos_exists:
                print("Creando tabla mpa_mantenimientos...")
                cursor.execute("""
                CREATE TABLE mpa_mantenimientos (
                    id_mpa_mantenimientos INT AUTO_INCREMENT PRIMARY KEY,
                    placa VARCHAR(10) NOT NULL,
                    fecha_mantenimiento DATETIME NOT NULL,
                    kilometraje INT,
                    id_categoria_mantenimiento INT,
                    observaciones TEXT,
                    foto_taller VARCHAR(255),
                    foto_factura VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (placa) REFERENCES mpa_vehiculos(placa),
                    FOREIGN KEY (id_categoria_mantenimiento) REFERENCES mpa_categoria_mantenimiento(id_categoria_mantenimiento)
                )
                """)
                print("✅ Tabla mpa_mantenimientos creada")
            
            connection.commit()
            print("\n✅ Todas las tablas de mantenimientos están listas")
        else:
            print("\n✅ Todas las tablas de mantenimientos ya existen")
            
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    check_tables()