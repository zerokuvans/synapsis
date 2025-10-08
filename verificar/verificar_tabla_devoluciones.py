#!/usr/bin/env python3
"""
Script para verificar y corregir la estructura de la tabla devoluciones
"""

import mysql.connector

def verificar_tabla_devoluciones():
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = connection.cursor(dictionary=True)
        
        print("🔍 Verificando estructura de la tabla devoluciones_dotacion...")
        
        # Verificar estructura actual
        cursor.execute("DESCRIBE devoluciones_dotacion")
        estructura = cursor.fetchall()
        
        print("\n📋 Estructura actual de la tabla devoluciones_dotacion:")
        columnas_existentes = []
        for campo in estructura:
            columnas_existentes.append(campo['Field'])
            print(f"  - {campo['Field']}: {campo['Type']} {'NULL' if campo['Null'] == 'YES' else 'NOT NULL'}")
        
        # Verificar si existe la columna updated_by
        if 'updated_by' not in columnas_existentes:
            print("\n❌ La columna 'updated_by' no existe")
            print("🔧 Agregando columna 'updated_by'...")
            
            cursor.execute("""
                ALTER TABLE devoluciones_dotacion 
                ADD COLUMN updated_by INT NULL,
                ADD CONSTRAINT fk_devoluciones_dotacion_updated_by 
                FOREIGN KEY (updated_by) REFERENCES recurso_operativo(id_codigo_consumidor)
            """)
            print("✅ Columna 'updated_by' agregada")
        else:
            print("✅ La columna 'updated_by' ya existe")
        
        # Verificar si existe la columna updated_at
        if 'updated_at' not in columnas_existentes:
            print("\n❌ La columna 'updated_at' no existe")
            print("🔧 Agregando columna 'updated_at'...")
            
            cursor.execute("""
                ALTER TABLE devoluciones_dotacion 
                ADD COLUMN updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            """)
            print("✅ Columna 'updated_at' agregada")
        else:
            print("✅ La columna 'updated_at' ya existe")
        
        connection.commit()
        
        # Verificar estructura final
        cursor.execute("DESCRIBE devoluciones_dotacion")
        estructura_final = cursor.fetchall()
        
        print("\n📋 Estructura final de la tabla devoluciones_dotacion:")
        for campo in estructura_final:
            print(f"  - {campo['Field']}: {campo['Type']} {'NULL' if campo['Null'] == 'YES' else 'NOT NULL'}")
        
        cursor.close()
        connection.close()
        
        print("\n✅ Verificación completada")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    verificar_tabla_devoluciones()