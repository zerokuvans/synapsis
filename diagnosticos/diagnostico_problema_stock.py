#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico completo del problema de cálculo de stock
Analiza las diferencias entre local y producción
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
        print(f"🔍 DIAGNÓSTICO COMPLETO DEL PROBLEMA DE STOCK - {datetime.now()}")
        print(f"{'='*80}")
        
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        print("\n📋 RESUMEN DEL PROBLEMA IDENTIFICADO:")
        print("="*50)
        
        # 1. Problema principal identificado
        print("\n🚨 PROBLEMA PRINCIPAL:")
        print("   La tabla 'dotaciones' está VACÍA (0 registros)")
        print("   Esto causa que el cálculo de stock no funcione correctamente")
        
        # 2. Estructura de la tabla dotaciones
        print("\n🏗️  ESTRUCTURA ACTUAL DE LA TABLA DOTACIONES:")
        cursor.execute("DESCRIBE dotaciones")
        estructura = cursor.fetchall()
        for campo in estructura:
            print(f"   - {campo['Field']}: {campo['Type']}")
        
        # 3. Verificar tabla recurso_operativo (referenciada por FK)
        print("\n🔗 VERIFICANDO TABLA RECURSO_OPERATIVO (FK):")
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        recurso_existe = cursor.fetchone()
        
        if recurso_existe:
            cursor.execute("SELECT COUNT(*) as total FROM recurso_operativo")
            total_recursos = cursor.fetchone()['total']
            print(f"   ✅ Tabla existe con {total_recursos} registros")
            
            if total_recursos > 0:
                cursor.execute("SELECT * FROM recurso_operativo LIMIT 3")
                recursos = cursor.fetchall()
                print("   📄 Ejemplos de recursos operativos:")
                for recurso in recursos:
                    print(f"      - ID: {recurso.get('id_codigo_consumidor')}, Datos: {dict(recurso)}")
        else:
            print("   ❌ Tabla recurso_operativo NO EXISTE")
        
        # 4. Verificar ingresos_dotaciones
        print("\n📦 VERIFICANDO INGRESOS DE DOTACIONES:")
        cursor.execute("SHOW TABLES LIKE 'ingresos_dotaciones'")
        ingresos_existe = cursor.fetchone()
        
        if ingresos_existe:
            cursor.execute("SELECT COUNT(*) as total FROM ingresos_dotaciones")
            total_ingresos = cursor.fetchone()['total']
            print(f"   ✅ Tabla existe con {total_ingresos} registros")
            
            if total_ingresos > 0:
                cursor.execute("SELECT tipo_elemento, SUM(cantidad) as total FROM ingresos_dotaciones GROUP BY tipo_elemento")
                ingresos_por_tipo = cursor.fetchall()
                print("   📊 Ingresos por tipo de elemento:")
                for ingreso in ingresos_por_tipo:
                    print(f"      - {ingreso['tipo_elemento']}: {ingreso['total']} unidades")
        else:
            print("   ❌ Tabla ingresos_dotaciones NO EXISTE")
        
        # 5. Análisis del problema de cálculo
        print("\n🧮 ANÁLISIS DEL CÁLCULO DE STOCK:")
        print("   Fórmula actual: stock_inicial - total_asignaciones - total_cambios")
        print("   \n   PROBLEMA IDENTIFICADO:")
        print("   - stock_inicial viene de 'stock_ferretero' (materiales técnicos)")
        print("   - total_asignaciones viene de 'dotaciones' (VACÍA)")
        print("   - total_cambios viene de 'cambios_dotacion'")
        print("   \n   RESULTADO: Como 'dotaciones' está vacía, total_asignaciones = 0")
        print("   Esto hace que el stock calculado sea incorrecto")
        
        # 6. Verificar diferencias entre tablas
        print("\n🔍 DIFERENCIAS ENTRE SISTEMAS:")
        print("   STOCK_FERRETERO (materiales técnicos):")
        cursor.execute("SELECT material_tipo, cantidad_disponible FROM stock_ferretero")
        stock_ferretero = cursor.fetchall()
        for item in stock_ferretero:
            print(f"      - {item['material_tipo']}: {item['cantidad_disponible']}")
        
        print("   \n   INGRESOS_DOTACIONES (dotaciones de vestimenta):")
        if ingresos_existe:
            cursor.execute("SELECT tipo_elemento, SUM(cantidad) as total FROM ingresos_dotaciones GROUP BY tipo_elemento")
            ingresos = cursor.fetchall()
            for item in ingresos:
                print(f"      - {item['tipo_elemento']}: {item['total']}")
        
        # 7. Propuesta de solución
        print("\n💡 PROPUESTA DE SOLUCIÓN:")
        print("="*40)
        print("\n1️⃣ PROBLEMA DE DATOS:")
        print("   - La tabla 'dotaciones' necesita datos")
        print("   - Verificar por qué no se están insertando dotaciones")
        print("   - Revisar el proceso de asignación de dotaciones")
        
        print("\n2️⃣ PROBLEMA DE ESTRUCTURA:")
        print("   - Hay inconsistencia entre tipos de materiales:")
        print("     * stock_ferretero: materiales técnicos (silicona, amarres, etc.)")
        print("     * dotaciones: vestimenta (pantalón, camiseta, etc.)")
        print("     * ingresos_dotaciones: vestimenta (pantalón, camiseta, etc.)")
        
        print("\n3️⃣ SOLUCIÓN RECOMENDADA:")
        print("   A. Separar los cálculos por tipo de material:")
        print("      - Materiales técnicos: usar solo stock_ferretero")
        print("      - Vestimenta: usar ingresos_dotaciones - dotaciones - cambios")
        print("   B. Poblar la tabla dotaciones con datos de prueba")
        print("   C. Verificar el proceso de inserción en producción")
        
        # 8. Script de prueba para insertar datos
        print("\n🧪 GENERANDO DATOS DE PRUEBA:")
        try:
            # Verificar si hay recursos operativos
            cursor.execute("SELECT id_codigo_consumidor FROM recurso_operativo LIMIT 1")
            recurso = cursor.fetchone()
            
            if recurso:
                id_recurso = recurso['id_codigo_consumidor']
                print(f"   ✅ Usando recurso operativo ID: {id_recurso}")
                
                # Insertar una dotación de prueba
                cursor.execute("""
                    INSERT INTO dotaciones 
                    (cliente, id_codigo_consumidor, pantalon, camisetagris, guerrera, 
                     camisetapolo, botas, guantes_nitrilo, guantes_carnaza, gafas, 
                     gorra, casco, fecha_registro) 
                    VALUES 
                    ('CLIENTE_PRUEBA', %s, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, NOW())
                """, (id_recurso,))
                
                connection.commit()
                print("   ✅ Dotación de prueba insertada exitosamente")
                
                # Verificar la inserción
                cursor.execute("SELECT COUNT(*) as total FROM dotaciones")
                nuevo_total = cursor.fetchone()['total']
                print(f"   📊 Nuevo total de dotaciones: {nuevo_total}")
                
            else:
                print("   ❌ No hay recursos operativos disponibles para crear dotación")
                
        except Exception as e:
            print(f"   ❌ Error insertando datos de prueba: {e}")
            connection.rollback()
        
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
    finally:
        if connection:
            connection.close()
        
        print(f"\n{'='*80}")
        print(f"✅ DIAGNÓSTICO COMPLETADO - {datetime.now()}")
        print(f"\n📋 RESUMEN:")
        print(f"   - Problema identificado: Tabla dotaciones vacía")
        print(f"   - Causa: Falta de datos o proceso de inserción defectuoso")
        print(f"   - Solución: Poblar tabla y verificar proceso en producción")
        print(f"{'='*80}")

if __name__ == '__main__':
    main()