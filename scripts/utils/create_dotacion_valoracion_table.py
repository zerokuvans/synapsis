#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error

def create_dotacion_valoracion_table():
    """Crear tabla para gestionar el estado de valoración de elementos de dotación"""
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Crear tabla de configuración de valoración de elementos
            create_table_query = """
            CREATE TABLE IF NOT EXISTS dotacion_elementos_config (
                id INT AUTO_INCREMENT PRIMARY KEY,
                elemento VARCHAR(50) NOT NULL UNIQUE,
                es_valorado BOOLEAN NOT NULL DEFAULT FALSE,
                precio_unitario DECIMAL(10,2) DEFAULT 0.00,
                descripcion TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            
            cursor.execute(create_table_query)
            print("Tabla 'dotacion_elementos_config' creada exitosamente")
            
            # Insertar configuración inicial de elementos
            elementos_config = [
                ('pantalon', True, 45000.00, 'Pantalón de trabajo'),
                ('camisetagris', False, 25000.00, 'Camiseta gris'),
                ('guerrera', True, 65000.00, 'Guerrera de trabajo'),
                ('camisetapolo', False, 30000.00, 'Camiseta polo'),
                ('guantes_nitrilo', False, 8000.00, 'Guantes de nitrilo'),
                ('guantes_carnaza', True, 15000.00, 'Guantes de carnaza'),
                ('gafas', True, 25000.00, 'Gafas de seguridad'),
                ('gorra', False, 12000.00, 'Gorra'),
                ('casco', True, 35000.00, 'Casco de seguridad'),
                ('botas', True, 85000.00, 'Botas de seguridad')
            ]
            
            insert_query = """
            INSERT IGNORE INTO dotacion_elementos_config 
            (elemento, es_valorado, precio_unitario, descripcion) 
            VALUES (%s, %s, %s, %s)
            """
            
            cursor.executemany(insert_query, elementos_config)
            connection.commit()
            
            print(f"Insertados {cursor.rowcount} elementos de configuración")
            
            # Verificar los datos insertados
            cursor.execute("SELECT * FROM dotacion_elementos_config ORDER BY elemento")
            elementos = cursor.fetchall()
            
            print("\nConfiguración de elementos de dotación:")
            for elemento in elementos:
                valorado = "VALORADO" if elemento[2] else "NO VALORADO"
                print(f"  {elemento[1]}: {valorado} - ${elemento[3]:,.2f}")
                
    except Error as e:
        print(f"Error de base de datos: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    create_dotacion_valoracion_table()