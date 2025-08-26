#!/usr/bin/env python3
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT')),
    'time_zone': '+00:00'
}

def verificar_filtrado():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        print("\n=== VERIFICACIÓN DEL FILTRADO POR ZONA ===")
        
        # Consulta para módulo OPERATIVO (zona = 'OP')
        print("\n1. Consulta para módulo OPERATIVO (zona = 'OP'):")
        cursor.execute("""
            SELECT codigo_tipificacion, nombre_tipificacion, zona
            FROM tipificacion_asistencia
            WHERE estado = '1' AND zona = 'OP'
            ORDER BY codigo_tipificacion
        """)
        resultados_op = cursor.fetchall()
        
        if resultados_op:
            print(f"   Encontrados {len(resultados_op)} registros:")
            for registro in resultados_op:
                print(f"   - {registro['codigo_tipificacion']}: {registro['nombre_tipificacion']} (Zona: {registro['zona']})")
        else:
            print("   ⚠️  No se encontraron registros con zona = 'OP'")
        
        # Consulta para módulo ADMINISTRATIVO (zona = 'RRHH')
        print("\n2. Consulta para módulo ADMINISTRATIVO (zona = 'RRHH'):")
        cursor.execute("""
            SELECT codigo_tipificacion, nombre_tipificacion, zona
            FROM tipificacion_asistencia
            WHERE estado = '1' AND zona = 'RRHH'
            ORDER BY codigo_tipificacion
        """)
        resultados_rrhh = cursor.fetchall()
        
        if resultados_rrhh:
            print(f"   Encontrados {len(resultados_rrhh)} registros:")
            for registro in resultados_rrhh:
                print(f"   - {registro['codigo_tipificacion']}: {registro['nombre_tipificacion']} (Zona: {registro['zona']})")
        else:
            print("   ⚠️  No se encontraron registros con zona = 'RRHH'")
        
        # Mostrar todas las zonas disponibles
        print("\n3. Todas las zonas disponibles en la tabla:")
        cursor.execute("""
            SELECT DISTINCT zona, COUNT(*) as cantidad
            FROM tipificacion_asistencia
            WHERE estado = '1'
            GROUP BY zona
            ORDER BY zona
        """)
        zonas = cursor.fetchall()
        
        for zona in zonas:
            print(f"   - Zona '{zona['zona']}': {zona['cantidad']} registros")
        
        print("\n=== RESUMEN ===")
        print(f"✅ Módulo OPERATIVO mostrará {len(resultados_op)} carpetas_dia (zona OP)")
        print(f"✅ Módulo ADMINISTRATIVO mostrará {len(resultados_rrhh)} carpetas_dia (zona RRHH)")
        
        if len(resultados_op) == 0:
            print("⚠️  ADVERTENCIA: No hay registros con zona 'OP' - el módulo operativo estará vacío")
        
        if len(resultados_rrhh) == 0:
            print("⚠️  ADVERTENCIA: No hay registros con zona 'RRHH' - el módulo administrativo estará vacío")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    verificar_filtrado()