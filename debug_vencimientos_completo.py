#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar por qué no se muestran todos los vencimientos
"""

import mysql.connector
import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime, date

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
            database='capired',
            raise_on_warnings=True
        )
        return connection
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def verificar_tabla_soat():
    """Verificar datos en la tabla mpa_soat"""
    print("\n" + "="*60)
    print("1️⃣ VERIFICANDO TABLA MPA_SOAT")
    print("="*60)
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Total de registros
        cursor.execute("SELECT COUNT(*) as total FROM mpa_soat")
        total = cursor.fetchone()['total']
        print(f"📊 Total de registros: {total}")
        
        # Registros con fecha válida
        cursor.execute("""
            SELECT COUNT(*) as con_fecha 
            FROM mpa_soat 
            WHERE fecha_vencimiento IS NOT NULL 
            AND fecha_vencimiento != '0000-00-00'
        """)
        con_fecha = cursor.fetchone()['con_fecha']
        print(f"📅 Con fecha válida: {con_fecha}")
        
        # Registros con técnico asignado
        cursor.execute("""
            SELECT COUNT(*) as con_tecnico 
            FROM mpa_soat 
            WHERE tecnico_asignado IS NOT NULL 
            AND TRIM(tecnico_asignado) != ''
        """)
        con_tecnico = cursor.fetchone()['con_tecnico']
        print(f"👤 Con técnico asignado: {con_tecnico}")
        
        # Ejemplos de registros
        cursor.execute("""
            SELECT placa, fecha_vencimiento, tecnico_asignado, estado 
            FROM mpa_soat 
            WHERE fecha_vencimiento IS NOT NULL 
            AND fecha_vencimiento != '0000-00-00'
            LIMIT 5
        """)
        ejemplos = cursor.fetchall()
        print(f"\n📋 Ejemplos de registros:")
        for ejemplo in ejemplos:
            print(f"   Placa: {ejemplo['placa']}, Fecha: {ejemplo['fecha_vencimiento']}, Técnico: {ejemplo['tecnico_asignado']}, Estado: {ejemplo['estado']}")
        
        # Verificar JOIN con recurso_operativo
        cursor.execute("""
            SELECT COUNT(*) as con_join 
            FROM mpa_soat s
            LEFT JOIN recurso_operativo ro ON s.tecnico_asignado = ro.id_codigo_consumidor
            WHERE s.fecha_vencimiento IS NOT NULL 
            AND s.fecha_vencimiento != '0000-00-00'
            AND (
                s.tecnico_asignado IS NULL
                OR TRIM(s.tecnico_asignado) = ''
                OR ro.estado = 'Activo'
            )
        """)
        con_join = cursor.fetchone()['con_join']
        print(f"🔗 Registros que pasan el filtro JOIN: {con_join}")
        
        return con_fecha, con_join
        
    except Exception as e:
        print(f"❌ Error verificando tabla SOAT: {e}")
        return 0, 0
    finally:
        cursor.close()
        connection.close()

def verificar_tabla_tecnico_mecanica():
    """Verificar datos en la tabla mpa_tecnico_mecanica"""
    print("\n" + "="*60)
    print("2️⃣ VERIFICANDO TABLA MPA_TECNICO_MECANICA")
    print("="*60)
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Total de registros
        cursor.execute("SELECT COUNT(*) as total FROM mpa_tecnico_mecanica")
        total = cursor.fetchone()['total']
        print(f"📊 Total de registros: {total}")
        
        # Registros con fecha válida
        cursor.execute("""
            SELECT COUNT(*) as con_fecha 
            FROM mpa_tecnico_mecanica 
            WHERE fecha_vencimiento IS NOT NULL 
            AND fecha_vencimiento != '0000-00-00'
        """)
        con_fecha = cursor.fetchone()['con_fecha']
        print(f"📅 Con fecha válida: {con_fecha}")
        
        # Registros con técnico asignado
        cursor.execute("""
            SELECT COUNT(*) as con_tecnico 
            FROM mpa_tecnico_mecanica 
            WHERE tecnico_asignado IS NOT NULL 
            AND TRIM(tecnico_asignado) != ''
        """)
        con_tecnico = cursor.fetchone()['con_tecnico']
        print(f"👤 Con técnico asignado: {con_tecnico}")
        
        # Ejemplos de registros
        cursor.execute("""
            SELECT placa, fecha_vencimiento, tecnico_asignado, estado 
            FROM mpa_tecnico_mecanica 
            WHERE fecha_vencimiento IS NOT NULL 
            AND fecha_vencimiento != '0000-00-00'
            LIMIT 5
        """)
        ejemplos = cursor.fetchall()
        print(f"\n📋 Ejemplos de registros:")
        for ejemplo in ejemplos:
            print(f"   Placa: {ejemplo['placa']}, Fecha: {ejemplo['fecha_vencimiento']}, Técnico: {ejemplo['tecnico_asignado']}, Estado: {ejemplo['estado']}")
        
        # Verificar JOIN con recurso_operativo
        cursor.execute("""
            SELECT COUNT(*) as con_join 
            FROM mpa_tecnico_mecanica tm
            LEFT JOIN recurso_operativo ro ON tm.tecnico_asignado = ro.id_codigo_consumidor
            WHERE tm.fecha_vencimiento IS NOT NULL 
            AND tm.fecha_vencimiento != '0000-00-00'
            AND (
                tm.tecnico_asignado IS NULL
                OR TRIM(tm.tecnico_asignado) = ''
                OR ro.estado = 'Activo'
            )
        """)
        con_join = cursor.fetchone()['con_join']
        print(f"🔗 Registros que pasan el filtro JOIN: {con_join}")
        
        return con_fecha, con_join
        
    except Exception as e:
        print(f"❌ Error verificando tabla Técnico Mecánica: {e}")
        return 0, 0
    finally:
        cursor.close()
        connection.close()

def verificar_tabla_licencias():
    """Verificar datos en la tabla mpa_licencia_conducir"""
    print("\n" + "="*60)
    print("3️⃣ VERIFICANDO TABLA MPA_LICENCIA_CONDUCIR")
    print("="*60)
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Total de registros
        cursor.execute("SELECT COUNT(*) as total FROM mpa_licencia_conducir")
        total = cursor.fetchone()['total']
        print(f"📊 Total de registros: {total}")
        
        # Registros con fecha válida
        cursor.execute("""
            SELECT COUNT(*) as con_fecha 
            FROM mpa_licencia_conducir 
            WHERE fecha_vencimiento IS NOT NULL 
            AND fecha_vencimiento != '0000-00-00'
        """)
        con_fecha = cursor.fetchone()['con_fecha']
        print(f"📅 Con fecha válida: {con_fecha}")
        
        # Registros con técnico asignado
        cursor.execute("""
            SELECT COUNT(*) as con_tecnico 
            FROM mpa_licencia_conducir 
            WHERE tecnico IS NOT NULL 
            AND TRIM(tecnico) != ''
        """)
        con_tecnico = cursor.fetchone()['con_tecnico']
        print(f"👤 Con técnico asignado: {con_tecnico}")
        
        # Ejemplos de registros
        cursor.execute("""
            SELECT tecnico, fecha_vencimiento 
            FROM mpa_licencia_conducir 
            WHERE fecha_vencimiento IS NOT NULL 
            AND fecha_vencimiento != '0000-00-00'
            LIMIT 5
        """)
        ejemplos = cursor.fetchall()
        print(f"\n📋 Ejemplos de registros:")
        for ejemplo in ejemplos:
            print(f"   Técnico: {ejemplo['tecnico']}, Fecha: {ejemplo['fecha_vencimiento']}")
        
        # Verificar JOIN con recurso_operativo
        cursor.execute("""
            SELECT COUNT(*) as con_join 
            FROM mpa_licencia_conducir lc
            LEFT JOIN recurso_operativo ro ON lc.tecnico = ro.id_codigo_consumidor
            WHERE lc.fecha_vencimiento IS NOT NULL 
            AND lc.fecha_vencimiento != '0000-00-00'
            AND (
                lc.tecnico IS NULL
                OR TRIM(lc.tecnico) = ''
                OR ro.estado = 'Activo'
            )
        """)
        con_join = cursor.fetchone()['con_join']
        print(f"🔗 Registros que pasan el filtro JOIN: {con_join}")
        
        return con_fecha, con_join
        
    except Exception as e:
        print(f"❌ Error verificando tabla Licencias: {e}")
        return 0, 0
    finally:
        cursor.close()
        connection.close()

def probar_endpoint_api():
    """Probar el endpoint de la API"""
    print("\n" + "="*60)
    print("4️⃣ PROBANDO ENDPOINT /api/mpa/vencimientos")
    print("="*60)
    
    try:
        # Hacer login primero
        session = requests.Session()
        login_url = "http://localhost:8080/"
        
        # Usar credenciales de administrador
        login_data = {
            'username': '80833959',  # Usuario administrador
            'password': 'M4r14l4r@'
        }
        
        print("🔐 Haciendo login...")
        login_response = session.post(login_url, data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.status_code}")
            return 0
        
        print("✅ Login exitoso")
        
        # Llamar al endpoint de vencimientos
        api_url = "http://localhost:8080/api/mpa/vencimientos"
        print(f"📡 Llamando a {api_url}...")
        
        response = session.get(api_url)
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data:
                vencimientos = data['data']
                total_api = len(vencimientos)
                print(f"📈 Total vencimientos devueltos por API: {total_api}")
                
                # Contar por tipo
                tipos = {}
                for v in vencimientos:
                    tipo = v.get('tipo', 'Sin tipo')
                    tipos[tipo] = tipos.get(tipo, 0) + 1
                
                print(f"📋 Distribución por tipo:")
                for tipo, cantidad in tipos.items():
                    print(f"   {tipo}: {cantidad}")
                
                # Mostrar algunos ejemplos
                print(f"\n📋 Ejemplos de vencimientos devueltos:")
                for i, v in enumerate(vencimientos[:5]):
                    print(f"   {i+1}. Tipo: {v.get('tipo')}, Placa: {v.get('placa', 'N/A')}, Fecha: {v.get('fecha_vencimiento')}, Técnico: {v.get('tecnico_nombre', 'N/A')}")
                
                return total_api
            else:
                print("❌ Respuesta de API no tiene campo 'data'")
                print(f"Respuesta: {data}")
                return 0
        else:
            print(f"❌ Error en API: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Respuesta: {response.text[:200]}")
            return 0
            
    except Exception as e:
        print(f"❌ Error probando endpoint: {e}")
        return 0

def main():
    """Función principal"""
    print("🔍 DIAGNÓSTICO COMPLETO DE VENCIMIENTOS")
    print("="*60)
    
    # Verificar cada tabla
    soat_total, soat_join = verificar_tabla_soat()
    tm_total, tm_join = verificar_tabla_tecnico_mecanica()
    lc_total, lc_join = verificar_tabla_licencias()
    
    # Probar endpoint
    api_total = probar_endpoint_api()
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print("="*60)
    
    total_esperado_bd = soat_total + tm_total + lc_total
    total_esperado_join = soat_join + tm_join + lc_join
    
    print(f"📈 Total registros con fecha válida en BD: {total_esperado_bd}")
    print(f"   - SOAT: {soat_total}")
    print(f"   - Técnico Mecánica: {tm_total}")
    print(f"   - Licencias: {lc_total}")
    
    print(f"\n🔗 Total que pasa filtros JOIN: {total_esperado_join}")
    print(f"   - SOAT: {soat_join}")
    print(f"   - Técnico Mecánica: {tm_join}")
    print(f"   - Licencias: {lc_join}")
    
    print(f"\n📡 Total devuelto por API: {api_total}")
    
    # Análisis de discrepancias
    if api_total < total_esperado_join:
        print(f"\n⚠️ PROBLEMA DETECTADO:")
        print(f"   La API devuelve {api_total} registros")
        print(f"   Pero deberían ser {total_esperado_join} según los filtros")
        print(f"   Diferencia: {total_esperado_join - api_total} registros faltantes")
        
        print(f"\n🔍 POSIBLES CAUSAS:")
        print(f"   1. Problemas en los filtros de fecha")
        print(f"   2. Problemas en los JOINs con recurso_operativo")
        print(f"   3. Filtros adicionales en el código de la API")
        print(f"   4. Errores en el procesamiento de fechas")
    elif api_total == total_esperado_join:
        print(f"\n✅ TODO CORRECTO:")
        print(f"   La API devuelve exactamente los registros esperados")
    else:
        print(f"\n❓ SITUACIÓN INESPERADA:")
        print(f"   La API devuelve más registros de los esperados")

if __name__ == "__main__":
    main()