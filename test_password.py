#!/usr/bin/env python3
"""
Script para probar la contraseña del usuario
"""

import bcrypt

def test_password():
    # Hash de la base de datos
    stored_hash = '$2b$12$kn784qsqZVBb7YYsyzV.E.xeXHGuzZy4IvILQogFfRyEzUqHknely'
    
    # Contraseñas a probar
    passwords_to_test = [
        'CE1019112308',
        'Capired2024*',
        '1019112308',
        'ALARCON',
        'alarcon'
    ]
    
    print('=== PROBANDO CONTRASEÑAS ===')
    
    for password in passwords_to_test:
        try:
            result = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            print(f'Contraseña "{password}": {"✅ CORRECTA" if result else "❌ INCORRECTA"}')
        except Exception as e:
            print(f'Error probando "{password}": {e}')

if __name__ == "__main__":
    test_password()