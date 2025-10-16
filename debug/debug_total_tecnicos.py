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
    
    supervisor = 'SILVA CASTRO DANIEL ALBERTO'
    
    print('=== TOTAL TÉCNICOS DESDE RECURSO_OPERATIVO ===')
    cursor.execute('''
        SELECT COUNT(*) AS total
        FROM recurso_operativo
        WHERE super = %s AND estado = 'Activo'
    ''', (supervisor,))
    
    result = cursor.fetchone()
    total_recurso_operativo = result['total']
    print(f'Total técnicos activos en recurso_operativo: {total_recurso_operativo}')
    
    print('\n=== TÉCNICOS EN RECURSO_OPERATIVO ===')
    cursor.execute('''
        SELECT recurso_operativo_cedula, nombre
        FROM recurso_operativo
        WHERE super = %s AND estado = 'Activo'
        ORDER BY recurso_operativo_cedula
    ''', (supervisor,))
    
    tecnicos_recurso = cursor.fetchall()
    cedulas_recurso = set(t['recurso_operativo_cedula'] for t in tecnicos_recurso)
    print(f'Cédulas en recurso_operativo: {len(cedulas_recurso)}')
    
    print('\n=== TÉCNICOS EN ASISTENCIA ===')
    cursor.execute('''
        SELECT DISTINCT cedula, tecnico
        FROM asistencia 
        WHERE super = %s 
        AND DATE(fecha_asistencia) = '2025-10-08'
        ORDER BY cedula
    ''', (supervisor,))
    
    tecnicos_asistencia = cursor.fetchall()
    cedulas_asistencia = set(t['cedula'] for t in tecnicos_asistencia)
    print(f'Cédulas en asistencia: {len(cedulas_asistencia)}')
    
    print('\n=== COMPARACIÓN ===')
    solo_en_recurso = cedulas_recurso - cedulas_asistencia
    solo_en_asistencia = cedulas_asistencia - cedulas_recurso
    
    if solo_en_recurso:
        print(f'Técnicos solo en recurso_operativo ({len(solo_en_recurso)}):')
        for cedula in solo_en_recurso:
            tecnico = next(t for t in tecnicos_recurso if t['recurso_operativo_cedula'] == cedula)
            nombre = tecnico['nombre']
            print(f'  {cedula} - {nombre}')
    
    if solo_en_asistencia:
        print(f'Técnicos solo en asistencia ({len(solo_en_asistencia)}):')
        for cedula in solo_en_asistencia:
            tecnico = next(t for t in tecnicos_asistencia if t['cedula'] == cedula)
            nombre = tecnico['tecnico']
            print(f'  {cedula} - {nombre}')
            
except Exception as e:
    print(f'Error: {e}')
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()