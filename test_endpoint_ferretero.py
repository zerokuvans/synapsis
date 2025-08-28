#!/usr/bin/env python3
import requests
import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

# Crear una sesión para mantener las cookies
session = requests.Session()

# Configuración de la base de datos desde variables de entorno
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'capired')
}

# URL del endpoint (asumiendo que el servidor está corriendo en localhost:8080)
BASE_URL = "http://localhost:8080"

def login():
    """Función para autenticarse en el sistema"""
    login_data = {
        'username': '80833959',  # Usuario activo con rol ADMINISTRATIVO
        'password': 'M4r14l4r@'  # Contraseña correcta
    }
    
    try:
        response = session.post(f"{BASE_URL}/", data=login_data)
        if response.status_code == 200:
            print("✅ Login exitoso")
            return True
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return False

def verificar_stock():
    """Verificar stock actual"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        cursor.execute("SELECT cantidad_disponible FROM stock_ferretero WHERE material_tipo = 'silicona'")
        stock = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return stock[0] if stock else 0
    except Exception as e:
        print(f"Error verificando stock: {e}")
        return 0

def test_endpoint():
    print("🧪 PRUEBA DEL ENDPOINT REGISTRAR_FERRETERO")
    print("=" * 50)
    
    # Verificar stock inicial
    stock_inicial = verificar_stock()
    print(f"Stock inicial de silicona: {stock_inicial}")
    
    # Caso 1: Asignación válida
    print("\n=== CASO 1: Asignación válida ===")
    cantidad_valida = min(5, stock_inicial) if stock_inicial > 0 else 0
    
    if cantidad_valida > 0:
        data_valida = {
            'id_codigo_consumidor': '1',  # ID del usuario con cédula 80833959
            'password': 'M4r14l4r@',
            'fecha': datetime.now().strftime('%Y-%m-%d'),  # Fecha actual
            'silicona': str(cantidad_valida),
            'grapas_negras': '0',
            'grapas_blancas': '0',
            'amarres_negros': '0',
            'amarres_blancos': '0',
            'cinta_aislante': '0'
        }
        
        try:
            response = session.post(f"{BASE_URL}/logistica/registrar_ferretero", data=data_valida)
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            print(f"Response Text: {response.text}")
            
            try:
                response_json = response.json()
                print(f"Response JSON: {response_json}")
            except ValueError as json_error:
                print(f"❌ Error parsing JSON: {json_error}")
            
            if response.status_code == 200:
                stock_despues = verificar_stock()
                print(f"Stock después: {stock_despues}")
                print(f"Diferencia: {stock_inicial - stock_despues}")
                
                if stock_despues == (stock_inicial - cantidad_valida):
                    print("✅ ASIGNACIÓN VÁLIDA PROCESADA CORRECTAMENTE")
                else:
                    print("❌ PROBLEMA CON LA ACTUALIZACIÓN DE STOCK")
            else:
                print("❌ ASIGNACIÓN VÁLIDA RECHAZADA")
                
        except requests.exceptions.ConnectionError:
            print("❌ No se pudo conectar al servidor. ¿Está corriendo la aplicación Flask?")
            return
        except Exception as e:
            print(f"❌ Error en la petición: {e}")
            return
    else:
        print("❌ No hay stock suficiente para hacer una asignación válida")
    
    # Caso 2: Asignación que excede el stock
    print("\n=== CASO 2: Asignación que excede stock ===")
    stock_actual = verificar_stock()
    cantidad_excesiva = stock_actual + 100
    
    print(f"Stock disponible: {stock_actual}")
    print(f"Intentando asignar: {cantidad_excesiva}")
    
    data_excesiva = {
        'id_codigo_consumidor': '1',  # ID del usuario con cédula 80833959
        'password': 'M4r14l4r@',
        'fecha': datetime.now().strftime('%Y-%m-%d'),  # Fecha actual
        'silicona': str(cantidad_excesiva),
        'grapas_negras': '0',
        'grapas_blancas': '0',
        'amarres_negros': '0',
        'amarres_blancos': '0',
        'cinta_aislante': '0'
    }
    
    try:
        response = session.post(f"{BASE_URL}/logistica/registrar_ferretero", data=data_excesiva)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Text: {response.text}")
        
        try:
            response_json = response.json()
            print(f"Response JSON: {response_json}")
        except ValueError as json_error:
            print(f"❌ Error parsing JSON: {json_error}")
        
        if response.status_code == 400 or response.status_code == 422:
            print("✅ ASIGNACIÓN EXCESIVA CORRECTAMENTE RECHAZADA")
        else:
            print("❌ ASIGNACIÓN EXCESIVA FUE PERMITIDA (PROBLEMA)")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. ¿Está corriendo la aplicación Flask?")
    except Exception as e:
        print(f"❌ Error en la petición: {e}")

if __name__ == "__main__":
    # Autenticarse primero
    if not login():
        print("❌ No se pudo autenticar. Terminando prueba.")
        exit(1)
    
    test_endpoint()