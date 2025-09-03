import sqlite3
import os
from datetime import datetime, timedelta

# Conectar a la base de datos
db_path = os.path.join(os.getcwd(), 'synapsis.db')
print(f"Conectando a la base de datos: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Verificar si existe la tabla parque_automotor
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parque_automotor';")
    tabla_existe = cursor.fetchone()
    print(f"\n1. Tabla parque_automotor existe: {tabla_existe is not None}")
    
    if tabla_existe:
        # 2. Verificar estructura de la tabla
        cursor.execute("PRAGMA table_info(parque_automotor);")
        columnas = cursor.fetchall()
        print("\n2. Estructura de la tabla parque_automotor:")
        for col in columnas:
            print(f"   - {col[1]} ({col[2]})")
        
        # 3. Contar total de registros
        cursor.execute("SELECT COUNT(*) FROM parque_automotor;")
        total_registros = cursor.fetchone()[0]
        print(f"\n3. Total de registros en parque_automotor: {total_registros}")
        
        # 4. Verificar registros con fechas de vencimiento
        cursor.execute("""
            SELECT COUNT(*) 
            FROM parque_automotor 
            WHERE soat_vencimiento IS NOT NULL OR tecnomecanica_vencimiento IS NOT NULL;
        """)
        registros_con_vencimientos = cursor.fetchone()[0]
        print(f"\n4. Registros con fechas de vencimiento: {registros_con_vencimientos}")
        
        # 5. Mostrar algunos registros de ejemplo
        cursor.execute("""
            SELECT placa, tipo_vehiculo, soat_vencimiento, tecnomecanica_vencimiento 
            FROM parque_automotor 
            WHERE soat_vencimiento IS NOT NULL OR tecnomecanica_vencimiento IS NOT NULL
            LIMIT 5;
        """)
        ejemplos = cursor.fetchall()
        print("\n5. Ejemplos de registros con vencimientos:")
        for ejemplo in ejemplos:
            print(f"   Placa: {ejemplo[0]}, Tipo: {ejemplo[1]}, SOAT: {ejemplo[2]}, Tecnomecánica: {ejemplo[3]}")
        
        # 6. Verificar registros próximos a vencer (60 días)
        fecha_limite = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT COUNT(*) 
            FROM parque_automotor 
            WHERE (soat_vencimiento IS NOT NULL AND soat_vencimiento <= ?) 
               OR (tecnomecanica_vencimiento IS NOT NULL AND tecnomecanica_vencimiento <= ?);
        """, (fecha_limite, fecha_limite))
        proximos_vencer = cursor.fetchone()[0]
        print(f"\n6. Registros que vencen en los próximos 60 días: {proximos_vencer}")
        
        # 7. Verificar si existe la tabla historial_documentos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historial_documentos';")
        historial_existe = cursor.fetchone()
        print(f"\n7. Tabla historial_documentos existe: {historial_existe is not None}")
        
        if historial_existe:
            cursor.execute("SELECT COUNT(*) FROM historial_documentos;")
            total_historial = cursor.fetchone()[0]
            print(f"   Total de registros en historial_documentos: {total_historial}")
            
            # Mostrar algunos registros del historial
            cursor.execute("""
                SELECT h.id_vehiculo, p.placa, h.tipo_documento, h.fecha_vencimiento, h.fecha_renovacion
                FROM historial_documentos h
                LEFT JOIN parque_automotor p ON h.id_vehiculo = p.id
                LIMIT 5;
            """)
            historial_ejemplos = cursor.fetchall()
            print("   Ejemplos del historial:")
            for hist in historial_ejemplos:
                print(f"     ID: {hist[0]}, Placa: {hist[1]}, Documento: {hist[2]}, Vencimiento: {hist[3]}, Renovación: {hist[4]}")
    
    conn.close()
    print("\n✓ Consulta SQL completada exitosamente")
    
except Exception as e:
    print(f"✗ Error en la consulta SQL: {e}")
    if 'conn' in locals():
        conn.close()