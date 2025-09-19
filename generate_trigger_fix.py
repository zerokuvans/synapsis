#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar comandos SQL directos para cambiar definers de triggers
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import re

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

def get_triggers_with_wrong_definer():
    """Obtener todos los triggers con definer incorrecto"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        query = """
        SELECT TRIGGER_NAME, EVENT_OBJECT_TABLE, EVENT_MANIPULATION, ACTION_TIMING
        FROM information_schema.TRIGGERS 
        WHERE TRIGGER_SCHEMA = %s
        AND DEFINER = 'vnaranjos@localhost'
        ORDER BY EVENT_OBJECT_TABLE, TRIGGER_NAME
        """
        
        cursor.execute(query, (db_config['database'],))
        triggers = cursor.fetchall()
        
        return triggers
        
    except Error as e:
        print(f"Error al obtener triggers: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_trigger_definition(trigger_name):
    """Obtener la definición completa de un trigger"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        cursor.execute(f"SHOW CREATE TRIGGER {trigger_name}")
        result = cursor.fetchone()
        
        if result:
            return result[2]  # SQL Original Statement
        return None
        
    except Error as e:
        print(f"Error al obtener definición del trigger {trigger_name}: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def generate_fix_script():
    """Generar script SQL para corregir definers"""
    print("Obteniendo triggers con definer incorrecto...")
    triggers = get_triggers_with_wrong_definer()
    
    if not triggers:
        print("No se encontraron triggers con definer incorrecto.")
        return
    
    print(f"Encontrados {len(triggers)} triggers para corregir:")
    for trigger in triggers:
        print(f"  - {trigger[0]} en tabla {trigger[1]}")
    
    sql_script = []
    sql_script.append("-- =====================================================\n")
    sql_script.append("-- SCRIPT DIRECTO PARA CORREGIR DEFINERS DE TRIGGERS\n")
    sql_script.append("-- Sistema de Gestión Synapsis\n")
    sql_script.append(f"-- Fecha: {os.popen('date /t').read().strip()}\n")
    sql_script.append("-- Descripción: Cambia el definer de triggers de vnaranjos@localhost a root@localhost\n")
    sql_script.append("-- =====================================================\n\n")
    
    sql_script.append("-- Configurar variables de sesión\n")
    sql_script.append("SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';\n")
    sql_script.append("SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, AUTOCOMMIT=0;\n\n")
    
    sql_script.append("-- Verificación inicial\n")
    sql_script.append("SELECT 'VERIFICACIÓN INICIAL - Triggers con definer incorrecto:' as 'ESTADO';\n")
    sql_script.append("SELECT TRIGGER_NAME, EVENT_OBJECT_TABLE, DEFINER FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA = DATABASE() AND DEFINER = 'vnaranjos@localhost';\n\n")
    
    sql_script.append("-- Iniciar transacción\n")
    sql_script.append("START TRANSACTION;\n\n")
    
    for trigger_name, table_name, event_type, timing in triggers:
        print(f"Procesando trigger: {trigger_name}...")
        
        # Obtener definición del trigger
        definition = get_trigger_definition(trigger_name)
        if not definition:
            print(f"  Error: No se pudo obtener la definición del trigger {trigger_name}")
            continue
        
        # Extraer el cuerpo del trigger (después de FOR EACH ROW)
        match = re.search(r'FOR EACH ROW\s+(.*)', definition, re.DOTALL | re.IGNORECASE)
        if not match:
            print(f"  Error: No se pudo extraer el cuerpo del trigger {trigger_name}")
            continue
        
        trigger_body = match.group(1).strip()
        
        sql_script.append(f"-- Corregir trigger: {trigger_name}\n")
        sql_script.append(f"DROP TRIGGER IF EXISTS {trigger_name};\n")
        sql_script.append(f"CREATE DEFINER=`root`@`localhost` TRIGGER {trigger_name}\n")
        sql_script.append(f"    {timing} {event_type} ON {table_name}\n")
        sql_script.append(f"    FOR EACH ROW {trigger_body}\n\n")
        
        print(f"  ✓ Trigger {trigger_name} procesado correctamente")
    
    sql_script.append("-- Verificación final\n")
    sql_script.append("SELECT 'VERIFICACIÓN FINAL - Estado de todos los triggers:' as 'ESTADO';\n")
    sql_script.append("SELECT TRIGGER_NAME, EVENT_OBJECT_TABLE, DEFINER,\n")
    sql_script.append("       CASE WHEN DEFINER = 'root@localhost' THEN 'CORRECTO'\n")
    sql_script.append("            WHEN DEFINER = 'vnaranjos@localhost' THEN 'PENDIENTE'\n")
    sql_script.append("            ELSE 'REVISAR' END as 'Estado'\n")
    sql_script.append("FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA = DATABASE()\n")
    sql_script.append("ORDER BY EVENT_OBJECT_TABLE, TRIGGER_NAME;\n\n")
    
    sql_script.append("-- Confirmar cambios\n")
    sql_script.append("COMMIT;\n\n")
    
    sql_script.append("-- Restaurar configuraciones\n")
    sql_script.append("SET SQL_MODE=@OLD_SQL_MODE;\n")
    sql_script.append("SET AUTOCOMMIT=@OLD_AUTOCOMMIT;\n\n")
    
    sql_script.append("SELECT 'Script de corrección de definers completado exitosamente' as 'RESULTADO_FINAL';\n")
    
    # Escribir el script a archivo
    script_content = ''.join(sql_script)
    with open('fix_trigger_definers_direct.sql', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"\n✓ Script generado exitosamente: fix_trigger_definers_direct.sql")
    print(f"✓ Total de triggers a corregir: {len(triggers)}")
    print("\nPara ejecutar el script:")
    print(f"mysql -u root -p{db_config['password']} -D {db_config['database']} < fix_trigger_definers_direct.sql")

if __name__ == "__main__":
    generate_fix_script()