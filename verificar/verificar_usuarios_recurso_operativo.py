#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar usuarios en la tabla recurso_operativo
y probar el endpoint de vencimientos
"""

import mysql.connector
import requests
import bcrypt
from datetime import datetime

# Configuración de la base de datos
DB_CONFIG = {
    'host': '192.168.1.100',
    'database': 'capired',
    'user': 'usuario_app',
    'password': 'Capired2024*',
    'port': 3306
}

def verificar_usuarios_logistica():
    """Verificar usuarios con rol de logística en recurso_operativo"""
    try:
        print("=== VERIFICACIÓN DE USUARIOS LOGÍSTICA ===")
        
        # Conectar a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # 1. Verificar estructura de la tabla
        print("\n1. Estructura de tabla recurso_operativo:")
        cursor.execute("DESCRIBE recurso_operativo")
        columnas = cursor.fetchall()
        for col in columnas:
            print(f"   - {col['Field']}: {col['Type']}")
        
        # 2. Contar total de usuarios
        cursor.execute("SELECT COUNT(*) as total FROM recurso_operativo")
        total = cursor.fetchone()['total']
        print(f"\n2. Total de usuarios en recurso_operativo: {total}")
        
        # 3. Buscar usuarios con rol de logística (id_roles = 5)
        print("\n3. Usuarios con rol de logística (id_roles = 5):")
        cursor.execute("""
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula,
                nombre,
                id_roles,
                estado,
                recurso_operativo_password
            FROM recurso_operativo 
            WHERE id_roles = 5
        """)
        
        usuarios_logistica = cursor.fetchall()
        
        if usuarios_logistica:
            print(f"   Encontrados {len(usuarios_logistica)} usuarios con rol logística:")
            for usuario in usuarios_logistica:
                print(f"     - ID: {usuario['id_codigo_consumidor']}")
                print(f"       Cédula: {usuario['recurso_operativo_cedula']}")
                print(f"       Nombre: {usuario['nombre']}")
                print(f"       Estado: {usuario['estado']}")
                print(f"       Password hash: {usuario['recurso_operativo_password'][:50]}...")
                print()
        else:
            print("   No se encontraron usuarios con rol logística")
        
        # 4. Mostrar todos los roles disponibles
        print("\n4. Distribución de roles:")
        cursor.execute("""
            SELECT id_roles, COUNT(*) as cantidad
            FROM recurso_operativo 
            GROUP BY id_roles
            ORDER BY id_roles
        """)
        
        roles = cursor.fetchall()
        roles_dict = {
            '1': 'administrativo',
            '2': 'tecnicos', 
            '3': 'operativo',
            '4': 'contabilidad',
            '5': 'logistica'
        }
        
        for rol in roles:
            nombre_rol = roles_dict.get(str(rol['id_roles']), 'desconocido')
            print(f"   - Rol {rol['id_roles']} ({nombre_rol}): {rol['cantidad']} usuarios")
        
        # 5. Crear usuario de prueba si no existe
        print("\n5. Verificando/creando usuario de prueba para logística:")
        cursor.execute("""
            SELECT * FROM recurso_operativo 
            WHERE recurso_operativo_cedula = 'test_logistica'
        """)
        
        usuario_test = cursor.fetchone()
        
        if not usuario_test:
            print("   Creando usuario de prueba...")
            # Crear password hash para '123456'
            password = '123456'
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO recurso_operativo 
                (recurso_operativo_cedula, nombre, recurso_operativo_password, id_roles, estado)
                VALUES (%s, %s, %s, %s, %s)
            """, ('test_logistica', 'Usuario Test Logística', hashed_password, 5, 'Activo'))
            
            connection.commit()
            print("   ✅ Usuario de prueba creado: test_logistica / 123456")
        else:
            print("   ✅ Usuario de prueba ya existe: test_logistica")
        
        cursor.close()
        connection.close()
        
        return usuarios_logistica
        
    except Exception as e:
        print(f"❌ Error al verificar usuarios: {e}")
        return []

def probar_endpoint_vencimientos():
    """Probar el endpoint /api/vehiculos/vencimientos"""
    try:
        print("\n=== PRUEBA DEL ENDPOINT VENCIMIENTOS ===")
        
        # URL base del servidor
        base_url = "http://localhost:5000"
        
        # Crear sesión para mantener cookies
        session = requests.Session()
        
        # 1. Obtener token CSRF
        print("\n1. Obteniendo token CSRF...")
        response = session.get(f"{base_url}/")
        
        if response.status_code == 200:
            print("   ✅ Página de login obtenida")
        else:
            print(f"   ❌ Error al obtener página de login: {response.status_code}")
            return
        
        # 2. Intentar login con usuario de logística
        print("\n2. Intentando login con usuario test_logistica...")
        login_data = {
            'username': 'test_logistica',
            'password': '123456'
        }
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        login_response = session.post(f"{base_url}/", data=login_data, headers=headers)
        
        print(f"   Status code: {login_response.status_code}")
        print(f"   Response: {login_response.text[:200]}...")
        
        if login_response.status_code == 200:
            try:
                login_json = login_response.json()
                if login_json.get('status') == 'success':
                    print("   ✅ Login exitoso")
                else:
                    print(f"   ❌ Login fallido: {login_json.get('message')}")
                    return
            except:
                print("   ❌ Respuesta no es JSON válido")
                return
        else:
            print(f"   ❌ Error en login: {login_response.status_code}")
            return
        
        # 3. Probar endpoint de vencimientos
        print("\n3. Probando endpoint /api/vehiculos/vencimientos...")
        vencimientos_response = session.get(f"{base_url}/api/vehiculos/vencimientos")
        
        print(f"   Status code: {vencimientos_response.status_code}")
        print(f"   Content-Type: {vencimientos_response.headers.get('Content-Type')}")
        
        if vencimientos_response.status_code == 200:
            try:
                vencimientos_data = vencimientos_response.json()
                print(f"   ✅ Respuesta JSON recibida")
                print(f"   Número de vehículos: {len(vencimientos_data)}")
                
                if vencimientos_data:
                    print("   Primeros 3 vehículos:")
                    for i, vehiculo in enumerate(vencimientos_data[:3]):
                        print(f"     {i+1}. Placa: {vehiculo.get('placa')}")
                        print(f"        SOAT: {vehiculo.get('soat_vencimiento')}")
                        print(f"        Tecnomecánica: {vehiculo.get('tecnomecanica_vencimiento')}")
                        print(f"        Días SOAT: {vehiculo.get('dias_soat')}")
                        print(f"        Días Tecnomecánica: {vehiculo.get('dias_tecnomecanica')}")
                else:
                    print("   ⚠️ No hay datos de vencimientos")
                    
            except Exception as e:
                print(f"   ❌ Error al parsear JSON: {e}")
                print(f"   Respuesta: {vencimientos_response.text[:500]}...")
        else:
            print(f"   ❌ Error en endpoint: {vencimientos_response.status_code}")
            print(f"   Respuesta: {vencimientos_response.text[:200]}...")
        
    except Exception as e:
        print(f"❌ Error al probar endpoint: {e}")

def verificar_datos_parque_automotor():
    """Verificar datos en la tabla parque_automotor"""
    try:
        print("\n=== VERIFICACIÓN DE DATOS PARQUE_AUTOMOTOR ===")
        
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # 1. Contar total de vehículos
        cursor.execute("SELECT COUNT(*) as total FROM parque_automotor")
        total = cursor.fetchone()['total']
        print(f"\n1. Total de vehículos en parque_automotor: {total}")
        
        # 2. Verificar vehículos con fechas de vencimiento
        cursor.execute("""
            SELECT COUNT(*) as con_soat
            FROM parque_automotor 
            WHERE soat_vencimiento IS NOT NULL
        """)
        con_soat = cursor.fetchone()['con_soat']
        
        cursor.execute("""
            SELECT COUNT(*) as con_tecnomecanica
            FROM parque_automotor 
            WHERE tecnomecanica_vencimiento IS NOT NULL
        """)
        con_tecnomecanica = cursor.fetchone()['con_tecnomecanica']
        
        print(f"\n2. Vehículos con fechas de vencimiento:")
        print(f"   - Con SOAT: {con_soat}")
        print(f"   - Con Tecnomecánica: {con_tecnomecanica}")
        
        # 3. Mostrar ejemplos de vencimientos
        cursor.execute("""
            SELECT 
                placa,
                soat_vencimiento,
                tecnomecanica_vencimiento,
                DATEDIFF(soat_vencimiento, CURDATE()) as dias_soat,
                DATEDIFF(tecnomecanica_vencimiento, CURDATE()) as dias_tecnomecanica
            FROM parque_automotor 
            WHERE soat_vencimiento IS NOT NULL 
               OR tecnomecanica_vencimiento IS NOT NULL
            ORDER BY soat_vencimiento ASC
            LIMIT 5
        """)
        
        ejemplos = cursor.fetchall()
        
        if ejemplos:
            print(f"\n3. Ejemplos de vencimientos:")
            for vehiculo in ejemplos:
                print(f"   - Placa: {vehiculo['placa']}")
                print(f"     SOAT: {vehiculo['soat_vencimiento']} (días: {vehiculo['dias_soat']})")
                print(f"     Tecnomecánica: {vehiculo['tecnomecanica_vencimiento']} (días: {vehiculo['dias_tecnomecanica']})")
                print()
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error al verificar parque automotor: {e}")

if __name__ == "__main__":
    print("INICIANDO VERIFICACIÓN COMPLETA...")
    print("=" * 50)
    
    # 1. Verificar usuarios de logística
    usuarios = verificar_usuarios_logistica()
    
    # 2. Verificar datos del parque automotor
    verificar_datos_parque_automotor()
    
    # 3. Probar endpoint
    probar_endpoint_vencimientos()
    
    print("\n" + "=" * 50)
    print("VERIFICACIÓN COMPLETADA")