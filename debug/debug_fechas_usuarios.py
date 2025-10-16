#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar el problema con las fechas de usuarios
"""

import mysql.connector
import json
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'capired'),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def diagnosticar_fechas_usuario(cedula="80633959"):
    """Diagnosticar las fechas de un usuario específico"""
    print("="*60)
    print("DIAGNÓSTICO DE FECHAS DE USUARIO")
    print("="*60)
    print(f"Analizando usuario con cédula: {cedula}")
    print()
    
    connection = None
    cursor = None
    
    try:
        # 1. Conectar a la base de datos
        connection = get_db_connection()
        if connection is None:
            print("❌ Error: No se pudo conectar a la base de datos")
            return
        
        cursor = connection.cursor(dictionary=True)
        print("✅ Conexión a la base de datos exitosa")
        
        # 2. Buscar el usuario por cédula
        print(f"\n📋 Buscando usuario con cédula: {cedula}")
        cursor.execute("""
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula,
                nombre,
                fecha_ingreso,
                fecha_retiro
            FROM recurso_operativo 
            WHERE recurso_operativo_cedula = %s
        """, (cedula,))
        
        usuario = cursor.fetchone()
        
        if not usuario:
            print(f"❌ No se encontró usuario con cédula: {cedula}")
            return
        
        print(f"✅ Usuario encontrado: {usuario['nombre']}")
        print(f"   ID: {usuario['id_codigo_consumidor']}")
        
        # 3. Mostrar datos raw de la base de datos
        print("\n📊 DATOS RAW DE LA BASE DE DATOS:")
        print("-" * 40)
        print(f"fecha_ingreso: {usuario['fecha_ingreso']} (tipo: {type(usuario['fecha_ingreso'])})")
        print(f"fecha_retiro: {usuario['fecha_retiro']} (tipo: {type(usuario['fecha_retiro'])})")
        
        # 4. Verificar formato de fechas
        print("\n📅 ANÁLISIS DE FORMATO DE FECHAS:")
        print("-" * 40)
        
        if usuario['fecha_ingreso']:
            if isinstance(usuario['fecha_ingreso'], datetime):
                fecha_ingreso_str = usuario['fecha_ingreso'].strftime('%Y-%m-%d')
                print(f"fecha_ingreso como datetime: {usuario['fecha_ingreso']}")
                print(f"fecha_ingreso formato YYYY-MM-DD: {fecha_ingreso_str}")
            else:
                print(f"fecha_ingreso como string: '{usuario['fecha_ingreso']}'")
        else:
            print("fecha_ingreso: NULL o vacío")
        
        if usuario['fecha_retiro']:
            if isinstance(usuario['fecha_retiro'], datetime):
                fecha_retiro_str = usuario['fecha_retiro'].strftime('%Y-%m-%d')
                print(f"fecha_retiro como datetime: {usuario['fecha_retiro']}")
                print(f"fecha_retiro formato YYYY-MM-DD: {fecha_retiro_str}")
            else:
                print(f"fecha_retiro como string: '{usuario['fecha_retiro']}'")
        else:
            print("fecha_retiro: NULL o vacío")
        
        # 5. Probar la API directamente
        print("\n🌐 PROBANDO API /obtener_usuario:")
        print("-" * 40)
        
        try:
            # Hacer petición a la API
            api_url = f"http://127.0.0.1:8080/obtener_usuario/{usuario['id_codigo_consumidor']}"
            print(f"URL de la API: {api_url}")
            
            # Nota: Esta petición fallará sin autenticación, pero podemos simular la respuesta
            print("⚠️  Nota: La API requiere autenticación, simulando respuesta...")
            
            # Simular lo que devolvería la API
            api_response = {
                'id_codigo_consumidor': usuario['id_codigo_consumidor'],
                'recurso_operativo_cedula': usuario['recurso_operativo_cedula'],
                'nombre': usuario['nombre'],
                'fecha_ingreso': usuario['fecha_ingreso'].strftime('%Y-%m-%d') if usuario['fecha_ingreso'] else '',
                'fecha_retiro': usuario['fecha_retiro'].strftime('%Y-%m-%d') if usuario['fecha_retiro'] else ''
            }
            
            print("📤 Respuesta simulada de la API:")
            print(json.dumps(api_response, indent=2, default=str))
            
        except Exception as e:
            print(f"❌ Error al probar la API: {e}")
        
        # 6. Verificar estructura de la tabla
        print("\n🏗️  ESTRUCTURA DE LA TABLA:")
        print("-" * 40)
        cursor.execute("DESCRIBE recurso_operativo")
        columns = cursor.fetchall()
        
        for col in columns:
            if 'fecha' in col['Field'].lower():
                print(f"Columna: {col['Field']}")
                print(f"  Tipo: {col['Type']}")
                print(f"  Null: {col['Null']}")
                print(f"  Default: {col['Default']}")
                print()
        
        # 7. Verificar si hay datos de fecha en la tabla
        print("\n📈 ESTADÍSTICAS DE FECHAS EN LA TABLA:")
        print("-" * 40)
        
        cursor.execute("SELECT COUNT(*) as total FROM recurso_operativo")
        total_usuarios = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as con_fecha_ingreso FROM recurso_operativo WHERE fecha_ingreso IS NOT NULL")
        con_fecha_ingreso = cursor.fetchone()['con_fecha_ingreso']
        
        cursor.execute("SELECT COUNT(*) as con_fecha_retiro FROM recurso_operativo WHERE fecha_retiro IS NOT NULL")
        con_fecha_retiro = cursor.fetchone()['con_fecha_retiro']
        
        print(f"Total de usuarios: {total_usuarios}")
        print(f"Usuarios con fecha_ingreso: {con_fecha_ingreso}")
        print(f"Usuarios con fecha_retiro: {con_fecha_retiro}")
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
    
    except Exception as e:
        print(f"❌ Error general: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("\n✅ Conexión a la base de datos cerrada")

def probar_actualizacion_fecha(cedula="80633959", fecha_ingreso="2024-01-15"):
    """Probar actualización de fecha para un usuario"""
    print("\n" + "="*60)
    print("PRUEBA DE ACTUALIZACIÓN DE FECHA")
    print("="*60)
    
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if connection is None:
            print("❌ Error: No se pudo conectar a la base de datos")
            return
        
        cursor = connection.cursor()
        
        # Actualizar fecha de ingreso
        print(f"🔄 Actualizando fecha_ingreso a '{fecha_ingreso}' para cédula {cedula}")
        
        cursor.execute("""
            UPDATE recurso_operativo 
            SET fecha_ingreso = %s 
            WHERE recurso_operativo_cedula = %s
        """, (fecha_ingreso, cedula))
        
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Fecha actualizada exitosamente. Filas afectadas: {cursor.rowcount}")
        else:
            print("⚠️  No se actualizó ninguna fila. Verificar que la cédula existe.")
        
        # Verificar la actualización
        cursor.execute("""
            SELECT fecha_ingreso, fecha_retiro 
            FROM recurso_operativo 
            WHERE recurso_operativo_cedula = %s
        """, (cedula,))
        
        resultado = cursor.fetchone()
        if resultado:
            print(f"📅 Fecha verificada en BD: {resultado[0]}")
        
    except mysql.connector.Error as e:
        print(f"❌ Error al actualizar: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    print("🔍 INICIANDO DIAGNÓSTICO DE FECHAS DE USUARIOS")
    print("=" * 60)
    
    # Diagnosticar usuario específico
    diagnosticar_fechas_usuario("80633959")
    
    # Preguntar si quiere probar actualización
    print("\n" + "="*60)
    respuesta = input("¿Desea probar una actualización de fecha? (s/n): ").lower()
    
    if respuesta == 's':
        fecha = input("Ingrese fecha de ingreso (YYYY-MM-DD) [2024-01-15]: ").strip()
        if not fecha:
            fecha = "2024-01-15"
        probar_actualizacion_fecha("80633959", fecha)
        
        # Diagnosticar nuevamente después de la actualización
        print("\n🔄 DIAGNÓSTICO DESPUÉS DE LA ACTUALIZACIÓN:")
        diagnosticar_fechas_usuario("80633959")
    
    print("\n✅ Diagnóstico completado")