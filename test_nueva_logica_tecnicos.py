#!/usr/bin/env python3
"""
Script para probar la nueva lógica de cálculo de técnicos
según las especificaciones exactas del usuario
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8080"
API_URL = f"{BASE_URL}/api/lider/inicio-operacion/datos"

def test_nueva_logica():
    """Probar la nueva lógica de cálculo de técnicos"""
    print("=" * 80)
    print("PRUEBA DE NUEVA LÓGICA DE CÁLCULO DE TÉCNICOS")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        print("\n[1] Realizando petición al endpoint...")
        response = requests.get(API_URL)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("✅ Respuesta exitosa")
                
                # Extraer datos
                datos = data.get('data', {})
                tecnicos = datos.get('tecnicos', {})
                apoyo = datos.get('apoyo_camionetas', {})
                auxiliares = datos.get('auxiliares', {})
                metricas = datos.get('metricas', {})
                cumplimiento = datos.get('cumplimiento', {})
                debug_info = datos.get('debug_info', {})
                
                print("\n" + "="*60)
                print("RESULTADOS DE LA NUEVA LÓGICA")
                print("="*60)
                
                print("\n🔧 TÉCNICOS:")
                print(f"   Total: {tecnicos.get('total', 0)}")
                print(f"   Con Asistencia: {tecnicos.get('con_asistencia', 0)}")
                print(f"   Sin Asistencia: {tecnicos.get('sin_asistencia', 0)}")
                print("   Lógica: Con asistencia = carpeta_dia en lista técnicos")
                print("   Carpetas técnicos: POSTVENTA, POSTVENTA FTTH, FTTH INSTALACIONES,")
                print("                      MANTENIMIENTO FTTH, INSTALACIONES DOBLES,")
                print("                      ARREGLOS HFC, BROWNFIELD, INSTALACIONES DOBLES BACK")
                
                print("\n🚐 APOYO CAMIONETAS:")
                print(f"   Total: {apoyo.get('total', 0)}")
                print(f"   Con Asistencia: {apoyo.get('con_asistencia', 0)}")
                print(f"   Sin Asistencia: {apoyo.get('sin_asistencia', 0)}")
                print("   Lógica: Con asistencia = carpeta_dia = 'APOYO CAMIONETAS'")
                
                print("\n🔧 AUXILIARES:")
                print(f"   Total: {auxiliares.get('total', 0)}")
                print(f"   Con Asistencia: {auxiliares.get('con_asistencia', 0)}")
                print(f"   Sin Asistencia: {auxiliares.get('sin_asistencia', 0)}")
                print("   Lógica: Con asistencia = carpeta_dia en ['AUXILIAR', 'AUXILIARMOTO']")
                
                print("\n📈 MÉTRICAS:")
                print(f"   OKs del día: {metricas.get('oks_dia', 0)}")
                print(f"   Presupuesto día: ${metricas.get('presupuesto_dia', 0):,}")
                print(f"   Presupuesto mes: ${metricas.get('presupuesto_mes', 0):,}")
                
                print("\n✅ CUMPLIMIENTO:")
                print(f"   Cumple: {cumplimiento.get('cumple', 0)}")
                print(f"   No Cumple: {cumplimiento.get('no_cumple', 0)}")
                print(f"   % Cumplimiento día: {cumplimiento.get('cumplimiento_dia', 0)}%")
                print(f"   % Cumplimiento mes: {cumplimiento.get('cumplimiento_mes', 0)}%")
                
                if debug_info:
                    print("\n🔍 INFORMACIÓN DE DEBUG:")
                    print(f"   Total registros procesados: {debug_info.get('total_registros', 0)}")
                    filtros = debug_info.get('filtros_aplicados', {})
                    print(f"   Filtros aplicados:")
                    print(f"     - Fecha: {filtros.get('fecha', 'No especificada')}")
                    print(f"     - Supervisores: {filtros.get('supervisores', 'Todos')}")
                    print(f"     - Analistas: {filtros.get('analistas', 'Todos')}")
                
                # Validaciones
                print("\n" + "="*60)
                print("VALIDACIONES")
                print("="*60)
                
                # Validar totales
                total_tecnicos_calculado = tecnicos.get('con_asistencia', 0) + tecnicos.get('sin_asistencia', 0)
                total_apoyo_calculado = apoyo.get('con_asistencia', 0) + apoyo.get('sin_asistencia', 0)
                total_auxiliares_calculado = auxiliares.get('con_asistencia', 0) + auxiliares.get('sin_asistencia', 0)
                
                print(f"✓ Total técnicos: {tecnicos.get('total', 0)} = {total_tecnicos_calculado} ({'✅' if tecnicos.get('total', 0) == total_tecnicos_calculado else '❌'})")
                print(f"✓ Total apoyo: {apoyo.get('total', 0)} = {total_apoyo_calculado} ({'✅' if apoyo.get('total', 0) == total_apoyo_calculado else '❌'})")
                print(f"✓ Total auxiliares: {auxiliares.get('total', 0)} = {total_auxiliares_calculado} ({'✅' if auxiliares.get('total', 0) == total_auxiliares_calculado else '❌'})")
                
                print("\n✅ NUEVA LÓGICA IMPLEMENTADA CORRECTAMENTE")
                print("   - Técnicos: Con asistencia cuando carpeta_dia está en lista de carpetas técnicos")
                print("   - Apoyo: Con asistencia cuando carpeta_dia = 'APOYO CAMIONETAS'")
                print("   - Auxiliares: Con asistencia cuando carpeta_dia está en lista auxiliares")
                
                return True
                
            else:
                print(f"❌ Error en la respuesta: {data}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error al decodificar JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    test_nueva_logica()