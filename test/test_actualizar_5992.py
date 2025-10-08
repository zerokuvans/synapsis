#!/usr/bin/env python3
"""
Test específico para actualizar el registro 5992
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8080"
CEDULA = "5694500"  # Cédula del registro 5992
FECHA = "2024-09-30"  # Fecha del registro 5992

def test_actualizar_registro_5992():
    """Test para actualizar el registro 5992 con los datos específicos"""
    
    print("=== TEST ACTUALIZACIÓN REGISTRO 5992 ===")
    print(f"Cédula: {CEDULA}")
    print(f"Fecha: {FECHA}")
    print()
    
    # Datos a actualizar
    actualizaciones = [
        {"campo": "hora_inicio", "valor": "16:33"},
        {"campo": "estado", "valor": "NOVEDAD"},
        {"campo": "novedad", "valor": "prueba"}
    ]
    
    # Realizar cada actualización
    for actualizacion in actualizaciones:
        print(f"Actualizando {actualizacion['campo']} = {actualizacion['valor']}")
        
        payload = {
            "cedula": CEDULA,
            "campo": actualizacion["campo"],
            "valor": actualizacion["valor"],
            "fecha": FECHA
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/asistencia/actualizar-campo",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Respuesta: {data}")
                if data.get('success'):
                    print("✅ Actualización exitosa")
                else:
                    print(f"❌ Error: {data.get('message')}")
            else:
                print(f"❌ Error HTTP: {response.text}")
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
        
        print("-" * 50)
    
    # Verificar los cambios consultando el registro
    print("\n=== VERIFICACIÓN DE CAMBIOS ===")
    try:
        response = requests.get(
            f"{BASE_URL}/api/asistencia/consultar",
            params={"supervisor": "CARLOS ANDRES VARGAS TORRES", "fecha": FECHA}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                # Buscar el registro específico
                registro_encontrado = None
                for registro in data['data']:
                    if registro.get('cedula') == CEDULA:
                        registro_encontrado = registro
                        break
                
                if registro_encontrado:
                    print("✅ Registro encontrado:")
                    print(f"ID: {registro_encontrado.get('id_asistencia')}")
                    print(f"Cédula: {registro_encontrado.get('cedula')}")
                    print(f"Técnico: {registro_encontrado.get('tecnico')}")
                    print(f"Hora Inicio: {registro_encontrado.get('hora_inicio')}")
                    print(f"Estado: {registro_encontrado.get('estado')}")
                    print(f"Novedad: {registro_encontrado.get('novedad')}")
                    print(f"Fecha: {registro_encontrado.get('fecha_registro_bogota')}")
                else:
                    print("❌ No se encontró el registro")
            else:
                print(f"❌ Error en consulta: {data.get('message')}")
        else:
            print(f"❌ Error HTTP en consulta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión en consulta: {e}")

if __name__ == "__main__":
    test_actualizar_registro_5992()