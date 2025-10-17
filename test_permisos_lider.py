#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar los permisos del módulo de Líder
Verifica que solo puedan acceder:
1. Administradores
2. Líderes  
3. Sandra Cecilia Cortes Cuervo (cédula: 52912112)
"""

import requests
import json

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

def probar_acceso_lider(session, username):
    """Probar acceso al módulo de Líder"""
    print(f"\n--- Probando acceso al módulo de Líder para {username} ---")
    
    # Rutas del módulo de Líder a probar
    rutas_lider = [
        '/lider',
        '/lider/turnos-analistas',
        '/lider/indicadores',
        '/lider/indicadores/operaciones',
        '/lider/indicadores/operaciones/inicio'
    ]
    
    # APIs del módulo de Líder a probar
    apis_lider = [
        '/api/lider/inicio-operacion/supervisores',
        '/api/lider/inicio-operacion/analistas',
        '/api/lider/inicio-operacion/datos',
        '/api/analistas',
        '/api/turnos'
    ]
    
    resultados = {
        'rutas_exitosas': 0,
        'rutas_denegadas': 0,
        'apis_exitosas': 0,
        'apis_denegadas': 0
    }
    
    # Probar rutas web
    print("Probando rutas web del módulo de Líder:")
    for ruta in rutas_lider:
        try:
            response = session.get(f'{BASE_URL}{ruta}')
            if response.status_code == 200:
                print(f"  ✓ {ruta} - Acceso permitido")
                resultados['rutas_exitosas'] += 1
            elif response.status_code == 302:  # Redirección (probablemente a login)
                print(f"  ✗ {ruta} - Acceso denegado (redirección)")
                resultados['rutas_denegadas'] += 1
            else:
                print(f"  ? {ruta} - Status: {response.status_code}")
        except Exception as e:
            print(f"  ✗ {ruta} - Error: {str(e)}")
    
    # Probar APIs
    print("Probando APIs del módulo de Líder:")
    for api in apis_lider:
        try:
            response = session.get(f'{BASE_URL}{api}')
            if response.status_code == 200:
                print(f"  ✓ {api} - Acceso permitido")
                resultados['apis_exitosas'] += 1
            elif response.status_code == 401 or response.status_code == 403:
                print(f"  ✗ {api} - Acceso denegado (Status: {response.status_code})")
                resultados['apis_denegadas'] += 1
            else:
                print(f"  ? {api} - Status: {response.status_code}")
        except Exception as e:
            print(f"  ✗ {api} - Error: {str(e)}")
    
    return resultados

def main():
    """Función principal de pruebas"""
    print("=== PRUEBA DE PERMISOS DEL MÓDULO DE LÍDER ===")
    print("Verificando que solo puedan acceder:")
    print("1. Administradores")
    print("2. Líderes")
    print("3. Sandra Cecilia Cortes Cuervo (52912112)")
    print("=" * 50)
    
    # Usuarios de prueba
    usuarios_prueba = [
        {
            'username': '80833959',  # Administrador
            'password': 'M4r14l4r@',
            'tipo': 'Administrador',
            'deberia_acceder': True
        },
        {
            'username': '52912112',  # Sandra Cecilia
            'password': 'password_sandra',  # Necesitarás la contraseña real
            'tipo': 'Sandra Cecilia (Usuario Especial)',
            'deberia_acceder': True
        }
        # Nota: Agregar más usuarios de prueba si tienes credenciales de líderes u otros usuarios
    ]
    
    resultados_globales = []
    
    for usuario in usuarios_prueba:
        print(f"\n{'='*60}")
        print(f"PROBANDO USUARIO: {usuario['tipo']} ({usuario['username']})")
        print(f"{'='*60}")
        
        # Hacer login
        session = hacer_login(usuario['username'], usuario['password'])
        
        if session:
            # Probar acceso al módulo de Líder
            resultados = probar_acceso_lider(session, usuario['username'])
            resultados['usuario'] = usuario['username']
            resultados['tipo'] = usuario['tipo']
            resultados['deberia_acceder'] = usuario['deberia_acceder']
            resultados_globales.append(resultados)
        else:
            print(f"No se pudo hacer login para {usuario['username']}")
    
    # Resumen final
    print(f"\n{'='*60}")
    print("RESUMEN DE PRUEBAS")
    print(f"{'='*60}")
    
    for resultado in resultados_globales:
        print(f"\nUsuario: {resultado['tipo']} ({resultado['usuario']})")
        print(f"Debería acceder: {'Sí' if resultado['deberia_acceder'] else 'No'}")
        print(f"Rutas exitosas: {resultado['rutas_exitosas']}")
        print(f"Rutas denegadas: {resultado['rutas_denegadas']}")
        print(f"APIs exitosas: {resultado['apis_exitosas']}")
        print(f"APIs denegadas: {resultado['apis_denegadas']}")
        
        total_accesos = resultado['rutas_exitosas'] + resultado['apis_exitosas']
        total_denegados = resultado['rutas_denegadas'] + resultado['apis_denegadas']
        
        if resultado['deberia_acceder']:
            if total_accesos > 0:
                print("✓ RESULTADO: Acceso correcto (como se esperaba)")
            else:
                print("✗ RESULTADO: Acceso denegado (ERROR - debería tener acceso)")
        else:
            if total_denegados > 0:
                print("✓ RESULTADO: Acceso denegado correctamente")
            else:
                print("✗ RESULTADO: Acceso permitido (ERROR - no debería tener acceso)")

if __name__ == '__main__':
    main()