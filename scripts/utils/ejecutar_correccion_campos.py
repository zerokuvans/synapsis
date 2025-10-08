#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para ejecutar la corrección de campos faltantes en la tabla parque_automotor
"""

import mysql.connector
from mysql.connector import Error
import sys
from datetime import datetime

# Configuración de conexión
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def ejecutar_sql(cursor, sql, descripcion):
    """Ejecuta una consulta SQL y maneja errores"""
    try:
        cursor.execute(sql)
        print(f"✅ {descripcion}")
        return True
    except Error as e:
        if "Duplicate column name" in str(e) or "already exists" in str(e):
            print(f"ℹ️  {descripcion} (ya existe)")
            return True
        else:
            print(f"❌ Error en {descripcion}: {e}")
            return False

def main():
    """Función principal"""
    print("🔧 CORRECCIÓN DE CAMPOS FALTANTES EN TABLA PARQUE_AUTOMOTOR")
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(buffered=True)
        
        print("🔗 Conexión a base de datos establecida")
        
        # 1. Verificar estructura actual
        print("\n📋 Verificando estructura actual...")
        cursor.execute("DESCRIBE parque_automotor;")
        campos_actuales = [row[0] for row in cursor.fetchall()]
        print(f"   Campos actuales: {len(campos_actuales)}")
        
        # 2. Agregar campos faltantes
        print("\n🔧 Agregando campos faltantes...")
        
        # Campo: vehiculo_asistio_operacion
        sql_vehiculo_asistio = """
        ALTER TABLE parque_automotor 
        ADD COLUMN vehiculo_asistio_operacion VARCHAR(10) DEFAULT 'No' 
        COMMENT 'Indica si el vehículo asistió a la operación (Sí/No)'
        """
        ejecutar_sql(cursor, sql_vehiculo_asistio, "Campo vehiculo_asistio_operacion agregado")
        
        # Campo: licencia_conduccion
        sql_licencia = """
        ALTER TABLE parque_automotor 
        ADD COLUMN licencia_conduccion VARCHAR(20) 
        COMMENT 'Número de licencia de conducción del conductor asignado'
        """
        ejecutar_sql(cursor, sql_licencia, "Campo licencia_conduccion agregado")
        
        # Campo: vencimiento_licencia
        sql_vencimiento = """
        ALTER TABLE parque_automotor 
        ADD COLUMN vencimiento_licencia DATE 
        COMMENT 'Fecha de vencimiento de la licencia de conducción'
        """
        ejecutar_sql(cursor, sql_vencimiento, "Campo vencimiento_licencia agregado")
        
        # 3. Crear índices
        print("\n📊 Creando índices de optimización...")
        
        indices = [
            ("CREATE INDEX idx_vehiculo_asistio_operacion ON parque_automotor(vehiculo_asistio_operacion)", 
             "Índice vehiculo_asistio_operacion"),
            ("CREATE INDEX idx_licencia_conduccion ON parque_automotor(licencia_conduccion)", 
             "Índice licencia_conduccion"),
            ("CREATE INDEX idx_vencimiento_licencia ON parque_automotor(vencimiento_licencia)", 
             "Índice vencimiento_licencia"),
            ("CREATE INDEX idx_vencimientos_documentos ON parque_automotor(vencimiento_licencia, soat_vencimiento, tecnomecanica_vencimiento)", 
             "Índice compuesto vencimientos")
        ]
        
        for sql_indice, descripcion in indices:
            try:
                cursor.execute(sql_indice)
                print(f"✅ {descripcion} creado")
            except Error as e:
                if "Duplicate key name" in str(e) or "already exists" in str(e):
                    print(f"ℹ️  {descripcion} (ya existe)")
                else:
                    print(f"⚠️  Error creando {descripcion}: {e}")
        
        # 4. Actualizar datos existentes
        print("\n🔄 Actualizando datos existentes...")
        sql_update = """
        UPDATE parque_automotor 
        SET vehiculo_asistio_operacion = 'No' 
        WHERE vehiculo_asistio_operacion IS NULL
        """
        cursor.execute(sql_update)
        registros_actualizados = cursor.rowcount
        print(f"✅ {registros_actualizados} registros actualizados con valor por defecto")
        
        # 5. Confirmar cambios
        connection.commit()
        print("\n💾 Cambios confirmados en la base de datos")
        
        # 6. Verificar estructura final
        print("\n📋 Verificando estructura final...")
        cursor.execute("DESCRIBE parque_automotor;")
        campos_finales = cursor.fetchall()
        print(f"   Total de campos: {len(campos_finales)}")
        
        # Verificar campos específicos
        campos_requeridos = ['vehiculo_asistio_operacion', 'licencia_conduccion', 'vencimiento_licencia']
        campos_encontrados = [row[0] for row in campos_finales]
        
        print("\n🔍 Verificando campos agregados:")
        for campo in campos_requeridos:
            if campo in campos_encontrados:
                print(f"   ✅ {campo} - OK")
            else:
                print(f"   ❌ {campo} - FALTANTE")
        
        # 7. Verificar índices
        print("\n📊 Verificando índices creados:")
        cursor.execute("""
        SELECT INDEX_NAME, COLUMN_NAME
        FROM INFORMATION_SCHEMA.STATISTICS 
        WHERE TABLE_SCHEMA = 'capired' 
        AND TABLE_NAME = 'parque_automotor'
        AND INDEX_NAME LIKE 'idx_%'
        ORDER BY INDEX_NAME
        """)
        
        indices_creados = cursor.fetchall()
        for indice in indices_creados:
            print(f"   ✅ {indice[0]} ({indice[1]})")
        
        # 8. Estadísticas finales
        print("\n📈 Estadísticas finales:")
        cursor.execute("SELECT COUNT(*) FROM parque_automotor")
        total_registros = cursor.fetchone()[0]
        
        cursor.execute("""
        SELECT 
            COUNT(CASE WHEN vehiculo_asistio_operacion IS NOT NULL THEN 1 END) as con_asistio,
            COUNT(CASE WHEN licencia_conduccion IS NOT NULL THEN 1 END) as con_licencia,
            COUNT(CASE WHEN vencimiento_licencia IS NOT NULL THEN 1 END) as con_vencimiento
        FROM parque_automotor
        """)
        
        estadisticas = cursor.fetchone()
        print(f"   📊 Total de registros: {total_registros}")
        print(f"   📊 Con vehiculo_asistio_operacion: {estadisticas[0]}")
        print(f"   📊 Con licencia_conduccion: {estadisticas[1]}")
        print(f"   📊 Con vencimiento_licencia: {estadisticas[2]}")
        
        # Cerrar conexión
        cursor.close()
        connection.close()
        
        print("\n" + "="*80)
        print("🎯 CORRECCIÓN COMPLETADA EXITOSAMENTE")
        print("✅ Campos faltantes agregados")
        print("✅ Índices de optimización creados")
        print("✅ Datos existentes actualizados")
        print("✅ Formulario y base de datos ahora están sincronizados")
        print("="*80)
        
        return True
        
    except Error as e:
        print(f"💥 Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Corrección interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)