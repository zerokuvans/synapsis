#!/usr/bin/env python3
"""
Script para probar directamente la validación de mantenimientos
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

def test_validation_logic():
    print('=== PROBANDO LÓGICA DE VALIDACIÓN DIRECTAMENTE ===')
    
    connection = get_db_connection()
    if not connection:
        print('No se pudo conectar a la base de datos')
        return
    
    cursor = connection.cursor()
    
    # Simular la validación exacta del código
    placa_vehiculo = 'TON81E'
    
    print(f'1. Verificando mantenimientos abiertos para {placa_vehiculo}...')
    
    cursor.execute("""
        SELECT COUNT(*) FROM mpa_mantenimientos 
        WHERE placa = %s AND estado = 'Abierto'
    """, (placa_vehiculo,))
    
    mantenimientos_abiertos = cursor.fetchone()[0]
    
    print(f'   Mantenimientos abiertos encontrados: {mantenimientos_abiertos}')
    
    if mantenimientos_abiertos > 0:
        print(f'   ✅ VALIDACIÓN CORRECTA: Se encontraron {mantenimientos_abiertos} mantenimiento(s) abierto(s)')
        print(f'   📝 Mensaje que debería mostrarse:')
        print(f'      "No se puede completar el preoperacional. El vehículo {placa_vehiculo} tiene {mantenimientos_abiertos} mantenimiento(s) abierto(s) pendiente(s). Contacte al área de MPA para finalizar el mantenimiento antes de continuar."')
        
        # Mostrar detalles del mantenimiento
        cursor.execute("""
            SELECT placa, estado, fecha_mantenimiento, tipo_mantenimiento, tecnico
            FROM mpa_mantenimientos 
            WHERE placa = %s AND estado = 'Abierto'
        """, (placa_vehiculo,))
        
        mantenimientos = cursor.fetchall()
        print(f'\n   📋 Detalles de los mantenimientos abiertos:')
        for mant in mantenimientos:
            print(f'      - Placa: {mant[0]}, Estado: {mant[1]}, Fecha: {mant[2]}, Tipo: {mant[3]}, Técnico: {mant[4]}')
    else:
        print(f'   ❌ ERROR: No se encontraron mantenimientos abiertos (la validación NO debería bloquear)')
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    test_validation_logic()