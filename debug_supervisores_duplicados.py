import mysql.connector

try:
    # Conectar a la base de datos
    connection = mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='732137A031E4b@',
        database='capired'
    )
    
    cursor = connection.cursor()
    
    print("=== SUPERVISORES EN TABLA ASISTENCIA ===")
    cursor.execute("""
        SELECT DISTINCT super as supervisor
        FROM asistencia 
        WHERE super IS NOT NULL AND super != ''
        ORDER BY super
    """)
    supervisores_asistencia = cursor.fetchall()
    print(f"Total supervisores en asistencia: {len(supervisores_asistencia)}")
    for sup in supervisores_asistencia:
        print(f"  - {sup[0]}")
    
    print("\n=== SUPERVISORES EN TABLA RECURSO_OPERATIVO ===")
    cursor.execute("""
        SELECT DISTINCT super as supervisor
        FROM recurso_operativo 
        WHERE super IS NOT NULL AND super != ''
        ORDER BY super
    """)
    supervisores_recurso = cursor.fetchall()
    print(f"Total supervisores en recurso_operativo: {len(supervisores_recurso)}")
    for sup in supervisores_recurso:
        print(f"  - {sup[0]}")
    
    print("\n=== SUPERVISORES ÚNICOS COMBINADOS ===")
    cursor.execute("""
        SELECT DISTINCT supervisor FROM (
            SELECT DISTINCT super as supervisor FROM asistencia WHERE super IS NOT NULL AND super != ''
            UNION
            SELECT DISTINCT super as supervisor FROM recurso_operativo WHERE super IS NOT NULL AND super != ''
        ) AS combined_supervisors
        ORDER BY supervisor
    """)
    supervisores_combinados = cursor.fetchall()
    print(f"Total supervisores únicos combinados: {len(supervisores_combinados)}")
    for sup in supervisores_combinados:
        print(f"  - {sup[0]}")
    
    # Verificar si hay diferencias
    set_asistencia = set([sup[0] for sup in supervisores_asistencia])
    set_recurso = set([sup[0] for sup in supervisores_recurso])
    set_combinados = set([sup[0] for sup in supervisores_combinados])
    
    print(f"\n=== ANÁLISIS DE DIFERENCIAS ===")
    print(f"Solo en asistencia: {set_asistencia - set_recurso}")
    print(f"Solo en recurso_operativo: {set_recurso - set_asistencia}")
    print(f"En ambas tablas: {set_asistencia & set_recurso}")
    
except mysql.connector.Error as e:
    print(f"Error de base de datos: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()