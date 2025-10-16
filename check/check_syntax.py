#!/usr/bin/env python3
"""
Script para verificar errores de sintaxis en app.py
"""

import ast
import sys

def check_syntax(filename):
    """Verificar sintaxis de un archivo Python"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Intentar compilar el código
        ast.parse(content)
        print(f"✅ {filename}: Sintaxis correcta")
        return True
        
    except SyntaxError as e:
        print(f"❌ {filename}: Error de sintaxis")
        print(f"   Línea {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ {filename}: Error al leer archivo: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verificando sintaxis de app.py...")
    check_syntax("app.py")