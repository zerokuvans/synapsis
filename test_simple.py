import requests
import json

def test_login():
    base_url = "http://localhost:8080"
    
    # Probar diferentes credenciales
    credenciales = [
        {'username': '1002407101', 'password': '123456'},
        {'username': 'test123', 'password': '123456'},
        {'username': '1002407101', 'password': '1002407101'},
        {'username': 'admin', 'password': 'admin'},
        {'username': 'logistica', 'password': 'logistica'}
    ]
    
    with open('test_results.txt', 'w', encoding='utf-8') as f:
        f.write("=== Resultados de Test de Login ===\n\n")
        
        for i, cred in enumerate(credenciales, 1):
            f.write(f"Test {i}: {cred['username']} / {cred['password']}\n")
            
            try:
                response = requests.post(f"{base_url}/", data=cred, timeout=10)
                f.write(f"Status: {response.status_code}\n")
                f.write(f"Response: {response.text[:200]}\n")
                
                if response.status_code == 200:
                    f.write("✓ LOGIN EXITOSO!\n")
                    # Probar endpoint de vencimientos
                    try:
                        venc_response = requests.get(f"{base_url}/api/vehiculos/vencimientos", 
                                                   cookies=response.cookies, timeout=10)
                        f.write(f"Vencimientos Status: {venc_response.status_code}\n")
                        f.write(f"Vencimientos Response: {venc_response.text[:200]}\n")
                    except Exception as e:
                        f.write(f"Error en vencimientos: {e}\n")
                else:
                    f.write("✗ Login fallido\n")
                    
            except Exception as e:
                f.write(f"Error: {e}\n")
                
            f.write("-" * 50 + "\n\n")
            
        f.write("=== Fin de Tests ===\n")
    
    print("Test completado. Revisa test_results.txt")

if __name__ == "__main__":
    test_login()