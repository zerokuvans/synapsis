#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error

def analizar_tablas_turnos():
    """
    Analiza las tablas existentes 'turnos', 'analistas_turnos_base' y 'recurso_operativo'
    en la base de datos capired para generar documentación precisa.
    """
    try:
        # Configuración de conexión a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password=''
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            print("✅ Conexión exitosa a la base de datos capired")
            print("=" * 80)
            
            # 1. Analizar tabla 'turnos'
            print("\n📋 ANÁLISIS DE LA TABLA 'turnos'")
            print("-" * 50)
            
            # Describir estructura de la tabla turnos
            cursor.execute("DESCRIBE turnos")
            turnos_columns = cursor.fetchall()
            
            print("Estructura de la tabla 'turnos':")
            for column in turnos_columns:
                print(f"  - {column[0]} ({column[1]}) - {column[2]} - {column[3]} - {column[4]}")
            
            # Mostrar datos de ejemplo de turnos
            cursor.execute("SELECT * FROM turnos LIMIT 5")
            turnos_data = cursor.fetchall()
            
            print("\nDatos de ejemplo (primeros 5 registros):")
            if turnos_data:
                for row in turnos_data:
                    print(f"  {row}")
            else:
                print("  No hay datos en la tabla turnos")
            
            # 2. Analizar tabla 'analistas_turnos_base'
            print("\n\n👥 ANÁLISIS DE LA TABLA 'analistas_turnos_base'")
            print("-" * 50)
            
            # Describir estructura de la tabla analistas_turnos_base
            cursor.execute("DESCRIBE analistas_turnos_base")
            analistas_turnos_columns = cursor.fetchall()
            
            print("Estructura de la tabla 'analistas_turnos_base':")
            for column in analistas_turnos_columns:
                print(f"  - {column[0]} ({column[1]}) - {column[2]} - {column[3]} - {column[4]}")
            
            # Mostrar datos de ejemplo de analistas_turnos_base
            cursor.execute("SELECT * FROM analistas_turnos_base LIMIT 5")
            analistas_turnos_data = cursor.fetchall()
            
            print("\nDatos de ejemplo (primeros 5 registros):")
            if analistas_turnos_data:
                for row in analistas_turnos_data:
                    print(f"  {row}")
            else:
                print("  No hay datos en la tabla analistas_turnos_base")
            
            # 3. Analizar tabla 'recurso_operativo'
            print("\n\n👤 ANÁLISIS DE LA TABLA 'recurso_operativo'")
            print("-" * 50)
            
            # Describir estructura de la tabla recurso_operativo
            cursor.execute("DESCRIBE recurso_operativo")
            recurso_operativo_columns = cursor.fetchall()
            
            print("Estructura de la tabla 'recurso_operativo':")
            for column in recurso_operativo_columns:
                print(f"  - {column[0]} ({column[1]}) - {column[2]} - {column[3]} - {column[4]}")
            
            # Verificar valores únicos en la columna 'cargo' para filtrar analistas
            cursor.execute("SELECT DISTINCT cargo FROM recurso_operativo WHERE cargo IS NOT NULL")
            cargos_data = cursor.fetchall()
            
            print("\nValores únicos en la columna 'cargo':")
            if cargos_data:
                for cargo in cargos_data:
                    print(f"  - {cargo[0]}")
            else:
                print("  No hay datos en la columna cargo")
            
            # 4. Análisis de relaciones entre tablas
            print("\n\n🔗 ANÁLISIS DE RELACIONES ENTRE TABLAS")
            print("-" * 50)
            
            # Verificar si hay datos relacionados
            cursor.execute("""
                SELECT COUNT(*) as total_asignaciones 
                FROM analistas_turnos_base atb
                INNER JOIN turnos t ON atb.analistas_turnos_turno = t.turnos_id
                INNER JOIN recurso_operativo ro ON atb.analistas_turnos_analista = ro.recurso_operativo_id
            """)
            relaciones_count = cursor.fetchone()
            
            print(f"Total de asignaciones de turnos a analistas: {relaciones_count[0]}")
            
            # Mostrar ejemplo de datos relacionados
            cursor.execute("""
                SELECT 
                    ro.recurso_operativo_nombre as analista,
                    ro.cargo,
                    t.turnos_horario,
                    atb.analistas_turnos_fecha
                FROM analistas_turnos_base atb
                INNER JOIN turnos t ON atb.analistas_turnos_turno = t.turnos_id
                INNER JOIN recurso_operativo ro ON atb.analistas_turnos_analista = ro.recurso_operativo_id
                LIMIT 5
            """)
            relaciones_data = cursor.fetchall()
            
            print("\nEjemplo de datos relacionados:")
            if relaciones_data:
                for row in relaciones_data:
                    print(f"  Analista: {row[0]} | Cargo: {row[1]} | Turno: {row[2]} | Fecha: {row[3]}")
            else:
                print("  No hay datos relacionados entre las tablas")
            
            print("\n" + "=" * 80)
            print("✅ Análisis completado exitosamente")
            
    except Error as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Conexión a la base de datos cerrada")

if __name__ == "__main__":
    analizar_tablas_turnos()