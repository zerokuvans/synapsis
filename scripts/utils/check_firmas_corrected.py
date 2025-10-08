import mysql.connector
import json

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
    'autocommit': True
}

try:
    # Conectar a la base de datos
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor(dictionary=True)
    
    # Verificar estructura de la tabla
    print("=== ESTRUCTURA DE LA TABLA DOTACIONES ===")
    cursor.execute("DESCRIBE dotaciones")
    columns = cursor.fetchall()
    
    print("Todas las columnas de la tabla:")
    for col in columns:
        print(f"- {col['Field']}: {col['Type']} (NULL: {col['Null']})")
    
    print("\n=== COLUMNAS RELACIONADAS CON FIRMA ===")
    firma_columns = [col for col in columns if 'firma' in col['Field'].lower()]
    if firma_columns:
        for col in firma_columns:
            print(f"- {col['Field']}: {col['Type']} (NULL: {col['Null']})")
    else:
        print("No se encontraron columnas relacionadas con firma")
    
    # Verificar algunas dotaciones recientes
    print("\n=== DOTACIONES RECIENTES ===")
    cursor.execute("SELECT * FROM dotaciones ORDER BY id_dotacion DESC LIMIT 3")
    dotaciones = cursor.fetchall()
    
    if dotaciones:
        print(f"Encontradas {len(dotaciones)} dotaciones:")
        for dotacion in dotaciones:
            print(f"ID: {dotacion['id_dotacion']}, Cliente: {dotacion.get('cliente', 'N/A')}")
            # Buscar campos que contengan 'firma'
            firma_fields = {k: v for k, v in dotacion.items() if 'firma' in k.lower()}
            if firma_fields:
                print(f"  Campos de firma: {firma_fields}")
            else:
                print("  Sin campos de firma")
    
    connection.close()
    print("\nVerificación completada exitosamente")
    
except mysql.connector.Error as e:
    print(f"Error de base de datos: {e}")
except Exception as e:
    print(f"Error: {e}")