import sqlite3
import os

# Conectar a la base de datos
db_path = os.path.join(os.getcwd(), 'synapsis.db')
print(f"Conectando a la base de datos: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar si el archivo de base de datos existe
    if not os.path.exists(db_path):
        print(f"\n✗ El archivo de base de datos no existe: {db_path}")
    else:
        print(f"\n✓ El archivo de base de datos existe: {db_path}")
        print(f"   Tamaño del archivo: {os.path.getsize(db_path)} bytes")
    
    # Listar todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()
    
    print(f"\nTablas encontradas en la base de datos ({len(tablas)} total):")
    for tabla in tablas:
        print(f"  - {tabla[0]}")
        
        # Contar registros en cada tabla
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla[0]};")
            count = cursor.fetchone()[0]
            print(f"    Registros: {count}")
        except Exception as e:
            print(f"    Error contando registros: {e}")
    
    # Buscar tablas relacionadas con vehículos
    print("\nBuscando tablas relacionadas con vehículos:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%vehiculo%' OR name LIKE '%automotor%' OR name LIKE '%parque%';")
    tablas_vehiculos = cursor.fetchall()
    
    if tablas_vehiculos:
        for tabla in tablas_vehiculos:
            print(f"  - {tabla[0]}")
    else:
        print("  No se encontraron tablas relacionadas con vehículos")
    
    # Verificar si hay tablas con nombres similares
    print("\nBuscando tablas con nombres similares:")
    for tabla in tablas:
        nombre = tabla[0].lower()
        if any(palabra in nombre for palabra in ['vehiculo', 'auto', 'parque', 'flota', 'transporte']):
            print(f"  - {tabla[0]} (posible tabla de vehículos)")
            
            # Mostrar estructura de la tabla
            cursor.execute(f"PRAGMA table_info({tabla[0]});")
            columnas = cursor.fetchall()
            print(f"    Columnas:")
            for col in columnas:
                print(f"      {col[1]} ({col[2]})")
    
    conn.close()
    print("\n✓ Verificación de tablas completada")
    
except Exception as e:
    print(f"✗ Error verificando tablas: {e}")
    if 'conn' in locals():
        conn.close()