#!/usr/bin/env python3
"""
Script para verificar el contenido específico de la página de login
"""

import requests

BASE_URL = "http://127.0.0.1:8080"

def main():
    """Función principal"""
    print("🔍 VERIFICANDO CONTENIDO DE LA PÁGINA DE LOGIN")
    print("=" * 60)
    
    try:
        # Verificar página de login
        response = requests.get(f"{BASE_URL}/login", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        print(f"Tamaño: {len(response.text)} caracteres")
        
        # Mostrar las primeras líneas del contenido
        lines = response.text.split('\n')[:20]
        print("\n📄 PRIMERAS 20 LÍNEAS DEL CONTENIDO:")
        print("-" * 40)
        for i, line in enumerate(lines, 1):
            print(f"{i:2d}: {line[:80]}")
        
        # Buscar elementos clave
        content = response.text.lower()
        
        print("\n🔍 ELEMENTOS CLAVE ENCONTRADOS:")
        print("-" * 40)
        
        elements_to_check = [
            ("<!doctype html", "Declaración DOCTYPE"),
            ("<html", "Etiqueta HTML"),
            ("<head", "Sección HEAD"),
            ("<body", "Sección BODY"),
            ("login", "Texto 'login'"),
            ("form", "Formulario"),
            ("input", "Campos de entrada"),
            ("button", "Botones"),
            ("usuario", "Campo usuario"),
            ("contraseña", "Campo contraseña"),
            ("password", "Campo password"),
            ("synapsis", "Nombre de la aplicación"),
            ("css", "Estilos CSS"),
            ("javascript", "JavaScript")
        ]
        
        for element, description in elements_to_check:
            found = element in content
            icon = "✅" if found else "❌"
            print(f"{icon} {description}")
        
        # Verificar si es una página de error
        if "error" in content or "404" in content or "500" in content:
            print("\n⚠️  POSIBLE PÁGINA DE ERROR DETECTADA")
        
        # Verificar si hay contenido mínimo esperado
        if len(response.text) < 1000:
            print("\n⚠️  CONTENIDO MUY PEQUEÑO - POSIBLE PROBLEMA")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()