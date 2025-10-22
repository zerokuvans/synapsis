#!/usr/bin/env python3
"""
Script para verificar el procedimiento almacenado sp_validar_unicidad_documento
"""

import mysql.connector
from mysql.connector import Error

# Configuración
DB_CONFIG = {
    'host': 'localhost',
    'database': 'capired',
    'user': 'root',
    'password': '732137A031E4b@'
}

def check_stored_procedure():
    """Verificar el procedimiento almacenado"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        print("=== VERIFICANDO PROCEDIMIENTO ALMACENADO ===")
        
        # Verificar si existe el procedimiento
        cursor.execute("""
            SELECT ROUTINE_NAME, ROUTINE_TYPE, ROUTINE_DEFINITION 
            FROM INFORMATION_SCHEMA.ROUTINES 
            WHERE ROUTINE_SCHEMA = 'capired' 
            AND ROUTINE_NAME = 'sp_validar_unicidad_documento'
        """)
        
        procedure = cursor.fetchone()
        
        if procedure:
            print("✅ Procedimiento encontrado")
            print(f"Nombre: {procedure['ROUTINE_NAME']}")
            print(f"Tipo: {procedure['ROUTINE_TYPE']}")
            print("\nDefinición:")
            print(procedure['ROUTINE_DEFINITION'])
            
            # Verificar parámetros
            cursor.execute("""
                SELECT PARAMETER_NAME, PARAMETER_MODE, DATA_TYPE, ORDINAL_POSITION
                FROM INFORMATION_SCHEMA.PARAMETERS 
                WHERE SPECIFIC_SCHEMA = 'capired' 
                AND SPECIFIC_NAME = 'sp_validar_unicidad_documento'
                ORDER BY ORDINAL_POSITION
            """)
            
            parameters = cursor.fetchall()
            
            if parameters:
                print(f"\nParámetros ({len(parameters)}):")
                for param in parameters:
                    print(f"  {param['ORDINAL_POSITION']}. {param['PARAMETER_NAME']} ({param['PARAMETER_MODE']}) - {param['DATA_TYPE']}")
            else:
                print("\nNo se encontraron parámetros definidos")
                
        else:
            print("❌ Procedimiento NO encontrado")
            
            # Buscar procedimientos similares
            cursor.execute("""
                SELECT ROUTINE_NAME 
                FROM INFORMATION_SCHEMA.ROUTINES 
                WHERE ROUTINE_SCHEMA = 'capired' 
                AND ROUTINE_NAME LIKE '%validar%'
            """)
            
            similar = cursor.fetchall()
            if similar:
                print("\nProcedimientos similares encontrados:")
                for proc in similar:
                    print(f"  - {proc['ROUTINE_NAME']}")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"❌ Error: {e}")

def main():
    check_stored_procedure()

if __name__ == "__main__":
    main()