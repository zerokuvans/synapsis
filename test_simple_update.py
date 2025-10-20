import requests
import json

def test_simple_update():
    update_data = {
        'observaciones': 'Prueba de actualizacion desde script',
        'estado': 'Activo'
    }
    
    url = "http://localhost:8080/api/mpa/tecnico_mecanica/2"
    
    print(f"Probando PUT a: {url}")
    print(f"Datos: {json.dumps(update_data, indent=2)}")
    
    try:
        response = requests.put(
            url,
            json=update_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 401:
            print("Error 401: No autenticado")
        elif response.status_code == 403:
            print("Error 403: Sin permisos")
        elif response.status_code == 500:
            print("Error 500: Error interno del servidor")
            try:
                error_data = response.json()
                print(f"Error JSON: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error texto: {response.text}")
        else:
            try:
                data = response.json()
                print(f"Respuesta: {json.dumps(data, indent=2)}")
            except:
                print(f"Respuesta texto: {response.text}")
                
    except Exception as e:
        print(f"Error en peticion: {e}")

if __name__ == "__main__":
    test_simple_update()