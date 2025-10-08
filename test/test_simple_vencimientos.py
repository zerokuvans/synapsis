#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para verificar datos de vencimientos
"""

import mysql.connector
import sys

# Configuración de la base de datos
DB_CONFIG = {
    'host': '192.168.1.100',
    'database': 'capired',
    'user': 'usuario_app',
    'password': 'Capired2024*',
    'port': 3306
}

def main():
    try:
        print("Conectando a la base de datos...")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        print("✅ Conexión exitosa")
        
        # 1. Verificar tabla parque_automotor
        print("\n1. Verificando tabla parque_automotor:")
        cursor.execute("SELECT COUNT(*) as total FROM parque_automotor")
        total = cursor.fetchone()['total']
        print(f"   Total vehículos: {total}")
        
        # 2. Verificar vehículos con fechas de vencimiento
        cursor.execute("""
            SELECT COUNT(*) as con_fechas
            FROM parque_automotor 
            WHERE soat_vencimiento IS NOT NULL 
               OR tecnomecanica_vencimiento IS NOT NULL
        """)
        con_fechas = cursor.fetchone()['con_fechas']
        print(f"   Vehículos con fechas de vencimiento: {con_fechas}")
        
        # 3. Mostrar algunos ejemplos
        cursor.execute("""
            SELECT 
                placa,
                soat_vencimiento,
                tecnomecanica_vencimiento
            FROM parque_automotor 
            WHERE soat_vencimiento IS NOT NULL 
               OR tecnomecanica_vencimiento IS NOT NULL
            LIMIT 3
        """)
        
        ejemplos = cursor.fetchall()
        print(f"\n2. Ejemplos de vehículos con fechas:")
        for vehiculo in ejemplos:
            print(f"   - Placa: {vehiculo['placa']}")
            print(f"     SOAT: {vehiculo['soat_vencimiento']}")
            print(f"     Tecnomecánica: {vehiculo['tecnomecanica_vencimiento']}")
        
        # 4. Verificar usuarios de logística
        print("\n3. Verificando usuarios de logística:")
        cursor.execute("""
            SELECT COUNT(*) as total_logistica
            FROM recurso_operativo 
            WHERE id_roles = 5
        """)
        total_logistica = cursor.fetchone()['total_logistica']
        print(f"   Usuarios con rol logística: {total_logistica}")
        
        if total_logistica > 0:
            cursor.execute("""
                SELECT 
                    recurso_operativo_cedula,
                    nombre,
                    estado
                FROM recurso_operativo 
                WHERE id_roles = 5
                LIMIT 3
            """)
            
            usuarios = cursor.fetchall()
            print("   Usuarios de logística:")
            for usuario in usuarios:
                print(f"     - Cédula: {usuario['recurso_operativo_cedula']}")
                print(f"       Nombre: {usuario['nombre']}")
                print(f"       Estado: {usuario['estado']}")
        
        cursor.close()
        connection.close()
        print("\n✅ Verificación completada")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()