#!/usr/bin/env python3
"""
Script para actualizar la estructura de la tabla mpa_soat
"""

import mysql.connector
from mysql.connector import Error

def fix_mpa_soat_table():
    """Actualizar la estructura de la tabla mpa_soat"""
    try:
        # Configuración de la base de datos (misma que app.py)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("🔧 Actualizando estructura de tabla mpa_soat...")
            
            # Lista de alteraciones necesarias
            alterations = [
                # Cambiar nombre de columna fecha_inicial a fecha_inicio
                "ALTER TABLE mpa_soat CHANGE COLUMN fecha_inicial fecha_inicio DATE",
                
                # Cambiar nombre de columna tecnico a tecnico_asignado
                "ALTER TABLE mpa_soat CHANGE COLUMN tecnico tecnico_asignado VARCHAR(45)",
                
                # Cambiar tipo de numero_poliza de int a varchar
                "ALTER TABLE mpa_soat MODIFY COLUMN numero_poliza VARCHAR(50)",
                
                # Agregar columnas faltantes
                "ALTER TABLE mpa_soat ADD COLUMN aseguradora VARCHAR(100) AFTER numero_poliza",
                "ALTER TABLE mpa_soat ADD COLUMN valor_prima DECIMAL(10,2) AFTER fecha_vencimiento",
                "ALTER TABLE mpa_soat ADD COLUMN estado ENUM('Activo', 'Inactivo', 'Vencido') DEFAULT 'Activo' AFTER tecnico_asignado",
                "ALTER TABLE mpa_soat ADD COLUMN observaciones TEXT AFTER estado",
                "ALTER TABLE mpa_soat ADD COLUMN fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP AFTER observaciones",
                "ALTER TABLE mpa_soat ADD COLUMN fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER fecha_creacion"
            ]
            
            # Ejecutar cada alteración
            for i, alteration in enumerate(alterations, 1):
                try:
                    print(f"  {i}. Ejecutando: {alteration}")
                    cursor.execute(alteration)
                    connection.commit()
                    print(f"     ✅ Completado")
                except Error as e:
                    if "Duplicate column name" in str(e) or "Unknown column" in str(e):
                        print(f"     ⚠️ Columna ya existe o no encontrada: {e}")
                    else:
                        print(f"     ❌ Error: {e}")
                        raise e
            
            print("\n📋 Verificando estructura actualizada...")
            cursor.execute("DESCRIBE mpa_soat")
            columns = cursor.fetchall()
            
            print("-" * 80)
            print(f"{'Campo':<25} {'Tipo':<20} {'Null':<8} {'Key':<8} {'Default':<15} {'Extra'}")
            print("-" * 80)
            
            for column in columns:
                field, type_info, null, key, default, extra = column
                print(f"{field:<25} {type_info:<20} {null:<8} {key:<8} {str(default):<15} {extra}")
            
            print("\n✅ Estructura de tabla mpa_soat actualizada exitosamente")
            
    except Error as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return False
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión cerrada")
    
    return True

if __name__ == "__main__":
    print("🔧 Iniciando actualización de tabla mpa_soat...")
    success = fix_mpa_soat_table()
    if success:
        print("\n🎉 ¡Actualización completada! El módulo SOAT debería funcionar ahora.")
    else:
        print("\n❌ Falló la actualización. Revisa los errores anteriores.")