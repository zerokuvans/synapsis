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

def test_validacion_dual():
    print("=== PRUEBA DE VALIDACIÓN DUAL CORREGIDA ===\n")
    
    connection = get_db_connection()
    if not connection:
        print("No se pudo conectar a la base de datos")
        return
    
    cursor = connection.cursor()
    
    try:
        # Casos de prueba
        test_cases = [
            ("BROWNFIELD", "TECNICO CONDUCTOR"),
            ("BROWNFIELD", "TECNICO"),
            ("POSTVENTA", "TECNICO"),
            ("INEXISTENTE", "TECNICO"),
            ("BROWNFIELD", "CARGO_INEXISTENTE")
        ]
        
        for carpeta, cargo in test_cases:
            print(f"🔍 Probando: carpeta='{carpeta}' + cargo='{cargo}'")
            
            # Ejecutar la consulta de validación dual (igual que en main.py)
            cursor.execute("""
                SELECT presupuesto_diario, presupuesto_eventos 
                FROM presupuesto_carpeta 
                WHERE presupuesto_carpeta = %s AND presupuesto_cargo = %s
                LIMIT 1
            """, (carpeta, cargo))
            
            result = cursor.fetchone()
            
            if result:
                eventos = result[1]
                diario = result[0]
                print(f"   ✅ VÁLIDO: eventos={eventos}, diario={diario}")
            else:
                print(f"   ❌ INVÁLIDO: No se encontró la combinación")
            print()
        
        # Mostrar todas las combinaciones válidas disponibles
        print("📋 COMBINACIONES VÁLIDAS DISPONIBLES:")
        cursor.execute("""
            SELECT presupuesto_carpeta, presupuesto_cargo, presupuesto_eventos, presupuesto_diario
            FROM presupuesto_carpeta 
            ORDER BY presupuesto_carpeta, presupuesto_cargo
        """)
        
        all_combinations = cursor.fetchall()
        for combo in all_combinations:
            carpeta = combo[0]
            cargo = combo[1]
            eventos = combo[2]
            diario = combo[3]
            print(f"   • {carpeta} + {cargo} → eventos={eventos}, diario={diario}")
        
    except mysql.connector.Error as err:
        print(f"Error en la consulta: {err}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    test_validacion_dual()