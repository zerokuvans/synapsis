#!/usr/bin/env python3
"""
Test final para confirmar que el problema de "camiseta polo VALORADO" está resuelto.
Este test simula exactamente el escenario del error original.
"""

import requests
import json

def test_escenario_original():
    """
    Simula el escenario exacto que causaba el error original:
    - Solicitar 1 camiseta polo VALORADO
    - Con campos de talla vacíos para otros elementos
    """
    
    print("=" * 60)
    print("🔍 TEST FINAL: Escenario del error original")
    print("=" * 60)
    
    # URL del endpoint
    url = "http://localhost:8080/api/cambios_dotacion"
    
    # Datos que simulan exactamente el formulario del frontend
    datos_formulario = {
        "id_codigo_consumidor": 12345,
        "fecha_cambio": "2024-01-20",
        
        # El elemento que causaba el problema
        "camisetapolo": 1,
        "camiseta_polo_talla": "M",
        "camisetapolo_valorado": True,
        
        # Otros elementos con valores por defecto (campos vacíos)
        "pantalon": 0,
        "pantalon_talla": "",  # Campo vacío que causaba el error
        "pantalon_valorado": False,
        
        "camisetagris": 0,
        "camiseta_gris_talla": "",
        "camisetagris_valorado": False,
        
        "guerrera": 0,
        "guerrera_talla": "",  # Campo vacío que causaba el error
        "guerrera_valorado": False,
        
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
        "botas_talla": "",  # Campo vacío que causaba el error
        "botas_valorado": False,
        
        "observaciones": "Test final - escenario original"
    }
    
    print("📤 DATOS ENVIADOS (simulando formulario frontend):")
    print(json.dumps(datos_formulario, indent=2, ensure_ascii=False))
    print()
    
    try:
        # Realizar la petición
        response = requests.post(url, json=datos_formulario)
        
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
            print("✅ ¡ÉXITO! El problema original ha sido resuelto")
            print("   - La camiseta polo VALORADO se procesó correctamente")
            print("   - Los campos vacíos se manejaron sin errores")
            print("   - El endpoint respondió con código 201 (Created)")
            return True
        else:
            print("❌ ERROR: El problema persiste")
            print(f"   - Código de estado: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al servidor")
        print("   - Asegúrate de que el servidor esté ejecutándose en http://localhost:8080")
        return False
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
        return False

def verificar_stock_actual():
    """
    Verifica el stock actual de camisetapolo para contexto
    """
    print("\n" + "=" * 60)
    print("📊 VERIFICACIÓN DE STOCK ACTUAL")
    print("=" * 60)
    
    try:
        import mysql.connector
        
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = connection.cursor()
        
        # Stock en ingresos
        cursor.execute("""
            SELECT COUNT(*) as total_valorado 
            FROM ingresos_dotaciones 
            WHERE tipo_elemento = 'camisetapolo' AND estado = 'VALORADO'
        """)
        stock_valorado = cursor.fetchone()[0]
        
        # Stock usado en cambios
        cursor.execute("""
            SELECT COALESCE(SUM(camisetapolo), 0) as total_usado
            FROM cambios_dotacion 
            WHERE estado_camiseta_polo = 'VALORADO'
        """)
        stock_usado = cursor.fetchone()[0]
        
        stock_disponible = stock_valorado - stock_usado
        
        print(f"📦 Stock de camisetapolo VALORADO:")
        print(f"   - Total en ingresos: {stock_valorado}")
        print(f"   - Total usado: {stock_usado}")
        print(f"   - Disponible: {stock_disponible}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error al verificar stock: {e}")

if __name__ == "__main__":
    print("🧪 PRUEBA FINAL: Resolución del problema 'camiseta polo VALORADO'")
    print("Este test confirma que el error original ha sido corregido.\n")
    
    # Verificar stock actual
    verificar_stock_actual()
    
    # Ejecutar test principal
    exito = test_escenario_original()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN FINAL")
    print("=" * 60)
    
    if exito:
        print("✅ PROBLEMA RESUELTO EXITOSAMENTE")
        print("   El error 'Incorrect integer value: '' for column 'pantalon_talla'' ha sido corregido.")
        print("   El endpoint ahora maneja correctamente los campos vacíos.")
        print("   Las camisetas polo VALORADO se pueden procesar sin problemas.")
    else:
        print("❌ EL PROBLEMA PERSISTE")
        print("   Se requiere investigación adicional.")
    
    print("\n🔧 SOLUCIÓN IMPLEMENTADA:")
    print("   - Se agregó una función 'procesar_talla()' que convierte strings vacíos a None")
    print("   - Esto permite que la base de datos maneje correctamente los campos NULL")
    print("   - Se aplicó a todos los campos de talla en el endpoint de cambios de dotación")