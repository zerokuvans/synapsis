import mysql.connector
import pandas as pd

# Configuración de la base de datos
config = {
    'user': 'root',
    'password': '732137A031E4b@',
    'host': 'localhost',
    'database': 'capired'
}

try:
    # Conectar a la base de datos
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    
    print("=== ANÁLISIS DE LA TABLA recurso_operativo ===")
    print()
    
    # Obtener la estructura de la tabla
    cursor.execute("DESCRIBE recurso_operativo")
    columns = cursor.fetchall()
    
    print("ESTRUCTURA DE LA TABLA:")
    print("-" * 80)
    for column in columns:
        print(f"Campo: {column[0]:<20} | Tipo: {column[1]:<20} | Null: {column[2]:<5} | Key: {column[3]:<5} | Default: {column[4]}")
    
    print("\n" + "=" * 80)
    
    # Obtener algunos registros de ejemplo
    cursor.execute("SELECT * FROM recurso_operativo LIMIT 10")
    records = cursor.fetchall()
    
    print("\nPRIMEROS 10 REGISTROS:")
    print("-" * 80)
    
    # Obtener nombres de columnas
    cursor.execute("SHOW COLUMNS FROM recurso_operativo")
    column_names = [column[0] for column in cursor.fetchall()]
    
    # Mostrar registros
    for i, record in enumerate(records, 1):
        print(f"\nRegistro {i}:")
        for j, value in enumerate(record):
            print(f"  {column_names[j]}: {value}")
    
    print("\n" + "=" * 80)
    
    # Analizar la columna 'super' específicamente
    cursor.execute("SELECT DISTINCT super FROM recurso_operativo WHERE super IS NOT NULL ORDER BY super")
    supervisores = cursor.fetchall()
    
    print("\nSUPERVISORES ÚNICOS EN LA COLUMNA 'super':")
    print("-" * 50)
    for supervisor in supervisores:
        print(f"- {supervisor[0]}")
    
    print("\n" + "=" * 80)
    
    # Contar técnicos por supervisor
    cursor.execute("""
        SELECT super, COUNT(*) as cantidad_tecnicos 
        FROM recurso_operativo 
        WHERE super IS NOT NULL 
        GROUP BY super 
        ORDER BY cantidad_tecnicos DESC
    """)
    
    conteo_supervisores = cursor.fetchall()
    
    print("\nCONTEO DE TÉCNICOS POR SUPERVISOR:")
    print("-" * 50)
    for supervisor, cantidad in conteo_supervisores:
        print(f"{supervisor}: {cantidad} técnicos")
    
    print("\n" + "=" * 80)
    
    # Mostrar algunos técnicos con sus supervisores
    cursor.execute("""
        SELECT nombre, recurso_operativo_cedula, super 
        FROM recurso_operativo 
        WHERE super IS NOT NULL 
        LIMIT 15
    """)
    
    tecnicos_supervisores = cursor.fetchall()
    
    print("\nEJEMPLOS DE TÉCNICOS CON SUS SUPERVISORES:")
    print("-" * 80)
    for nombre, cedula, supervisor in tecnicos_supervisores:
        print(f"Técnico: {nombre} | Cédula: {cedula} | Supervisor: {supervisor}")
    
except mysql.connector.Error as err:
    print(f"Error de base de datos: {err}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("\nConexión cerrada.")