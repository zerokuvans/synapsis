#!/usr/bin/env python3
# Script temporal para depurar el técnico específico

import mysql.connector
from datetime import datetime
import os

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', ''),
            database=os.environ.get('DB_NAME', 'synapsis'),
            port=int(os.environ.get('DB_PORT', 3306))
        )
        return connection
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def debug_tecnico_especifico():
    print("=== DEPURACIÓN TÉCNICO ESPECÍFICO ===")
    print("Buscando: MARTIN MARTINEZ JULIAN CAMILO - 1014216655")
    
    connection = get_db_connection()
    if not connection:
        print("ERROR: No se pudo conectar a la base de datos")
        return
    
    cursor = connection.cursor(dictionary=True)
    
    # Buscar el técnico por nombre
    print("\n1. Buscando por nombre...")
    cursor.execute("""
        SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula, cargo, carpeta 
        FROM recurso_operativo 
        WHERE nombre LIKE %s
    """, ('%MARTIN MARTINEZ JULIAN CAMILO%',))
    
    tecnicos_nombre = cursor.fetchall()
    print(f"Técnicos encontrados por nombre: {len(tecnicos_nombre)}")
    for tecnico in tecnicos_nombre:
        print(f"  - ID: {tecnico['id_codigo_consumidor']}, Nombre: {tecnico['nombre']}, Cédula: {tecnico['recurso_operativo_cedula']}")
        print(f"    Cargo: {tecnico['cargo']}, Carpeta: {tecnico['carpeta']}")
    
    # Buscar por cédula
    print("\n2. Buscando por cédula 1014216655...")
    cursor.execute("""
        SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula, cargo, carpeta 
        FROM recurso_operativo 
        WHERE recurso_operativo_cedula = %s
    """, ('1014216655',))
    
    tecnico_cedula = cursor.fetchone()
    if tecnico_cedula:
        print(f"Técnico encontrado por cédula:")
        print(f"  - ID: {tecnico_cedula['id_codigo_consumidor']}, Nombre: {tecnico_cedula['nombre']}")
        print(f"  - Cédula: {tecnico_cedula['recurso_operativo_cedula']}, Cargo: {tecnico_cedula['cargo']}")
        print(f"  - Carpeta: {tecnico_cedula['carpeta']}")
        
        # Verificar asignaciones de este técnico
        print("\n3. Verificando asignaciones...")
        cursor.execute("""
            SELECT COUNT(*) as total_asignaciones,
                   MAX(fecha_asignacion) as ultima_asignacion,
                   SUM(silicona) as total_silicona,
                   SUM(cinta_aislante) as total_cintas
            FROM ferretero 
            WHERE id_codigo_consumidor = %s
        """, (tecnico_cedula['id_codigo_consumidor'],))
        
        stats = cursor.fetchone()
        print(f"  - Total asignaciones: {stats['total_asignaciones']}")
        print(f"  - Última asignación: {stats['ultima_asignacion']}")
        print(f"  - Total silicona: {stats['total_silicona']}")
        print(f"  - Total cintas: {stats['total_cintas']}")
        
        # Verificar asignaciones recientes (últimos 30 días)
        print("\n4. Asignaciones recientes (últimos 30 días)...")
        cursor.execute("""
            SELECT fecha_asignacion, silicona, cinta_aislante, amarres_negros, amarres_blancos
            FROM ferretero 
            WHERE id_codigo_consumidor = %s 
            AND fecha_asignacion >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            ORDER BY fecha_asignacion DESC
            LIMIT 5
        """, (tecnico_cedula['id_codigo_consumidor'],))
        
        asignaciones_recientes = cursor.fetchall()
        print(f"  - Asignaciones recientes: {len(asignaciones_recientes)}")
        for asig in asignaciones_recientes:
            print(f"    {asig['fecha_asignacion']}: Silicona={asig['silicona']}, Cintas={asig['cinta_aislante']}, Amarres={asig['amarres_negros']+asig['amarres_blancos']}")
    else:
        print("No se encontró técnico con cédula 1014216655")
    
    # Buscar técnicos con IDs similares
    print("\n5. Buscando técnicos con IDs similares...")
    cursor.execute("""
        SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula 
        FROM recurso_operativo 
        WHERE recurso_operativo_cedula LIKE %s
        ORDER BY id_codigo_consumidor
    """, ('%1014216%',))
    
    similares = cursor.fetchall()
    print(f"Técnicos con cédulas similares: {len(similares)}")
    for sim in similares:
        print(f"  - ID: {sim['id_codigo_consumidor']}, Cédula: {sim['recurso_operativo_cedula']}, Nombre: {sim['nombre']}")
    
    cursor.close()
    connection.close()
    print("\n=== FIN DEPURACIÓN ===")

if __name__ == "__main__":
    debug_tecnico_especifico()