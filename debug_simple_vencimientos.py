#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debugging simple para identificar el problema de vencimientos
"""

import mysql.connector
import requests
from datetime import datetime, timedelta

# Configuración
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': '',
    'database': 'capired'
}

BASE_URL = 'http://127.0.0.1:5000'

def verificar_datos_bd():
    """Verificación rápida de datos en BD"""
    print("=== VERIFICANDO DATOS EN BD ===")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Contar vehículos
        cursor.execute("SELECT COUNT(*) as total FROM parque_automotor")
        total = cursor.fetchone()['total']
        print(f"Total vehículos: {total}")
        
        # Vehículos con fechas
        cursor.execute("""
            SELECT COUNT(*) as total FROM parque_automotor 
            WHERE fecha_vencimiento_soat IS NOT NULL 
               OR fecha_vencimiento_tecnomecanica IS NOT NULL
        """)
        con_fechas = cursor.fetchone()['total']
        print(f"Vehículos con fechas: {con_fechas}")
        
        # Ejemplos
        cursor.execute("""
            SELECT placa, fecha_vencimiento_soat, fecha_vencimiento_tecnomecanica
            FROM parque_automotor 
            WHERE fecha_vencimiento_soat IS NOT NULL 
               OR fecha_vencimiento_tecnomecanica IS NOT NULL
            LIMIT 3
        """)
        ejemplos = cursor.fetchall()
        
        print("Ejemplos:")
        for ej in ejemplos:
            print(f"  {ej['placa']}: SOAT={ej['fecha_vencimiento_soat']}, TM={ej['fecha_vencimiento_tecnomecanica']}")
            
        conn.close()
        return con_fechas > 0
        
    except Exception as e:
        print(f"Error BD: {e}")
        return False

def verificar_usuario_logistica():
    """Verificar usuario logística"""
    print("\n=== VERIFICANDO USUARIO LOGÍSTICA ===")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT recurso_operativo_cedula, recurso_operativo_nombre 
            FROM recurso_operativo 
            WHERE id_roles = '5' AND recurso_operativo_estado = 'activo'
            LIMIT 1
        """)
        usuario = cursor.fetchone()
        
        if usuario:
            print(f"Usuario encontrado: {usuario['recurso_operativo_cedula']} - {usuario['recurso_operativo_nombre']}")
            conn.close()
            return usuario
        else:
            print("No hay usuarios logística")
            conn.close()
            return None
            
    except Exception as e:
        print(f"Error verificando usuario: {e}")
        return None

def probar_endpoint_simple():
    """Prueba simple del endpoint sin autenticación"""
    print("\n=== PROBANDO ENDPOINT (sin auth) ===")
    try:
        response = requests.get(f"{BASE_URL}/api/vehiculos/vencimientos")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("Endpoint requiere autenticación (correcto)")
        elif response.status_code == 200:
            data = response.json()
            print(f"Respuesta: {data}")
        else:
            print(f"Respuesta inesperada: {response.text[:200]}")
            
    except Exception as e:
        print(f"Error probando endpoint: {e}")

def main():
    print("DEBUGGING SIMPLE - MÓDULO VENCIMIENTOS")
    print("=" * 40)
    
    # Verificar datos
    hay_datos = verificar_datos_bd()
    
    # Verificar usuario
    usuario = verificar_usuario_logistica()
    
    # Probar endpoint
    probar_endpoint_simple()
    
    print("\n=== RESUMEN ===")
    print(f"Hay datos de vencimientos: {'SÍ' if hay_datos else 'NO'}")
    print(f"Hay usuario logística: {'SÍ' if usuario else 'NO'}")
    
    if not hay_datos:
        print("\n⚠️  PROBLEMA: No hay datos de vencimientos en la BD")
        print("   Solución: Agregar fechas de vencimiento a los vehículos")
    
    if not usuario:
        print("\n⚠️  PROBLEMA: No hay usuarios con rol logística")
        print("   Solución: Crear usuario con id_roles = '5'")
        
    print("\nDebugging completado.")

if __name__ == "__main__":
    main()