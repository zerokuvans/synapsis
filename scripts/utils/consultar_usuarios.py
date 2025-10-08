#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error

def consultar_usuarios():
    """Consultar usuarios en la tabla recurso_operativo"""
    try:
        # Configuración de la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@',
            port=3306
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            print("=== USUARIOS EN TABLA RECURSO_OPERATIVO ===")
            cursor.execute("""
                SELECT 
                    id_codigo_consumidor,
                    recurso_operativo_cedula,
                    nombre,
                    estado,
                    id_roles
                FROM recurso_operativo 
                WHERE estado = 'Activo'
                LIMIT 10
            """)
            
            usuarios = cursor.fetchall()
            
            if usuarios:
                print(f"\nEncontrados {len(usuarios)} usuarios activos:")
                print("-" * 80)
                for usuario in usuarios:
                    print(f"ID: {usuario['id_codigo_consumidor']}")
                    print(f"Cédula: {usuario['recurso_operativo_cedula']}")
                    print(f"Nombre: {usuario['nombre']}")
                    print(f"Estado: {usuario['estado']}")
                    print(f"Rol ID: {usuario['id_roles']}")
                    print("-" * 40)
            else:
                print("No se encontraron usuarios activos")
                
    except Error as e:
        print(f"Error de MySQL: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    consultar_usuarios()