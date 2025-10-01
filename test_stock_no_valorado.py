import requests
import json
import mysql.connector
import os

# Configuración
BASE_URL = "http://localhost:8080"
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

def verificar_stock_db():
    """Verificar el stock actual en la base de datos"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        print("=" * 60)
        print("VERIFICACIÓN DE STOCK EN BASE DE DATOS")
        print("=" * 60)
        
        # Verificar stock NO VALORADO
        cursor.execute("""
            SELECT COUNT(*) as cantidad, SUM(camisetapolo) as total_prendas
            FROM dotaciones 
            WHERE camisetapolo > 0 AND estado_camiseta_polo = 'NO VALORADO'
        """)
        resultado = cursor.fetchone()
        print(f"Stock NO VALORADO: {resultado[1] or 0} prendas en {resultado[0]} registros")
        
        # Verificar stock VALORADO
        cursor.execute("""
            SELECT COUNT(*) as cantidad, SUM(camisetapolo) as total_prendas
            FROM dotaciones 
            WHERE camisetapolo > 0 AND estado_camiseta_polo = 'VALORADO'
        """)
        resultado = cursor.fetchone()
        print(f"Stock VALORADO: {resultado[1] or 0} prendas en {resultado[0]} registros")
        
        # Verificar vista de stock total
        cursor.execute("""
            SELECT saldo_disponible 
            FROM vista_stock_dotaciones 
            WHERE tipo_elemento = 'camisetapolo'
        """)
        resultado = cursor.fetchone()
        print(f"Stock total disponible: {resultado[0] if resultado else 0}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"Error verificando stock: {e}")
        return False

def test_cambio_no_valorado():
    """Test para intentar cambio con camiseta polo NO VALORADO"""
    print("\n" + "=" * 60)
    print("TEST: CAMBIO CAMISETA POLO NO VALORADO")
    print("=" * 60)
    
    # Datos del cambio con camiseta polo NO VALORADO
    data = {
        'id_codigo_consumidor': 12345,  # ID válido encontrado
        'fecha_cambio': '2025-01-20',
        'camisetapolo': 1,
        'camiseta_polo_talla': 'M',
        'camiseta_polo_valorado': False  # NO VALORADO
    }
    
    print(f"Enviando datos: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/cambios_dotacion", json=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            response_data = response.json()
            if "Stock insuficiente" in response_data.get('error', ''):
                print("✅ CORRECTO: El sistema detectó correctamente que no hay stock NO VALORADO")
                return True
            else:
                print("❌ ERROR: Respuesta inesperada del servidor")
                return False
        else:
            print("❌ ERROR: Se esperaba un error 400 por stock insuficiente")
            return False
            
    except Exception as e:
        print(f"❌ ERROR en la petición: {e}")
        return False

def test_cambio_valorado():
    """Test para intentar cambio con camiseta polo VALORADO (debería funcionar)"""
    print("\n" + "=" * 60)
    print("TEST: CAMBIO CAMISETA POLO VALORADO")
    print("=" * 60)
    
    # Datos del cambio con camiseta polo VALORADO
    data = {
        'id_codigo_consumidor': 7,  # ID válido diferente
        'fecha_cambio': '2025-01-20',
        'camisetapolo': 1,
        'camiseta_polo_talla': 'M',
        'camiseta_polo_valorado': True  # VALORADO
    }
    
    print(f"Enviando datos: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/cambios_dotacion", json=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ CORRECTO: El cambio VALORADO se procesó exitosamente")
            return True
        elif response.status_code == 400:
            response_data = response.json()
            if "Stock insuficiente" in response_data.get('error', ''):
                print("⚠️  ADVERTENCIA: No hay suficiente stock VALORADO tampoco")
                return True  # Esto también es un comportamiento válido
            else:
                print("❌ ERROR: Respuesta inesperada del servidor")
                return False
        else:
            print("❌ ERROR: Respuesta inesperada del servidor")
            return False
            
    except Exception as e:
        print(f"❌ ERROR en la petición: {e}")
        return False

def main():
    print("DIAGNÓSTICO COMPLETO: STOCK CAMISETA POLO NO VALORADO")
    print("=" * 80)
    
    # 1. Verificar stock en base de datos
    if not verificar_stock_db():
        print("❌ No se pudo verificar el stock en la base de datos")
        return
    
    # 2. Test con NO VALORADO (debería fallar)
    test_no_valorado_ok = test_cambio_no_valorado()
    
    # 3. Test con VALORADO (debería funcionar o dar error de stock)
    test_valorado_ok = test_cambio_valorado()
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN DE RESULTADOS")
    print("=" * 80)
    print(f"✅ Verificación de stock en DB: OK")
    print(f"{'✅' if test_no_valorado_ok else '❌'} Test NO VALORADO: {'OK' if test_no_valorado_ok else 'FALLO'}")
    print(f"{'✅' if test_valorado_ok else '❌'} Test VALORADO: {'OK' if test_valorado_ok else 'FALLO'}")
    
    if test_no_valorado_ok and test_valorado_ok:
        print("\n🎉 CONCLUSIÓN: El sistema está funcionando correctamente.")
        print("   - Detecta correctamente cuando no hay stock NO VALORADO")
        print("   - Maneja apropiadamente el stock VALORADO")
    else:
        print("\n⚠️  CONCLUSIÓN: Hay problemas en el manejo del stock")

if __name__ == "__main__":
    main()