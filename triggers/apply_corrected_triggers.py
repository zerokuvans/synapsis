#!/usr/bin/env python3
"""
Script para aplicar triggers corregidos al sistema de gestión de vehículos
Este script elimina los triggers antiguos y aplica los nuevos con la estructura correcta
"""

import mysql.connector
import os
from dotenv import load_dotenv

def get_db_connection():
    """Obtener conexión a la base de datos"""
    load_dotenv()
    
    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DB'),
        'autocommit': True
    }
    
    return mysql.connector.connect(**config)

def execute_sql_statements(cursor, sql_content):
    """Ejecutar declaraciones SQL individuales"""
    statements = []
    current_statement = ""
    in_delimiter_block = False
    custom_delimiter = ";"
    
    for line in sql_content.split('\n'):
        line = line.strip()
        
        # Ignorar comentarios y líneas vacías
        if not line or line.startswith('--'):
            continue
            
        # Manejar cambios de delimitador
        if line.upper().startswith('DELIMITER'):
            if 'DELIMITER //' in line.upper():
                custom_delimiter = "//"
                in_delimiter_block = True
            elif 'DELIMITER ;' in line.upper():
                custom_delimiter = ";"
                in_delimiter_block = False
            continue
            
        current_statement += line + " "
        
        # Verificar si la declaración está completa
        if line.endswith(custom_delimiter):
            # Remover el delimitador del final
            statement = current_statement.rstrip().rstrip(custom_delimiter).strip()
            if statement:
                statements.append(statement)
            current_statement = ""
    
    # Ejecutar cada declaración
    for i, statement in enumerate(statements, 1):
        try:
            print(f"Ejecutando declaración {i}...")
            cursor.execute(statement)
            print(f"✓ Declaración {i} ejecutada exitosamente")
        except mysql.connector.Error as e:
            print(f"❌ Error en declaración {i}: {e}")
            print(f"Declaración: {statement[:100]}...")
            continue

def drop_old_triggers(cursor):
    """Eliminar triggers antiguos"""
    print("\n🗑️ Eliminando triggers antiguos...")
    
    old_triggers = [
        'tr_parque_automotor_historial_insert',
        'tr_parque_automotor_historial_update', 
        'tr_generar_alertas_vencimiento',
        'tr_crear_alertas_vencimiento',
        'tr_parque_automotor_update'
    ]
    
    old_procedures = [
        'sp_generar_alertas_masivas'
    ]
    
    old_events = [
        'ev_generar_alertas_diarias'
    ]
    
    # Eliminar triggers
    for trigger in old_triggers:
        try:
            cursor.execute(f"DROP TRIGGER IF EXISTS {trigger}")
            print(f"✓ Trigger {trigger} eliminado")
        except mysql.connector.Error as e:
            print(f"⚠️ No se pudo eliminar trigger {trigger}: {e}")
    
    # Eliminar procedimientos
    for procedure in old_procedures:
        try:
            cursor.execute(f"DROP PROCEDURE IF EXISTS {procedure}")
            print(f"✓ Procedimiento {procedure} eliminado")
        except mysql.connector.Error as e:
            print(f"⚠️ No se pudo eliminar procedimiento {procedure}: {e}")
    
    # Eliminar eventos
    for event in old_events:
        try:
            cursor.execute(f"DROP EVENT IF EXISTS {event}")
            print(f"✓ Evento {event} eliminado")
        except mysql.connector.Error as e:
            print(f"⚠️ No se pudo eliminar evento {event}: {e}")

def verify_triggers(cursor):
    """Verificar que los triggers se crearon correctamente"""
    print("\n🔍 Verificando triggers creados...")
    
    # Verificar triggers
    cursor.execute("SHOW TRIGGERS")
    triggers = cursor.fetchall()
    trigger_names = [trigger[0] for trigger in triggers]
    
    expected_triggers = [
        'tr_parque_automotor_historial_insert_v2',
        'tr_parque_automotor_historial_update_v2'
    ]
    
    print(f"📊 Triggers encontrados: {len(trigger_names)}")
    for trigger in expected_triggers:
        if trigger in trigger_names:
            print(f"  ✓ {trigger}")
        else:
            print(f"  ❌ {trigger} - NO ENCONTRADO")
    
    return len([t for t in expected_triggers if t in trigger_names])

def main():
    """Función principal"""
    print("============================================================")
    print("APLICACIÓN DE TRIGGERS CORREGIDOS")
    print("Fecha: 2025-01-20")
    print("============================================================")
    
    try:
        # Conectar a la base de datos
        print("\n🔌 Conectando a la base de datos...")
        conn = get_db_connection()
        cursor = conn.cursor()
        print("✓ Conexión establecida")
        
        # Eliminar triggers antiguos
        drop_old_triggers(cursor)
        
        # Leer y ejecutar el archivo SQL
        sql_file = '../supabase/migrations/004_triggers_corregidos.sql'
        print(f"\n📖 Leyendo archivo: {sql_file}")
        
        if not os.path.exists(sql_file):
            print(f"❌ Error: El archivo {sql_file} no existe")
            return
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("✓ Archivo leído correctamente")
        
        # Ejecutar las declaraciones SQL
        print("\n⚙️ Ejecutando declaraciones SQL...")
        execute_sql_statements(cursor, sql_content)
        
        # Verificar la instalación
        triggers_created = verify_triggers(cursor)
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        print("\n============================================================")
        if triggers_created >= 2:
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print(f"📊 Triggers creados: {triggers_created}/2")
        else:
            print("⚠️ MIGRACIÓN COMPLETADA CON ADVERTENCIAS")
            print(f"📊 Triggers creados: {triggers_created}/2")
        print("============================================================")
        
    except mysql.connector.Error as e:
        print(f"\n❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()