import mysql.connector
from main import get_db_connection

try:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("=== Eliminando duplicados de tipificacion_asistencia ===")
    
    # Primero, verificar el estado actual
    cursor.execute("SELECT COUNT(*) as total FROM tipificacion_asistencia")
    total_antes = cursor.fetchone()['total']
    print(f"Registros antes de la limpieza: {total_antes}")
    
    # Verificar duplicados por codigo_tipificacion
    cursor.execute("""
        SELECT codigo_tipificacion, COUNT(*) as count 
        FROM tipificacion_asistencia 
        GROUP BY codigo_tipificacion 
        HAVING COUNT(*) > 1 
        ORDER BY count DESC
    """)
    duplicados_antes = cursor.fetchall()
    print(f"Códigos duplicados encontrados: {len(duplicados_antes)}")
    
    # Crear una tabla temporal con solo el primer registro de cada codigo_tipificacion
    print("\nCreando tabla temporal con registros únicos por código...")
    cursor.execute("""
        CREATE TEMPORARY TABLE tipificacion_temp AS
        SELECT t1.*
        FROM tipificacion_asistencia t1
        INNER JOIN (
            SELECT codigo_tipificacion, MIN(idtipificacion_asistencia) as min_id
            FROM tipificacion_asistencia
            WHERE codigo_tipificacion IS NOT NULL AND codigo_tipificacion != ''
            GROUP BY codigo_tipificacion
        ) t2 ON t1.codigo_tipificacion = t2.codigo_tipificacion 
               AND t1.idtipificacion_asistencia = t2.min_id
    """)
    
    # Verificar cuántos registros únicos tenemos
    cursor.execute("SELECT COUNT(*) as total FROM tipificacion_temp")
    total_unicos = cursor.fetchone()['total']
    print(f"Registros únicos identificados: {total_unicos}")
    
    # Respaldar la tabla original
    print("\nCreando respaldo de la tabla original...")
    cursor.execute("DROP TABLE IF EXISTS tipificacion_asistencia_backup")
    cursor.execute("""
        CREATE TABLE tipificacion_asistencia_backup AS 
        SELECT * FROM tipificacion_asistencia
    """)
    
    # Eliminar todos los registros de la tabla original
    print("\nEliminando todos los registros...")
    cursor.execute("DELETE FROM tipificacion_asistencia")
    
    # Insertar solo los registros únicos
    print("Insertando registros únicos...")
    cursor.execute("""
        INSERT INTO tipificacion_asistencia 
        (idtipificacion_asistencia, codigo_tipificacion, nombre_tipificacion, estado, valor, zona)
        SELECT idtipificacion_asistencia, codigo_tipificacion, nombre_tipificacion, estado, valor, zona
        FROM tipificacion_temp
        ORDER BY codigo_tipificacion
    """)
    
    # Verificar el resultado
    cursor.execute("SELECT COUNT(*) as total FROM tipificacion_asistencia")
    total_despues = cursor.fetchone()['total']
    print(f"\nRegistros después de la limpieza: {total_despues}")
    print(f"Registros eliminados: {total_antes - total_despues}")
    
    # Verificar que no hay duplicados
    cursor.execute("""
        SELECT codigo_tipificacion, COUNT(*) as count 
        FROM tipificacion_asistencia 
        GROUP BY codigo_tipificacion 
        HAVING COUNT(*) > 1
    """)
    
    duplicados_restantes = cursor.fetchall()
    if duplicados_restantes:
        print(f"\n⚠️  Aún quedan {len(duplicados_restantes)} códigos duplicados:")
        for d in duplicados_restantes:
            print(f"  {d['codigo_tipificacion']}: {d['count']} veces")
    else:
        print("\n✅ ¡Limpieza exitosa! No quedan duplicados.")
    
    # Mostrar algunos registros finales
    print("\n=== Muestra de registros finales ===")
    cursor.execute("SELECT codigo_tipificacion, nombre_tipificacion FROM tipificacion_asistencia ORDER BY codigo_tipificacion LIMIT 15")
    muestra = cursor.fetchall()
    for reg in muestra:
        print(f"  {reg['codigo_tipificacion']}: {reg['nombre_tipificacion']}")
    
    # Confirmar cambios
    conn.commit()
    print("\n✅ Cambios guardados en la base de datos.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    if 'conn' in locals():
        conn.rollback()
        print("Cambios revertidos.")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()