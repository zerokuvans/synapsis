import requests
import json

# Probar el endpoint con la corrección aplicada
print("=== PRUEBA FINAL DEL ENDPOINT ===")

# Usar la IP que está funcionando
base_url = "http://192.168.80.15:8080"
url = f"{base_url}/api/turnos-semana"
params = {
    'fecha_inicio': '2025-10-06',
    'fecha_fin': '2025-10-12'
}

print(f"URL: {url}")
print(f"Parámetros: {params}")

try:
    # Crear una sesión para mantener cookies
    session = requests.Session()
    
    # Hacer la petición
    response = session.get(url, params=params)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nRespuesta exitosa:")
        print(f"Success: {data.get('success')}")
        
        if data.get('success') and 'turnos' in data:
            turnos = data['turnos']
            print(f"Cantidad de turnos: {len(turnos)}")
            
            if len(turnos) > 0:
                print(f"\nPrimer turno:")
                primer_turno = turnos[0]
                print(json.dumps(primer_turno, indent=2, ensure_ascii=False))
                
                print(f"\nTipo de fecha: {type(primer_turno.get('analistas_turnos_fecha'))}")
                print(f"Valor de fecha: {primer_turno.get('analistas_turnos_fecha')}")
                print(f"Analista: {primer_turno.get('analistas_turnos_analista')}")
                print(f"Turno: {primer_turno.get('analistas_turnos_turno')}")
                
                # Simular el filtrado que hace el frontend
                print(f"\n=== SIMULACIÓN DEL FILTRADO FRONTEND ===")
                target_date = "2025-10-06"
                filtered_turnos = []
                
                for turno in turnos:
                    fecha_raw = turno.get('analistas_turnos_fecha')
                    if fecha_raw:
                        if isinstance(fecha_raw, str):
                            fecha_str = fecha_raw[:10]
                        else:
                            fecha_str = str(fecha_raw)[:10]
                        
                        if fecha_str == target_date:
                            filtered_turnos.append(turno)
                
                print(f"Turnos filtrados para {target_date}: {len(filtered_turnos)}")
                if filtered_turnos:
                    print("Primer turno filtrado:")
                    print(json.dumps(filtered_turnos[0], indent=2, ensure_ascii=False))
            else:
                print("No hay turnos en la respuesta")
        else:
            print(f"Error en la respuesta: {data}")
    else:
        print(f"Error HTTP: {response.status_code}")
        print(f"Respuesta: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")