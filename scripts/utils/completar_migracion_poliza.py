#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para completar la migración de datos de póliza al historial
"""

import mysql.connector
from mysql.connector import Error
import sys

# Configuración de conexión
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def main():
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(buffered=True)
        
        print("Verificando campos de poliza en parque_automotor...")
        
        # Obtener estructura de la tabla
        cursor.execute("DESCRIBE parque_automotor;")
        campos = cursor.fetchall()
        
        # Buscar campos relacionados con póliza
        campos_poliza = []
        for campo in campos:
            field_name = campo[0].lower()
            if 'poliza' in field_name or 'seguro' in field_name:
                campos_poliza.append(campo[0])
                print(f"Campo encontrado: {campo[0]} - {campo[1]}")
        
        if not campos_poliza:
            print("No se encontraron campos de poliza")
            return False
        
        # Intentar migrar con el campo correcto
        for campo_poliza in campos_poliza:
            print(f"\nIntentando migrar con campo: {campo_poliza}")
            
            sql_poliza = f"""
            INSERT INTO historial_documentos_vehiculos 
            (id_parque_automotor, tipo_documento, fecha_vencimiento_nueva, observaciones)
            SELECT 
                id_parque_automotor,
                'Poliza de Seguro' as tipo_documento,
                {campo_poliza} as fecha_vencimiento_nueva,
                'Migracion automatica de datos existentes' as observaciones
            FROM parque_automotor 
            WHERE {campo_poliza} IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM historial_documentos_vehiculos h 
                WHERE h.id_parque_automotor = parque_automotor.id_parque_automotor 
                AND h.tipo_documento = 'Poliza de Seguro'
            );
            """
            
            try:
                cursor.execute(sql_poliza)
                rows_affected = cursor.rowcount
                connection.commit()
                print(f"Exito: {rows_affected} registros migrados")
                
                # Verificar total de registros
                cursor.execute("SELECT COUNT(*) FROM historial_documentos_vehiculos;")
                total = cursor.fetchone()[0]
                print(f"Total de registros en historial: {total}")
                
                cursor.execute("""
                    SELECT tipo_documento, COUNT(*) as cantidad 
                    FROM historial_documentos_vehiculos 
                    GROUP BY tipo_documento;
                """)
                estadisticas = cursor.fetchall()
                
                print("\nDistribucion por tipo de documento:")
                for tipo, cantidad in estadisticas:
                    print(f"  - {tipo}: {cantidad} registros")
                
                return True
                
            except Error as e:
                print(f"Error con campo {campo_poliza}: {e}")
                continue
        
        print("No se pudo completar la migracion de polizas")
        return False
        
    except Error as e:
        print(f"Error de conexion: {e}")
        return False
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexion cerrada")

if __name__ == "__main__":
    exito = main()
    sys.exit(0 if exito else 1)