import mysql.connector

def buscar_supervisores():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@'
        )
        cursor = connection.cursor()
        
        # Buscar supervisores con registros en octubre 2025
        print("=== SUPERVISORES CON REGISTROS EN OCTUBRE 2025 ===")
        cursor.execute("""
            SELECT super, COUNT(*) as total_registros,
                   SUM(CASE WHEN estado = 'CUMPLE' THEN 1 ELSE 0 END) as cumple,
                   SUM(CASE WHEN estado = 'NOVEDAD' THEN 1 ELSE 0 END) as novedad,
                   SUM(CASE WHEN estado = 'NO CUMPLE' THEN 1 ELSE 0 END) as no_cumple
            FROM asistencia 
            WHERE fecha_asistencia >= '2025-10-01' 
            AND fecha_asistencia <= '2025-10-31'
            GROUP BY super
            ORDER BY total_registros DESC
            LIMIT 10
        """)
        
        supervisores = cursor.fetchall()
        for supervisor in supervisores:
            print(f"Supervisor: {supervisor[0]}")
            print(f"  Total: {supervisor[1]}, CUMPLE: {supervisor[2]}, NOVEDAD: {supervisor[3]}, NO CUMPLE: {supervisor[4]}")
            print()
        
        # Verificar si Cáceres tiene registros con otro identificador
        print("=== BUSCAR REGISTROS DE CACERES ===")
        cursor.execute("""
            SELECT super, COUNT(*) as total
            FROM asistencia 
            WHERE super LIKE %s
            AND fecha_asistencia >= '2025-10-01' 
            AND fecha_asistencia <= '2025-10-31'
            GROUP BY super
        """, ('%CACERES%',))
        
        caceres = cursor.fetchall()
        if caceres:
            for c in caceres:
                print(f"Encontrado: {c[0]} - {c[1]} registros")
        else:
            print("No se encontraron registros con CACERES en el nombre")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    buscar_supervisores()