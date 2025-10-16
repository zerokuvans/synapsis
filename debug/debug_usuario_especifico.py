#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar específicamente el usuario con cédula 80833959
"""

import mysql.connector
import json
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

def diagnosticar_usuario_80833959():
    """Diagnosticar específicamente el usuario con cédula 80833959"""
    print("🔍 DIAGNÓSTICO ESPECÍFICO - USUARIO 80833959")
    print("="*60)
    
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if connection is None:
            print("❌ Error de conexión")
            return
        
        cursor = connection.cursor(dictionary=True)
        
        # 1. Buscar el usuario por cédula
        print("1️⃣ BUSCANDO USUARIO POR CÉDULA...")
        cursor.execute("""
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula,
                nombre,
                fecha_ingreso,
                fecha_retiro
            FROM recurso_operativo 
            WHERE recurso_operativo_cedula = %s
        """, ('80833959',))
        
        usuario = cursor.fetchone()
        
        if not usuario:
            print("❌ Usuario con cédula 80833959 NO ENCONTRADO")
            
            # Buscar usuarios similares
            print("\n🔍 BUSCANDO USUARIOS CON CÉDULAS SIMILARES...")
            cursor.execute("""
                SELECT 
                    id_codigo_consumidor,
                    recurso_operativo_cedula,
                    nombre,
                    fecha_ingreso
                FROM recurso_operativo 
                WHERE recurso_operativo_cedula LIKE %s
                ORDER BY recurso_operativo_cedula
            """, ('%80833959%',))
            
            similares = cursor.fetchall()
            
            if similares:
                print("✅ Usuarios con cédulas similares encontrados:")
                for sim in similares:
                    print(f"   ID: {sim['id_codigo_consumidor']} | Cédula: {sim['recurso_operativo_cedula']} | Nombre: {sim['nombre']}")
            else:
                print("❌ No se encontraron usuarios con cédulas similares")
            
            return
        
        print("✅ Usuario encontrado:")
        print(f"   ID: {usuario['id_codigo_consumidor']}")
        print(f"   Cédula: {usuario['recurso_operativo_cedula']}")
        print(f"   Nombre: {usuario['nombre']}")
        print(f"   Fecha Ingreso (BD): {usuario['fecha_ingreso']} (tipo: {type(usuario['fecha_ingreso'])})")
        print(f"   Fecha Retiro (BD): {usuario['fecha_retiro']} (tipo: {type(usuario['fecha_retiro'])})")
        
        # 2. Simular la API obtener_usuario
        print(f"\n2️⃣ SIMULANDO API /obtener_usuario/{usuario['id_codigo_consumidor']}")
        print("-" * 50)
        
        # Obtener todos los datos como lo haría la API
        cursor.execute("""
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula,
                nombre,
                id_roles,
                estado,
                cargo,
                carpeta,
                cliente,
                ciudad,
                super,
                analista,
                fecha_ingreso,
                fecha_retiro
            FROM recurso_operativo 
            WHERE id_codigo_consumidor = %s
        """, (usuario['id_codigo_consumidor'],))
        
        datos_api = cursor.fetchone()
        
        if datos_api:
            print("✅ Datos completos obtenidos:")
            
            # Procesar fechas como lo haría la API
            fecha_ingreso_api = None
            fecha_retiro_api = None
            
            if isinstance(datos_api['fecha_ingreso'], datetime):
                fecha_ingreso_api = datos_api['fecha_ingreso'].strftime('%Y-%m-%d')
            elif datos_api['fecha_ingreso']:
                fecha_ingreso_api = str(datos_api['fecha_ingreso'])
            
            if isinstance(datos_api['fecha_retiro'], datetime):
                fecha_retiro_api = datos_api['fecha_retiro'].strftime('%Y-%m-%d')
            elif datos_api['fecha_retiro']:
                fecha_retiro_api = str(datos_api['fecha_retiro'])
            
            print(f"   📅 Fecha Ingreso (API): '{fecha_ingreso_api}' (tipo: {type(fecha_ingreso_api)})")
            print(f"   📅 Fecha Retiro (API): '{fecha_retiro_api}' (tipo: {type(fecha_retiro_api)})")
            
            # Crear respuesta JSON como la API
            respuesta_json = {
                'id_codigo_consumidor': datos_api['id_codigo_consumidor'],
                'recurso_operativo_cedula': datos_api['recurso_operativo_cedula'],
                'nombre': datos_api['nombre'],
                'id_roles': datos_api['id_roles'],
                'estado': datos_api['estado'],
                'cargo': datos_api['cargo'],
                'carpeta': datos_api['carpeta'],
                'cliente': datos_api['cliente'],
                'ciudad': datos_api['ciudad'],
                'super': datos_api['super'],
                'analista': datos_api['analista'],
                'fecha_ingreso': fecha_ingreso_api,
                'fecha_retiro': fecha_retiro_api
            }
            
            print(f"\n📤 RESPUESTA JSON COMPLETA:")
            print(json.dumps(respuesta_json, indent=2, ensure_ascii=False))
            
            # 3. Verificar formato para input type="date"
            print(f"\n3️⃣ VERIFICACIÓN PARA INPUT TYPE='DATE'")
            print("-" * 50)
            
            if fecha_ingreso_api:
                # Verificar si el formato es válido para input date
                try:
                    fecha_parseada = datetime.strptime(fecha_ingreso_api, '%Y-%m-%d')
                    print(f"✅ Fecha ingreso válida para input date: {fecha_ingreso_api}")
                    print(f"   Fecha parseada: {fecha_parseada}")
                except ValueError as e:
                    print(f"❌ Fecha ingreso NO válida para input date: {fecha_ingreso_api}")
                    print(f"   Error: {e}")
            else:
                print(f"⚠️  Fecha ingreso está vacía o es null")
            
            if fecha_retiro_api:
                try:
                    fecha_parseada = datetime.strptime(fecha_retiro_api, '%Y-%m-%d')
                    print(f"✅ Fecha retiro válida para input date: {fecha_retiro_api}")
                except ValueError as e:
                    print(f"❌ Fecha retiro NO válida para input date: {fecha_retiro_api}")
                    print(f"   Error: {e}")
            else:
                print(f"ℹ️  Fecha retiro está vacía o es null (normal)")
        
        # 4. Verificar si hay problemas de codificación o caracteres especiales
        print(f"\n4️⃣ VERIFICACIÓN DE CODIFICACIÓN")
        print("-" * 50)
        
        if fecha_ingreso_api:
            print(f"Fecha ingreso bytes: {fecha_ingreso_api.encode('utf-8')}")
            print(f"Fecha ingreso repr: {repr(fecha_ingreso_api)}")
            print(f"Longitud: {len(fecha_ingreso_api)}")
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
    
    print(f"\n🏁 DIAGNÓSTICO COMPLETADO")
    print("="*60)

if __name__ == "__main__":
    diagnosticar_usuario_80833959()