#!/usr/bin/env python3
"""
Script para revisar la estructura de la tabla analistas_turnos_base
y entender qué campos contienen la información de horas
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def conectar_db():
    """Conectar a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            database=os.getenv('MYSQL_DB', 'capired'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            port=int(os.getenv('MYSQL_PORT', '3306'))
        )
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def revisar_estructura_tabla():
    """Revisar la estructura de la tabla analistas_turnos_base"""
    connection = conectar_db()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        print("=== ESTRUCTURA DE LA TABLA analistas_turnos_base ===")
        cursor.execute("DESCRIBE analistas_turnos_base")
        columns = cursor.fetchall()
        
        print("\nCampos de la tabla:")
        for column in columns:
            field, type_, null, key, default, extra = column
            print(f"- {field}: {type_} (NULL: {null}, Key: {key}, Default: {default})")
        
        print("\n=== DATOS DE EJEMPLO ===")
        cursor.execute("SELECT * FROM analistas_turnos_base LIMIT 5")
        rows = cursor.fetchall()
        
        if rows:
            # Obtener nombres de columnas
            column_names = [desc[0] for desc in cursor.description]
            print(f"\nColumnas: {', '.join(column_names)}")
            
            for i, row in enumerate(rows, 1):
                print(f"\nRegistro {i}:")
                for j, value in enumerate(row):
                    print(f"  {column_names[j]}: {value}")
        else:
            print("No hay datos en la tabla")
        
        print("\n=== CAMPOS RELACIONADOS CON HORAS ===")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'analistas_turnos_base' 
            AND (COLUMN_NAME LIKE '%hora%' OR COLUMN_NAME LIKE '%almuerzo%' OR COLUMN_NAME LIKE '%break%')
        """, (os.getenv('MYSQL_DB', 'capired'),))
        
        hora_fields = cursor.fetchall()
        if hora_fields:
            print("Campos relacionados con horas:")
            for field in hora_fields:
                print(f"- {field[0]}: {field[1]} ({field[2] if field[2] else 'Sin comentario'})")
        else:
            print("No se encontraron campos específicos de horas")
        
        print("\n=== CONTEO DE REGISTROS POR FECHA ===")
        cursor.execute("""
            SELECT analistas_turnos_fecha, COUNT(*) as total_registros
            FROM analistas_turnos_base 
            GROUP BY analistas_turnos_fecha 
            ORDER BY analistas_turnos_fecha DESC 
            LIMIT 10
        """)
        
        fecha_counts = cursor.fetchall()
        if fecha_counts:
            print("Registros por fecha (últimas 10 fechas):")
            for fecha, count in fecha_counts:
                print(f"- {fecha}: {count} registros")
        
    except Error as e:
        print(f"Error al consultar la base de datos: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def revisar_relacion_recurso_operativo():
    """Revisar la relación con la tabla recurso_operativo"""
    connection = conectar_db()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        print("\n=== RELACIÓN CON RECURSO_OPERATIVO ===")
        cursor.execute("""
            SELECT 
                atb.analistas_turnos_analista,
                ro.recurso_operativo_nombre,
                COUNT(*) as total_turnos
            FROM analistas_turnos_base atb
            LEFT JOIN recurso_operativo ro ON atb.analistas_turnos_analista = ro.id_codigo_consumidor
            GROUP BY atb.analistas_turnos_analista, ro.recurso_operativo_nombre
            LIMIT 10
        """)
        
        relations = cursor.fetchall()
        if relations:
            print("Relación analista-recurso operativo:")
            for analista_id, nombre, total in relations:
                print(f"- ID {analista_id}: {nombre if nombre else 'SIN NOMBRE'} ({total} turnos)")
        
    except Error as e:
        print(f"Error al consultar relaciones: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("Revisando estructura de analistas_turnos_base...")
    revisar_estructura_tabla()
    revisar_relacion_recurso_operativo()
    print("\n¡Revisión completada!")