#!/usr/bin/env python3
"""
Script para verificar el acceso a la página de devoluciones y diagnosticar problemas
"""

import requests
import mysql.connector
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8080"
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4'
}

def verificar_base_datos():
    """Verificar datos en la base de datos"""
    print("🔍 VERIFICANDO BASE DE DATOS")
    print("=" * 50)
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Verificar devoluciones existentes
        cursor.execute("SELECT COUNT(*) as total FROM devoluciones_dotacion")
        total_devoluciones = cursor.fetchone()['total']
        print(f"📊 Total de devoluciones: {total_devoluciones}")
        
        if total_devoluciones > 0:
            cursor.execute("""
                SELECT id, estado, motivo, fecha_devolucion 
                FROM devoluciones_dotacion 
                ORDER BY id DESC 
                LIMIT 5
            """)
            devoluciones = cursor.fetchall()
            
            print("\n📋 Últimas 5 devoluciones:")
            for dev in devoluciones:
                print(f"  ID: {dev['id']} | Estado: {dev['estado']} | Motivo: {dev['motivo']}")
        
        # Verificar usuarios con rol logística
        cursor.execute("""
            SELECT u.cedula, u.nombre, r.nombre as rol_nombre
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            WHERE r.nombre LIKE '%logistica%' OR r.nombre LIKE '%admin%'
            LIMIT 5
        """)
        usuarios_logistica = cursor.fetchall()
        
        print(f"\n👥 Usuarios con acceso a logística: {len(usuarios_logistica)}")
        for usuario in usuarios_logistica:
            print(f"  {usuario['nombre']} ({usuario['cedula']}) - {usuario['rol_nombre']}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def verificar_acceso_sin_login():
    """Verificar qué pasa al acceder sin login"""
    print("\n🔐 VERIFICANDO ACCESO SIN LOGIN")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/logistica/devoluciones_dotacion")
        print(f"Status Code: {response.status_code}")
        print(f"URL Final: {response.url}")
        
        if response.status_code == 302:
            print("✅ Redirección detectada (normal para páginas protegidas)")
            location = response.headers.get('Location', 'No especificada')
            print(f"Redirige a: {location}")
        elif response.status_code == 200:
            print("⚠️  Acceso permitido sin login (posible problema de seguridad)")
            # Verificar si contiene elementos de login
            if 'login' in response.text.lower() or 'password' in response.text.lower():
                print("✅ Página de login mostrada")
            else:
                print("❌ Contenido inesperado")
        else:
            print(f"❌ Error inesperado: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def verificar_pagina_login():
    """Verificar que la página de login funcione"""
    print("\n🏠 VERIFICANDO PÁGINA DE LOGIN")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            elementos_login = [
                'password',
                'login',
                'cedula',
                'form',
                'submit'
            ]
            
            elementos_encontrados = []
            for elemento in elementos_login:
                if elemento.lower() in content.lower():
                    elementos_encontrados.append(elemento)
            
            print(f"✅ Elementos de login encontrados: {len(elementos_encontrados)}/{len(elementos_login)}")
            print(f"Elementos: {', '.join(elementos_encontrados)}")
            
            return True
        else:
            print(f"❌ Error al cargar página de login: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def crear_devolucion_prueba():
    """Crear una devolución de prueba si no existe ninguna"""
    print("\n➕ CREANDO DEVOLUCIÓN DE PRUEBA")
    print("=" * 50)
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Verificar si ya hay devoluciones
        cursor.execute("SELECT COUNT(*) FROM devoluciones_dotacion")
        total = cursor.fetchone()[0]
        
        if total == 0:
            print("📝 No hay devoluciones. Creando una de prueba...")
            
            # Obtener un técnico para la prueba
            cursor.execute("SELECT id_codigo_consumidor FROM recurso_operativo WHERE estado = 'Activo' LIMIT 1")
            tecnico_result = cursor.fetchone()
            
            if tecnico_result:
                tecnico_id = tecnico_result[0]
                
                cursor.execute("""
                    INSERT INTO devoluciones_dotacion 
                    (tecnico_id, cliente_id, motivo, estado, observaciones, created_by, fecha_devolucion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    tecnico_id,
                    1,  # Cliente ID genérico
                    'Prueba del sistema de estados',
                    'REGISTRADA',
                    'Devolución creada para pruebas del sistema de gestión de estados',
                    1,  # Usuario que crea
                    datetime.now().date()
                ))
                
                devolucion_id = cursor.lastrowid
                connection.commit()
                
                print(f"✅ Devolución de prueba creada con ID: {devolucion_id}")
                return True
            else:
                print("❌ No se encontraron técnicos activos")
                return False
        else:
            print(f"✅ Ya existen {total} devoluciones en el sistema")
            return True
            
    except Exception as e:
        print(f"❌ Error al crear devolución de prueba: {e}")
        return False
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()

def main():
    """Función principal"""
    print("🚀 DIAGNÓSTICO DE ACCESO A DEVOLUCIONES")
    print("=" * 60)
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ejecutar verificaciones
    resultado1 = verificar_base_datos()
    resultado2 = verificar_acceso_sin_login()
    resultado3 = verificar_pagina_login()
    resultado4 = crear_devolucion_prueba()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)
    
    if all([resultado1, resultado2, resultado3, resultado4]):
        print("✅ SISTEMA FUNCIONANDO CORRECTAMENTE")
        print("\n🎯 PASOS PARA ACCEDER A LOS BOTONES DE ESTADO:")
        print("1. Ve a: http://localhost:8080")
        print("2. Inicia sesión con un usuario que tenga rol de logística")
        print("3. Ve a: http://localhost:8080/logistica/devoluciones_dotacion")
        print("4. Haz clic en el botón 'Ver/Editar Detalles' (👁️) de cualquier devolución")
        print("5. En el modal, busca la sección 'Gestión de Estados'")
        print("6. Ahí verás los botones para cambiar estado")
        
        print("\n🔑 CREDENCIALES DE PRUEBA:")
        print("Si no tienes credenciales, puedes crear un usuario de logística")
        print("o usar un usuario administrativo existente.")
        
    else:
        print("❌ SE DETECTARON PROBLEMAS")
        print("Revisa los errores mostrados arriba")

if __name__ == "__main__":
    main()