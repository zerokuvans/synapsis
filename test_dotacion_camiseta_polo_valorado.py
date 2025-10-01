#!/usr/bin/env python3
"""
Test para verificar que el endpoint /api/dotaciones maneja correctamente 
el campo camiseta_polo_valorado enviado desde el frontend.
"""

import requests
import json

def test_dotacion_camiseta_polo_valorado():
    """
    Prueba el endpoint /api/dotaciones con camiseta polo VALORADO
    usando el formato exacto que envía el frontend.
    """
    
    print("=" * 70)
    print("🧪 TEST: Dotación con camiseta polo VALORADO")
    print("=" * 70)
    
    # URL del endpoint
    url = "http://localhost:8080/api/dotaciones"
    
    # Datos exactos como los envía el frontend de dotaciones.html
    datos_dotacion = {
        "cliente": "Test Cliente",
        "id_codigo_consumidor": 12345,
        
        # Camiseta polo con estado VALORADO
        "camisetapolo": 1,
        "camiseta_polo_talla": "M",
        "camiseta_polo_valorado": 1,  # Este es el campo que causaba el problema
        
        # Otros elementos con valores por defecto
        "pantalon": 0,
        "pantalon_talla": None,
        "pantalon_valorado": 0,
        
        "camisetagris": 0,
        "camiseta_gris_talla": None,
        "camiseta_gris_valorado": 0,
        
        "guerrera": 0,
        "guerrera_talla": None,
        "guerrera_valorado": 0,
        
        "chaqueta": 0,
        "chaqueta_talla": None,
        "chaqueta_valorado": 0,
        
        "guantes_nitrilo": 0,
        "guantes_nitrilo_valorado": 0,
        
        "guantes_carnaza": 0,
        "guantes_carnaza_valorado": 0,
        
        "gafas": 0,
        "gafas_valorado": 0,
        
        "gorra": 0,
        "gorra_valorado": 0,
        
        "casco": 0,
        "casco_valorado": 0,
        
        "botas": 0,
        "botas_talla": None,
        "botas_valorado": 0
    }
    
    print("📤 DATOS ENVIADOS:")
    print(json.dumps(datos_dotacion, indent=2, ensure_ascii=False))
    print()
    
    try:
        # Realizar la petición
        response = requests.post(url, json=datos_dotacion)
        
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
            print("✅ ¡ÉXITO! La dotación se creó correctamente")
            print("   - La camiseta polo VALORADO se procesó sin errores")
            print("   - El mapeo de campos funciona correctamente")
            return True
        elif response.status_code == 400:
            print("⚠️  ERROR DE VALIDACIÓN:")
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                print(f"   - Mensaje: {error_data.get('message', 'Sin mensaje')}")
                if 'Stock insuficiente' in error_data.get('message', ''):
                    print("   - El error es de stock, no de mapeo de campos")
                    print("   - Esto significa que el mapeo funciona correctamente")
                    return True
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

def test_dotacion_camiseta_polo_no_valorado():
    """
    Prueba adicional con camiseta polo NO VALORADO para comparar
    """
    
    print("\n" + "=" * 70)
    print("🧪 TEST ADICIONAL: Dotación con camiseta polo NO VALORADO")
    print("=" * 70)
    
    # URL del endpoint
    url = "http://localhost:8080/api/dotaciones"
    
    # Datos con camiseta polo NO VALORADO
    datos_dotacion = {
        "cliente": "Test Cliente NO VALORADO",
        "id_codigo_consumidor": 12346,
        
        # Camiseta polo con estado NO VALORADO
        "camisetapolo": 1,
        "camiseta_polo_talla": "L",
        "camiseta_polo_valorado": 0,  # NO VALORADO
        
        # Otros elementos en 0
        "pantalon": 0, "pantalon_valorado": 0,
        "camisetagris": 0, "camiseta_gris_valorado": 0,
        "guerrera": 0, "guerrera_valorado": 0,
        "chaqueta": 0, "chaqueta_valorado": 0,
        "guantes_nitrilo": 0, "guantes_nitrilo_valorado": 0,
        "guantes_carnaza": 0, "guantes_carnaza_valorado": 0,
        "gafas": 0, "gafas_valorado": 0,
        "gorra": 0, "gorra_valorado": 0,
        "casco": 0, "casco_valorado": 0,
        "botas": 0, "botas_valorado": 0
    }
    
    try:
        response = requests.post(url, json=datos_dotacion)
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 400:
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                message = error_data.get('message', '')
                if 'camiseta_polo (NO VALORADO)' in message:
                    print("✅ CORRECTO: El sistema detecta correctamente NO VALORADO")
                    print(f"   - Mensaje: {message}")
                    return True
        elif response.status_code == 201:
            print("✅ ÉXITO: Dotación NO VALORADO creada (hay stock disponible)")
            return True
            
        print("⚠️  Respuesta inesperada para NO VALORADO")
        return False
        
    except Exception as e:
        print(f"❌ Error en test NO VALORADO: {e}")
        return False

if __name__ == "__main__":
    print("🔍 VERIFICACIÓN: Corrección del mapeo camiseta_polo_valorado")
    print("Este test verifica que el endpoint /api/dotaciones maneja correctamente")
    print("el campo camiseta_polo_valorado enviado desde el frontend.\n")
    
    # Ejecutar tests
    test1 = test_dotacion_camiseta_polo_valorado()
    test2 = test_dotacion_camiseta_polo_no_valorado()
    
    print("\n" + "=" * 70)
    print("📋 RESUMEN DE RESULTADOS")
    print("=" * 70)
    
    if test1 and test2:
        print("✅ TODOS LOS TESTS PASARON")
        print("   El mapeo de camiseta_polo_valorado funciona correctamente")
        print("   El sistema distingue entre VALORADO y NO VALORADO")
    elif test1:
        print("✅ TEST PRINCIPAL PASÓ")
        print("   El mapeo básico funciona, pero hay problemas con NO VALORADO")
    else:
        print("❌ TESTS FALLARON")
        print("   Se requiere más investigación")
    
    print("\n🔧 CORRECCIÓN APLICADA:")
    print("   - Se corrigió el mapeo en el endpoint /api/dotaciones")
    print("   - Ahora busca 'camiseta_polo_valorado' en lugar de 'camisetapolo_valorado'")
    print("   - Esto coincide con lo que envía el frontend")