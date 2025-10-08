#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error

def verificar_credenciales():
    """Verificar las credenciales de la analista ESPITIA BARON LICED JOANA"""
    
    try:
        # Configuración de conexión
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            print("=== VERIFICANDO CREDENCIALES DE ANALISTA ===")
            print()
            
            # Buscar la analista por nombre
            print("1. Buscando analista por nombre...")
            cursor.execute("""
                SELECT 
                    id_codigo_consumidor,
                    recurso_operativo_cedula,
                    nombre,
                    analista,
                    estado,
                    id_roles
                FROM recurso_operativo 
                WHERE nombre LIKE '%ESPITIA BARON LICED JOANA%'
                OR analista LIKE '%ESPITIA BARON LICED JOANA%'
            """)
            
            analistas = cursor.fetchall()
            
            if analistas:
                print(f"✓ Encontrados {len(analistas)} registros:")
                for analista in analistas:
                    print(f"  - ID: {analista['id_codigo_consumidor']}")
                    print(f"    Cédula: {analista['recurso_operativo_cedula']}")
                    print(f"    Nombre: {analista['nombre']}")
                    print(f"    Analista: {analista['analista']}")
                    print(f"    Estado: {analista['estado']}")
                    print(f"    ID Roles: {analista['id_roles']}")
                    print()
            else:
                print("✗ No se encontró la analista por nombre")
            
            # Buscar por cédula específica
            print("2. Buscando por cédula 1002407090...")
            cursor.execute("""
                SELECT 
                    id_codigo_consumidor,
                    recurso_operativo_cedula,
                    nombre,
                    analista,
                    estado,
                    id_roles
                FROM recurso_operativo 
                WHERE recurso_operativo_cedula = '1002407090'
            """)
            
            usuario_cedula = cursor.fetchone()
            
            if usuario_cedula:
                print("✓ Usuario encontrado por cédula:")
                print(f"  - ID: {usuario_cedula['id_codigo_consumidor']}")
                print(f"  - Cédula: {usuario_cedula['recurso_operativo_cedula']}")
                print(f"  - Nombre: {usuario_cedula['nombre']}")
                print(f"  - Analista: {usuario_cedula['analista']}")
                print(f"  - Estado: {usuario_cedula['estado']}")
                print(f"  - ID Roles: {usuario_cedula['id_roles']}")
                print()
            else:
                print("✗ No se encontró usuario con cédula 1002407090")
            
            # Buscar todos los analistas activos
            print("3. Buscando todos los analistas activos...")
            cursor.execute("""
                SELECT DISTINCT
                    id_codigo_consumidor,
                    recurso_operativo_cedula,
                    nombre,
                    analista,
                    estado,
                    id_roles
                FROM recurso_operativo 
                WHERE analista IS NOT NULL 
                AND analista != ''
                AND estado = 'Activo'
                ORDER BY nombre
            """)
            
            analistas_activos = cursor.fetchall()
            
            if analistas_activos:
                print(f"✓ Encontrados {len(analistas_activos)} analistas activos:")
                for analista in analistas_activos:
                    print(f"  - {analista['nombre']} (Cédula: {analista['recurso_operativo_cedula']}, ID: {analista['id_codigo_consumidor']})")
            else:
                print("✗ No se encontraron analistas activos")
            
            print("\n=== VERIFICACIÓN COMPLETADA ===")
            
    except Error as e:
        print(f"Error de MySQL: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    verificar_credenciales()