import requests
import json

def test_endpoint():
    """Probar el endpoint de asistencia directamente"""
    
    url = "http://127.0.0.1:8080/api/operativo/inicio-operacion/asistencia"
    
    # Parámetros de prueba
    params = {
        'supervisor': 'SILVA CASTRO DANIEL ALBERTO',
        'fecha': '2025-10-08'
    }
    
    try:
        print("🔍 Probando endpoint de asistencia...")
        print(f"URL: {url}")
        print(f"Parámetros: {params}")
        print("=" * 60)
        
        response = requests.get(url, params=params)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"📊 Contenido de la respuesta:")
            print(f"   Texto: {response.text[:500]}...")
            print(f"   Headers: {dict(response.headers)}")
            
            try:
                data = response.json()
                print(f"   Total registros: {len(data)}")
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"   Respuesta completa: {response.text}")
                return False
            
            # Verificar duplicados por cédula
            cedulas_vistas = set()
            duplicados = []
            
            print(f"\n📋 REGISTROS DEVUELTOS:")
            for i, registro in enumerate(data, 1):
                cedula = registro.get('cedula')
                tecnico = registro.get('tecnico')
                
                if cedula in cedulas_vistas:
                    duplicados.append(registro)
                    print(f"🔴 DUPLICADO #{len(duplicados)}: {cedula} - {tecnico}")
                else:
                    cedulas_vistas.add(cedula)
                    print(f"✅ Fila {i:2d}: {cedula} - {tecnico}")
            
            print(f"\n📊 RESUMEN:")
            print(f"   Total registros: {len(data)}")
            print(f"   Técnicos únicos: {len(cedulas_vistas)}")
            print(f"   Duplicados encontrados: {len(duplicados)}")
            
            if duplicados:
                print(f"🔴 ¡PROBLEMA! El endpoint devuelve {len(duplicados)} duplicados")
                return False
            else:
                print("✅ ¡PERFECTO! El endpoint no devuelve duplicados")
                return True
                
        else:
            print(f"❌ Error en la respuesta: {response.status_code}")
            print(f"Contenido: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error al probar endpoint: {e}")
        return False

if __name__ == "__main__":
    test_endpoint()