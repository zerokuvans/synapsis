#!/usr/bin/env python3
import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='732137A031E4b@',
        database='capired'
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
        SELECT ro.recurso_operativo_cedula, ro.nombre, ro.id_roles, r.nombre_rol, ro.estado
        FROM recurso_operativo ro
        LEFT JOIN roles r ON ro.id_roles = r.id_roles
        WHERE ro.id_roles = 1 AND ro.estado = 'Activo'
    ''')
    users = cursor.fetchall()
    print('=== USUARIOS ADMINISTRATIVOS ACTIVOS ===')
    for user in users:
        cedula = user['recurso_operativo_cedula']
        nombre = user['nombre']
        rol_id = user['id_roles']
        rol_nombre = user['nombre_rol']
        estado = user['estado']
        print(f'Cédula: {cedula}')
        print(f'Nombre: {nombre}')
        print(f'Rol ID: {rol_id}')
        print(f'Rol: {rol_nombre}')
        print(f'Estado: {estado}')
        print('---')
    cursor.close()
    connection.close()
except Exception as e:
    print(f'Error: {e}')