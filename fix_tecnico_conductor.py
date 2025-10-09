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

def fix_tecnico_conductor():
    print("=== SOLUCIONANDO PROBLEMA: TECNICO CONDUCTOR ===\n")
    
    connection = get_db_connection()
    if not connection:
        print("No se pudo conectar a la base de datos")
        return
    
    cursor = connection.cursor()
    
    try:
        # 1. Verificar si ya existe 'TECNICO CONDUCTOR' en presupuesto_cargo
        print("1. Verificando si 'TECNICO CONDUCTOR' ya existe en presupuesto_cargo:")
        cursor.execute("SELECT * FROM presupuesto_cargo WHERE cargo = 'TECNICO CONDUCTOR'")
        existing_record = cursor.fetchone()
        
        if existing_record:
            print("   ✅ 'TECNICO CONDUCTOR' ya existe en presupuesto_cargo")
            print(f"   Registro: {existing_record}")
            return
        else:
            print("   ❌ 'TECNICO CONDUCTOR' NO existe en presupuesto_cargo")
        
        # 2. Buscar valores de referencia para TECNICO CONDUCTOR
        print("\n2. Buscando valores de referencia en presupuesto_carpeta:")
        cursor.execute("""
            SELECT presupuesto_eventos, presupuesto_diario 
            FROM presupuesto_carpeta 
            WHERE presupuesto_carpeta = 'BROWNFIELD' AND cargo = 'TECNICO CONDUCTOR'
        """)
        brownfield_conductor = cursor.fetchone()
        
        if brownfield_conductor:
            eventos_ref = brownfield_conductor[0]
            diario_ref = brownfield_conductor[1]
            print(f"   ✅ Valores de referencia encontrados: eventos={eventos_ref}, diario={diario_ref}")
        else:
            # Usar valores por defecto basados en TECNICO
            print("   ⚠️ No se encontraron valores específicos, usando valores por defecto")
            eventos_ref = 8  # Similar a TECNICO
            diario_ref = 120000.00  # Similar a TECNICO
        
        # 3. Insertar el registro faltante
        print(f"\n3. Insertando 'TECNICO CONDUCTOR' en presupuesto_cargo:")
        print(f"   Eventos: {eventos_ref}")
        print(f"   Diario: {diario_ref}")
        
        cursor.execute("""
            INSERT INTO presupuesto_cargo 
            (cargo, codigo_presupuesto, descripcion_presupuesto, presupuesto_eventos, presupuesto_diario)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            'TECNICO CONDUCTOR',
            'PRES_TECCON_001',
            'Presupuesto para técnicos conductores',
            eventos_ref,
            diario_ref
        ))
        
        connection.commit()
        print("   ✅ Registro insertado exitosamente")
        
        # 4. Verificar la inserción
        print("\n4. Verificando la inserción:")
        cursor.execute("SELECT * FROM presupuesto_cargo WHERE cargo = 'TECNICO CONDUCTOR'")
        new_record = cursor.fetchone()
        
        if new_record:
            print("   ✅ Verificación exitosa:")
            print(f"   ID: {new_record[0]}")
            print(f"   Cargo: {new_record[1]}")
            print(f"   Código: {new_record[2]}")
            print(f"   Descripción: {new_record[3]}")
            print(f"   Eventos: {new_record[4]}")
            print(f"   Diario: {new_record[5]}")
        else:
            print("   ❌ Error: No se pudo verificar la inserción")
        
        # 5. Probar la validación dual ahora
        print("\n5. Probando validación dual para BROWNFIELD + TECNICO CONDUCTOR:")
        
        # Buscar un técnico con esta combinación
        cursor.execute("""
            SELECT recurso_operativo_cedula, nombre, carpeta, cargo 
            FROM recurso_operativo 
            WHERE carpeta = 'BROWNFIELD' AND cargo = 'TECNICO CONDUCTOR'
            LIMIT 1
        """)
        tecnico_test = cursor.fetchone()
        
        if tecnico_test:
            print(f"   ✅ Técnico encontrado: {tecnico_test[1]} (Cédula: {tecnico_test[0]})")
            
            # Simular validación dual
            # Validación 1: Carpeta
            cursor.execute("""
                SELECT presupuesto_diario, presupuesto_eventos 
                FROM presupuesto_carpeta 
                WHERE presupuesto_carpeta = 'BROWNFIELD'
                LIMIT 1
            """)
            carpeta_result = cursor.fetchone()
            carpeta_valida = carpeta_result is not None
            
            # Validación 2: Cargo
            cursor.execute("""
                SELECT presupuesto_eventos, presupuesto_diario 
                FROM presupuesto_cargo 
                WHERE cargo = 'TECNICO CONDUCTOR'
                LIMIT 1
            """)
            cargo_result = cursor.fetchone()
            cargo_valido = cargo_result is not None
            
            print(f"   Carpeta válida: {carpeta_valida}")
            print(f"   Cargo válido: {cargo_valido}")
            
            if carpeta_valida and cargo_valido:
                print("   🎉 ¡VALIDACIÓN DUAL EXITOSA! El problema está solucionado.")
                print(f"   Valores que se aplicarían: eventos={carpeta_result[1]}, valor={carpeta_result[0]}")
            else:
                print("   ❌ La validación dual aún falla")
        else:
            print("   ⚠️ No se encontró ningún técnico con carpeta=BROWNFIELD y cargo=TECNICO CONDUCTOR")
            print("   Pero el registro en presupuesto_cargo ya está disponible para cuando se necesite")
        
    except mysql.connector.Error as err:
        print(f"Error en la operación: {err}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    fix_tecnico_conductor()