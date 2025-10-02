#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def add_asistencia_fields():
    """Agregar nuevos campos a la tabla asistencia para el módulo de inicio de operación"""
    try:
        print("=== MIGRACIÓN: AGREGAR CAMPOS A TABLA ASISTENCIA ===")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Conectar a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("✅ Conectado a la base de datos MySQL")
        
        # Verificar estructura actual de la tabla asistencia
        print("\n🔍 Verificando estructura actual de la tabla 'asistencia'...")
        cursor.execute("DESCRIBE asistencia")
        columns = cursor.fetchall()
        
        existing_columns = [col[0] for col in columns]
        print(f"Columnas existentes: {existing_columns}")
        
        # Campos a agregar
        new_fields = {
            'hora_inicio': 'TIME NULL COMMENT "Hora de inicio de operación del técnico"',
            'estado': 'ENUM("CUMPLE", "NO CUMPLE", "NOVEDAD", "NO APLICA") NULL COMMENT "Estado de cumplimiento del técnico"',
            'novedad': 'TEXT NULL COMMENT "Descripción de novedad cuando estado es NOVEDAD o NO APLICA"'
        }
        
        # Agregar cada campo si no existe
        for field_name, field_definition in new_fields.items():
            if field_name not in existing_columns:
                print(f"\n🔧 Agregando campo '{field_name}'...")
                
                alter_query = f"ALTER TABLE asistencia ADD COLUMN {field_name} {field_definition}"
                cursor.execute(alter_query)
                
                print(f"   ✅ Campo '{field_name}' agregado exitosamente")
            else:
                print(f"\n⚠️  Campo '{field_name}' ya existe, omitiendo...")
        
        # Confirmar cambios
        connection.commit()
        
        # Verificar estructura final
        print("\n🔍 Verificando estructura final de la tabla 'asistencia'...")
        cursor.execute("DESCRIBE asistencia")
        final_columns = cursor.fetchall()
        
        print("\nEstructura final:")
        for col in final_columns:
            field_name = col[0]
            field_type = col[1]
            is_null = col[2]
            default = col[4]
            extra = col[5]
            
            # Resaltar los nuevos campos
            marker = "🆕" if field_name in new_fields else "  "
            print(f"{marker} {field_name}: {field_type} (NULL: {is_null}, Default: {default}, Extra: {extra})")
        
        print(f"\n✅ Migración completada exitosamente")
        print(f"   - Se agregaron {len([f for f in new_fields.keys() if f not in existing_columns])} nuevos campos")
        print(f"   - Tabla 'asistencia' actualizada para soportar inicio de operación")
        
    except Error as e:
        print(f"\n❌ Error durante la migración: {e}")
        if connection:
            connection.rollback()
        return False
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión a la base de datos cerrada")
    
    return True

def verify_migration():
    """Verificar que la migración se aplicó correctamente"""
    try:
        print("\n=== VERIFICACIÓN DE MIGRACIÓN ===")
        
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Verificar que los nuevos campos existen
        cursor.execute("DESCRIBE asistencia")
        columns = cursor.fetchall()
        
        required_fields = ['hora_inicio', 'estado', 'novedad']
        existing_fields = [col['Field'] for col in columns]
        
        all_present = True
        for field in required_fields:
            if field in existing_fields:
                print(f"✅ Campo '{field}' presente")
            else:
                print(f"❌ Campo '{field}' NO encontrado")
                all_present = False
        
        if all_present:
            print("\n✅ Verificación exitosa: Todos los campos requeridos están presentes")
            
            # Mostrar algunos registros de ejemplo
            print("\n📊 Muestra de registros (primeros 3):")
            cursor.execute("SELECT id_asistencia, fecha_asistencia, hora_inicio, estado, novedad FROM asistencia LIMIT 3")
            sample = cursor.fetchall()
            
            for i, row in enumerate(sample, 1):
                print(f"   Registro {i}: ID={row['id_asistencia']}, Fecha={row['fecha_asistencia']}, "
                      f"Hora={row['hora_inicio']}, Estado={row['estado']}, Novedad={row['novedad']}")
        else:
            print("\n❌ Verificación fallida: Faltan campos requeridos")
            return False
            
    except Error as e:
        print(f"\n❌ Error durante la verificación: {e}")
        return False
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

if __name__ == "__main__":
    print("MIGRACIÓN DE BASE DE DATOS - CAMPOS DE ASISTENCIA")
    print("=" * 50)
    
    # Ejecutar migración
    if add_asistencia_fields():
        # Verificar migración
        verify_migration()
        print("\n🎉 Proceso completado exitosamente")
    else:
        print("\n💥 Proceso fallido")