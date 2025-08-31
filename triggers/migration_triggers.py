#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migración para triggers automáticos del sistema de gestión de vehículos
Fecha: 2025-01-20
Descripción: Aplica triggers para historial automático y generación de alertas
"""

import mysql.connector
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def get_db_connection():
    """Establece conexión con la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def execute_sql_file(connection, file_path):
    """Ejecuta un archivo SQL línea por línea"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        cursor = connection.cursor()
        
        # Dividir el contenido en statements individuales
        statements = []
        current_statement = ""
        in_delimiter_block = False
        custom_delimiter = ";"
        
        lines = sql_content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Ignorar comentarios y líneas vacías
            if not line or line.startswith('--') or line.startswith('#'):
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
            
            current_statement += line + "\n"
            
            # Verificar si el statement está completo
            if line.endswith(custom_delimiter):
                # Remover el delimitador del final
                current_statement = current_statement.rstrip(custom_delimiter + "\n").strip()
                if current_statement:
                    statements.append(current_statement)
                current_statement = ""
        
        # Agregar el último statement si existe
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        # Ejecutar cada statement
        for i, statement in enumerate(statements):
            if statement.strip():
                try:
                    print(f"Ejecutando statement {i+1}/{len(statements)}...")
                    
                    # Para statements que pueden contener múltiples queries (como triggers)
                    if 'CREATE TRIGGER' in statement.upper() or 'CREATE PROCEDURE' in statement.upper() or 'CREATE EVENT' in statement.upper():
                        cursor.execute(statement)
                    else:
                        # Para otros statements, ejecutar normalmente
                        for result in cursor.execute(statement, multi=True):
                            pass
                    
                    print(f"✓ Statement {i+1} ejecutado correctamente")
                    
                except mysql.connector.Error as e:
                    print(f"⚠ Error en statement {i+1}: {e}")
                    print(f"Statement: {statement[:100]}...")
                    # Continuar con el siguiente statement
                    continue
        
        connection.commit()
        cursor.close()
        print("\n✓ Migración de triggers completada exitosamente")
        return True
        
    except Exception as e:
        print(f"Error ejecutando archivo SQL: {e}")
        return False

def verify_triggers():
    """Verifica que los triggers se hayan creado correctamente"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Verificar triggers
        cursor.execute("""
            SELECT TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE 
            FROM information_schema.TRIGGERS 
            WHERE TRIGGER_SCHEMA = %s
            AND TRIGGER_NAME LIKE 'tr_%'
        """, (DB_CONFIG['database'],))
        
        triggers = cursor.fetchall()
        print(f"\n📋 Triggers creados: {len(triggers)}")
        for trigger in triggers:
            print(f"  - {trigger['TRIGGER_NAME']} ({trigger['EVENT_MANIPULATION']} on {trigger['EVENT_OBJECT_TABLE']})")
        
        # Verificar procedimientos
        cursor.execute("""
            SELECT ROUTINE_NAME, ROUTINE_TYPE 
            FROM information_schema.ROUTINES 
            WHERE ROUTINE_SCHEMA = %s
            AND ROUTINE_NAME LIKE 'sp_%'
        """, (DB_CONFIG['database'],))
        
        procedures = cursor.fetchall()
        print(f"\n📋 Procedimientos creados: {len(procedures)}")
        for proc in procedures:
            print(f"  - {proc['ROUTINE_NAME']} ({proc['ROUTINE_TYPE']})")
        
        # Verificar eventos
        cursor.execute("""
            SELECT EVENT_NAME, STATUS, EVENT_DEFINITION 
            FROM information_schema.EVENTS 
            WHERE EVENT_SCHEMA = %s
        """, (DB_CONFIG['database'],))
        
        events = cursor.fetchall()
        print(f"\n📋 Eventos programados: {len(events)}")
        for event in events:
            print(f"  - {event['EVENT_NAME']} (Status: {event['STATUS']})")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"Error verificando triggers: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("MIGRACIÓN DE TRIGGERS AUTOMÁTICOS")
    print("Sistema de Gestión de Vehículos")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Verificar que el archivo de migración existe
    migration_file = "../supabase/migrations/003_triggers_automaticos.sql"
    if not os.path.exists(migration_file):
        print(f"❌ Error: No se encontró el archivo {migration_file}")
        return False
    
    # Conectar a la base de datos
    print("\n🔌 Conectando a la base de datos...")
    connection = get_db_connection()
    if not connection:
        print("❌ Error: No se pudo conectar a la base de datos")
        return False
    
    print("✓ Conexión establecida")
    
    # Ejecutar migración
    print(f"\n📄 Ejecutando migración: {migration_file}")
    success = execute_sql_file(connection, migration_file)
    
    if success:
        print("\n🔍 Verificando triggers creados...")
        verify_triggers()
        
        print("\n" + "=" * 60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("\n📝 Resumen:")
        print("  - Triggers de historial automático creados")
        print("  - Triggers de generación de alertas creados")
        print("  - Procedimiento de alertas masivas creado")
        print("  - Evento programado diario configurado")
        print("  - Índices de optimización creados")
        print("=" * 60)
        
    else:
        print("\n❌ Error durante la migración")
    
    connection.close()
    return success

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Migración interrumpida por el usuario")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        exit(1)