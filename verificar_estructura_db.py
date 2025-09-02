#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la estructura real de la base de datos capired
Muestra todas las tablas existentes y sus campos
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

def imprimir_separador(titulo=""):
    """Imprime un separador visual"""
    print("\n" + "="*80)
    if titulo:
        print(f" {titulo} ".center(80, "="))
    print("="*80)

def verificar_todas_las_tablas():
    """Verifica todas las tablas en la base de datos capired"""
    imprimir_separador("ESTRUCTURA COMPLETA DE LA BASE DE DATOS 'capired'")
    
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        
        if connection.is_connected():
            print(f"✅ Conectado a MySQL Server")
            print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            cursor = connection.cursor(buffered=True)
            
            # Obtener todas las tablas
            cursor.execute("SHOW TABLES;")
            tablas = cursor.fetchall()
            
            print(f"\n📊 Total de tablas encontradas: {len(tablas)}")
            
            if not tablas:
                print("❌ No se encontraron tablas en la base de datos 'capired'")
                return False
            
            # Verificar cada tabla
            for (tabla_nombre,) in tablas:
                print(f"\n" + "-"*60)
                print(f"🔍 TABLA: {tabla_nombre}")
                print("-"*60)
                
                try:
                    # Obtener estructura de la tabla
                    cursor.execute(f"DESCRIBE {tabla_nombre};")
                    campos = cursor.fetchall()
                    
                    print(f"📋 Campos ({len(campos)}):")
                    for campo in campos:
                        field, type_info, null, key, default, extra = campo
                        key_info = f" [{key}]" if key else ""
                        null_info = "NULL" if null == "YES" else "NOT NULL"
                        default_info = f" DEFAULT: {default}" if default is not None else ""
                        extra_info = f" {extra}" if extra else ""
                        
                        print(f"   • {field}: {type_info} {null_info}{key_info}{default_info}{extra_info}")
                    
                    # Obtener número de registros
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla_nombre};")
                    count = cursor.fetchone()[0]
                    print(f"📊 Registros: {count}")
                    
                    # Verificar si es una tabla relacionada con automotor
                    if any(keyword in tabla_nombre.lower() for keyword in ['automotor', 'vehiculo', 'parque', 'historial', 'documento']):
                        print(f"🚗 ¡Tabla relacionada con módulo automotor!")
                    
                except Error as e:
                    print(f"❌ Error al verificar tabla {tabla_nombre}: {e}")
            
            # Buscar tablas específicas del módulo automotor
            print(f"\n" + "="*80)
            print(" ANÁLISIS ESPECÍFICO PARA MÓDULO AUTOMOTOR ".center(80, "="))
            print("="*80)
            
            tablas_automotor = [
                'parque_automotor',
                'historial_documentos_vehiculos',
                'usuarios'
            ]
            
            tablas_encontradas = [tabla[0] for tabla in tablas]
            
            for tabla_requerida in tablas_automotor:
                if tabla_requerida in tablas_encontradas:
                    print(f"✅ {tabla_requerida}: ENCONTRADA")
                else:
                    print(f"❌ {tabla_requerida}: NO ENCONTRADA")
                    
                    # Buscar tablas similares
                    similares = [t for t in tablas_encontradas if any(word in t.lower() for word in tabla_requerida.split('_'))]
                    if similares:
                        print(f"   🔍 Tablas similares encontradas: {', '.join(similares)}")
            
            cursor.close()
            connection.close()
            
            return True
            
    except Error as e:
        print(f"❌ Error de conexión: {e}")
        return False

def verificar_tabla_especifica(nombre_tabla):
    """Verifica una tabla específica en detalle"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor(buffered=True)
            
            print(f"\n🔍 ANÁLISIS DETALLADO DE LA TABLA: {nombre_tabla}")
            print("="*60)
            
            # Verificar si existe
            cursor.execute(f"SHOW TABLES LIKE '{nombre_tabla}';")
            result = cursor.fetchone()
            
            if not result:
                print(f"❌ La tabla '{nombre_tabla}' no existe")
                return False
            
            # Estructura completa
            cursor.execute(f"SHOW CREATE TABLE {nombre_tabla};")
            create_table = cursor.fetchone()[1]
            print(f"\n📋 ESTRUCTURA COMPLETA:")
            print(create_table)
            
            # Índices
            cursor.execute(f"SHOW INDEX FROM {nombre_tabla};")
            indices = cursor.fetchall()
            
            if indices:
                print(f"\n🔑 ÍNDICES:")
                for indice in indices:
                    print(f"   • {indice[2]} ({indice[4]}) - {indice[10] if indice[10] else 'BTREE'}")
            
            # Constraints
            cursor.execute(f"""
                SELECT 
                    CONSTRAINT_NAME,
                    CONSTRAINT_TYPE,
                    COLUMN_NAME
                FROM information_schema.TABLE_CONSTRAINTS tc
                JOIN information_schema.KEY_COLUMN_USAGE kcu 
                    ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                WHERE tc.TABLE_SCHEMA = 'capired' 
                    AND tc.TABLE_NAME = '{nombre_tabla}'
            """)
            constraints = cursor.fetchall()
            
            if constraints:
                print(f"\n🔒 CONSTRAINTS:")
                for constraint in constraints:
                    print(f"   • {constraint[0]}: {constraint[1]} en {constraint[2]}")
            
            cursor.close()
            connection.close()
            
            return True
            
    except Error as e:
        print(f"❌ Error al verificar tabla específica: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN DETALLADA DE ESTRUCTURA DE BASE DE DATOS")
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar todas las tablas
    if not verificar_todas_las_tablas():
        print("\n❌ No se pudo completar la verificación")
        return False
    
    # Verificar tablas específicas del automotor si existen
    tablas_especificas = ['parque_automotor', 'historial_documentos_vehiculos']
    
    for tabla in tablas_especificas:
        verificar_tabla_especifica(tabla)
    
    print(f"\n⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✅ Verificación completada")
    
    return True

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Verificación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)