#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime
import pytz

# Configuración
BASE_URL = "http://localhost:8080"
LOGIN_DATA = {
    'username': '80833959',
    'password': 'M4r14l4r@'
}

def test_frontend_complete():
    print("🧪 Prueba completa del flujo de edición de asistencia")
    print("=" * 60)
    
    # Crear sesión
    session = requests.Session()
    
    # 1. Login
    print("1️⃣ Realizando login...")
    response = session.post(f"{BASE_URL}/", data=LOGIN_DATA)
    if response.status_code == 200:
        print("✅ Login exitoso")
    else:
        print(f"❌ Error en login: {response.status_code}")
        return
    
    # 2. Obtener supervisores disponibles
    print("\n2️⃣ Obteniendo supervisores...")
    response = session.get(f"{BASE_URL}/api/supervisores")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            supervisores = data.get('supervisores', [])
            print(f"✅ Supervisores obtenidos: {len(supervisores)}")
            if supervisores:
                supervisor_test = supervisores[0]
                print(f"   Usando supervisor: {supervisor_test}")
            else:
                print("❌ No hay supervisores disponibles")
                return
        else:
            print(f"❌ Error en respuesta: {data.get('message')}")
            return
    else:
        print(f"❌ Error al obtener supervisores: {response.status_code}")
        return
    
    # 3. Consultar registros de asistencia (simular frontend)
    print("\n3️⃣ Consultando registros de asistencia...")
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    
    response = session.get(f"{BASE_URL}/api/asistencia/consultar", 
                          params={'supervisor': supervisor_test, 'fecha': fecha_hoy})
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            registros = data.get('registros', [])
            print(f"✅ Registros obtenidos: {len(registros)}")
            
            if registros:
                # Mostrar el primer registro con todos sus campos
                primer_registro = registros[0]
                print(f"\n📋 Primer registro:")
                print(f"   Cédula: {primer_registro.get('cedula')}")
                print(f"   Técnico: {primer_registro.get('tecnico')}")
                print(f"   Hora inicio: {primer_registro.get('hora_inicio', 'No definida')}")
                print(f"   Estado: {primer_registro.get('estado', 'No definido')}")
                print(f"   Novedad: {primer_registro.get('novedad', 'No definida')}")
                print(f"   Carpeta día: {primer_registro.get('carpeta_dia', 'No definida')}")
                
                # 4. Probar actualización de campos
                cedula_test = primer_registro.get('cedula')
                if cedula_test:
                    print(f"\n4️⃣ Probando actualización para cédula: {cedula_test}")
                    
                    # Actualizar hora_inicio
                    print("   📝 Actualizando hora_inicio...")
                    update_data = {
                        'cedula': cedula_test,
                        'campo': 'hora_inicio',
                        'valor': '14:30'
                    }
                    headers = {'Content-Type': 'application/json'}
                    response = session.post(f"{BASE_URL}/api/asistencia/actualizar-campo", 
                                          json=update_data, headers=headers)
                    
                    if response.status_code == 200:
                        print("   ✅ Hora inicio actualizada exitosamente")
                    else:
                        print(f"   ❌ Error actualizando hora inicio: {response.status_code}")
                        print(f"   Respuesta: {response.text}")
                    
                    # Actualizar estado
                    print("   📝 Actualizando estado...")
                    update_data = {
                        'cedula': cedula_test,
                        'campo': 'estado',
                        'valor': 'CUMPLE'
                    }
                    response = session.post(f"{BASE_URL}/api/asistencia/actualizar-campo", 
                                          json=update_data, headers=headers)
                    
                    if response.status_code == 200:
                        print("   ✅ Estado actualizado exitosamente")
                    else:
                        print(f"   ❌ Error actualizando estado: {response.status_code}")
                        print(f"   Respuesta: {response.text}")
                    
                    # Actualizar novedad
                    print("   📝 Actualizando novedad...")
                    update_data = {
                        'cedula': cedula_test,
                        'campo': 'novedad',
                        'valor': 'Prueba de edición completa'
                    }
                    response = session.post(f"{BASE_URL}/api/asistencia/actualizar-campo", 
                                          json=update_data, headers=headers)
                    
                    if response.status_code == 200:
                        print("   ✅ Novedad actualizada exitosamente")
                    else:
                        print(f"   ❌ Error actualizando novedad: {response.status_code}")
                        print(f"   Respuesta: {response.text}")
                    
                    # 5. Verificar que los cambios se reflejen en la consulta
                    print("\n5️⃣ Verificando cambios en nueva consulta...")
                    response = session.get(f"{BASE_URL}/api/asistencia/consultar", 
                                          params={'supervisor': supervisor_test, 'fecha': fecha_hoy})
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            registros_actualizados = data.get('registros', [])
                            
                            # Buscar el registro actualizado
                            registro_actualizado = None
                            for reg in registros_actualizados:
                                if reg.get('cedula') == cedula_test:
                                    registro_actualizado = reg
                                    break
                            
                            if registro_actualizado:
                                print(f"✅ Registro encontrado después de actualización:")
                                print(f"   Hora inicio: {registro_actualizado.get('hora_inicio', 'No definida')}")
                                print(f"   Estado: {registro_actualizado.get('estado', 'No definido')}")
                                print(f"   Novedad: {registro_actualizado.get('novedad', 'No definida')}")
                                
                                # Verificar que los cambios se aplicaron
                                cambios_correctos = 0
                                if registro_actualizado.get('hora_inicio') == '14:30':
                                    print("   ✅ Hora inicio actualizada correctamente")
                                    cambios_correctos += 1
                                else:
                                    print(f"   ❌ Hora inicio no se actualizó: {registro_actualizado.get('hora_inicio')}")
                                
                                if registro_actualizado.get('estado') == 'CUMPLE':
                                    print("   ✅ Estado actualizado correctamente")
                                    cambios_correctos += 1
                                else:
                                    print(f"   ❌ Estado no se actualizó: {registro_actualizado.get('estado')}")
                                
                                if registro_actualizado.get('novedad') == 'Prueba de edición completa':
                                    print("   ✅ Novedad actualizada correctamente")
                                    cambios_correctos += 1
                                else:
                                    print(f"   ❌ Novedad no se actualizó: {registro_actualizado.get('novedad')}")
                                
                                print(f"\n🎯 Resultado final: {cambios_correctos}/3 cambios aplicados correctamente")
                                
                                if cambios_correctos == 3:
                                    print("🎉 ¡FUNCIONALIDAD DE EDICIÓN COMPLETAMENTE FUNCIONAL!")
                                else:
                                    print("⚠️  Algunos cambios no se aplicaron correctamente")
                            else:
                                print("❌ No se encontró el registro después de la actualización")
                        else:
                            print(f"❌ Error en consulta de verificación: {data.get('message')}")
                    else:
                        print(f"❌ Error en consulta de verificación: {response.status_code}")
                
            else:
                print("ℹ️  No hay registros de asistencia para hoy")
                print("   Puede crear algunos registros primero usando la funcionalidad de registro")
        else:
            print(f"❌ Error en respuesta: {data.get('message')}")
    else:
        print(f"❌ Error al consultar registros: {response.status_code}")

if __name__ == "__main__":
    test_frontend_complete()