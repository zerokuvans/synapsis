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

def debug_actualizar_campo():
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Obtener fecha actual en zona horaria de Bogotá
        bogota_tz = pytz.timezone('America/Bogota')
        fecha_actual = datetime.now(bogota_tz).date()
        
        print(f"🔍 Depurando endpoint actualizar-campo")
        print(f"📅 Fecha actual: {fecha_actual}")
        print("=" * 60)
        
        # 1. Verificar registros existentes para hoy
        cursor.execute("""
            SELECT id_asistencia, cedula, tecnico, DATE(fecha_asistencia) as fecha_registro
            FROM asistencia 
            WHERE DATE(fecha_asistencia) = %s
            ORDER BY id_asistencia DESC
            LIMIT 10
        """, (fecha_actual,))
        
        registros_hoy = cursor.fetchall()
        
        print(f"📊 Registros de asistencia para hoy ({fecha_actual}):")
        if registros_hoy:
            for reg in registros_hoy:
                print(f"   ID: {reg['id_asistencia']}, Cédula: {reg['cedula']}, Técnico: {reg['tecnico']}")
        else:
            print("   ❌ No hay registros para hoy")
        
        # 2. Verificar el registro específico que está causando problemas (ID 6060)
        print(f"\n🔍 Verificando registro ID 6060:")
        cursor.execute("""
            SELECT id_asistencia, cedula, tecnico, fecha_asistencia, hora_inicio, estado, novedad
            FROM asistencia 
            WHERE id_asistencia = 6060
        """)
        
        registro_6060 = cursor.fetchone()
        
        if registro_6060:
            print("✅ Registro ID 6060 encontrado:")
            for key, value in registro_6060.items():
                print(f"   {key}: {value}")
        else:
            print("❌ Registro ID 6060 NO EXISTE")
        
        # 3. Buscar registros recientes que podrían estar causando el problema
        print(f"\n📋 Últimos 20 registros de asistencia:")
        cursor.execute("""
            SELECT id_asistencia, cedula, tecnico, DATE(fecha_asistencia) as fecha_registro
            FROM asistencia 
            ORDER BY id_asistencia DESC
            LIMIT 20
        """)
        
        ultimos_registros = cursor.fetchall()
        
        for reg in ultimos_registros:
            print(f"   ID: {reg['id_asistencia']}, Cédula: {reg['cedula']}, Fecha: {reg['fecha_registro']}")
        
        # 4. Verificar si hay registros duplicados o problemáticos
        print(f"\n🔍 Verificando registros duplicados para hoy:")
        cursor.execute("""
            SELECT cedula, COUNT(*) as cantidad
            FROM asistencia 
            WHERE DATE(fecha_asistencia) = %s
            GROUP BY cedula
            HAVING COUNT(*) > 1
        """, (fecha_actual,))
        
        duplicados = cursor.fetchall()
        
        if duplicados:
            print("⚠️ Registros duplicados encontrados:")
            for dup in duplicados:
                print(f"   Cédula: {dup['cedula']}, Cantidad: {dup['cantidad']}")
        else:
            print("✅ No hay registros duplicados")
        
        # 5. Simular la búsqueda que hace el endpoint
        cedula_test = "5694500"  # Cédula que aparece en los logs
        print(f"\n🧪 Simulando búsqueda del endpoint para cédula {cedula_test}:")
        
        cursor.execute("""
            SELECT id_asistencia, DATE(fecha_asistencia) as fecha_registro
            FROM asistencia 
            WHERE cedula = %s AND DATE(fecha_asistencia) = %s
            ORDER BY fecha_asistencia DESC
            LIMIT 1
        """, (cedula_test, fecha_actual))
        
        resultado_simulacion = cursor.fetchone()
        
        if resultado_simulacion:
            print(f"✅ Registro encontrado para cédula {cedula_test}:")
            print(f"   ID: {resultado_simulacion['id_asistencia']}")
            print(f"   Fecha: {resultado_simulacion['fecha_registro']}")
        else:
            print(f"❌ No se encontró registro para cédula {cedula_test} en fecha {fecha_actual}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    debug_actualizar_campo()