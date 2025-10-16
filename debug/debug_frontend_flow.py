import requests
import json
from datetime import datetime, timedelta

# Simular el flujo del frontend
print("=== DEBUG DEL FLUJO FRONTEND ===")

# 1. Simular la petición que hace loadWeekData
base_url = "http://192.168.80.15:8080"  # Usar la IP que está funcionando
fecha_inicio = "2025-10-06"
fecha_fin = "2025-10-12"

url = f"{base_url}/api/turnos-semana"
params = {
    'fecha_inicio': fecha_inicio,
    'fecha_fin': fecha_fin
}

print(f"1. Petición a: {url}")
print(f"   Parámetros: {params}")

try:
    # Simular una sesión con cookies (como haría el navegador)
    session = requests.Session()
    
    # Primero hacer login (simulado)
    print("\n2. Simulando autenticación...")
    
    # Hacer la petición al endpoint
    response = session.get(url, params=params)
    print(f"\n3. Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n4. Estructura de respuesta:")
        print(f"   Tipo: {type(data)}")
        print(f"   Keys: {list(data.keys()) if isinstance(data, dict) else 'No es dict'}")
        
        if 'success' in data and data['success']:
            turnos = data.get('turnos', [])
            print(f"\n5. Datos de turnos:")
            print(f"   Cantidad: {len(turnos)}")
            
            if len(turnos) > 0:
                print(f"\n6. Primer turno:")
                primer_turno = turnos[0]
                print(json.dumps(primer_turno, indent=2, ensure_ascii=False))
                
                print(f"\n7. Campos del primer turno:")
                for key, value in primer_turno.items():
                    print(f"   {key}: {value} (tipo: {type(value).__name__})")
                
                # Simular el filtrado por día que hace renderWeekCalendar
                print(f"\n8. Simulando filtrado por día (2025-10-06):")
                day_turnos = []
                for turno in turnos:
                    fecha_raw = turno.get('analistas_turnos_fecha')
                    if fecha_raw:
                        if isinstance(fecha_raw, str):
                            fecha_str = fecha_raw[:10]
                        else:
                            try:
                                fecha_str = str(fecha_raw)[:10]
                            except:
                                fecha_str = ""
                        
                        if fecha_str == "2025-10-06":
                            day_turnos.append(turno)
                
                print(f"   Turnos encontrados para 2025-10-06: {len(day_turnos)}")
                if day_turnos:
                    print(f"   Primer turno del día:")
                    print(json.dumps(day_turnos[0], indent=2, ensure_ascii=False))
            else:
                print("   No hay turnos en la respuesta")
        else:
            print(f"   Error en respuesta: {data}")
    else:
        print(f"   Error HTTP: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")