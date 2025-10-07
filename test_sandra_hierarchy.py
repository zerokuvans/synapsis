#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la corrección de la consulta de asistencia para Sandra
Ahora debe mostrar solo técnicos directos (que tienen a Sandra en la columna super)
"""

import mysql.connector
import requests
from datetime import datetime

# Configuración
SUPERVISOR = "CORTES CUERVO SANDRA CECILIA"
FECHA = "2023-10-07"
BASE_URL = "http://localhost:8080"

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def verificar_tecnicos_directos():
    """Verificar cuántos técnicos tienen directamente a Sandra como supervisor"""
    print("=== VERIFICACIÓN DIRECTA EN BASE DE DATOS ===")
    
    connection = get_db_connection()
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    # Contar técnicos directos de Sandra
    cursor.execute("""
        SELECT COUNT(*) as total_directos
        FROM recurso_operativo 
        WHERE super = %s AND estado = 'Activo'
    """, (SUPERVISOR,))
    
    result = cursor.fetchone()
    print(f"Sandra tiene {result['total_directos']} técnicos directos bajo ella")
    
    # Mostrar algunos técnicos directos
    cursor.execute("""
        SELECT nombre, cargo, recurso_operativo_cedula
        FROM recurso_operativo 
        WHERE super = %s AND estado = 'Activo'
        ORDER BY nombre
        LIMIT 10
    """, (SUPERVISOR,))
    
    tecnicos_directos = cursor.fetchall()
    print("\nPrimeros 10 técnicos directos:")
    for tecnico in tecnicos_directos:
        print(f"  - {tecnico['nombre']} ({tecnico['cargo']}) - Cédula: {tecnico['recurso_operativo_cedula']}")
    
    cursor.close()
    connection.close()

def test_consultar_asistencia():
    """Probar la consulta de asistencia para Sandra"""
    print("\n=== PROBANDO CONSULTA DE ASISTENCIA PARA SANDRA ===")
    
    # Hacer la petición al API
    url = f"{BASE_URL}/api/asistencia/consultar"
    params = {
        'supervisor': SUPERVISOR,
        'fecha': FECHA
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Success: {data.get('success')}")
                print(f"Total registros: {data.get('total', 0)}")
                
                if data.get('success') and data.get('registros'):
                    registros = data['registros']
                    print(f"\n=== ANÁLISIS DE REGISTROS ===")
                    print(f"Total de registros devueltos: {len(registros)}")
                    
                    # Verificar que todos los registros tienen a Sandra como supervisor directo
                    registros_correctos = 0
                    registros_incorrectos = 0
                    
                    for registro in registros:
                        if registro.get('super') == SUPERVISOR:
                            registros_correctos += 1
                        else:
                            registros_incorrectos += 1
                            print(f"  ❌ INCORRECTO: {registro.get('tecnico')} tiene supervisor: {registro.get('super')}")
                    
                    print(f"✅ Registros correctos (supervisor directo): {registros_correctos}")
                    print(f"❌ Registros incorrectos (supervisor indirecto): {registros_incorrectos}")
                    
                    if registros_incorrectos == 0:
                        print("🎉 ¡CORRECCIÓN EXITOSA! Todos los registros son de técnicos directos de Sandra")
                    else:
                        print("⚠️  Aún hay registros incorrectos")
                        
                else:
                    print("No se encontraron registros o hubo un error")
                    
            except ValueError as e:
                print(f"Error al parsear JSON: {e}")
                print(f"Respuesta recibida: {response.text[:200]}...")
        else:
            print(f"Error HTTP: {response.text}")
            
    except Exception as e:
        print(f"Error en la petición: {str(e)}")

def main():
    """Función principal"""
    print("=" * 60)
    print("PRUEBA DE CORRECCIÓN: CONSULTA DIRECTA PARA SANDRA")
    print(f"Supervisor: {SUPERVISOR}")
    print(f"Fecha: {FECHA}")
    print(f"Fecha de prueba: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Verificar técnicos directos en la base de datos
    verificar_tecnicos_directos()
    
    # Probar la API corregida
    test_consultar_asistencia()

if __name__ == "__main__":
    main()