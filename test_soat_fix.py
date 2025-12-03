#!/usr/bin/env python3
"""
Script para probar que la corrección del problema de SOAT funciona correctamente.
Verifica que el tecnico_asignado se guarde como ID en lugar del nombre.
"""

import requests
import json
from datetime import datetime, timedelta

def test_soat_creation():
    """Prueba la creación de SOAT para verificar que se guarda correctamente el técnico"""
    
    # Configuración
    base_url = "http://127.0.0.1:8080"
    
    # Datos de login (usar credenciales válidas)
    login_data = {
        'username': '80833959',
        'password': 'M4r14l4r@'
    }
    
    session = requests.Session()
    
    try:
        # 1. Hacer login
        print("🔐 Intentando login...")
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login falló: {login_response.status_code}")
            print(f"Respuesta: {login_response.text}")
            return False
        
        print("✅ Login exitoso")
        
        # 2. Obtener lista de vehículos para seleccionar uno
        print("🚗 Obteniendo lista de vehículos...")
        vehiculos_response = session.get(f"{base_url}/api/mpa/vehiculos")
        
        if vehiculos_response.status_code != 200:
            print(f"❌ Error obteniendo vehículos: {vehiculos_response.status_code}")
            return False
        
        vehiculos_data = vehiculos_response.json()
        if not vehiculos_data.get('success') or not vehiculos_data.get('data'):
            print("❌ No se encontraron vehículos")
            return False
        
        # Seleccionar un vehículo sin SOAT activo vigente
        vehiculo_seleccionado = None
        for vehiculo in vehiculos_data['data']:
            placa = vehiculo.get('placa')
            if not placa:
                continue
            soat_resp = session.get(f"{base_url}/api/mpa/soat", params={'placa': placa})
            if soat_resp.status_code != 200:
                continue
            soats = soat_resp.json().get('data', [])
            hoy = datetime.now().date()
            tiene_activo_vigente = False
            for s in soats:
                estado_reg = s.get('estado')
                fv = s.get('fecha_vencimiento')
                try:
                    fv_date = datetime.strptime(fv, '%Y-%m-%d').date() if fv else None
                except Exception:
                    fv_date = None
                if estado_reg == 'Activo' and fv_date and fv_date >= hoy:
                    tiene_activo_vigente = True
                    break
            if not tiene_activo_vigente:
                vehiculo_seleccionado = vehiculo
                break
        
        if not vehiculo_seleccionado:
            print("❌ No se encontró un vehículo con técnico asignado")
            return False
        
        print(f"✅ Vehículo seleccionado: {vehiculo_seleccionado['placa']}")
        print(f"   Técnico asignado (ID): {vehiculo_seleccionado.get('tecnico_asignado', 'N/A')}")
        print(f"   Técnico nombre: {vehiculo_seleccionado.get('tecnico_nombre', 'N/A')}")
        
        # 3. Crear datos de SOAT de prueba
        fecha_inicio = datetime.now().strftime('%Y-%m-%d')
        fecha_vencimiento = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        
        soat_data = {
            'placa': vehiculo_seleccionado['placa'],
            'numero_poliza': f'TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'aseguradora': 'SURA',
            'fecha_inicio': fecha_inicio,
            'fecha_vencimiento': fecha_vencimiento,
            'valor_prima': 150000,
            'tecnico_asignado': vehiculo_seleccionado['tecnico_asignado']  # Debe ser el ID
        }
        
        print("📝 Creando SOAT de prueba...")
        print(f"   Datos: {json.dumps(soat_data, indent=2)}")
        
        # 4. Crear SOAT
        soat_response = session.post(
            f"{base_url}/api/mpa/soat",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(soat_data)
        )
        
        if soat_response.status_code != 200:
            print(f"❌ Error creando SOAT: {soat_response.status_code}")
            print(f"Respuesta: {soat_response.text}")
            return False
        
        soat_result = soat_response.json()
        if not soat_result.get('success'):
            print(f"❌ Error en respuesta de SOAT: {soat_result.get('message')}")
            return False
        
        print("✅ SOAT creado exitosamente")
        
        # 5. Verificar que el SOAT se guardó correctamente
        print("🔍 Verificando que el SOAT se guardó correctamente...")
        
        # Verificar que el SOAT se guardó correctamente en /api/mpa/soat
        verif_resp = session.get(f"{base_url}/api/mpa/soat", params={'placa': vehiculo_seleccionado['placa']})
        if verif_resp.status_code != 200:
            print(f"❌ Error verificando SOAT: {verif_resp.status_code}")
            return False
        verif_data = verif_resp.json()
        soat_encontrado = None
        for s in verif_data.get('data', []):
            if s.get('numero_poliza') == soat_data['numero_poliza']:
                soat_encontrado = s
                break
        
        if not soat_encontrado:
            print("❌ El SOAT creado no aparece en los vencimientos")
            return False
        
        print("✅ SOAT encontrado en registros")
        print(f"   Técnico asignado: {soat_encontrado.get('tecnico_asignado')}")
        print(f"   Técnico nombre: {soat_encontrado.get('tecnico_nombre')}")
        
        # Verificar que el técnico asignado es un ID (número) y no un nombre
        tecnico_asignado = soat_encontrado.get('tecnico_asignado')
        if tecnico_asignado and str(tecnico_asignado).isdigit():
            print("✅ El técnico asignado se guardó correctamente como ID")
            return True
        else:
            print(f"❌ El técnico asignado no es un ID válido: {tecnico_asignado}")
            return False
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🧪 Iniciando prueba de corrección de SOAT...")
    print("=" * 50)
    
    success = test_soat_creation()
    
    print("=" * 50)
    if success:
        print("✅ PRUEBA EXITOSA: La corrección funciona correctamente")
    else:
        print("❌ PRUEBA FALLIDA: La corrección no funciona")
    
    return success

if __name__ == "__main__":
    main()
