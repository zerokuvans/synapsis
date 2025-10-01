#!/usr/bin/env python3
"""
Test específico para el endpoint /api/cambios_dotacion con camiseta polo VALORADO
Este es el endpoint que está causando el error según la imagen del usuario.
"""

import requests
import json
from datetime import datetime

def test_cambio_dotacion_camiseta_polo_valorado():
    """
    Prueba el endpoint /api/cambios_dotacion con camiseta polo VALORADO
    usando el formato exacto que envía el frontend de cambios_dotacion.html.
    """
    
    print("=" * 80)
    print("🧪 TEST: Cambio de dotación con camiseta polo VALORADO")
    print("=" * 80)
    
    # URL del endpoint que está causando el error
    url = "http://localhost:8080/api/cambios_dotacion"
    
    # Datos como los envía el frontend de cambios_dotacion.html
    datos_cambio = {
        "id_codigo_consumidor": 12345,
        "fecha_cambio": datetime.now().strftime("%Y-%m-%d"),
        
        # Camiseta polo con estado VALORADO
        "camisetapolo": 1,
        "camiseta_polo_talla": "M",
        "camiseta_polo_valorado": True,  # Este es el campo corregido
        
        # Otros elementos con valores por defecto
        "pantalon": 0,
        "pantalon_talla": None,
        "pantalon_valorado": False,
        
        "camisetagris": 0,
        "camiseta_gris_talla": None,
        "camisetagris_valorado": False,  # Este usa el formato del frontend
        
        "guerrera": 0,
        "guerrera_talla": None,
        "guerrera_valorado": False,
        
        "chaqueta": 0,
        "chaqueta_talla": None,
        "chaqueta_valorado": False,
        
        "guantes_nitrilo": 0,
        "guantes_nitrilo_valorado": False,
        
        "guantes_carnaza": 0,
        "guantes_carnaza_valorado": False,
        
        "gafas": 0,
        "gafas_valorado": False,
        
        "gorra": 0,
        "gorra_valorado": False,
        
        "casco": 0,
        "casco_valorado": False,
        
        "botas": 0,
        "botas_talla": None,
        "botas_valorado": False
    }
    
    print("📤 DATOS ENVIADOS AL ENDPOINT /api/cambios_dotacion:")
    print(json.dumps(datos_cambio, indent=2, ensure_ascii=False, default=str))
    print()
    
    try:
        # Realizar la petición
        response = requests.post(url, json=datos_cambio)
        
        print("📥 RESPUESTA:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            response_json = response.json()
            print("   JSON Response:")
            print(json.dumps(response_json, indent=4, ensure_ascii=False))
        else:
            print("   Text Response:")
            print(response.text)
        
        print()
        
        # Verificar el resultado
        if response.status_code == 201:
            print("✅ ¡ÉXITO! El cambio de dotación se registró correctamente")
            print("   - La camiseta polo VALORADO se procesó sin errores")
            print("   - El mapeo de campos funciona correctamente en /api/cambios_dotacion")
            return True
        elif response.status_code == 400:
            print("⚠️  ERROR DE VALIDACIÓN:")
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                message = error_data.get('message', 'Sin mensaje')
                print(f"   - Mensaje: {message}")
                
                if 'Stock insuficiente' in message:
                    if 'camiseta_polo (NO VALORADO)' in message:
                        print("❌ PROBLEMA PERSISTE: Sigue detectando como NO VALORADO")
                        print("   - El mapeo de campos aún no funciona correctamente")
                        return False
                    elif 'camiseta_polo (VALORADO)' in message:
                        print("✅ MAPEO CORRECTO: Detecta correctamente como VALORADO")
                        print("   - El error es de stock, no de mapeo")
                        return True
                else:
                    print(f"   - Otro tipo de error: {message}")
            return False
        else:
            print("❌ ERROR: Respuesta inesperada")
            print(f"   - Código de estado: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al servidor")
        print("   - Asegúrate de que el servidor esté ejecutándose en http://localhost:8080")
        return False
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
        return False

def test_cambio_dotacion_debug_campos():
    """
    Test adicional para verificar exactamente qué campos está recibiendo el endpoint
    """
    
    print("\n" + "=" * 80)
    print("🔍 TEST DEBUG: Verificación de campos recibidos")
    print("=" * 80)
    
    # Datos mínimos para activar los logs
    datos_debug = {
        "id_codigo_consumidor": 99999,
        "fecha_cambio": datetime.now().strftime("%Y-%m-%d"),
        "camisetapolo": 1,
        "camiseta_polo_valorado": True
    }
    
    print("📤 DATOS MÍNIMOS PARA DEBUG:")
    print(json.dumps(datos_debug, indent=2, ensure_ascii=False, default=str))
    print()
    print("🔍 Revisa los logs del servidor para ver el mapeo detallado...")
    
    try:
        url = "http://localhost:8080/api/cambios_dotacion"
        response = requests.post(url, json=datos_debug)
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code in [200, 201, 400]:
            print("✅ Endpoint respondió - revisa los logs del servidor")
        else:
            print(f"⚠️  Respuesta inesperada: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en debug: {e}")

if __name__ == "__main__":
    print("🔍 VERIFICACIÓN: Endpoint /api/cambios_dotacion")
    print("Este test verifica que el endpoint /api/cambios_dotacion maneja correctamente")
    print("el campo camiseta_polo_valorado enviado desde el frontend.\n")
    
    # Ejecutar tests
    test1 = test_cambio_dotacion_camiseta_polo_valorado()
    test_cambio_dotacion_debug_campos()
    
    print("\n" + "=" * 80)
    print("📋 RESUMEN")
    print("=" * 80)
    
    if test1:
        print("✅ TEST PRINCIPAL PASÓ")
        print("   El endpoint /api/cambios_dotacion funciona correctamente")
    else:
        print("❌ TEST FALLÓ")
        print("   Se requiere más investigación en /api/cambios_dotacion")
    
    print("\n🔧 CORRECCIÓN APLICADA:")
    print("   - Se corrigió el mapeo en /api/cambios_dotacion")
    print("   - Ahora busca 'camiseta_polo_valorado' en lugar de 'camisetapolo_valorado'")
    print("   - Esto debería coincidir con lo que envía el frontend de cambios_dotacion.html")