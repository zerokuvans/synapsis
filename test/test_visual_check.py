#!/usr/bin/env python3
"""
Script para verificar el contenido visual de las páginas principales
"""

import requests
import re

BASE_URL = "http://127.0.0.1:8080"

def check_page_content(route, expected_elements):
    """Verifica que una página contenga los elementos esperados"""
    try:
        url = f"{BASE_URL}{route}"
        response = requests.get(url, timeout=10)
        
        if response.status_code not in [200, 302]:
            print(f"❌ {route}: Status {response.status_code}")
            return False
        
        content = response.text
        
        print(f"\n🔍 Verificando {route}:")
        print(f"   Status: {response.status_code}")
        print(f"   Tamaño del contenido: {len(content)} caracteres")
        
        # Verificar elementos esperados
        missing_elements = []
        for element in expected_elements:
            if element.lower() not in content.lower():
                missing_elements.append(element)
        
        if missing_elements:
            print(f"   ❌ Elementos faltantes: {missing_elements}")
            return False
        else:
            print(f"   ✅ Todos los elementos encontrados")
            return True
            
    except Exception as e:
        print(f"❌ Error al verificar {route}: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN VISUAL DE PÁGINAS PRINCIPALES")
    print("=" * 60)
    
    # Verificar página de login
    login_elements = [
        "login", "usuario", "contraseña", "password", "form", "input", "button"
    ]
    login_ok = check_page_content("/login", login_elements)
    
    # Verificar página principal (debería redirigir a login)
    home_ok = check_page_content("/", ["login", "redirecting"])
    
    # Verificar que el dashboard requiera autenticación
    dashboard_ok = check_page_content("/dashboard", ["login", "redirecting"])
    
    # Verificar módulo MPA
    mpa_ok = check_page_content("/mpa", ["login", "redirecting"])
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN VISUAL:")
    print("=" * 60)
    print(f"Login:     {'✅' if login_ok else '❌'}")
    print(f"Home:      {'✅' if home_ok else '❌'}")
    print(f"Dashboard: {'✅' if dashboard_ok else '❌'}")
    print(f"MPA:       {'✅' if mpa_ok else '❌'}")
    
    total_ok = sum([login_ok, home_ok, dashboard_ok, mpa_ok])
    print(f"\nTotal: {total_ok}/4 páginas funcionando correctamente")
    
    if total_ok == 4:
        print("\n🎉 ¡TODAS LAS PÁGINAS FUNCIONAN CORRECTAMENTE!")
    else:
        print("\n⚠️  ALGUNAS PÁGINAS TIENEN PROBLEMAS")

if __name__ == "__main__":
    main()