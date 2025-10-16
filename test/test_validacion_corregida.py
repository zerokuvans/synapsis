import mysql.connector
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_validacion_corregida():
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            charset='utf8mb4'
        )
        cursor = connection.cursor(dictionary=True)
        
        print("=== PRUEBA DE VALIDACIÓN CORREGIDA ===\n")
        
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
            
            # Ejecutar la consulta de validación dual
            cursor.execute("""
                SELECT presupuesto_diario, presupuesto_eventos 
                FROM presupuesto_carpeta 
                WHERE presupuesto_carpeta = %s AND presupuesto_cargo = %s
                LIMIT 1
            """, (carpeta, cargo))
            
            result = cursor.fetchone()
            
            if result:
                print(f"   ✅ VÁLIDO: eventos={result['presupuesto_eventos']}, diario={result['presupuesto_diario']}")
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
            print(f"   • {combo['presupuesto_carpeta']} + {combo['presupuesto_cargo']} → eventos={combo['presupuesto_eventos']}, diario={combo['presupuesto_diario']}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_validacion_corregida()