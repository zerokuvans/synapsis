#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analizar la estructura de las tablas de mantenimientos MPA
"""

import mysql.connector
from mysql.connector import Error
import sys

# Configuración de la base de datos (usando las credenciales del app.py)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def analyze_mpa_mantenimientos():
    """Analiza la estructura de las tablas mpa_mantenimientos y mpa_categoria_mantenimiento"""
    
    connection = None
    cursor = None
    
    try:
        # Conectar a la base de datos
        print("Conectando a la base de datos...")
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            print("✓ Conexión exitosa a la base de datos")
            cursor = connection.cursor()
            
            # Verificar si existe la tabla mpa_mantenimientos
            print("\n1. Verificando tabla mpa_mantenimientos...")
            cursor.execute("SHOW TABLES LIKE 'mpa_mantenimientos'")
            mpa_mantenimientos_exists = cursor.fetchone() is not None
            
            if mpa_mantenimientos_exists:
                print("✓ Tabla mpa_mantenimientos existe")
                
                # Describir estructura
                cursor.execute("DESCRIBE mpa_mantenimientos")
                columns = cursor.fetchall()
                print("\nEstructura de mpa_mantenimientos:")
                for column in columns:
                    print(f"  - {column[0]}: {column[1]} {column[2]} {column[3]} {column[4]} {column[5]}")
                
                # Contar registros
                cursor.execute("SELECT COUNT(*) FROM mpa_mantenimientos")
                count = cursor.fetchone()[0]
                print(f"\nRegistros en mpa_mantenimientos: {count}")
                
                # Mostrar algunos registros de ejemplo
                if count > 0:
                    cursor.execute("SELECT * FROM mpa_mantenimientos LIMIT 3")
                    records = cursor.fetchall()
                    print("\nPrimeros 3 registros:")
                    for record in records:
                        print(f"  {record}")
            else:
                print("✗ Tabla mpa_mantenimientos NO existe")
                print("\nSugerencia de CREATE TABLE para mpa_mantenimientos:")
                print("""
CREATE TABLE mpa_mantenimientos (
    id_mantenimiento INT AUTO_INCREMENT PRIMARY KEY,
    placa VARCHAR(10) NOT NULL,
    id_codigo_consumidor INT NOT NULL,
    kilometraje INT,
    fecha_mantenimiento DATETIME DEFAULT CURRENT_TIMESTAMP,
    categoria_mantenimiento VARCHAR(50),
    tipo_mantenimiento VARCHAR(100),
    foto_taller LONGTEXT,
    foto_factura LONGTEXT,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (placa) REFERENCES mpa_vehiculos(placa),
    FOREIGN KEY (id_codigo_consumidor) REFERENCES recurso_operativo(id_codigo_consumidor)
);
                """)
            
            # Verificar si existe la tabla mpa_categoria_mantenimiento
            print("\n2. Verificando tabla mpa_categoria_mantenimiento...")
            cursor.execute("SHOW TABLES LIKE 'mpa_categoria_mantenimiento'")
            categoria_exists = cursor.fetchone() is not None
            
            if categoria_exists:
                print("✓ Tabla mpa_categoria_mantenimiento existe")
                
                # Describir estructura
                cursor.execute("DESCRIBE mpa_categoria_mantenimiento")
                columns = cursor.fetchall()
                print("\nEstructura de mpa_categoria_mantenimiento:")
                for column in columns:
                    print(f"  - {column[0]}: {column[1]} {column[2]} {column[3]} {column[4]} {column[5]}")
                
                # Contar registros
                cursor.execute("SELECT COUNT(*) FROM mpa_categoria_mantenimiento")
                count = cursor.fetchone()[0]
                print(f"\nRegistros en mpa_categoria_mantenimiento: {count}")
                
                # Mostrar registros
                if count > 0:
                    cursor.execute("SELECT * FROM mpa_categoria_mantenimiento")
                    records = cursor.fetchall()
                    print("\nTodos los registros:")
                    for record in records:
                        print(f"  {record}")
            else:
                print("✗ Tabla mpa_categoria_mantenimiento NO existe")
                print("\nSugerencia de CREATE TABLE para mpa_categoria_mantenimiento:")
                print("""
CREATE TABLE mpa_categoria_mantenimiento (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    categoria VARCHAR(50) NOT NULL UNIQUE,
    tipo_vehiculo ENUM('Moto', 'Camioneta') NOT NULL,
    tipos_mantenimiento JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Datos iniciales sugeridos
INSERT INTO mpa_categoria_mantenimiento (categoria, tipo_vehiculo, tipos_mantenimiento) VALUES
('Preventivo', 'Moto', '["Cambio de aceite", "Revisión de frenos", "Ajuste de cadena", "Revisión de luces"]'),
('Correctivo', 'Moto', '["Reparación de motor", "Cambio de llantas", "Reparación eléctrica", "Reparación de frenos"]'),
('Preventivo', 'Camioneta', '["Cambio de aceite", "Revisión de frenos", "Alineación", "Balanceo", "Revisión de suspensión"]'),
('Correctivo', 'Camioneta', '["Reparación de motor", "Cambio de llantas", "Reparación eléctrica", "Reparación de transmisión"]');
                """)
            
            # Verificar tablas relacionadas
            print("\n3. Verificando tablas relacionadas...")
            
            # Verificar mpa_vehiculos
            cursor.execute("SHOW TABLES LIKE 'mpa_vehiculos'")
            vehiculos_exists = cursor.fetchone() is not None
            print(f"✓ Tabla mpa_vehiculos: {'Existe' if vehiculos_exists else 'NO existe'}")
            
            if vehiculos_exists:
                cursor.execute("SELECT COUNT(*) FROM mpa_vehiculos")
                count = cursor.fetchone()[0]
                print(f"  Registros: {count}")
                
                # Mostrar estructura de campos relevantes
                cursor.execute("DESCRIBE mpa_vehiculos")
                columns = cursor.fetchall()
                relevant_fields = ['placa', 'tipo_vehiculo', 'id_codigo_consumidor']
                print("  Campos relevantes:")
                for column in columns:
                    if column[0] in relevant_fields:
                        print(f"    - {column[0]}: {column[1]}")
            
            # Verificar recurso_operativo (corregido el nombre)
            cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
            recursos_exists = cursor.fetchone() is not None
            print(f"✓ Tabla recurso_operativo: {'Existe' if recursos_exists else 'NO existe'}")
            
            if recursos_exists:
                cursor.execute("SELECT COUNT(*) FROM recurso_operativo WHERE id_roles = 3")  # Asumiendo que 3 es técnico
                count = cursor.fetchone()[0]
                print(f"  Técnicos disponibles: {count}")
            
            print("\n" + "="*50)
            print("RESUMEN DEL ANÁLISIS")
            print("="*50)
            print(f"mpa_mantenimientos: {'✓' if mpa_mantenimientos_exists else '✗'}")
            print(f"mpa_categoria_mantenimiento: {'✓' if categoria_exists else '✗'}")
            print(f"mpa_vehiculos: {'✓' if vehiculos_exists else '✗'}")
            print(f"recurso_operativo: {'✓' if recursos_exists else '✗'}")
            
            if not mpa_mantenimientos_exists or not categoria_exists:
                print("\n⚠️  ACCIÓN REQUERIDA:")
                print("Algunas tablas necesarias no existen. Ejecutar los CREATE TABLE sugeridos.")
            else:
                print("\n✅ Todas las tablas necesarias existen. Listo para implementar el módulo.")
            
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return False
    
    finally:
        if connection and connection.is_connected():
            if cursor:
                cursor.close()
            connection.close()
            print("\nConexión cerrada.")
    
    return True

if __name__ == "__main__":
    analyze_mpa_mantenimientos()