#!/usr/bin/env python3
"""
Script para verificar el usuario 11 en recurso_operativo
"""

import mysql.connector

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        return connection
    except mysql.connector.Error as e:
        print(f'Error al conectar a la base de datos: {e}')
        return None

def check_user_11():
    """Verificar el usuario 11 en recurso_operativo"""
    
    connection = get_db_connection()
    if not connection:
        print('No se pudo conectar a la base de datos')
        return
    
    cursor = connection.cursor()
    
    print('=== VERIFICANDO USUARIO 11 EN RECURSO_OPERATIVO ===\n')
    
    # 1. Verificar si el usuario 11 existe
    print('1. Verificando si el usuario 11 existe:')
    try:
        cursor.execute("SELECT id_codigo_consumidor FROM recurso_operativo WHERE id_codigo_consumidor = %s", ('11',))
        usuario_existe = cursor.fetchone()
        
        if usuario_existe:
            print(f'   ✅ Usuario 11 existe: {usuario_existe}')
        else:
            print('   ❌ Usuario 11 NO existe')
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
    
    # 2. Verificar con entero
    print('\n2. Verificando con entero:')
    try:
        cursor.execute("SELECT id_codigo_consumidor FROM recurso_operativo WHERE id_codigo_consumidor = %s", (11,))
        usuario_existe = cursor.fetchone()
        
        if usuario_existe:
            print(f'   ✅ Usuario 11 existe (entero): {usuario_existe}')
        else:
            print('   ❌ Usuario 11 NO existe (entero)')
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
    
    # 3. Listar todos los usuarios para ver qué IDs existen
    print('\n3. Listando primeros 10 usuarios:')
    try:
        cursor.execute("SELECT id_codigo_consumidor, nombre FROM recurso_operativo LIMIT 10")
        usuarios = cursor.fetchall()
        
        if usuarios:
            print('   Usuarios encontrados:')
            for usuario in usuarios:
                print(f'     ID: {usuario[0]}, Nombre: {usuario[1]}')
        else:
            print('   No hay usuarios')
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    check_user_11()