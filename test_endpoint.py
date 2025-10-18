import requests
import json

# Probar el endpoint con la cédula del técnico que sabemos que tiene licencia
cedula_tecnico = "1019112308"  # ALARCON SALAS LUIS HERNANDO

url = f"http://localhost:8080/api/tecnicos/datos-preoperacional?cedula={cedula_tecnico}"

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    
    if response.status_code == 200:
        print(f"\n=== CONTENIDO DE LA RESPUESTA ===")
        print(f"Primeros 500 caracteres: {response.text[:500]}")
        
        # Intentar parsear como JSON
        try:
            data = response.json()
            print("\n=== RESPUESTA DEL ENDPOINT (JSON) ===")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar específicamente los datos de licencia
            print("\n=== DATOS DE LICENCIA ===")
            print(f"Tipo de Licencia: {data.get('tipo_licencia', 'NO ENCONTRADO')}")
            print(f"Fecha Vencimiento Licencia: {data.get('fecha_venc_licencia', 'NO ENCONTRADO')}")
        except json.JSONDecodeError:
            print("La respuesta no es JSON válido - probablemente es HTML (página de login)")
        
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Error al hacer la petición: {e}")