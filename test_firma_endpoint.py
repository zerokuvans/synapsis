import requests
import mysql.connector

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
    'autocommit': True
}

try:
    # Conectar a la base de datos para encontrar una dotación firmada
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor(dictionary=True)
    
    # Buscar dotaciones firmadas
    cursor.execute("""
        SELECT id_dotacion, cliente, firmado, LENGTH(firma_imagen) as firma_size
        FROM dotaciones 
        WHERE firma_imagen IS NOT NULL AND firma_imagen != ''
        ORDER BY id_dotacion DESC
        LIMIT 5
    """)
    
    dotaciones_firmadas = cursor.fetchall()
    
    if dotaciones_firmadas:
        print(f"Encontradas {len(dotaciones_firmadas)} dotaciones con firma:")
        for dotacion in dotaciones_firmadas:
            print(f"ID: {dotacion['id_dotacion']}, Cliente: {dotacion['cliente']}, Firmado: {dotacion['firmado']}, Tamaño: {dotacion['firma_size']} bytes")
        
        # Probar el endpoint con la primera dotación firmada
        id_dotacion = dotaciones_firmadas[0]['id_dotacion']
        print(f"\nProbando endpoint /api/obtener-firma/{id_dotacion}")
        
        # Crear una sesión para mantener cookies
        session = requests.Session()
        
        # Datos de login (usar credenciales válidas)
        login_data = {
            'username': '80833959',  # Usuario administrativo
            'password': 'M4r14l4r@'  # Contraseña
        }
        
        # Definir BASE_URL
        BASE_URL = 'http://127.0.0.1:8080'
        
        # Intentar hacer login
        try:
            login_response = session.post(f'{BASE_URL}/', data=login_data)
            print(f"Login response status: {login_response.status_code}")
            if login_response.status_code == 200:
                print("✅ Login exitoso")
            else:
                print(f"❌ Login falló: {login_response.text[:200]}")
        except Exception as e:
            print(f"Error en login: {e}")
        
        # Probar el endpoint de firma
        try:
            response = session.get(f'{BASE_URL}/api/obtener-firma/{id_dotacion}')
            print(f"Endpoint response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Endpoint exitoso: {data}")
            else:
                print(f"❌ Endpoint falló: {response.text}")
        except Exception as e:
            print(f"Error al probar endpoint: {e}")
    
    else:
        print("No se encontraron dotaciones firmadas")
    
    connection.close()
    
except mysql.connector.Error as e:
    print(f"Error de base de datos: {e}")
except Exception as e:
    print(f"Error: {e}")