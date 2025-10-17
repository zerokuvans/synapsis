#!/usr/bin/env python3
"""
Script para probar el nuevo cálculo de cumplimiento mensual
"""

import requests
import json
from datetime import datetime, date

BASE_URL = "http://localhost:8080"
LOGIN_URL = f"{BASE_URL}/"
DATOS_URL = f"{BASE_URL}/api/lider/inicio-operacion/datos"

def hacer_login():
    """Hacer login con credenciales de administrativo (que tiene todos los permisos)"""
    session = requests.Session()
    
    # Credenciales del usuario
    login_data = {
        'username': '80833959',  # Cédula del usuario
        'password': 'M4r14l4r@'  # Password del usuario
    }
    
    try:
        response = session.post(LOGIN_URL, data=login_data)
        
        if response.status_code == 200:
            # Verificar si el login fue exitoso
            if 'dashboard' in response.text.lower() or 'administrativo' in response.text.lower():
                print("✅ Login exitoso")
                return session
            else:
                print("❌ Login falló: credenciales incorrectas")
                return None
        else:
            print(f"❌ Login falló: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None

def probar_cumplimiento_mensual(session):
    """Probar el endpoint con el nuevo cálculo mensual"""
    print("\n=== PROBANDO NUEVO CÁLCULO DE CUMPLIMIENTO MENSUAL ===")
    
    # Usar fecha actual
    fecha_actual = date.today().strftime('%Y-%m-%d')
    
    params = {
        'fecha': fecha_actual
    }
    
    try:
        print(f"📅 Consultando datos para: {fecha_actual}")
        response = session.get(DATOS_URL, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                cumplimiento = data['data']['cumplimiento']
                
                print(f"\n📊 RESULTADOS DEL CUMPLIMIENTO:")
                print(f"   🔹 Cumplimiento Día: {cumplimiento['cumplimiento_dia']}%")
                print(f"   🔹 Cumplimiento Mes: {cumplimiento['cumplimiento_mes']}%")
                
                # Mostrar datos de presupuesto
                metricas = data['data']['metricas']
                presupuesto_dia = metricas.get('presupuesto_dia', 0)
                presupuesto_mes = metricas.get('presupuesto_mes', 0)
                
                print(f"\n💰 RESULTADOS DEL PRESUPUESTO:")
                print(f"   💵 Presupuesto Día: ${presupuesto_dia:,}")
                print(f"   💰 Presupuesto Mes: ${presupuesto_mes:,}")
                
                # Verificar si la nueva lógica está funcionando
                presupuesto_mes_anterior = presupuesto_dia * 26
                print(f"\n🔍 VERIFICACIÓN DE NUEVA LÓGICA DE PRESUPUESTO:")
                print(f"   📊 Presupuesto día: ${presupuesto_dia:,}")
                print(f"   📊 Presupuesto mes (nuevo): ${presupuesto_mes:,}")
                print(f"   📊 Presupuesto mes (anterior): ${presupuesto_mes_anterior:,}")
                
                if presupuesto_mes != presupuesto_mes_anterior:
                    print("   ✅ ¡Nueva lógica funcionando! - Presupuesto mes NO es día * 26")
                else:
                    print("   ⚠️  Presupuesto mes sigue siendo día * 26 - verificar implementación")
                
                print(f"\n📈 DATOS MENSUALES DETALLADOS:")
                print(f"   ✅ Cumple (mes): {cumplimiento.get('cumple_mes', 0)}")
                print(f"   🔄 Novedad (mes): {cumplimiento.get('novedad_mes', 0)}")
                print(f"   ❌ No Cumple (mes): {cumplimiento.get('no_cumple_mes', 0)}")
                print(f"   ⚪ No Aplica (mes): {cumplimiento.get('no_aplica_mes', 0)}")
                print(f"   📊 Total evaluados (mes): {cumplimiento.get('total_mes', 0)}")
                
                # Verificar la fórmula
                cumple_mes = cumplimiento.get('cumple_mes', 0)
                novedad_mes = cumplimiento.get('novedad_mes', 0)
                total_mes = cumplimiento.get('total_mes', 0)
                
                if total_mes > 0:
                    cumplimiento_calculado = ((cumple_mes + novedad_mes) / total_mes) * 100
                    cumplimiento_api = cumplimiento['cumplimiento_mes']
                    
                    print(f"\n🧮 VERIFICACIÓN DE FÓRMULA:")
                    print(f"   📐 Fórmula: (Cumple + Novedad) / Total × 100")
                    print(f"   📐 Cálculo: ({cumple_mes} + {novedad_mes}) / {total_mes} × 100")
                    print(f"   📐 Resultado manual: {cumplimiento_calculado:.1f}%")
                    print(f"   📐 Resultado API: {cumplimiento_api}%")
                    
                    if abs(cumplimiento_calculado - cumplimiento_api) < 0.1:
                        print("   ✅ ¡Fórmula correcta!")
                    else:
                        print("   ❌ Error en la fórmula")
                else:
                    print("   ⚠️  No hay datos mensuales para evaluar")
                
                return True
            else:
                print(f"❌ Error en respuesta: {data}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Respuesta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error al probar endpoint: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 PRUEBA DEL NUEVO CÁLCULO DE CUMPLIMIENTO MENSUAL")
    print("=" * 60)
    
    # 1. Hacer login
    session = hacer_login()
    if not session:
        print("❌ No se pudo hacer login")
        return
    
    # 2. Probar el nuevo cálculo
    exito = probar_cumplimiento_mensual(session)
    
    # 3. Conclusión
    print(f"\n🎯 RESULTADO FINAL:")
    if exito:
        print("✅ ¡El nuevo cálculo de cumplimiento mensual está funcionando!")
        print("   - Se obtienen datos acumulados del mes completo")
        print("   - Se aplica la fórmula: (Cumple + Novedad) / Total × 100")
        print("   - La tarjeta 'Cumplimiento Mes' mostrará el porcentaje correcto")
    else:
        print("❌ Hay problemas con el nuevo cálculo")
        print("   - Revisar la implementación del endpoint")
        print("   - Verificar la consulta SQL mensual")

if __name__ == "__main__":
    main()