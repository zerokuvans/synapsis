#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir el problema de técnicos en vencimientos.
Convierte los nombres de técnicos a IDs en las tablas mpa_soat y mpa_tecnico_mecanica.
"""

import mysql.connector
import sys
import os
from datetime import datetime

# Función de conexión a la base de datos (igual que en main.py)
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def obtener_mapeo_tecnicos():
    """Obtener mapeo de nombres a IDs desde recurso_operativo"""
    print("🔍 Obteniendo mapeo de técnicos...")
    
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Obtener todos los técnicos con sus nombres e IDs
        cursor.execute("""
            SELECT id_codigo_consumidor, nombre 
            FROM recurso_operativo 
            WHERE nombre IS NOT NULL AND nombre != ''
        """)
        
        tecnicos = cursor.fetchall()
        mapeo = {}
        
        for tecnico in tecnicos:
            nombre = tecnico['nombre'].strip().upper()
            id_tecnico = tecnico['id_codigo_consumidor']
            mapeo[nombre] = id_tecnico
            
        print(f"✅ Se encontraron {len(mapeo)} técnicos en recurso_operativo")
        return mapeo
        
    except Exception as e:
        print(f"❌ Error obteniendo mapeo de técnicos: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def corregir_tabla_soat(mapeo_tecnicos):
    """Corregir la tabla mpa_soat"""
    print("\n🔧 Corrigiendo tabla mpa_soat...")
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Obtener registros con nombres en tecnico_asignado
        cursor.execute("""
            SELECT id_mpa_soat, placa, tecnico_asignado 
            FROM mpa_soat 
            WHERE tecnico_asignado IS NOT NULL 
            AND tecnico_asignado NOT REGEXP '^[0-9]+$'
        """)
        
        registros_soat = cursor.fetchall()
        print(f"📊 Encontrados {len(registros_soat)} registros de SOAT para corregir")
        
        actualizados = 0
        no_encontrados = []
        
        for registro in registros_soat:
            nombre_tecnico = registro['tecnico_asignado'].strip().upper()
            
            if nombre_tecnico in mapeo_tecnicos:
                id_tecnico = mapeo_tecnicos[nombre_tecnico]
                
                # Actualizar el registro
                cursor.execute("""
                    UPDATE mpa_soat 
                    SET tecnico_asignado = %s 
                    WHERE id_mpa_soat = %s
                """, (str(id_tecnico), registro['id_mpa_soat']))
                
                print(f"  ✅ {registro['placa']}: '{nombre_tecnico}' → ID {id_tecnico}")
                actualizados += 1
            else:
                no_encontrados.append({
                    'placa': registro['placa'],
                    'nombre': nombre_tecnico
                })
                print(f"  ❌ {registro['placa']}: No se encontró ID para '{nombre_tecnico}'")
        
        connection.commit()
        print(f"\n✅ SOAT: {actualizados} registros actualizados")
        
        if no_encontrados:
            print(f"⚠️  {len(no_encontrados)} registros no se pudieron actualizar:")
            for item in no_encontrados:
                print(f"    - {item['placa']}: {item['nombre']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo tabla mpa_soat: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def corregir_tabla_tecnico_mecanica(mapeo_tecnicos):
    """Corregir la tabla mpa_tecnico_mecanica"""
    print("\n🔧 Corrigiendo tabla mpa_tecnico_mecanica...")
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Obtener registros con nombres en tecnico_asignado
        cursor.execute("""
            SELECT id_mpa_tecnico_mecanica, placa, tecnico_asignado 
            FROM mpa_tecnico_mecanica 
            WHERE tecnico_asignado IS NOT NULL 
            AND tecnico_asignado NOT REGEXP '^[0-9]+$'
        """)
        
        registros_tm = cursor.fetchall()
        print(f"📊 Encontrados {len(registros_tm)} registros de Técnico Mecánica para corregir")
        
        actualizados = 0
        no_encontrados = []
        
        for registro in registros_tm:
            nombre_tecnico = registro['tecnico_asignado'].strip().upper()
            
            if nombre_tecnico in mapeo_tecnicos:
                id_tecnico = mapeo_tecnicos[nombre_tecnico]
                
                # Actualizar el registro
                cursor.execute("""
                    UPDATE mpa_tecnico_mecanica 
                    SET tecnico_asignado = %s 
                    WHERE id_mpa_tecnico_mecanica = %s
                """, (str(id_tecnico), registro['id_mpa_tecnico_mecanica']))
                
                print(f"  ✅ {registro['placa']}: '{nombre_tecnico}' → ID {id_tecnico}")
                actualizados += 1
            else:
                no_encontrados.append({
                    'placa': registro['placa'],
                    'nombre': nombre_tecnico
                })
                print(f"  ❌ {registro['placa']}: No se encontró ID para '{nombre_tecnico}'")
        
        connection.commit()
        print(f"\n✅ TÉCNICO MECÁNICA: {actualizados} registros actualizados")
        
        if no_encontrados:
            print(f"⚠️  {len(no_encontrados)} registros no se pudieron actualizar:")
            for item in no_encontrados:
                print(f"    - {item['placa']}: {item['nombre']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo tabla mpa_tecnico_mecanica: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def verificar_correccion():
    """Verificar que la corrección funcionó"""
    print("\n🔍 Verificando corrección...")
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Probar consulta SOAT con JOIN
        cursor.execute("""
            SELECT 
                s.placa,
                s.tecnico_asignado,
                ro.nombre as tecnico_nombre
            FROM mpa_soat s
            LEFT JOIN recurso_operativo ro ON s.tecnico_asignado = ro.id_codigo_consumidor
            WHERE s.fecha_vencimiento IS NOT NULL
            LIMIT 3
        """)
        
        resultados_soat = cursor.fetchall()
        print("\n✅ VERIFICACIÓN SOAT:")
        for resultado in resultados_soat:
            print(f"  Placa: {resultado['placa']} | ID: {resultado['tecnico_asignado']} | Nombre: {resultado['tecnico_nombre']}")
        
        # Probar consulta Técnico Mecánica con JOIN
        cursor.execute("""
            SELECT 
                tm.placa,
                tm.tecnico_asignado,
                ro.nombre as tecnico_nombre
            FROM mpa_tecnico_mecanica tm
            LEFT JOIN recurso_operativo ro ON tm.tecnico_asignado = ro.id_codigo_consumidor
            WHERE tm.fecha_vencimiento IS NOT NULL
            LIMIT 3
        """)
        
        resultados_tm = cursor.fetchall()
        print("\n✅ VERIFICACIÓN TÉCNICO MECÁNICA:")
        for resultado in resultados_tm:
            print(f"  Placa: {resultado['placa']} | ID: {resultado['tecnico_asignado']} | Nombre: {resultado['tecnico_nombre']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def main():
    """Función principal"""
    print("=" * 80)
    print("🔧 CORRECCIÓN DE TÉCNICOS EN VENCIMIENTOS")
    print("=" * 80)
    print(f"🚀 Iniciando corrección - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Obtener mapeo de técnicos
    mapeo_tecnicos = obtener_mapeo_tecnicos()
    if not mapeo_tecnicos:
        print("❌ No se pudo obtener el mapeo de técnicos")
        return
    
    # 2. Corregir tabla mpa_soat
    if not corregir_tabla_soat(mapeo_tecnicos):
        print("❌ Error corrigiendo tabla mpa_soat")
        return
    
    # 3. Corregir tabla mpa_tecnico_mecanica
    if not corregir_tabla_tecnico_mecanica(mapeo_tecnicos):
        print("❌ Error corrigiendo tabla mpa_tecnico_mecanica")
        return
    
    # 4. Verificar corrección
    verificar_correccion()
    
    print("\n" + "=" * 80)
    print("✅ CORRECCIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 80)
    print("\n💡 Los nombres de técnicos han sido convertidos a IDs.")
    print("💡 Ahora los JOINs deberían funcionar correctamente.")
    print("💡 Recarga la página de vencimientos para ver los cambios.")

if __name__ == "__main__":
    main()