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
    
    # Buscar técnicos con ciudad asignada
    cursor.execute('''
        SELECT 
            ro.id_codigo_consumidor,
            ro.recurso_operativo_cedula,
            ro.nombre,
            ro.ciudad
        FROM capired.recurso_operativo ro
        WHERE ro.id_roles = 2 
        AND ro.estado = 'Activo'
        AND ro.ciudad IS NOT NULL 
        AND ro.ciudad != ''
        LIMIT 5
    ''')
    
    tecnicos = cursor.fetchall()
    print('=== TÉCNICOS CON CIUDAD ASIGNADA ===')
    for tecnico in tecnicos:
        id_codigo = tecnico['id_codigo_consumidor']
        cedula = tecnico['recurso_operativo_cedula']
        nombre = tecnico['nombre']
        ciudad = tecnico['ciudad']
        print(f'ID: {id_codigo} - Cédula: {cedula} - Nombre: {nombre} - Ciudad: {ciudad}')
    
    cursor.close()
    connection.close()
except Exception as e:
    print(f'Error: {e}')