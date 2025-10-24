#!/usr/bin/env python3
"""
Script para verificar usuarios en la base de datos
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

def check_users():
    """Verificar usuarios en la base de datos"""
    
    connection = get_db_connection()
    if not connection:
        print('No se pudo conectar a la base de datos')
        return
    
    cursor = connection.cursor()
    
    print('=== VERIFICANDO USUARIOS EN LA BASE DE DATOS ===\n')
    
    # Verificar estructura de la tabla usuarios
    print('1. Estructura de la tabla usuarios:')
    try:
        cursor.execute("DESCRIBE usuarios")
        columns = cursor.fetchall()
        for column in columns:
            print(f'   {column[0]} - {column[1]}')
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
    
    print('\n2. Buscando usuario 1019112308:')
    try:
        cursor.execute("SELECT * FROM usuarios WHERE usuario_cedula = %s", (1019112308,))
        user = cursor.fetchone()
        if user:
            print(f'   Usuario encontrado: {user}')
        else:
            print('   Usuario NO encontrado')
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
    
    print('\n3. Primeros 10 usuarios en la tabla:')
    try:
        cursor.execute("SELECT idusuarios, usuario_nombre, usuario_cedula, usuario_contraseña FROM usuarios LIMIT 10")
        users = cursor.fetchall()
        for user in users:
            print(f'   ID: {user[0]}, Nombre: {user[1]}, Cédula: {user[2]}, Password: {user[3]}')
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
    
    print('\n4. Total de usuarios en la tabla:')
    try:
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        print(f'   Total usuarios: {count}')
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
    
    # Verificar también la tabla recurso_operativo que parece ser la principal
    print('\n5. Verificando tabla recurso_operativo:')
    try:
        cursor.execute("DESCRIBE recurso_operativo")
        columns = cursor.fetchall()
        print('   Estructura de recurso_operativo:')
        for column in columns:
            print(f'     {column[0]} - {column[1]}')
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
    
    print('\n6. Buscando usuario 1019112308 en recurso_operativo:')
    try:
        cursor.execute("SELECT * FROM recurso_operativo WHERE recurso_operativo_cedula = %s", ('1019112308',))
        user = cursor.fetchone()
        if user:
            print(f'   Usuario encontrado en recurso_operativo: {user}')
        else:
            print('   Usuario NO encontrado en recurso_operativo')
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    check_users()