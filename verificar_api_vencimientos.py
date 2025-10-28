import requests
import json

try:
    # Verificar el API de vencimientos
    print('🔌 Verificando API de vencimientos...')
    response = requests.get('http://127.0.0.1:8080/api/mpa/vencimientos')
    print(f'Status Code: {response.status_code}')
    
    if response.status_code == 200:
        print('✅ El API de vencimientos responde correctamente')
        
        # Imprimir la respuesta cruda para ver qué está devolviendo
        print('\n📄 Respuesta cruda:')
        print(response.text[:1000])
        
        try:
            data = response.json()
            print(f'\n📊 Total de vencimientos devueltos: {len(data)}')
            
            # Verificar el tipo de datos
            print(f'Tipo de datos: {type(data)}')
            
            if isinstance(data, list) and len(data) > 0:
                print(f'Tipo del primer elemento: {type(data[0])}')
                print(f'Primer elemento: {data[0]}')
                
                # Contar por tipo si es posible
                tipos = {}
                for item in data:
                    if isinstance(item, dict):
                        tipo = item.get('tipo', 'Sin tipo')
                        tipos[tipo] = tipos.get(tipo, 0) + 1
                    else:
                        print(f'Elemento no es dict: {item}')
                        
                print('📊 Distribución por tipo:')
                for tipo, count in tipos.items():
                    print(f'  - {tipo}: {count}')
            else:
                print('❌ Los datos no son una lista o están vacíos')
                
        except json.JSONDecodeError as e:
            print(f'❌ Error al decodificar JSON: {e}')
            
    else:
        print(f'❌ Error en el API: {response.status_code}')
        print(f'Respuesta: {response.text[:500]}...')
        
except Exception as e:
    print(f'❌ Error de conexión: {e}')