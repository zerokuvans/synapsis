import mysql.connector
from main import get_db_connection

try:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Verificar duplicados en tipificacion_asistencia
    print("=== Verificando duplicados en tipificacion_asistencia ===")
    cursor.execute("""
        SELECT codigo_tipificacion, COUNT(*) as count 
        FROM tipificacion_asistencia 
        GROUP BY codigo_tipificacion 
        HAVING COUNT(*) > 1 
        ORDER BY count DESC 
        LIMIT 10
    """)
    
    duplicados = cursor.fetchall()
    if duplicados:
        print("Códigos duplicados encontrados:")
        for d in duplicados:
            print(f"  {d['codigo_tipificacion']}: {d['count']} veces")
    else:
        print("No se encontraron duplicados en tipificacion_asistencia")
    
    # Verificar total de registros
    cursor.execute("SELECT COUNT(*) as total FROM tipificacion_asistencia")
    total = cursor.fetchone()['total']
    print(f"\nTotal de registros en tipificacion_asistencia: {total}")
    
    # Verificar registros únicos
    cursor.execute("SELECT COUNT(DISTINCT codigo_tipificacion) as unicos FROM tipificacion_asistencia")
    unicos = cursor.fetchone()['unicos']
    print(f"Códigos únicos: {unicos}")
    
    if total != unicos:
        print(f"¡PROBLEMA! Hay {total - unicos} registros duplicados")
    else:
        print("✓ No hay duplicados en la tabla")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()