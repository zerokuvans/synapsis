#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar los cálculos de técnicos en el endpoint de Inicio de Operación
"""

import requests
import json
from datetime import datetime

def test_tecnicos_endpoint():
    """Probar el endpoint de datos de inicio de operación"""
    
    # URL del endpoint
    url = "http://localhost:8080/api/lider/inicio-operacion/datos"
    
    # Parámetros de prueba (fecha actual)
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    params = {
        'fecha': fecha_actual
    }
    
    print("=" * 60)
    print("PROBANDO CÁLCULOS DE TÉCNICOS - INICIO DE OPERACIÓN")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Fecha: {fecha_actual}")
    print()
    
    try:
        # Hacer la petición
        response = requests.get(url, params=params)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                # Extraer datos de técnicos
                tecnicos = data['data']['tecnicos']
                apoyo = data['data']['apoyo_camionetas']
                auxiliares = data['data']['auxiliares']
                metricas = data['data']['metricas']
                cumplimiento = data['data']['cumplimiento']
                debug_info = data['data'].get('debug_info', {})
                
                print("✅ RESPUESTA EXITOSA")
                print()
                
                print("📊 TÉCNICOS:")
                print(f"   Total: {tecnicos['total']}")
                print(f"   Con Asistencia: {tecnicos['con_asistencia']}")
                print(f"   Sin Asistencia: {tecnicos['sin_asistencia']}")
                print()
                
                print("🚐 APOYO CAMIONETAS:")
                print(f"   Total: {apoyo['total']}")
                print(f"   Con Asistencia: {apoyo['con_asistencia']}")
                print(f"   Sin Asistencia: {apoyo['sin_asistencia']}")
                print()
                
                print("🔧 AUXILIARES:")
                print(f"   Total: {auxiliares['total']}")
                print(f"   Con Asistencia: {auxiliares['con_asistencia']}")
                print(f"   Sin Asistencia: {auxiliares['sin_asistencia']}")
                print()
                
                print("📈 MÉTRICAS:")
                print(f"   OKs del día: {metricas['oks_dia']}")
                print(f"   Presupuesto día: ${metricas['presupuesto_dia']:,}")
                print(f"   Presupuesto mes: ${metricas['presupuesto_mes']:,}")
                print()
                
                print("✅ CUMPLIMIENTO:")
                print(f"   Cumple: {cumplimiento['cumple']}")
                print(f"   No Cumple: {cumplimiento['no_cumple']}")
                print(f"   % Cumplimiento día: {cumplimiento['cumplimiento_dia']}%")
                print(f"   % Cumplimiento mes: {cumplimiento['cumplimiento_mes']}%")
                print()
                
                if debug_info:
                    print("🔍 DEBUG INFO:")
                    print(f"   Total registros procesados: {debug_info['total_registros']}")
                    print(f"   Filtros aplicados: {debug_info['filtros_aplicados']}")
                print()
                
                # Validaciones
                print("🔍 VALIDACIONES:")
                
                # Verificar que los totales sean consistentes
                total_calculado = tecnicos['con_asistencia'] + tecnicos['sin_asistencia']
                if total_calculado == tecnicos['total']:
                    print("   ✅ Total técnicos es consistente")
                else:
                    print(f"   ❌ Total técnicos inconsistente: {total_calculado} != {tecnicos['total']}")
                
                # Verificar que hay datos
                if tecnicos['total'] > 0:
                    print("   ✅ Se encontraron técnicos en los datos")
                else:
                    print("   ⚠️  No se encontraron técnicos")
                
                # Verificar porcentajes
                total_cumplimiento = cumplimiento['cumple'] + cumplimiento['no_cumple']
                if total_cumplimiento > 0:
                    porcentaje_calculado = (cumplimiento['cumple'] / total_cumplimiento) * 100
                    if abs(porcentaje_calculado - cumplimiento['cumplimiento_dia']) < 0.1:
                        print("   ✅ Porcentaje de cumplimiento es correcto")
                    else:
                        print(f"   ❌ Porcentaje incorrecto: {porcentaje_calculado:.1f}% != {cumplimiento['cumplimiento_dia']}%")
                
            else:
                print("❌ ERROR EN LA RESPUESTA:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
        else:
            print(f"❌ ERROR HTTP {response.status_code}:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al servidor")
        print("   Verifica que el servidor esté ejecutándose en http://localhost:8080")
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    test_tecnicos_endpoint()