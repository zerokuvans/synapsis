import requests
import json

def test_stock_api():
    print("=== PRUEBA API STOCK DOTACIONES ===")
    
    try:
        # Probar la API de stock
        response = requests.get('http://127.0.0.1:8080/api/stock-dotaciones')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API respondió correctamente")
            print(f"Success: {data.get('success')}")
            
            if 'stock' in data:
                print("\n📊 DATOS DE STOCK:")
                for item in data['stock']:
                    if item['tipo_elemento'] == 'pantalon':
                        print(f"\n🔍 PANTALONES:")
                        print(f"   Tipo: {item['tipo_elemento']}")
                        print(f"   Ingresado: {item['cantidad_ingresada']}")
                        print(f"   Entregado: {item['cantidad_entregada']}")
                        print(f"   Disponible: {item['saldo_disponible']}")
                        break
                
                print("\n📋 TODOS LOS ELEMENTOS:")
                for item in data['stock']:
                    print(f"   {item['tipo_elemento']}: Disponible {item['saldo_disponible']}")
            else:
                print("❌ No se encontraron datos de stock")
        else:
            print(f"❌ Error en API: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_stock_api()