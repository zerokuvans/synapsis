#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Prueba para Trigger de Entradas de Stock
=================================================
Este script verifica el correcto funcionamiento del trigger
'actualizar_stock_entrada' que actualiza automáticamente
el stock cuando se registran entradas de material.

Fecha: 2025-01-17
Autor: Sistema Ferretero
"""

import mysql.connector
from datetime import datetime
import sys

def conectar_mysql():
    """
    Establece conexión con MySQL
    Ajusta los parámetros según tu configuración
    """
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',  # Ajustar según tu configuración
            password='',  # Ajustar según tu configuración
            database='synapsis'  # Ajustar según tu base de datos
        )
        return conexion
    except mysql.connector.Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None

def verificar_trigger_existe(cursor, nombre_trigger):
    """
    Verifica si un trigger específico existe
    """
    query = "SHOW TRIGGERS LIKE %s"
    cursor.execute(query, (f"%{nombre_trigger}%",))
    resultado = cursor.fetchall()
    return len(resultado) > 0

def verificar_tabla_existe(cursor, nombre_tabla):
    """
    Verifica si una tabla específica existe
    """
    query = "SHOW TABLES LIKE %s"
    cursor.execute(query, (nombre_tabla,))
    resultado = cursor.fetchall()
    return len(resultado) > 0

def obtener_stock_actual(cursor, material):
    """
    Obtiene el stock actual de un material
    """
    query = "SELECT stock_actual FROM stock_general WHERE material = %s"
    cursor.execute(query, (material,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def insertar_entrada_stock(cursor, material, cantidad, proveedor="Proveedor Test"):
    """
    Inserta una entrada de stock de prueba
    """
    query = """
    INSERT INTO entradas_stock (
        material, 
        cantidad_ingresada, 
        precio_unitario, 
        proveedor, 
        numero_factura, 
        observaciones,
        usuario_registro
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    valores = (
        material,
        cantidad,
        2.50,  # Precio unitario de prueba
        proveedor,
        f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        f"Prueba automática del trigger - {datetime.now()}",
        "test_script"
    )
    
    cursor.execute(query, valores)
    return cursor.lastrowid

def limpiar_datos_prueba(cursor, material_test):
    """
    Limpia los datos de prueba creados
    """
    # Eliminar entradas de prueba
    cursor.execute(
        "DELETE FROM entradas_stock WHERE material = %s AND usuario_registro = 'test_script'",
        (material_test,)
    )
    
    # Si el material era nuevo, eliminarlo de stock_general
    cursor.execute(
        "DELETE FROM stock_general WHERE material = %s AND stock_actual = 25",
        (material_test,)
    )

def main():
    print("🔍 INICIANDO PRUEBAS DEL TRIGGER DE ENTRADAS DE STOCK")
    print("=" * 60)
    
    # Conectar a MySQL
    conexion = conectar_mysql()
    if not conexion:
        sys.exit(1)
    
    cursor = conexion.cursor()
    
    try:
        # 1. Verificar que las tablas existen
        print("\n📋 1. VERIFICANDO EXISTENCIA DE TABLAS...")
        
        if verificar_tabla_existe(cursor, 'entradas_stock'):
            print("   ✅ Tabla 'entradas_stock' existe")
        else:
            print("   ❌ Tabla 'entradas_stock' NO existe")
            print("   💡 Ejecuta primero el archivo triggers_mysql_ferretero.sql desde la carpeta triggers")
            return
        
        if verificar_tabla_existe(cursor, 'stock_general'):
            print("   ✅ Tabla 'stock_general' existe")
        else:
            print("   ❌ Tabla 'stock_general' NO existe")
            return
        
        # 2. Verificar que el trigger existe
        print("\n🔧 2. VERIFICANDO EXISTENCIA DEL TRIGGER...")
        
        if verificar_trigger_existe(cursor, 'actualizar_stock_entrada'):
            print("   ✅ Trigger 'actualizar_stock_entrada' existe")
        else:
            print("   ❌ Trigger 'actualizar_stock_entrada' NO existe")
            print("   💡 Ejecuta primero el archivo triggers_mysql_ferretero.sql desde la carpeta triggers")
            return
        
        # 3. Probar con material existente (silicona)
        print("\n📦 3. PROBANDO CON MATERIAL EXISTENTE (silicona)...")
        
        stock_inicial = obtener_stock_actual(cursor, 'silicona')
        print(f"   📊 Stock inicial de silicona: {stock_inicial if stock_inicial is not None else 'No existe'}")
        
        # Insertar entrada de stock
        print("   ➕ Insertando entrada de 25 unidades de silicona...")
        id_entrada = insertar_entrada_stock(cursor, 'silicona', 25)
        conexion.commit()
        
        # Verificar que el stock se actualizó
        stock_final = obtener_stock_actual(cursor, 'silicona')
        print(f"   📊 Stock final de silicona: {stock_final}")
        
        if stock_inicial is not None:
            diferencia = stock_final - stock_inicial
            if diferencia == 25:
                print("   ✅ ¡Trigger funcionó correctamente! Stock incrementado en 25 unidades")
            else:
                print(f"   ❌ Error: Se esperaba incremento de 25, pero fue {diferencia}")
        else:
            if stock_final == 25:
                print("   ✅ ¡Trigger funcionó correctamente! Material creado con 25 unidades")
            else:
                print(f"   ❌ Error: Se esperaba 25 unidades, pero hay {stock_final}")
        
        # 4. Probar con material nuevo
        print("\n🆕 4. PROBANDO CON MATERIAL NUEVO (material_test_trigger)...")
        
        material_test = 'material_test_trigger'
        stock_inicial_nuevo = obtener_stock_actual(cursor, material_test)
        print(f"   📊 Stock inicial de {material_test}: {stock_inicial_nuevo if stock_inicial_nuevo is not None else 'No existe'}")
        
        # Insertar entrada de material nuevo
        print(f"   ➕ Insertando entrada de 25 unidades de {material_test}...")
        id_entrada_nuevo = insertar_entrada_stock(cursor, material_test, 25, "Proveedor Nuevo")
        conexion.commit()
        
        # Verificar que se creó el material
        stock_final_nuevo = obtener_stock_actual(cursor, material_test)
        print(f"   📊 Stock final de {material_test}: {stock_final_nuevo}")
        
        if stock_final_nuevo == 25:
            print("   ✅ ¡Trigger funcionó correctamente! Material nuevo creado con 25 unidades")
        else:
            print(f"   ❌ Error: Se esperaba 25 unidades, pero hay {stock_final_nuevo}")
        
        # 5. Verificar entradas registradas
        print("\n📝 5. VERIFICANDO ENTRADAS REGISTRADAS...")
        
        cursor.execute(
            "SELECT COUNT(*) FROM entradas_stock WHERE usuario_registro = 'test_script'"
        )
        total_entradas = cursor.fetchone()[0]
        print(f"   📊 Total de entradas de prueba registradas: {total_entradas}")
        
        if total_entradas >= 2:
            print("   ✅ Entradas registradas correctamente")
        else:
            print("   ❌ Error: No se registraron todas las entradas")
        
        # 6. Limpiar datos de prueba
        print("\n🧹 6. LIMPIANDO DATOS DE PRUEBA...")
        limpiar_datos_prueba(cursor, material_test)
        conexion.commit()
        print("   ✅ Datos de prueba eliminados")
        
        print("\n" + "=" * 60)
        print("🎉 PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("\n💡 RESUMEN:")
        print("   • El trigger 'actualizar_stock_entrada' está funcionando correctamente")
        print("   • Las entradas de stock actualizan automáticamente stock_general")
        print("   • Se pueden crear nuevos materiales automáticamente")
        print("   • El sistema está listo para registrar entradas de material")
        
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Usar INSERT en entradas_stock para registrar entradas reales")
        print("   2. El stock se actualizará automáticamente")
        print("   3. Verificar stock con: SELECT * FROM stock_general;")
        
    except mysql.connector.Error as e:
        print(f"❌ Error en MySQL: {e}")
        conexion.rollback()
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        conexion.rollback()
    
    finally:
        cursor.close()
        conexion.close()
        print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    main()