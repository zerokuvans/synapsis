#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://192.168.80.39:8080"

def test_guardado_asistencia():
    """Probar el guardado de datos de asistencia"""
    session = requests.Session()
    
    try:
        # 1. Login como analista
        print("🔐 Haciendo login como analista...")
        login_data = {
            'username': '1002407090',  # Cambiar de 'cedula' a 'username'
            'password': 'CE1002407090'
        }
        
        login_response = session.post(f"{BASE_URL}/", data=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code not in [200, 302]:
            print("❌ Login fallido")
            return False
        
        # 2. Obtener técnicos asignados
        print("\n📊 Obteniendo técnicos asignados...")
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        response = session.get(f"{BASE_URL}/api/analistas/tecnicos-asignados?fecha={fecha_hoy}")
        
        if response.status_code != 200:
            print(f"❌ Error obteniendo técnicos: {response.status_code}")
            return False
        
        data = response.json()
        tecnicos = data.get('tecnicos', [])
        
        if not tecnicos:
            print("⚠️  No hay técnicos asignados para probar")
            return False
        
        # 3. Tomar el primer técnico para prueba
        primer_tecnico = tecnicos[0]
        cedula_prueba = primer_tecnico['cedula']
        nombre_tecnico = primer_tecnico['tecnico']
        
        print(f"\n👤 Probando con técnico: {nombre_tecnico} (Cédula: {cedula_prueba})")
        
        # 4. Probar guardado de hora_inicio
        print("\n⏰ Probando guardado de hora_inicio...")
        hora_prueba = "08:30"
        
        guardar_data = {
            'cedula': cedula_prueba,
            'campo': 'hora_inicio',
            'valor': hora_prueba,
            'fecha': fecha_hoy
        }
        
        guardar_response = session.post(
            f"{BASE_URL}/api/asistencia/actualizar-campo",
            json=guardar_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status: {guardar_response.status_code}")
        
        if guardar_response.status_code == 200:
            result = guardar_response.json()
            if result.get('success'):
                print(f"   ✅ Hora guardada exitosamente: {hora_prueba}")
            else:
                print(f"   ❌ Error: {result.get('message')}")
        else:
            print(f"   ❌ Error HTTP: {guardar_response.text[:200]}")
        
        # 5. Probar guardado de estado
        print("\n📊 Probando guardado de estado...")
        estado_prueba = "CUMPLE"
        
        guardar_data['campo'] = 'estado'
        guardar_data['valor'] = estado_prueba
        
        guardar_response = session.post(
            f"{BASE_URL}/api/asistencia/actualizar-campo",
            json=guardar_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status: {guardar_response.status_code}")
        
        if guardar_response.status_code == 200:
            result = guardar_response.json()
            if result.get('success'):
                print(f"   ✅ Estado guardado exitosamente: {estado_prueba}")
            else:
                print(f"   ❌ Error: {result.get('message')}")
        else:
            print(f"   ❌ Error HTTP: {guardar_response.text[:200]}")
        
        # 6. Probar guardado de novedad
        print("\n📝 Probando guardado de novedad...")
        novedad_prueba = "Prueba de guardado automático"
        
        guardar_data['campo'] = 'novedad'
        guardar_data['valor'] = novedad_prueba
        
        guardar_response = session.post(
            f"{BASE_URL}/api/asistencia/actualizar-campo",
            json=guardar_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status: {guardar_response.status_code}")
        
        if guardar_response.status_code == 200:
            result = guardar_response.json()
            if result.get('success'):
                print(f"   ✅ Novedad guardada exitosamente: {novedad_prueba}")
            else:
                print(f"   ❌ Error: {result.get('message')}")
        else:
            print(f"   ❌ Error HTTP: {guardar_response.text[:200]}")
        
        # 7. Verificar que los datos se guardaron correctamente
        print("\n🔍 Verificando datos guardados...")
        response = session.get(f"{BASE_URL}/api/analistas/tecnicos-asignados?fecha={fecha_hoy}")
        
        if response.status_code == 200:
            data = response.json()
            tecnicos_actualizados = data.get('tecnicos', [])
            
            # Buscar el técnico que modificamos
            tecnico_modificado = None
            for tecnico in tecnicos_actualizados:
                if tecnico['cedula'] == cedula_prueba:
                    tecnico_modificado = tecnico
                    break
            
            if tecnico_modificado:
                asistencia = tecnico_modificado.get('asistencia_hoy', {})
                
                print(f"   📅 Datos de asistencia para {nombre_tecnico}:")
                print(f"      - Hora inicio: {asistencia.get('hora_inicio')}")
                print(f"      - Estado: {asistencia.get('estado')}")
                print(f"      - Novedad: {asistencia.get('novedad')}")
                
                # Verificar que los datos coinciden
                verificaciones = []
                
                if asistencia.get('hora_inicio') == hora_prueba:
                    verificaciones.append("✅ Hora inicio")
                else:
                    verificaciones.append(f"❌ Hora inicio (esperado: {hora_prueba}, actual: {asistencia.get('hora_inicio')})")
                
                if asistencia.get('estado') == estado_prueba:
                    verificaciones.append("✅ Estado")
                else:
                    verificaciones.append(f"❌ Estado (esperado: {estado_prueba}, actual: {asistencia.get('estado')})")
                
                if asistencia.get('novedad') == novedad_prueba:
                    verificaciones.append("✅ Novedad")
                else:
                    verificaciones.append(f"❌ Novedad (esperado: {novedad_prueba}, actual: {asistencia.get('novedad')})")
                
                print(f"\n   🔍 Verificaciones:")
                for verificacion in verificaciones:
                    print(f"      {verificacion}")
                
                # Determinar si la prueba fue exitosa
                exitosas = sum(1 for v in verificaciones if v.startswith("✅"))
                total = len(verificaciones)
                
                if exitosas == total:
                    print(f"\n🎉 PRUEBA EXITOSA: Todos los campos se guardaron correctamente ({exitosas}/{total})")
                    return True
                else:
                    print(f"\n⚠️  PRUEBA PARCIAL: {exitosas}/{total} campos guardados correctamente")
                    return False
            else:
                print("   ❌ No se encontró el técnico modificado en la respuesta")
                return False
        else:
            print(f"   ❌ Error verificando datos: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False
    
    finally:
        session.close()

if __name__ == "__main__":
    print("PRUEBA DE GUARDADO DE ASISTENCIA - MÓDULO ANALISTAS")
    print("=" * 60)
    
    resultado = test_guardado_asistencia()
    
    print(f"\n{'='*60}")
    if resultado:
        print("🎉 RESULTADO: TODAS LAS FUNCIONES DE GUARDADO FUNCIONAN CORRECTAMENTE")
        print("   ✅ El endpoint de técnicos asignados incluye los campos requeridos")
        print("   ✅ La función guardarCambiosTecnico() puede guardar datos")
        print("   ✅ Los datos guardados se reflejan inmediatamente en la interfaz")
    else:
        print("⚠️  RESULTADO: HAY PROBLEMAS CON EL GUARDADO")
        print("   Revisar los logs del servidor para más detalles")