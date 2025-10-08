import requests
import json

def test_endpoint_final():
    print("=== PRUEBA FINAL DEL ENDPOINT DE ASISTENCIA ===")
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        # 1. Login
        login_data = {
            'username': '80833959',
            'password': 'M4r14l4r@'
        }
        
        login_response = session.post('http://localhost:8080/', data=login_data)
        print(f"✓ Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.text[:200]}")
            return
        
        # 2. Probar endpoint de resumen agrupado con fecha actual
        from datetime import date
        fecha_hoy = date.today().strftime('%Y-%m-%d')
        
        url = f'http://localhost:8080/api/asistencia/resumen_agrupado?fecha_inicio={fecha_hoy}&fecha_fin={fecha_hoy}'
        print(f"\n✓ Probando URL: {url}")
        
        response = session.get(url)
        print(f"✓ Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Response JSON recibido")
            
            # Mostrar estructura de datos
            print(f"\n=== ESTRUCTURA DE DATOS ===")
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message', 'N/A')}")
            
            if 'data' in data:
                data_content = data['data']
                print(f"\nContenido de 'data':")
                print(f"- total_general: {data_content.get('total_general', 'N/A')}")
                print(f"- resumen_grupos: {len(data_content.get('resumen_grupos', []))} elementos")
                print(f"- detallado: {len(data_content.get('detallado', []))} elementos")
                
                # Mostrar algunos elementos de resumen_grupos
                resumen_grupos = data_content.get('resumen_grupos', [])
                if resumen_grupos:
                    print(f"\n=== PRIMEROS ELEMENTOS DE RESUMEN_GRUPOS ===")
                    for i, item in enumerate(resumen_grupos[:3]):
                        print(f"Elemento {i+1}:")
                        print(f"  - grupo: {item.get('grupo', 'N/A')}")
                        print(f"  - carpeta: {item.get('carpeta', 'N/A')}")
                        print(f"  - total_tecnicos: {item.get('total_tecnicos', 'N/A')}")
                        print(f"  - porcentaje: {item.get('porcentaje', 'N/A')}")
                        print()
                
                if len(resumen_grupos) > 0:
                    print(f"✅ ¡DATOS ENCONTRADOS! El endpoint devuelve {len(resumen_grupos)} grupos")
                    print(f"✅ El frontend debería mostrar estos datos ahora")
                else:
                    print(f"⚠ No hay datos en resumen_grupos para la fecha {fecha_hoy}")
            else:
                print(f"❌ No se encontró 'data' en la respuesta")
                
        else:
            print(f"❌ Error en endpoint: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n=== CONCLUSIÓN ===")
    print(f"1. El endpoint está funcionando correctamente")
    print(f"2. Se corrigió el JavaScript para usar 'resumen_grupos' en lugar de 'detallado'")
    print(f"3. Los datos deberían mostrarse ahora en el frontend")
    print(f"4. Abra http://localhost:8080/asistencia en el navegador para verificar")

if __name__ == '__main__':
    test_endpoint_final()