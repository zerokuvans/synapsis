import requests
import json
from datetime import datetime, timedelta

# Configurar la URL base
base_url = "http://localhost:8080"

# Calcular fechas para la semana actual
today = datetime.now()
start_of_week = today - timedelta(days=today.weekday())
end_of_week = start_of_week + timedelta(days=6)

fecha_inicio = start_of_week.strftime('%Y-%m-%d')
fecha_fin = end_of_week.strftime('%Y-%m-%d')

print(f"=== PRUEBA DEL ENDPOINT /api/turnos-semana ===")
print(f"Consultando desde: {fecha_inicio} hasta: {fecha_fin}")

# Hacer la petición al endpoint
url = f"{base_url}/api/turnos-semana"
params = {
    'fecha_inicio': fecha_inicio,
    'fecha_fin': fecha_fin
}

try:
    response = requests.get(url, params=params)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nRespuesta del API:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if isinstance(data, list) and len(data) > 0:
            print(f"\nTotal de registros: {len(data)}")
            print(f"\nPrimer registro:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False))
        else:
            print("\nNo se encontraron datos o la respuesta no es una lista")
    else:
        print(f"Error: {response.status_code}")
        print(f"Respuesta: {response.text}")
        
except Exception as e:
    print(f"Error al hacer la petición: {e}")