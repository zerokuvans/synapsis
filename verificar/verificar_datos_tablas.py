#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar el estado de los datos en las tablas relacionadas con stock
Analiza por qué la tabla dotaciones puede estar vacía
"""

import mysql.connector
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de base de datos
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def verificar_conexion():
    """Verificar conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ Conexión exitosa a MySQL versión: {version[0]}")
        print(f"📊 Base de datos: {DB_CONFIG['database']}")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def analizar_tabla(nombre_tabla, descripcion=""):
    """Analizar una tabla específica"""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        print(f"\n{'='*60}")
        print(f"📋 ANÁLISIS DE TABLA: {nombre_tabla.upper()}")
        if descripcion:
            print(f"📝 Descripción: {descripcion}")
        print(f"{'='*60}")
        
        # Verificar si la tabla existe
        cursor.execute(f"SHOW TABLES LIKE '{nombre_tabla}'")
        tabla_existe = cursor.fetchone()
        
        if not tabla_existe:
            print(f"❌ La tabla '{nombre_tabla}' NO EXISTE")
            return
        
        print(f"✅ La tabla '{nombre_tabla}' existe")
        
        # Obtener estructura de la tabla
        cursor.execute(f"DESCRIBE {nombre_tabla}")
        estructura = cursor.fetchall()
        print(f"\n🏗️  ESTRUCTURA DE LA TABLA:")
        for campo in estructura:
            print(f"   - {campo['Field']}: {campo['Type']} {'(PK)' if campo['Key'] == 'PRI' else ''}")
        
        # Contar registros
        cursor.execute(f"SELECT COUNT(*) as total FROM {nombre_tabla}")
        total_registros = cursor.fetchone()['total']
        print(f"\n📊 TOTAL DE REGISTROS: {total_registros}")
        
        if total_registros > 0:
            # Mostrar algunos registros de ejemplo
            cursor.execute(f"SELECT * FROM {nombre_tabla} LIMIT 5")
            ejemplos = cursor.fetchall()
            print(f"\n📄 EJEMPLOS DE REGISTROS (primeros 5):")
            for i, registro in enumerate(ejemplos, 1):
                print(f"   Registro {i}: {dict(registro)}")
            
            # Fechas de creación si existe campo de fecha
            campos_fecha = ['fecha_creacion', 'created_at', 'fecha', 'timestamp']
            campo_fecha_encontrado = None
            for campo in campos_fecha:
                cursor.execute(f"SHOW COLUMNS FROM {nombre_tabla} LIKE '{campo}'")
                if cursor.fetchone():
                    campo_fecha_encontrado = campo
                    break
            
            if campo_fecha_encontrado:
                cursor.execute(f"SELECT MIN({campo_fecha_encontrado}) as primera, MAX({campo_fecha_encontrado}) as ultima FROM {nombre_tabla}")
                fechas = cursor.fetchone()
                print(f"\n📅 RANGO DE FECHAS:")
                print(f"   Primera: {fechas['primera']}")
                print(f"   Última: {fechas['ultima']}")
        else:
            print(f"\n⚠️  LA TABLA ESTÁ VACÍA - POSIBLES CAUSAS:")
            print(f"   1. No se han insertado datos aún")
            print(f"   2. Los datos fueron eliminados")
            print(f"   3. Problema en el proceso de inserción")
            print(f"   4. Configuración incorrecta de la aplicación")
        
    except Exception as e:
        print(f"❌ Error analizando tabla {nombre_tabla}: {e}")
    finally:
        if connection:
            connection.close()

def verificar_relaciones():
    """Verificar las relaciones entre tablas"""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        print(f"\n{'='*60}")
        print(f"🔗 ANÁLISIS DE RELACIONES ENTRE TABLAS")
        print(f"{'='*60}")
        
        # Verificar si hay técnicos (usuarios) que puedan tener dotaciones
        cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE rol = 'tecnico'")
        tecnicos = cursor.fetchone()['total']
        print(f"\n👥 TÉCNICOS DISPONIBLES: {tecnicos}")
        
        if tecnicos > 0:
            cursor.execute("SELECT id, nombre, email FROM usuarios WHERE rol = 'tecnico' LIMIT 5")
            ejemplos_tecnicos = cursor.fetchall()
            print(f"📄 Ejemplos de técnicos:")
            for tecnico in ejemplos_tecnicos:
                print(f"   - ID: {tecnico['id']}, Nombre: {tecnico['nombre']}, Email: {tecnico['email']}")
        
        # Verificar materiales disponibles en stock
        cursor.execute("SELECT DISTINCT material_tipo, SUM(cantidad_disponible) as total FROM stock_ferretero GROUP BY material_tipo")
        materiales = cursor.fetchall()
        print(f"\n📦 MATERIALES EN STOCK: {len(materiales)}")
        for material in materiales:
            print(f"   - {material['material_tipo']}: {material['total']} unidades")
        
        # Verificar si existen foreign keys
        cursor.execute(f"""
            SELECT 
                TABLE_NAME,
                COLUMN_NAME,
                CONSTRAINT_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
            WHERE REFERENCED_TABLE_SCHEMA = '{DB_CONFIG['database']}'
            AND TABLE_NAME IN ('dotaciones', 'cambios_dotacion')
        """)
        foreign_keys = cursor.fetchall()
        
        if foreign_keys:
            print(f"\n🔑 FOREIGN KEYS ENCONTRADAS:")
            for fk in foreign_keys:
                print(f"   - {fk['TABLE_NAME']}.{fk['COLUMN_NAME']} -> {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}")
        else:
            print(f"\n⚠️  NO SE ENCONTRARON FOREIGN KEYS DEFINIDAS")
        
    except Exception as e:
        print(f"❌ Error verificando relaciones: {e}")
    finally:
        if connection:
            connection.close()

def verificar_vista_stock():
    """Verificar la vista vista_stock_dotaciones"""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        print(f"\n{'='*60}")
        print(f"👁️  ANÁLISIS DE VISTA: vista_stock_dotaciones")
        print(f"{'='*60}")
        
        # Verificar si la vista existe
        cursor.execute("SHOW TABLES LIKE 'vista_stock_dotaciones'")
        vista_existe = cursor.fetchone()
        
        if not vista_existe:
            print(f"❌ La vista 'vista_stock_dotaciones' NO EXISTE")
            return
        
        print(f"✅ La vista 'vista_stock_dotaciones' existe")
        
        # Obtener definición de la vista
        cursor.execute("SHOW CREATE VIEW vista_stock_dotaciones")
        definicion = cursor.fetchone()
        print(f"\n📋 DEFINICIÓN DE LA VISTA:")
        print(f"{definicion['Create View']}")
        
        # Probar la vista
        cursor.execute("SELECT * FROM vista_stock_dotaciones LIMIT 5")
        resultados = cursor.fetchall()
        print(f"\n📊 RESULTADOS DE LA VISTA: {len(resultados)} registros")
        
        for i, resultado in enumerate(resultados, 1):
            print(f"   Registro {i}: {dict(resultado)}")
        
    except Exception as e:
        print(f"❌ Error verificando vista: {e}")
    finally:
        if connection:
            connection.close()

def main():
    """Función principal"""
    print(f"🔍 VERIFICACIÓN DE DATOS DE TABLAS - {datetime.now()}")
    print(f"{'='*80}")
    
    # Verificar conexión
    if not verificar_conexion():
        return
    
    # Analizar cada tabla
    tablas_analizar = [
        ('usuarios', 'Tabla de usuarios del sistema'),
        ('stock_ferretero', 'Inventario de materiales disponibles'),
        ('dotaciones', 'Asignaciones de materiales a técnicos'),
        ('cambios_dotacion', 'Registro de cambios en dotaciones')
    ]
    
    for nombre_tabla, descripcion in tablas_analizar:
        analizar_tabla(nombre_tabla, descripcion)
    
    # Verificar relaciones
    verificar_relaciones()
    
    # Verificar vista
    verificar_vista_stock()
    
    print(f"\n{'='*80}")
    print(f"✅ VERIFICACIÓN COMPLETADA - {datetime.now()}")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()