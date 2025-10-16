#!/usr/bin/env python3
import mysql.connector

# Configuración de la base de datos
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
    fecha = '2025-10-08'
    
    print('=== CONSULTA DIRECTA (16 técnicos) ===')
    cursor.execute('''
        SELECT DISTINCT cedula, tecnico
        FROM asistencia 
        WHERE super = %s 
        AND DATE(fecha_asistencia) = %s
        ORDER BY cedula
    ''', (supervisor, fecha))
    
    tecnicos_directa = cursor.fetchall()
    print(f'Total técnicos únicos: {len(tecnicos_directa)}')
    cedulas_directa = set(t['cedula'] for t in tecnicos_directa)
    
    print('\n=== CONSULTA DEL ENDPOINT (15 técnicos) ===')
    cursor.execute('''
        SELECT DISTINCT a.cedula, a.tecnico
        FROM asistencia a
        WHERE a.super = %s AND DATE(a.fecha_asistencia) = %s
        AND a.id_asistencia = (
            SELECT MAX(a2.id_asistencia)
            FROM asistencia a2
            WHERE a2.cedula = a.cedula 
            AND a2.super = %s 
            AND DATE(a2.fecha_asistencia) = %s
        )
        ORDER BY a.cedula
    ''', (supervisor, fecha, supervisor, fecha))
    
    tecnicos_endpoint = cursor.fetchall()
    print(f'Total técnicos únicos: {len(tecnicos_endpoint)}')
    cedulas_endpoint = set(t['cedula'] for t in tecnicos_endpoint)
    
    print('\n=== TÉCNICO FALTANTE ===')
    faltante = cedulas_directa - cedulas_endpoint
    if faltante:
        cedula_faltante = list(faltante)[0]
        print(f'Cédula faltante: {cedula_faltante}')
        
        # Investigar por qué falta este técnico
        cursor.execute('''
            SELECT id_asistencia, cedula, tecnico, super, fecha_asistencia, carpeta_dia
            FROM asistencia 
            WHERE cedula = %s
            ORDER BY fecha_asistencia DESC, id_asistencia DESC
            LIMIT 5
        ''', (cedula_faltante,))
        
        registros_tecnico = cursor.fetchall()
        print(f'Últimos registros del técnico {cedula_faltante}:')
        for r in registros_tecnico:
            print(f'  ID: {r["id_asistencia"]}, Fecha: {r["fecha_asistencia"]}, Super: {r["super"]}, Carpeta: {r["carpeta_dia"]}')
    else:
        print('No hay técnicos faltantes (esto no debería pasar)')
        
except Exception as e:
    print(f'Error: {e}')
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()