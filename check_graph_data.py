import mysql.connector
import os
from datetime import datetime, timedelta

def verificar_datos_graficas():
    try:
        # Configuración de la base de datos
        config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
            'database': os.getenv('MYSQL_DB', 'capired'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
        
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        print("=== Verificando tabla tipificacion_asistencia ===")
        
        # 1. Verificar si existe tabla tipificacion_asistencia
        cursor.execute("SHOW TABLES LIKE 'tipificacion_asistencia'")
        tabla_tipificacion = cursor.fetchone()
        if tabla_tipificacion:
            print("✅ Tabla tipificacion_asistencia existe")
            
            # Verificar estructura
            cursor.execute("DESCRIBE tipificacion_asistencia")
            columnas_tipificacion = cursor.fetchall()
            print("\n=== Estructura tabla tipificacion_asistencia ===")
            for columna in columnas_tipificacion:
                print(f"- {columna[0]} ({columna[1]})")
            
            # Verificar datos
            cursor.execute("SELECT COUNT(*) FROM tipificacion_asistencia")
            total_tipificacion = cursor.fetchone()[0]
            print(f"\nTotal registros en tipificacion_asistencia: {total_tipificacion}")
            
            # Verificar algunos registros
            cursor.execute("SELECT * FROM tipificacion_asistencia LIMIT 10")
            registros_tipificacion = cursor.fetchall()
            print(f"\n=== Primeros 10 registros de tipificacion_asistencia ===")
            for i, registro in enumerate(registros_tipificacion):
                print(f"Registro {i+1}: {registro}")
                
        else:
            print("❌ Tabla tipificacion_asistencia NO existe")
            print("Los endpoints de gráficas fallarán porque dependen de esta tabla")
        
        # 2. Verificar qué códigos de carpeta_dia existen en asistencia
        cursor.execute("""
            SELECT DISTINCT carpeta_dia, COUNT(*) as total
            FROM asistencia 
            WHERE carpeta_dia IS NOT NULL AND carpeta_dia != ''
            GROUP BY carpeta_dia
            ORDER BY total DESC
        """)
        carpetas_dia = cursor.fetchall()
        print(f"\n=== Códigos carpeta_dia únicos en asistencia ===")
        for carpeta in carpetas_dia:
            print(f"- {carpeta[0]}: {carpeta[1]} registros")
        
        # 3. Verificar qué carpetas existen en asistencia
        cursor.execute("""
            SELECT DISTINCT carpeta, COUNT(*) as total
            FROM asistencia 
            WHERE carpeta IS NOT NULL AND carpeta != ''
            GROUP BY carpeta
            ORDER BY total DESC
        """)
        carpetas = cursor.fetchall()
        print(f"\n=== Carpetas únicas en asistencia ===")
        for carpeta in carpetas:
            print(f"- {carpeta[0]}: {carpeta[1]} registros")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"❌ Error al verificar datos: {err}")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    verificar_datos_graficas()