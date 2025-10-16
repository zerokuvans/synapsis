import os
import mysql.connector
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos usando las mismas variables que main.py
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT')),
    'time_zone': '+00:00'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return None

def debug_brownfield_conductor():
    print("=== DEPURACIÓN: brownfield + tecnico conductor ===\n")
    
    connection = get_db_connection()
    if not connection:
        print("No se pudo conectar a la base de datos")
        return
    
    cursor = connection.cursor()
    
    try:
        # 1. Verificar si existe 'brownfield' en presupuesto_carpeta
        print("1. Verificando 'brownfield' en presupuesto_carpeta:")
        cursor.execute("SELECT * FROM presupuesto_carpeta WHERE carpeta LIKE '%brownfield%'")
        brownfield_results = cursor.fetchall()
        
        if brownfield_results:
            print(f"   ✓ Encontrados {len(brownfield_results)} registros:")
            for row in brownfield_results:
                print(f"     - ID: {row[0]}, Carpeta: '{row[1]}', Eventos: {row[2]}, Diario: {row[3]}")
        else:
            print("   ✗ No se encontró 'brownfield' en presupuesto_carpeta")
            
        # Buscar variaciones
        print("\n   Buscando variaciones de 'brownfield':")
        cursor.execute("SELECT DISTINCT carpeta FROM presupuesto_carpeta WHERE carpeta LIKE '%brown%'")
        brown_variations = cursor.fetchall()
        if brown_variations:
            for var in brown_variations:
                print(f"     - '{var[0]}'")
        
        # 2. Verificar si existe 'tecnico conductor' en presupuesto_cargo
        print("\n2. Verificando 'tecnico conductor' en presupuesto_cargo:")
        cursor.execute("SELECT * FROM presupuesto_cargo WHERE cargo LIKE '%tecnico conductor%'")
        conductor_results = cursor.fetchall()
        
        if conductor_results:
            print(f"   ✓ Encontrados {len(conductor_results)} registros:")
            for row in conductor_results:
                print(f"     - ID: {row[0]}, Cargo: '{row[1]}', Eventos: {row[2]}, Diario: {row[3]}")
        else:
            print("   ✗ No se encontró 'tecnico conductor' en presupuesto_cargo")
            
        # Buscar variaciones
        print("\n   Buscando variaciones de 'tecnico conductor':")
        cursor.execute("SELECT DISTINCT cargo FROM presupuesto_cargo WHERE cargo LIKE '%conductor%' OR cargo LIKE '%tecnico%'")
        conductor_variations = cursor.fetchall()
        if conductor_variations:
            for var in conductor_variations:
                print(f"     - '{var[0]}'")
        
        # 3. Mostrar todos los registros de ambas tablas para referencia
        print("\n3. Todos los registros en presupuesto_carpeta:")
        cursor.execute("SELECT * FROM presupuesto_carpeta")
        all_carpetas = cursor.fetchall()
        for row in all_carpetas:
            print(f"   - ID: {row[0]}, Carpeta: '{row[1]}', Eventos: {row[2]}, Diario: {row[3]}")
            
        print("\n4. Todos los registros en presupuesto_cargo:")
        cursor.execute("SELECT * FROM presupuesto_cargo")
        all_cargos = cursor.fetchall()
        for row in all_cargos:
            print(f"   - ID: {row[0]}, Cargo: '{row[1]}', Eventos: {row[2]}, Diario: {row[3]}")
        
        # 5. Buscar técnicos con esta combinación
        print("\n5. Buscando técnicos con carpeta='brownfield' y cargo='tecnico conductor':")
        cursor.execute("""
            SELECT id, nombre, carpeta, cargo 
            FROM tecnicos 
            WHERE carpeta LIKE '%brownfield%' AND cargo LIKE '%tecnico conductor%'
        """)
        tecnicos_combo = cursor.fetchall()
        
        if tecnicos_combo:
            print(f"   ✓ Encontrados {len(tecnicos_combo)} técnicos:")
            for row in tecnicos_combo:
                print(f"     - ID: {row[0]}, Nombre: '{row[1]}', Carpeta: '{row[2]}', Cargo: '{row[3]}'")
        else:
            print("   ✗ No se encontraron técnicos con esta combinación exacta")
            
            # Buscar técnicos con carpeta brownfield
            print("\n   Buscando técnicos con carpeta que contenga 'brownfield':")
            cursor.execute("SELECT id, nombre, carpeta, cargo FROM tecnicos WHERE carpeta LIKE '%brownfield%'")
            tecnicos_brownfield = cursor.fetchall()
            if tecnicos_brownfield:
                for row in tecnicos_brownfield:
                    print(f"     - ID: {row[0]}, Nombre: '{row[1]}', Carpeta: '{row[2]}', Cargo: '{row[3]}'")
            
            # Buscar técnicos con cargo conductor
            print("\n   Buscando técnicos con cargo que contenga 'conductor':")
            cursor.execute("SELECT id, nombre, carpeta, cargo FROM tecnicos WHERE cargo LIKE '%conductor%'")
            tecnicos_conductor = cursor.fetchall()
            if tecnicos_conductor:
                for row in tecnicos_conductor:
                    print(f"     - ID: {row[0]}, Nombre: '{row[1]}', Carpeta: '{row[2]}', Cargo: '{row[3]}'")
        
    except mysql.connector.Error as err:
        print(f"Error en la consulta: {err}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    debug_brownfield_conductor()