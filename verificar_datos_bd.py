#!/usr/bin/env python3
"""
Script para verificar datos en la base de datos para CORTES CUERVO SANDRA CECILIA
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def verificar_datos_bd():
    try:
        # Configuración de la base de datos
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'capired'),
            'port': int(os.getenv('DB_PORT', 3306))
        }
        
        print(f"🔍 Conectando a la base de datos: {config['host']}:{config['port']}/{config['database']}")
        print("-" * 70)
        
        # Conectar a la base de datos
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        
        # 1. Verificar asistencia
        print("📋 1. VERIFICANDO ASISTENCIA:")
        query_asistencia = """
        SELECT * FROM capired.asistencia 
        WHERE super = 'CORTES CUERVO SANDRA CECILIA' 
        AND fecha_asistencia = '2025-10-07'
        """
        
        cursor.execute(query_asistencia)
        asistencias = cursor.fetchall()
        
        print(f"   - Registros de asistencia encontrados: {len(asistencias)}")
        if asistencias:
            for i, asistencia in enumerate(asistencias[:5]):  # Mostrar primeros 5
                print(f"     {i+1}. {asistencia.get('nombre', 'N/A')} - {asistencia.get('fecha_asistencia', 'N/A')}")
            if len(asistencias) > 5:
                print(f"     ... y {len(asistencias) - 5} más")
        
        print()
        
        # 2. Verificar técnicos en recurso_operativo
        print("👥 2. VERIFICANDO TÉCNICOS EN RECURSO_OPERATIVO:")
        query_tecnicos = """
        SELECT * FROM capired.recurso_operativo 
        WHERE supervisor = 'CORTES CUERVO SANDRA CECILIA' 
        AND estado = 'Activo'
        """
        
        cursor.execute(query_tecnicos)
        tecnicos = cursor.fetchall()
        
        print(f"   - Técnicos activos encontrados: {len(tecnicos)}")
        if tecnicos:
            for i, tecnico in enumerate(tecnicos):
                print(f"     {i+1}. {tecnico.get('nombre', 'N/A')} - Estado: {tecnico.get('estado', 'N/A')}")
        
        print()
        
        # 3. Verificar preoperacionales
        print("🔧 3. VERIFICANDO PREOPERACIONALES:")
        if tecnicos:
            # Obtener IDs de técnicos
            tecnico_ids = [str(t.get('id', '')) for t in tecnicos if t.get('id')]
            if tecnico_ids:
                query_preop = f"""
                SELECT * FROM capired.preoperacional 
                WHERE tecnico_id IN ({','.join(tecnico_ids)}) 
                AND fecha = '2025-10-07'
                """
                
                cursor.execute(query_preop)
                preoperacionales = cursor.fetchall()
                
                print(f"   - Registros preoperacionales encontrados: {len(preoperacionales)}")
                if preoperacionales:
                    for i, preop in enumerate(preoperacionales[:5]):
                        print(f"     {i+1}. Técnico ID: {preop.get('tecnico_id', 'N/A')} - Fecha: {preop.get('fecha', 'N/A')}")
                    if len(preoperacionales) > 5:
                        print(f"     ... y {len(preoperacionales) - 5} más")
        
        print()
        print("=" * 70)
        print("📊 RESUMEN:")
        print(f"   - Asistencias: {len(asistencias)} registros")
        print(f"   - Técnicos activos: {len(tecnicos)} registros")
        print(f"   - Preoperacionales: {len(preoperacionales) if 'preoperacionales' in locals() else 0} registros")
        
        if len(tecnicos) > 0:
            print(f"\n✅ HAY DATOS REALES para 'CORTES CUERVO SANDRA CECILIA'")
        else:
            print(f"\n❌ NO HAY TÉCNICOS ACTIVOS para 'CORTES CUERVO SANDRA CECILIA'")
        
    except Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    verificar_datos_bd()