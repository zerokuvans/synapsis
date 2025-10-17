#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que Sandra Cecilia (52912112) 
pueda ver el menú de Líder en la navegación
"""

import requests
from bs4 import BeautifulSoup

# Configuración del servidor
BASE_URL = 'http://127.0.0.1:8080'

def hacer_login(username, password):
    """Función para hacer login y obtener la sesión"""
    session = requests.Session()
    
    # Hacer login
    login_data = {
        'username': username,
        'password': password
    }
    
    response = session.post(f'{BASE_URL}/login', data=login_data)
    
    if response.status_code == 200 and 'dashboard' in response.url:
        print(f"✓ Login exitoso para usuario: {username}")
        return session
    else:
        print(f"✗ Error en login para usuario: {username} - Status: {response.status_code}")
        return None

def verificar_menu_lider(session, username):
    """Verificar si el menú de Líder está visible"""
    print(f"\n--- Verificando menú de Líder para usuario {username} ---")
    
    try:
        # Obtener la página del dashboard
        response = session.get(f'{BASE_URL}/dashboard')
        
        if response.status_code != 200:
            print(f"✗ Error al acceder al dashboard: {response.status_code}")
            return False
        
        # Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar el enlace del menú de Líder
        lider_link = soup.find('a', {'href': '/lider'})
        
        if lider_link:
            print("✓ Menú de Líder encontrado en la navegación")
            print(f"  Texto del enlace: {lider_link.get_text().strip()}")
            return True
        else:
            print("✗ Menú de Líder NO encontrado en la navegación")
            
            # Buscar todos los enlaces de navegación para debug
            nav_links = soup.find_all('a', class_='nav-link')
            print("Enlaces de navegación encontrados:")
            for link in nav_links:
                print(f"  - {link.get_text().strip()} -> {link.get('href', 'N/A')}")
            
            return False
            
    except Exception as e:
        print(f"✗ Error al verificar el menú: {str(e)}")
        return False

def probar_acceso_lider(session, username):
    """Probar acceso directo al módulo de Líder"""
    print(f"\n--- Probando acceso directo al módulo de Líder para {username} ---")
    
    try:
        response = session.get(f'{BASE_URL}/lider')
        
        if response.status_code == 200:
            print("✓ Acceso directo al módulo de Líder exitoso")
            return True
        elif response.status_code == 302:
            print("✗ Acceso denegado - Redirección (probablemente a login)")
            return False
        else:
            print(f"? Respuesta inesperada: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error al probar acceso directo: {str(e)}")
        return False

def main():
    """Función principal de pruebas"""
    print("=== PRUEBA DE MENÚ DE LÍDER PARA SANDRA CECILIA ===")
    print("Verificando que el usuario 52912112 pueda ver el menú de Líder")
    print("=" * 60)
    
    # Credenciales de Sandra Cecilia
    # Nota: Necesitarás proporcionar la contraseña real
    username = '52912112'
    password = 'password_sandra'  # Cambiar por la contraseña real
    
    print(f"Intentando login con usuario: {username}")
    
    # Hacer login
    session = hacer_login(username, password)
    
    if session:
        # Verificar menú
        menu_visible = verificar_menu_lider(session, username)
        
        # Probar acceso directo
        acceso_directo = probar_acceso_lider(session, username)
        
        # Resumen
        print(f"\n{'='*60}")
        print("RESUMEN DE PRUEBAS")
        print(f"{'='*60}")
        print(f"Usuario: {username}")
        print(f"Menú de Líder visible: {'✓ SÍ' if menu_visible else '✗ NO'}")
        print(f"Acceso directo funciona: {'✓ SÍ' if acceso_directo else '✗ NO'}")
        
        if menu_visible and acceso_directo:
            print("\n🎉 ¡ÉXITO! Sandra Cecilia puede ver y acceder al módulo de Líder")
        else:
            print("\n❌ PROBLEMA: Sandra Cecilia no puede acceder completamente al módulo de Líder")
            
    else:
        print(f"\n❌ No se pudo hacer login para el usuario {username}")
        print("Verifica que:")
        print("1. El usuario existe en la base de datos")
        print("2. La contraseña es correcta")
        print("3. El servidor está funcionando")

if __name__ == '__main__':
    main(