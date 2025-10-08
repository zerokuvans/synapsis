#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def debug_camisetagris_field():
    """Analizar el campo camisetagris y identificar la causa del error 1366"""
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
            database='capired'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            print("=" * 80)
            print("ANÁLISIS DEL CAMPO 'camisetagris' - ERROR 1366")
            print("=" * 80)
            
            # 1. Verificar la estructura específica del campo camisetagris
            print("\n1. ESTRUCTURA DEL CAMPO 'camisetagris':")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, 
                       CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'capired' 
                AND TABLE_NAME = 'cambios_dotacion' 
                AND COLUMN_NAME = 'camisetagris'
            """)
            
            campo_info = cursor.fetchone()
            if campo_info:
                print(f"  Nombre: {campo_info['COLUMN_NAME']}")
                print(f"  Tipo: {campo_info['DATA_TYPE']}")
                print(f"  Permite NULL: {campo_info['IS_NULLABLE']}")
                print(f"  Valor por defecto: {campo_info['COLUMN_DEFAULT']}")
                print(f"  Longitud máxima: {campo_info['CHARACTER_MAXIMUM_LENGTH']}")
                print(f"  Precisión numérica: {campo_info['NUMERIC_PRECISION']}")
                print(f"  Escala numérica: {campo_info['NUMERIC_SCALE']}")
            else:
                print("  ❌ Campo 'camisetagris' no encontrado")
            
            # 2. Verificar datos existentes en el campo
            print("\n2. DATOS EXISTENTES EN EL CAMPO 'camisetagris':")
            cursor.execute("""
                SELECT camisetagris, COUNT(*) as cantidad
                FROM cambios_dotacion 
                WHERE camisetagris IS NOT NULL
                GROUP BY camisetagris
                ORDER BY camisetagris
            """)
            
            datos_existentes = cursor.fetchall()
            if datos_existentes:
                print("  Valores encontrados:")
                for dato in datos_existentes:
                    print(f"    {dato['camisetagris']} (aparece {dato['cantidad']} veces)")
            else:
                print("  ❌ No hay datos existentes en el campo")
            
            # 3. Probar inserción con diferentes valores
            print("\n3. PRUEBAS DE INSERCIÓN:")
            
            # Valores de prueba que podrían causar el error
            valores_prueba = [
                ('', 'cadena vacía'),
                (None, 'NULL'),
                ('0', 'cero como string'),
                (0, 'cero como entero'),
                ('1', 'uno como string'),
                (1, 'uno como entero'),
                ('abc', 'texto no numérico'),
                ('1.5', 'decimal como string'),
                (1.5, 'decimal como float')
            ]
            
            for valor, descripcion in valores_prueba:
                try:
                    # Intentar insertar un registro de prueba
                    test_query = """
                        INSERT INTO cambios_dotacion 
                        (id_codigo_consumidor, fecha_cambio, camisetagris, observaciones) 
                        VALUES (%s, %s, %s, %s)
                    """
                    
                    cursor.execute(test_query, ('TEST_001', '2024-01-01', valor, f'Prueba: {descripcion}'))
                    
                    # Si llegamos aquí, la inserción fue exitosa
                    print(f"  ✅ {descripcion}: ÉXITO")
                    
                    # Eliminar el registro de prueba
                    cursor.execute("DELETE FROM cambios_dotacion WHERE id_codigo_consumidor = 'TEST_001'")
                    
                except Error as e:
                    if '1366' in str(e):
                        print(f"  ❌ {descripcion}: ERROR 1366 - {e}")
                    else:
                        print(f"  ⚠️  {descripcion}: OTRO ERROR - {e}")
                
                # Hacer rollback para limpiar cualquier cambio
                connection.rollback()
            
            # 4. Verificar restricciones y triggers
            print("\n4. RESTRICCIONES Y TRIGGERS:")
            
            # Verificar constraints
            cursor.execute("""
                SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                WHERE TABLE_SCHEMA = 'capired' 
                AND TABLE_NAME = 'cambios_dotacion'
            """)
            
            constraints = cursor.fetchall()
            if constraints:
                print("  Restricciones encontradas:")
                for constraint in constraints:
                    print(f"    {constraint['CONSTRAINT_NAME']}: {constraint['CONSTRAINT_TYPE']}")
            else:
                print("  No se encontraron restricciones")
            
            # Verificar triggers
            cursor.execute("""
                SELECT TRIGGER_NAME, EVENT_MANIPULATION, ACTION_TIMING
                FROM INFORMATION_SCHEMA.TRIGGERS
                WHERE EVENT_OBJECT_SCHEMA = 'capired' 
                AND EVENT_OBJECT_TABLE = 'cambios_dotacion'
            """)
            
            triggers = cursor.fetchall()
            if triggers:
                print("  Triggers encontrados:")
                for trigger in triggers:
                    print(f"    {trigger['TRIGGER_NAME']}: {trigger['ACTION_TIMING']} {trigger['EVENT_MANIPULATION']}")
            else:
                print("  No se encontraron triggers")
            
            print("\n" + "=" * 80)
            print("ANÁLISIS COMPLETADO")
            print("=" * 80)
            
    except Error as e:
        print(f"Error de base de datos: {e}")
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada.")

if __name__ == "__main__":
    debug_camisetagris_field()