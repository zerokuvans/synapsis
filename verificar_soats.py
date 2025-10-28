#!/usr/bin/env python3
"""
Script para verificar que los SOATs ahora aparecen en los vencimientos
"""

import mysql.connector
from datetime import datetime

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='synapsis',
            user='root',
            password='732137A031E4b@'
        )
        return connection
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def main():
    print("🔍 Verificando vencimientos de SOAT en la base de datos...")
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Consulta para obtener vencimientos de SOAT
        query_soat = """
        SELECT 
            s.id_mpa_soat,
            s.placa,
            s.numero_poliza,
            s.fecha_vencimiento,
            s.tecnico_asignado,
            ro.nombre as tecnico_nombre,
            DATEDIFF(s.fecha_vencimiento, CURDATE()) as dias_restantes
        FROM mpa_soat s
        LEFT JOIN recurso_operativo ro ON s.tecnico_asignado = ro.id_codigo_consumidor
        WHERE s.estado = 'activo'
        ORDER BY s.fecha_vencimiento
        LIMIT 10
        """
        
        cursor.execute(query_soat)
        soats = cursor.fetchall()
        
        print(f"📊 SOATs encontrados: {len(soats)}")
        
        if soats:
            print("\n📋 Primeros SOATs:")
            for i, soat in enumerate(soats):
                placa = soat.get('placa', 'N/A')
                tecnico_id = soat.get('tecnico_asignado', 'N/A')
                tecnico_nombre = soat.get('tecnico_nombre', 'N/A')
                dias = soat.get('dias_restantes', 'N/A')
                print(f"  {i+1}. Placa: {placa}, Técnico ID: {tecnico_id}, Técnico: {tecnico_nombre}, Días: {dias}")
        
        # Verificar si hay SOATs con técnico asignado como ID (número)
        query_check = """
        SELECT COUNT(*) as total_soats,
               SUM(CASE WHEN s.tecnico_asignado REGEXP '^[0-9]+$' THEN 1 ELSE 0 END) as soats_con_id,
               SUM(CASE WHEN s.tecnico_asignado NOT REGEXP '^[0-9]+$' AND s.tecnico_asignado IS NOT NULL THEN 1 ELSE 0 END) as soats_con_nombre
        FROM mpa_soat s
        WHERE s.estado = 'activo'
        """
        
        cursor.execute(query_check)
        stats = cursor.fetchone()
        
        print(f"\n📈 Estadísticas de técnicos asignados:")
        print(f"  Total SOATs activos: {stats['total_soats']}")
        print(f"  SOATs con ID de técnico: {stats['soats_con_id']}")
        print(f"  SOATs con nombre de técnico: {stats['soats_con_nombre']}")
        
        if stats['soats_con_id'] > 0:
            print("\n✅ ¡Corrección exitosa! Los SOATs ahora tienen IDs de técnico.")
        else:
            print("\n❌ Los SOATs aún tienen nombres en lugar de IDs.")
            
        # Contar todos los vencimientos
        query_all = """
        SELECT 'Licencia de Conducir' as tipo, COUNT(*) as total
        FROM mpa_licencia_conducir 
        WHERE estado = 'activo'
        UNION ALL
        SELECT 'Técnico Mecánica' as tipo, COUNT(*) as total
        FROM mpa_tecnico_mecanica 
        WHERE estado = 'activo'
        UNION ALL
        SELECT 'SOAT' as tipo, COUNT(*) as total
        FROM mpa_soat 
        WHERE estado = 'activo'
        """
        
        cursor.execute(query_all)
        totales = cursor.fetchall()
        
        print(f"\n📊 Total de vencimientos por tipo:")
        total_general = 0
        for row in totales:
            print(f"  {row['tipo']}: {row['total']}")
            total_general += row['total']
        
        print(f"  TOTAL GENERAL: {total_general}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    main()