#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from datetime import datetime
import pytz

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def debug_registro_5992():
    """Debug específico para el registro 5992"""
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        print("🔍 DEBUG ESPECÍFICO - REGISTRO 5992")
        print("=" * 60)
        
        # 1. Verificar si existe el registro 5992
        print("1️⃣ Verificando existencia del registro 5992...")
        cursor.execute("""
            SELECT id_asistencia, cedula, tecnico, hora_inicio, estado, novedad, 
                   DATE(fecha_asistencia) as fecha_registro,
                   fecha_asistencia
            FROM asistencia 
            WHERE id_asistencia = 5992
        """)
        
        registro_5992 = cursor.fetchone()
        
        if registro_5992:
            print("✅ Registro 5992 ENCONTRADO:")
            for key, value in registro_5992.items():
                print(f"   {key}: {value}")
        else:
            print("❌ Registro 5992 NO ENCONTRADO")
            
            # Buscar registros cercanos
            print("\n🔍 Buscando registros cercanos al ID 5992...")
            cursor.execute("""
                SELECT id_asistencia, cedula, tecnico, DATE(fecha_asistencia) as fecha_registro
                FROM asistencia 
                WHERE id_asistencia BETWEEN 5990 AND 5995
                ORDER BY id_asistencia
            """)
            
            registros_cercanos = cursor.fetchall()
            if registros_cercanos:
                print("📋 Registros cercanos encontrados:")
                for reg in registros_cercanos:
                    print(f"   ID: {reg['id_asistencia']}, Cédula: {reg['cedula']}, Técnico: {reg['tecnico']}")
            else:
                print("❌ No hay registros cercanos")
        
        # 2. Verificar registros de hoy
        bogota_tz = pytz.timezone('America/Bogota')
        fecha_hoy = datetime.now(bogota_tz).date()
        
        print(f"\n2️⃣ Verificando registros de hoy ({fecha_hoy})...")
        cursor.execute("""
            SELECT id_asistencia, cedula, tecnico, hora_inicio, estado, novedad
            FROM asistencia 
            WHERE DATE(fecha_asistencia) = %s
            ORDER BY id_asistencia DESC
            LIMIT 10
        """, (fecha_hoy,))
        
        registros_hoy = cursor.fetchall()
        
        if registros_hoy:
            print("📋 Últimos 10 registros de hoy:")
            for reg in registros_hoy:
                print(f"   ID: {reg['id_asistencia']}, Cédula: {reg['cedula']}, Técnico: {reg['tecnico']}")
                print(f"      Hora: {reg['hora_inicio']}, Estado: {reg['estado']}, Novedad: {reg['novedad']}")
        else:
            print("❌ No hay registros para hoy")
        
        # 3. Buscar por cédula específica si el usuario tiene una cédula asociada
        print(f"\n3️⃣ Buscando registros por cédulas comunes...")
        cedulas_comunes = ['5694500', '1032402333', '1019112308']  # Cédulas que aparecen en logs
        
        for cedula in cedulas_comunes:
            cursor.execute("""
                SELECT id_asistencia, cedula, tecnico, hora_inicio, estado, novedad,
                       DATE(fecha_asistencia) as fecha_registro
                FROM asistencia 
                WHERE cedula = %s AND DATE(fecha_asistencia) = %s
                ORDER BY fecha_asistencia DESC
                LIMIT 1
            """, (cedula, fecha_hoy))
            
            resultado = cursor.fetchone()
            if resultado:
                print(f"✅ Registro encontrado para cédula {cedula}:")
                print(f"   ID: {resultado['id_asistencia']}, Técnico: {resultado['tecnico']}")
                print(f"   Hora: {resultado['hora_inicio']}, Estado: {resultado['estado']}, Novedad: {resultado['novedad']}")
        
        # 4. Verificar el último registro actualizado
        print(f"\n4️⃣ Último registro actualizado...")
        cursor.execute("""
            SELECT id_asistencia, cedula, tecnico, hora_inicio, estado, novedad,
                   DATE(fecha_asistencia) as fecha_registro
            FROM asistencia 
            ORDER BY id_asistencia DESC
            LIMIT 5
        """)
        
        ultimos_registros = cursor.fetchall()
        if ultimos_registros:
            print("📋 Últimos 5 registros en la base de datos:")
            for reg in ultimos_registros:
                print(f"   ID: {reg['id_asistencia']}, Cédula: {reg['cedula']}, Técnico: {reg['tecnico']}")
                print(f"      Hora: {reg['hora_inicio']}, Estado: {reg['estado']}, Novedad: {reg['novedad']}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    debug_registro_5992()