#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migración para agregar campo 'estado' a la tabla mpa_mantenimientos
Fecha: 2024-12-20
Descripción: Agrega columna estado con valores 'Abierto' (por defecto) y 'Finalizado'
"""

import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def add_estado_column():
    """Agrega la columna estado a la tabla mpa_mantenimientos"""
    
    connection = None
    cursor = None
    
    try:
        print("🔄 Conectando a la base de datos...")
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            print("✅ Conexión exitosa a la base de datos")
            cursor = connection.cursor()
            
            # Verificar si la tabla existe
            print("🔍 Verificando si la tabla mpa_mantenimientos existe...")
            cursor.execute("SHOW TABLES LIKE 'mpa_mantenimientos'")
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                print("❌ Error: La tabla mpa_mantenimientos no existe")
                return False
            
            # Verificar si la columna estado ya existe
            print("🔍 Verificando si la columna 'estado' ya existe...")
            cursor.execute("SHOW COLUMNS FROM mpa_mantenimientos LIKE 'estado'")
            column_exists = cursor.fetchone() is not None
            
            if column_exists:
                print("⚠️  La columna 'estado' ya existe en la tabla")
                
                # Verificar los valores actuales
                cursor.execute("SELECT DISTINCT estado FROM mpa_mantenimientos")
                existing_values = [row[0] for row in cursor.fetchall()]
                print(f"📊 Valores existentes en la columna estado: {existing_values}")
                
                return True
            
            # Agregar la columna estado
            print("🔧 Agregando columna 'estado' a la tabla mpa_mantenimientos...")
            
            alter_query = """
            ALTER TABLE mpa_mantenimientos 
            ADD COLUMN estado ENUM('Abierto', 'Finalizado') NOT NULL DEFAULT 'Abierto'
            AFTER observacion
            """
            
            cursor.execute(alter_query)
            
            # Actualizar registros existentes para que tengan estado 'Abierto'
            print("🔄 Actualizando registros existentes con estado 'Abierto'...")
            cursor.execute("UPDATE mpa_mantenimientos SET estado = 'Abierto' WHERE estado IS NULL")
            
            connection.commit()
            
            print("✅ Columna 'estado' agregada exitosamente")
            
            # Verificar la estructura actualizada
            print("📋 Verificando estructura actualizada...")
            cursor.execute("DESCRIBE mpa_mantenimientos")
            columns = cursor.fetchall()
            
            print("\n📊 Estructura actualizada de mpa_mantenimientos:")
            for column in columns:
                status = "🆕" if column[0] == 'estado' else "  "
                print(f"{status} {column[0]}: {column[1]} {column[2]} {column[3]} {column[4]} {column[5]}")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM mpa_mantenimientos")
            total_records = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM mpa_mantenimientos WHERE estado = 'Abierto'")
            abierto_records = cursor.fetchone()[0]
            
            print(f"\n📈 Estadísticas:")
            print(f"   Total de registros: {total_records}")
            print(f"   Registros con estado 'Abierto': {abierto_records}")
            print(f"   Registros con estado 'Finalizado': {total_records - abierto_records}")
            
            return True
            
    except Error as e:
        print(f"❌ Error al ejecutar migración: {e}")
        if connection:
            connection.rollback()
        return False
    
    finally:
        if connection and connection.is_connected():
            if cursor:
                cursor.close()
            connection.close()
            print("🔌 Conexión cerrada")

def rollback_migration():
    """Rollback: elimina la columna estado (solo para desarrollo)"""
    
    connection = None
    cursor = None
    
    try:
        print("🔄 Conectando a la base de datos para rollback...")
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar si la columna existe
            cursor.execute("SHOW COLUMNS FROM mpa_mantenimientos LIKE 'estado'")
            column_exists = cursor.fetchone() is not None
            
            if not column_exists:
                print("⚠️  La columna 'estado' no existe, no hay nada que revertir")
                return True
            
            print("🔧 Eliminando columna 'estado'...")
            cursor.execute("ALTER TABLE mpa_mantenimientos DROP COLUMN estado")
            connection.commit()
            
            print("✅ Rollback completado - columna 'estado' eliminada")
            return True
            
    except Error as e:
        print(f"❌ Error en rollback: {e}")
        return False
    
    finally:
        if connection and connection.is_connected():
            if cursor:
                cursor.close()
            connection.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        print("🔄 Ejecutando rollback de migración...")
        rollback_migration()
    else:
        print("🚀 Ejecutando migración: Agregar campo 'estado' a mpa_mantenimientos")
        print("=" * 60)
        success = add_estado_column()
        
        if success:
            print("\n🎉 ¡Migración completada exitosamente!")
            print("📝 La tabla mpa_mantenimientos ahora incluye el campo 'estado'")
            print("🔧 Próximo paso: Actualizar el formulario y APIs")
        else:
            print("\n❌ La migración falló. Revisa los errores anteriores.")
            print("💡 Tip: Puedes ejecutar con --rollback para revertir cambios")