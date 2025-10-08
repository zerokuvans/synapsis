#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

# Configuración del servidor
BASE_URL = 'http://localhost:8080'
LOGIN_URL = f'{BASE_URL}/'

# Credenciales de prueba
USERNAME = '80833959'  # Usar una cédula de administrador
PASSWORD = 'M4r14l4r@'

def test_inicio_operacion_endpoints():
    """Probar los nuevos endpoints de inicio de operación"""
    print("=" * 70)
    print("PRUEBA DE ENDPOINTS DE INICIO DE OPERACIÓN")
    print("=" * 70)
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        # 1. Login
        print("\n1. Realizando login...")
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        login_response = session.post(LOGIN_URL, data=login_data)
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("   ❌ Error en login")
            return False
        
        print("   ✅ Login exitoso")
        
        # 2. Probar endpoint de obtener campos de inicio
        print("\n2. Probando endpoint /api/asistencia/obtener-campos-inicio...")
        
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        obtener_url = f'{BASE_URL}/api/asistencia/obtener-campos-inicio?fecha={fecha_actual}'
        
        obtener_response = session.get(obtener_url)
        print(f"   Status: {obtener_response.status_code}")
        
        if obtener_response.status_code == 200:
            obtener_data = obtener_response.json()
            print(f"   ✅ Datos obtenidos: {obtener_data.get('total_registros', 0)} registros")
            
            # Mostrar algunos datos de ejemplo
            if obtener_data.get('data'):
                print("   📊 Muestra de datos:")
                for i, registro in enumerate(obtener_data['data'][:3]):
                    print(f"      {i+1}. Cédula: {registro['cedula']}, Técnico: {registro['tecnico']}")
                    print(f"         Hora: {registro['hora_inicio']}, Estado: {registro['estado']}")
        else:
            print(f"   ❌ Error obteniendo datos: {obtener_response.text}")
        
        # 3. Probar endpoint de actualizar campo individual
        print("\n3. Probando endpoint /api/asistencia/actualizar-campo...")
        
        # Obtener una cédula de prueba de los datos anteriores
        cedula_prueba = None
        if obtener_response.status_code == 200:
            obtener_data = obtener_response.json()
            if obtener_data.get('data'):
                cedula_prueba = obtener_data['data'][0]['cedula']
        
        if cedula_prueba:
            # Probar actualizar hora_inicio
            actualizar_data = {
                'cedula': cedula_prueba,
                'campo': 'hora_inicio',
                'valor': '08:30'
            }
            
            actualizar_url = f'{BASE_URL}/api/asistencia/actualizar-campo'
            actualizar_response = session.post(
                actualizar_url,
                json=actualizar_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"   Status: {actualizar_response.status_code}")
            if actualizar_response.status_code == 200:
                print("   ✅ Campo hora_inicio actualizado correctamente")
            else:
                print(f"   ❌ Error actualizando campo: {actualizar_response.text}")
            
            # Probar actualizar estado
            actualizar_data_estado = {
                'cedula': cedula_prueba,
                'campo': 'estado',
                'valor': 'CUMPLE'
            }
            
            actualizar_response_estado = session.post(
                actualizar_url,
                json=actualizar_data_estado,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"   Status estado: {actualizar_response_estado.status_code}")
            if actualizar_response_estado.status_code == 200:
                print("   ✅ Campo estado actualizado correctamente")
            else:
                print(f"   ❌ Error actualizando estado: {actualizar_response_estado.text}")
        else:
            print("   ⚠️  No se encontró cédula de prueba para actualizar")
        
        # 4. Probar endpoint de actualización masiva
        print("\n4. Probando endpoint /api/asistencia/actualizar-masivo...")
        
        if obtener_response.status_code == 200:
            obtener_data = obtener_response.json()
            if obtener_data.get('data') and len(obtener_data['data']) >= 2:
                # Preparar datos de prueba para actualización masiva
                asistencias_masivas = []
                for i, registro in enumerate(obtener_data['data'][:2]):
                    asistencias_masivas.append({
                        'cedula': registro['cedula'],
                        'hora_inicio': f'0{8+i}:00',
                        'estado': 'CUMPLE' if i == 0 else 'NO CUMPLE',
                        'novedad': '' if i == 0 else 'Prueba de novedad'
                    })
                
                masivo_data = {
                    'asistencias': asistencias_masivas
                }
                
                masivo_url = f'{BASE_URL}/api/asistencia/actualizar-masivo'
                masivo_response = session.post(
                    masivo_url,
                    json=masivo_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"   Status: {masivo_response.status_code}")
                if masivo_response.status_code == 200:
                    masivo_result = masivo_response.json()
                    print(f"   ✅ Actualización masiva exitosa: {masivo_result.get('actualizaciones_exitosas', 0)} registros")
                    if masivo_result.get('errores'):
                        print(f"   ⚠️  Errores encontrados: {len(masivo_result['errores'])}")
                else:
                    print(f"   ❌ Error en actualización masiva: {masivo_response.text}")
            else:
                print("   ⚠️  No hay suficientes datos para prueba masiva")
        
        # 5. Verificar cambios realizados
        print("\n5. Verificando cambios realizados...")
        
        verificar_response = session.get(obtener_url)
        if verificar_response.status_code == 200:
            verificar_data = verificar_response.json()
            print("   📊 Estado final de algunos registros:")
            for i, registro in enumerate(verificar_data['data'][:3]):
                print(f"      {i+1}. Cédula: {registro['cedula']}")
                print(f"         Hora: {registro['hora_inicio']}, Estado: {registro['estado']}")
                print(f"         Novedad: {registro['novedad'][:50]}..." if len(registro['novedad']) > 50 else f"         Novedad: {registro['novedad']}")
        
        print("\n" + "=" * 70)
        print("✅ PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 70)
        return True
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar al servidor")
        print("   Asegúrese de que el servidor esté ejecutándose en http://localhost:8080")
        return False
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        return False

def test_validaciones():
    """Probar las validaciones de los endpoints"""
    print("\n" + "=" * 70)
    print("PRUEBA DE VALIDACIONES")
    print("=" * 70)
    
    session = requests.Session()
    
    # Login
    login_data = {'username': USERNAME, 'password': PASSWORD}
    session.post(LOGIN_URL, data=login_data)
    
    # Probar validaciones del endpoint actualizar-campo
    print("\n1. Probando validaciones de actualizar-campo...")
    
    actualizar_url = f'{BASE_URL}/api/asistencia/actualizar-campo'
    
    # Test 1: Campo faltante
    test_data = {'cedula': '123456789', 'valor': 'test'}  # Falta 'campo'
    response = session.post(actualizar_url, json=test_data, headers={'Content-Type': 'application/json'})
    print(f"   Test campo faltante - Status: {response.status_code} (esperado: 400)")
    
    # Test 2: Campo no permitido
    test_data = {'cedula': '123456789', 'campo': 'campo_invalido', 'valor': 'test'}
    response = session.post(actualizar_url, json=test_data, headers={'Content-Type': 'application/json'})
    print(f"   Test campo no permitido - Status: {response.status_code} (esperado: 400)")
    
    # Test 3: Estado inválido
    test_data = {'cedula': '123456789', 'campo': 'estado', 'valor': 'ESTADO_INVALIDO'}
    response = session.post(actualizar_url, json=test_data, headers={'Content-Type': 'application/json'})
    print(f"   Test estado inválido - Status: {response.status_code} (esperado: 400)")
    
    # Test 4: Formato de hora inválido
    test_data = {'cedula': '123456789', 'campo': 'hora_inicio', 'valor': '25:70'}
    response = session.post(actualizar_url, json=test_data, headers={'Content-Type': 'application/json'})
    print(f"   Test hora inválida - Status: {response.status_code} (esperado: 400)")
    
    print("   ✅ Validaciones probadas")

if __name__ == "__main__":
    print("INICIANDO PRUEBAS DE ENDPOINTS DE INICIO DE OPERACIÓN")
    print(f"Servidor: {BASE_URL}")
    print(f"Usuario: {USERNAME}")
    print()
    
    # Ejecutar pruebas principales
    if test_inicio_operacion_endpoints():
        # Ejecutar pruebas de validaciones
        test_validaciones()
        print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS")
    else:
        print("\n💥 PRUEBAS FALLIDAS")