#!/usr/bin/env python3
"""
Script para verificar si el usuario Cáceres (1032402333) tiene registros de asistencia
"""

import mysql.connector
from datetime import datetime

def conectar_bd():
    """Conectar a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='synapsis',
            user='root',
            password='root'
        )
        return connection
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def verificar_usuario_caceres():
    """Verificar si el usuario Cáceres existe y tiene registros"""
    connection = conectar_bd()
    if not connection:
        return
    
    cursor = connection.cursor()
    
    try:
        # Verificar en recurso_operativo
        print("🔍 Verificando usuario en recurso_operativo...")
        cursor.execute("""
            SELECT recurso_operativo_cedula, recurso_operativo_nombre, id_roles, estado
            FROM recurso_operativo 
            WHERE recurso_operativo_cedula = %s
        """, ('1032402333',))
        
        usuario = cursor.fetchone()
        if usuario:
            print(f"✅ Usuario encontrado: {usuario[1]} - Rol: {usuario[2]} - Estado: {usuario[3]}")
        else:
            print("❌ Usuario no encontrado en recurso_operativo")
            return
        
        # Verificar registros de asistencia
        print("\n🔍 Verificando registros de asistencia...")
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN estado_asistencia = 'CUMPLE' THEN 1 ELSE 0 END) as cumple,
                   SUM(CASE WHEN estado_asistencia = 'NOVEDAD' THEN 1 ELSE 0 END) as novedad,
                   SUM(CASE WHEN estado_asistencia = 'NO CUMPLE' THEN 1 ELSE 0 END) as no_cumple
            FROM asistencia 
            WHERE supervisor = %s
            AND fecha_asistencia >= '2025-10-01' 
            AND fecha_asistencia <= '2025-10-31'
        """, ('1032402333',))
        
        resultado = cursor.fetchone()
        if resultado and resultado[0] > 0:
            print(f"📊 Registros encontrados:")
            print(f"   Total: {resultado[0]}")
            print(f"   CUMPLE: {resultado[1]}")
            print(f"   NOVEDAD: {resultado[2]}")
            print(f"   NO CUMPLE: {resultado[3]}")
        else:
            print("❌ No se encontraron registros de asistencia para este supervisor")
            
            # Buscar por nombre
            print("\n🔍 Buscando por nombre...")
            cursor.execute("""
                SELECT DISTINCT supervisor, COUNT(*) as total
                FROM asistencia 
                WHERE supervisor LIKE %s
                GROUP BY supervisor
                LIMIT 5
            """, ('%CACERES%',))
            
            supervisores = cursor.fetchall()
            if supervisores:
                print("📋 Supervisores encontrados con nombre similar:")
                for sup in supervisores:
                    print(f"   {sup[0]}: {sup[1]} registros")
            else:
                print("❌ No se encontraron supervisores con nombre similar")
        
    except Exception as e:
        print(f"❌ Error en la consulta: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    verificar_usuario_caceres