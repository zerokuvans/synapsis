#!/usr/bin/env python3
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

try:
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor(dictionary=True)
    
    cedula_problema = '1063560283'
    supervisor = 'SILVA CASTRO DANIEL ALBERTO'
    
    print('=== INVESTIGACIÓN DEL TÉCNICO CENTENO LIMA ENDER ===')
    print(f'Cédula: {cedula_problema}')
    
    print('\n1. Estado en recurso_operativo:')
    cursor.execute('''
        SELECT recurso_operativo_cedula, nombre, super, estado, analista
        FROM recurso_operativo
        WHERE recurso_operativo_cedula = %s
    ''', (cedula_problema,))
    
    recurso = cursor.fetchone()
    if recurso:
        print('   Encontrado en recurso_operativo:')
        print(f'   - Nombre: {recurso["nombre"]}')
        print(f'   - Supervisor: {recurso["super"]}')
        print(f'   - Estado: {recurso["estado"]}')
        print(f'   - Analista: {recurso["analista"]}')
    else:
        print('   NO encontrado en recurso_operativo')
    
    print('\n2. Registros en asistencia:')
    cursor.execute('''
        SELECT fecha_asistencia, super, tecnico, carpeta_dia, estado
        FROM asistencia
        WHERE cedula = %s
        ORDER BY fecha_asistencia DESC
        LIMIT 5
    ''', (cedula_problema,))
    
    asistencias = cursor.fetchall()
    if asistencias:
        print(f'   Últimos {len(asistencias)} registros de asistencia:')
        for a in asistencias:
            fecha = a["fecha_asistencia"]
            super_a = a["super"]
            tecnico = a["tecnico"]
            print(f'   - Fecha: {fecha}, Super: {super_a}, Técnico: {tecnico}')
    else:
        print('   NO encontrado en asistencia')
        
    print('\n3. Verificar si existe con otro supervisor en recurso_operativo:')
    cursor.execute('''
        SELECT recurso_operativo_cedula, nombre, super, estado
        FROM recurso_operativo
        WHERE nombre LIKE %s OR nombre LIKE %s
    ''', ('%CENTENO%', '%ENDER%'))
    
    similares = cursor.fetchall()
    if similares:
        print('   Técnicos similares en recurso_operativo:')
        for s in similares:
            cedula = s["recurso_operativo_cedula"]
            nombre = s["nombre"]
            super_s = s["super"]
            estado = s["estado"]
            print(f'   - Cédula: {cedula}, Nombre: {nombre}, Super: {super_s}, Estado: {estado}')
    else:
        print('   No se encontraron técnicos similares')
        
except Exception as e:
    print(f'Error: {e}')
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()