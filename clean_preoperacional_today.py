#!/usr/bin/env python3
"""
Script para limpiar registros de preoperacional de hoy para permitir la prueba
"""

import mysql.connector
from datetime import datetime

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

def clean_preoperacional_today():
    """Limpiar registros de preoperacional de hoy para el usuario de prueba"""
    
    connection = get_db_connection()
    if not connection:
        print('No se pudo conectar a la base de datos')
        return
    
    cursor = connection.cursor()
    
    print('=== LIMPIANDO REGISTROS DE PREOPERACIONAL DE HOY ===\n')
    
    # Primero verificar la estructura de la tabla
    print('0. Verificando estructura de la tabla preoperacional:')
    try:
        cursor.execute("DESCRIBE preoperacional")
        columns = cursor.fetchall()
        print('   Columnas disponibles:')
        for column in columns:
            print(f'     {column[0]} - {column[1]}')
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
        return
    
    # Usuario de prueba
    id_codigo_consumidor = '11'  # ID del usuario 1019112308
    fecha_actual = datetime.now().date()
    
    print(f'\nUsuario: {id_codigo_consumidor}')
    print(f'Fecha actual: {fecha_actual}')
    
    # Verificar registros existentes (usando columnas que sabemos que existen)
    print('\n1. Verificando registros existentes para hoy:')
    try:
        cursor.execute("""
            SELECT fecha, placa_vehiculo 
            FROM preoperacional 
            WHERE id_codigo_consumidor = %s 
            AND DATE(CONVERT_TZ(fecha, '+00:00', '-05:00')) = %s
        """, (id_codigo_consumidor, fecha_actual))
        
        registros = cursor.fetchall()
        
        if registros:
            print(f'   Encontrados {len(registros)} registro(s):')
            for registro in registros:
                print(f'     Fecha: {registro[0]}, Placa: {registro[1]}')
        else:
            print('   No hay registros para hoy')
            return
    
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
        return
    
    # Eliminar registros de hoy
    print('\n2. Eliminando registros de hoy:')
    try:
        cursor.execute("""
            DELETE FROM preoperacional 
            WHERE id_codigo_consumidor = %s 
            AND DATE(CONVERT_TZ(fecha, '+00:00', '-05:00')) = %s
        """, (id_codigo_consumidor, fecha_actual))
        
        registros_eliminados = cursor.rowcount
        connection.commit()
        
        print(f'   ✅ Eliminados {registros_eliminados} registro(s)')
        
    except mysql.connector.Error as e:
        print(f'   ❌ Error eliminando registros: {e}')
        connection.rollback()
    
    # Verificar que se eliminaron
    print('\n3. Verificando eliminación:')
    try:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM preoperacional 
            WHERE id_codigo_consumidor = %s 
            AND DATE(CONVERT_TZ(fecha, '+00:00', '-05:00')) = %s
        """, (id_codigo_consumidor, fecha_actual))
        
        count = cursor.fetchone()[0]
        
        if count == 0:
            print('   ✅ No hay registros para hoy - listo para la prueba')
        else:
            print(f'   ❌ Aún quedan {count} registro(s)')
    
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    clean_preoperacional_today()