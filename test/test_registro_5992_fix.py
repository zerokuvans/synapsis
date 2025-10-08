#!/usr/bin/env python3
"""
Test específico para verificar que el registro 5992 se puede actualizar correctamente
con la fecha 2025-09-30 después de la corrección del endpoint.
"""

import requests
import json
import mysql.connector
from datetime import datetime

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

# URL del servidor
BASE_URL = "http://localhost:8080"
LOGIN_URL = f"{BASE_URL}/"

# Credenciales de prueba
LOGIN_DATA = {
    'username': '1032402333',
    'password': 'CE1032402333'
}

def conectar_db():
    """Conectar a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def obtener_registro_5992():
    """Obtener el registro 5992 de la base de datos"""
    connection = conectar_db()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM asistencia WHERE id_asistencia = 5992")
        registro = cursor.fetchone()
        return registro
    except Exception as e:
        print(f"Error obteniendo registro 5992: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def test_actualizar_registro_5992():
    """Test para actualizar el registro 5992 con la fecha correcta"""
    print("=== TEST: Actualización del registro 5992 ===")
    
    # 0. Crear sesión y hacer login
    print("0. Iniciando sesión...")
    session = requests.Session()
    
    try:
        login_response = session.post(LOGIN_URL, data=LOGIN_DATA)
        if login_response.status_code != 200:
            print(f"❌ ERROR: Login falló con código {login_response.status_code}")
            return False
        print("   ✅ Login exitoso")
    except Exception as e:
        print(f"❌ ERROR en login: {e}")
        return False
    
    # 1. Obtener el registro actual
    print("1. Obteniendo registro 5992...")
    registro_inicial = obtener_registro_5992()
    if not registro_inicial:
        print("❌ ERROR: No se pudo obtener el registro 5992")
        return False
    
    print(f"   Registro encontrado:")
    print(f"   - ID: {registro_inicial['id_asistencia']}")
    print(f"   - Cédula: {registro_inicial['cedula']}")
    print(f"   - Fecha: {registro_inicial['fecha_asistencia']}")
    print(f"   - Estado actual: {registro_inicial['estado']}")
    print(f"   - Hora inicio actual: {registro_inicial['hora_inicio']}")
    
    # 2. Preparar datos de prueba
    cedula = registro_inicial['cedula']
    fecha_registro = "2025-09-30"  # Fecha del registro 5992
    
    # Valores de prueba (usando estados válidos)
    nuevo_estado = "CUMPLE"
    nueva_hora = "08:30"
    nueva_novedad = "Test de actualización"
    
    print(f"\n2. Preparando actualización para cédula {cedula} en fecha {fecha_registro}...")
    
    # 3. Actualizar estado
    print("3. Actualizando estado...")
    try:
        response = session.post(
            f"{BASE_URL}/api/asistencia/actualizar-campo",
            headers={'Content-Type': 'application/json'},
            json={
                'cedula': cedula,
                'campo': 'estado',
                'valor': nuevo_estado,
                'fecha': fecha_registro
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Estado actualizado exitosamente")
            else:
                print(f"   ❌ Error en respuesta: {data.get('message')}")
                return False
        else:
            print(f"   ❌ Error HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error actualizando estado: {e}")
        return False
    
    # 4. Actualizar hora_inicio
    print("4. Actualizando hora_inicio...")
    try:
        response = session.post(
            f"{BASE_URL}/api/asistencia/actualizar-campo",
            headers={'Content-Type': 'application/json'},
            json={
                'cedula': cedula,
                'campo': 'hora_inicio',
                'valor': nueva_hora,
                'fecha': fecha_registro
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Hora inicio actualizada exitosamente")
            else:
                print(f"   ❌ Error en respuesta: {data.get('message')}")
                return False
        else:
            print(f"   ❌ Error HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error actualizando hora_inicio: {e}")
        return False
    
    # 5. Verificar que los cambios se guardaron en la base de datos
    print("5. Verificando cambios en la base de datos...")
    registro_actualizado = obtener_registro_5992()
    if not registro_actualizado:
        print("   ❌ ERROR: No se pudo obtener el registro actualizado")
        return False
    
    print(f"   Registro después de la actualización:")
    print(f"   - Estado: {registro_actualizado['estado']} (esperado: {nuevo_estado})")
    print(f"   - Hora inicio: {registro_actualizado['hora_inicio']} (esperado: {nueva_hora})")
    
    # Verificar que los cambios se persistieron
    estado_correcto = registro_actualizado['estado'] == nuevo_estado
    
    # Comparar hora considerando diferentes formatos (8:30:00 vs 08:30)
    hora_db = str(registro_actualizado['hora_inicio'])
    # Normalizar ambos formatos a HH:MM para comparar
    try:
        # Convertir hora de DB (ej: 8:30:00) a formato HH:MM
        partes_db = hora_db.split(':')
        hora_db_fmt = f"{partes_db[0].zfill(2)}:{partes_db[1]}"
        
        # Asegurar que nueva_hora esté en formato HH:MM
        hora_nueva_fmt = nueva_hora
        if ':' not in hora_nueva_fmt and len(hora_nueva_fmt) == 4:
            hora_nueva_fmt = f"{hora_nueva_fmt[:2]}:{hora_nueva_fmt[2:]}"
        
        hora_correcta = hora_db_fmt == hora_nueva_fmt
        print(f"   Comparación detallada - DB: {hora_db_fmt}, Esperada: {hora_nueva_fmt}, Iguales: {hora_correcta}")
    except:
        # Fallback a comparación simple
        hora_correcta = (hora_db == nueva_hora or 
                        hora_db == nueva_hora + ":00")
    
    if estado_correcto and hora_correcta:
        print("   ✅ ÉXITO: Todos los cambios se guardaron correctamente en la base de datos")
        return True
    else:
        print("   ❌ ERROR: Los cambios NO se guardaron correctamente:")
        if not estado_correcto:
            print(f"      - Estado esperado: {nuevo_estado}, obtenido: {registro_actualizado['estado']}")
        if not hora_correcta:
            print(f"      - Hora esperada: {nueva_hora}, obtenida: {registro_actualizado['hora_inicio']}")
        return False

def main():
    """Función principal"""
    print("🔧 Test de corrección del registro 5992")
    print("=" * 50)
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print("✅ Servidor accesible")
    except:
        print("❌ ERROR: No se puede conectar al servidor en http://localhost:8080")
        print("   Asegúrese de que el servidor esté corriendo")
        return
    
    # Ejecutar el test
    resultado = test_actualizar_registro_5992()
    
    print("\n" + "=" * 50)
    if resultado:
        print("🎉 TEST EXITOSO: El problema del registro 5992 ha sido corregido")
        print("   Los cambios ahora se guardan correctamente en la base de datos")
    else:
        print("❌ TEST FALLIDO: El problema persiste")
        print("   Los cambios no se están guardando en la base de datos")

if __name__ == "__main__":
    main()