#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script específico para analizar la tabla dotaciones
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

def main():
    connection = None
    try:
        print(f"🔍 ANÁLISIS ESPECÍFICO DE TABLA DOTACIONES - {datetime.now()}")
        print(f"{'='*70}")
        
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # 1. Verificar si la tabla dotaciones existe
        print("\n1️⃣ VERIFICANDO EXISTENCIA DE TABLA DOTACIONES")
        cursor.execute("SHOW TABLES LIKE 'dotaciones'")
        tabla_existe = cursor.fetchone()
        
        if not tabla_existe:
            print("❌ La tabla 'dotaciones' NO EXISTE")
            return
        
        print("✅ La tabla 'dotaciones' existe")
        
        # 2. Estructura de la tabla
        print("\n2️⃣ ESTRUCTURA DE LA TABLA DOTACIONES")
        cursor.execute("DESCRIBE dotaciones")
        estructura = cursor.fetchall()
        for campo in estructura:
            print(f"   - {campo['Field']}: {campo['Type']} {'(PK)' if campo['Key'] == 'PRI' else ''}")
        
        # 3. Contar registros
        print("\n3️⃣ CONTEO DE REGISTROS")
        cursor.execute("SELECT COUNT(*) as total FROM dotaciones")
        total_registros = cursor.fetchone()['total']
        print(f"📊 TOTAL DE REGISTROS EN DOTACIONES: {total_registros}")
        
        if total_registros == 0:
            print("\n⚠️  LA TABLA DOTACIONES ESTÁ VACÍA")
            print("\n🔍 POSIBLES CAUSAS:")
            print("   1. No se han creado dotaciones aún")
            print("   2. Los datos fueron eliminados")
            print("   3. Error en el proceso de inserción")
            print("   4. Problema de permisos en la base de datos")
            print("   5. La aplicación no está insertando datos correctamente")
        else:
            # Mostrar algunos registros
            cursor.execute("SELECT * FROM dotaciones LIMIT 5")
            registros = cursor.fetchall()
            print("\n📄 EJEMPLOS DE REGISTROS:")
            for i, registro in enumerate(registros, 1):
                print(f"   Registro {i}: {dict(registro)}")
        
        # 4. Verificar tabla de usuarios (técnicos)
        print("\n4️⃣ VERIFICANDO USUARIOS/TÉCNICOS DISPONIBLES")
        cursor.execute("SELECT COUNT(*) as total FROM usuarios")
        total_usuarios = cursor.fetchone()['total']
        print(f"👥 TOTAL DE USUARIOS: {total_usuarios}")
        
        if total_usuarios > 0:
            cursor.execute("SELECT * FROM usuarios LIMIT 3")
            usuarios = cursor.fetchall()
            print("📄 Ejemplos de usuarios:")
            for usuario in usuarios:
                print(f"   - ID: {usuario.get('idusuarios', 'N/A')}, Nombre: {usuario.get('usuario_nombre', 'N/A')}")
        
        # 5. Verificar tabla ingresos_dotaciones
        print("\n5️⃣ VERIFICANDO TABLA INGRESOS_DOTACIONES")
        cursor.execute("SHOW TABLES LIKE 'ingresos_dotaciones'")
        ingresos_existe = cursor.fetchone()
        
        if ingresos_existe:
            print("✅ La tabla 'ingresos_dotaciones' existe")
            cursor.execute("SELECT COUNT(*) as total FROM ingresos_dotaciones")
            total_ingresos = cursor.fetchone()['total']
            print(f"📊 TOTAL DE INGRESOS: {total_ingresos}")
            
            if total_ingresos > 0:
                cursor.execute("SELECT * FROM ingresos_dotaciones LIMIT 3")
                ingresos = cursor.fetchall()
                print("📄 Ejemplos de ingresos:")
                for ingreso in ingresos:
                    print(f"   - {dict(ingreso)}")
        else:
            print("❌ La tabla 'ingresos_dotaciones' NO EXISTE")
        
        # 6. Verificar si hay datos en cambios_dotacion
        print("\n6️⃣ VERIFICANDO TABLA CAMBIOS_DOTACION")
        cursor.execute("SELECT COUNT(*) as total FROM cambios_dotacion")
        total_cambios = cursor.fetchone()['total']
        print(f"📊 TOTAL DE CAMBIOS: {total_cambios}")
        
        if total_cambios > 0:
            cursor.execute("SELECT * FROM cambios_dotacion LIMIT 3")
            cambios = cursor.fetchall()
            print("📄 Ejemplos de cambios:")
            for cambio in cambios:
                print(f"   - {dict(cambio)}")
        
        # 7. Verificar permisos de la tabla
        print("\n7️⃣ VERIFICANDO PERMISOS DE TABLA")
        try:
            cursor.execute("INSERT INTO dotaciones (usuario_id, pantalon, camisetagris) VALUES (999, 0, 0)")
            print("✅ Permisos de INSERT: OK")
            cursor.execute("DELETE FROM dotaciones WHERE usuario_id = 999")
            print("✅ Permisos de DELETE: OK")
        except Exception as e:
            print(f"❌ Error de permisos: {e}")
        
        # 8. Mostrar el CREATE TABLE de dotaciones
        print("\n8️⃣ DEFINICIÓN COMPLETA DE LA TABLA")
        cursor.execute("SHOW CREATE TABLE dotaciones")
        create_table = cursor.fetchone()
        print(f"📋 CREATE TABLE:")
        print(f"{create_table['Create Table']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if connection:
            connection.close()
        
        print(f"\n{'='*70}")
        print(f"✅ ANÁLISIS COMPLETADO - {datetime.now()}")
        print(f"{'='*70}")

if __name__ == '__main__':
    main()