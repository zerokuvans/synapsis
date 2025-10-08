#!/usr/bin/env python3
"""
Script para probar la funcionalidad de bloqueo de campos en el módulo de analistas.
Este script verifica que los campos se bloqueen correctamente después del guardado.
"""

import requests
import time
import json

# Configuración
BASE_URL = "http://192.168.80.39:8080"
LOGIN_URL = f"{BASE_URL}/"
TECNICOS_URL = f"{BASE_URL}/api/analistas/tecnicos-asignados"
ACTUALIZAR_URL = f"{BASE_URL}/api/asistencia/actualizar-campo"

# Credenciales de prueba
USERNAME = "analista"
PASSWORD = "analista123"

def login():
    """Realizar login y obtener la sesión"""
    session = requests.Session()
    
    # Hacer login
    login_data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    
    response = session.post(LOGIN_URL, data=login_data)
    
    if response.status_code == 200:
        print("✅ Login exitoso")
        return session
    else:
        print(f"❌ Error en login: {response.status_code}")
        return None

def obtener_tecnicos(session):
    """Obtener lista de técnicos asignados"""
    response = session.get(TECNICOS_URL)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            tecnicos = data.get('tecnicos', [])
            print(f"✅ Obtenidos {len(tecnicos)} técnicos")
            return tecnicos
        else:
            print(f"❌ Error en respuesta: {data.get('error')}")
            return []
    else:
        print(f"❌ Error al obtener técnicos: {response.status_code}")
        return []

def probar_guardado_y_bloqueo(session, cedula):
    """Probar el guardado de datos y verificar que se bloqueen los campos"""
    print(f"\n🔧 Probando guardado y bloqueo para técnico {cedula}")
    
    # Datos de prueba
    hora_inicio = "08:30"
    estado = "CUMPLE"
    novedad = "Técnico presente y operativo"
    
    # Guardar hora_inicio
    response1 = session.post(ACTUALIZAR_URL, json={
        'cedula': cedula,
        'campo': 'hora_inicio',
        'valor': hora_inicio
    })
    
    # Guardar estado
    response2 = session.post(ACTUALIZAR_URL, json={
        'cedula': cedula,
        'campo': 'estado',
        'valor': estado
    })
    
    # Guardar novedad
    response3 = session.post(ACTUALIZAR_URL, json={
        'cedula': cedula,
        'campo': 'novedad',
        'valor': novedad
    })
    
    # Verificar respuestas
    if all(r.status_code == 200 for r in [response1, response2, response3]):
        print(f"✅ Datos guardados exitosamente para técnico {cedula}")
        print(f"   - Hora inicio: {hora_inicio}")
        print(f"   - Estado: {estado}")
        print(f"   - Novedad: {novedad}")
        
        # Verificar que los datos se guardaron
        tecnicos_actualizados = obtener_tecnicos(session)
        tecnico_actualizado = next((t for t in tecnicos_actualizados if t['cedula'] == cedula), None)
        
        if tecnico_actualizado:
            asistencia = tecnico_actualizado.get('asistencia_hoy', {})
            hora_guardada = asistencia.get('hora_inicio', '')
            estado_guardado = asistencia.get('estado', '')
            novedad_guardada = asistencia.get('novedad', '')
            
            print(f"✅ Verificación de datos guardados:")
            print(f"   - Hora inicio guardada: {hora_guardada}")
            print(f"   - Estado guardado: {estado_guardado}")
            print(f"   - Novedad guardada: {novedad_guardada}")
            
            # Verificar que todos los campos están completos (esto debería activar el bloqueo en el frontend)
            if hora_guardada and estado_guardado and novedad_guardada:
                print(f"✅ Todos los campos están completos para técnico {cedula}")
                print(f"   🔒 Los campos deberían estar BLOQUEADOS en el frontend")
                return True
            else:
                print(f"⚠️  Algunos campos están vacíos, no se debería bloquear")
                return False
        else:
            print(f"❌ No se encontró el técnico {cedula} en la respuesta actualizada")
            return False
    else:
        print(f"❌ Error al guardar datos para técnico {cedula}")
        for i, response in enumerate([response1, response2, response3], 1):
            if response.status_code != 200:
                print(f"   - Error en guardado {i}: {response.status_code}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando prueba de funcionalidad de bloqueo de campos")
    print("=" * 60)
    
    # Login
    session = login()
    if not session:
        return
    
    # Obtener técnicos
    tecnicos = obtener_tecnicos(session)
    if not tecnicos:
        return
    
    # Probar con el primer técnico que no tenga datos completos
    tecnico_prueba = None
    for tecnico in tecnicos:
        asistencia = tecnico.get('asistencia_hoy', {})
        hora = asistencia.get('hora_inicio', '')
        estado = asistencia.get('estado', '')
        novedad = asistencia.get('novedad', '')
        
        # Buscar un técnico que no tenga todos los campos completos
        if not (hora and estado and novedad):
            tecnico_prueba = tecnico
            break
    
    if tecnico_prueba:
        cedula = tecnico_prueba['cedula']
        nombre = tecnico_prueba['tecnico']
        print(f"\n📋 Técnico seleccionado para prueba:")
        print(f"   - Cédula: {cedula}")
        print(f"   - Nombre: {nombre}")
        
        # Probar guardado y bloqueo
        exito = probar_guardado_y_bloqueo(session, cedula)
        
        if exito:
            print(f"\n✅ PRUEBA EXITOSA")
            print(f"   Los datos se guardaron correctamente para el técnico {cedula}")
            print(f"   🔒 Los campos deberían estar BLOQUEADOS en el frontend")
            print(f"   📱 Abre el navegador en: {BASE_URL}/analistas/inicio-operacion-tecnicos")
            print(f"   🔍 Busca el técnico {cedula} y verifica que los campos estén deshabilitados")
        else:
            print(f"\n❌ PRUEBA FALLIDA")
            print(f"   Hubo un error al guardar o verificar los datos")
    else:
        print(f"\n⚠️  No se encontró ningún técnico con campos incompletos para probar")
        print(f"   Todos los técnicos ya tienen sus datos completos y bloqueados")
    
    print("\n" + "=" * 60)
    print("🏁 Prueba completada")

if __name__ == "__main__":
    main()