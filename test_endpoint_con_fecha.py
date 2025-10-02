#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

# Configuración del servidor
BASE_URL = "http://192.168.80.39:8080"
LOGIN_URL = f"{BASE_URL}/"  # La ruta de login es la raíz
API_URL = f"{BASE_URL}/api/analistas/tecnicos-asignados"

# Credenciales de la analista ESPITIA BARON LICED JOANA
USERNAME = "1002407090"  # Cédula de la analista
PASSWORD = "CE1002407090"  # Contraseña correcta

def test_endpoint_with_date():
    """Probar el endpoint con fecha específica donde tenemos datos"""
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        print("=== PROBANDO ENDPOINT CON FECHA ESPECÍFICA ===")
        print(f"URL: {API_URL}")
        print(f"Usuario: {USERNAME}")
        print(f"Fecha de prueba: 2025-10-02")
        print()
        
        # 1. Hacer login
        print("1. Realizando login...")
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        login_response = session.post(LOGIN_URL, data=login_data)
        
        if login_response.status_code == 200:
            print("✓ Login exitoso")
        else:
            print(f"✗ Error en login: {login_response.status_code}")
            return
        
        # 2. Probar endpoint sin fecha (fecha actual del servidor)
        print("\n2. Probando endpoint sin parámetro de fecha (fecha actual del servidor)...")
        response_sin_fecha = session.get(API_URL)
        
        if response_sin_fecha.status_code == 200:
            data_sin_fecha = response_sin_fecha.json()
            
            # Verificar si la respuesta es una lista o un diccionario
            if isinstance(data_sin_fecha, dict) and 'tecnicos' in data_sin_fecha:
                tecnicos = data_sin_fecha['tecnicos']
            elif isinstance(data_sin_fecha, list):
                tecnicos = data_sin_fecha
            else:
                print(f"Formato de respuesta inesperado: {type(data_sin_fecha)}")
                print(f"Contenido: {data_sin_fecha}")
                return
            
            print(f"✓ Respuesta exitosa - {len(tecnicos)} técnicos encontrados")
            
            # Contar técnicos con y sin datos de asistencia
            con_datos = 0
            sin_datos = 0
            
            for tecnico in tecnicos:
                if tecnico.get('asistencia_hoy') and tecnico['asistencia_hoy'].get('hora_inicio'):
                    con_datos += 1
                    print(f"  - {tecnico['nombre']} ({tecnico['cedula']}): CON DATOS")
                    print(f"    Hora: {tecnico['asistencia_hoy'].get('hora_inicio')}")
                    print(f"    Estado: {tecnico['asistencia_hoy'].get('estado')}")
                    print(f"    Novedad: {tecnico['asistencia_hoy'].get('novedad')}")
                else:
                    sin_datos += 1
                    print(f"  - {tecnico['nombre']} ({tecnico['cedula']}): Sin datos de asistencia para hoy")
            
            print(f"\nResumen sin fecha: {con_datos} con datos, {sin_datos} sin datos")
        else:
            print(f"✗ Error en endpoint sin fecha: {response_sin_fecha.status_code}")
        
        # 3. Probar endpoint con fecha específica (2025-10-02)
        print("\n3. Probando endpoint con fecha específica (2025-10-02)...")
        params = {'fecha': '2025-10-02'}
        response_con_fecha = session.get(API_URL, params=params)
        
        if response_con_fecha.status_code == 200:
            data_con_fecha = response_con_fecha.json()
            
            # Verificar si la respuesta es una lista o un diccionario
            if isinstance(data_con_fecha, dict) and 'tecnicos' in data_con_fecha:
                tecnicos = data_con_fecha['tecnicos']
            elif isinstance(data_con_fecha, list):
                tecnicos = data_con_fecha
            else:
                print(f"Formato de respuesta inesperado: {type(data_con_fecha)}")
                print(f"Contenido: {data_con_fecha}")
                return
            
            print(f"✓ Respuesta exitosa - {len(tecnicos)} técnicos encontrados")
            
            # Contar técnicos con y sin datos de asistencia
            con_datos = 0
            sin_datos = 0
            
            for tecnico in tecnicos:
                if tecnico.get('asistencia_hoy') and tecnico['asistencia_hoy'].get('hora_inicio'):
                    con_datos += 1
                    print(f"  - {tecnico['nombre']} ({tecnico['cedula']}): CON DATOS")
                    print(f"    Hora: {tecnico['asistencia_hoy'].get('hora_inicio')}")
                    print(f"    Estado: {tecnico['asistencia_hoy'].get('estado')}")
                    print(f"    Novedad: {tecnico['asistencia_hoy'].get('novedad')}")
                else:
                    sin_datos += 1
                    print(f"  - {tecnico['nombre']} ({tecnico['cedula']}): Sin datos de asistencia para esta fecha")
            
            print(f"\nResumen con fecha 2025-10-02: {con_datos} con datos, {sin_datos} sin datos")
        else:
            print(f"✗ Error en endpoint con fecha: {response_con_fecha.status_code}")
        
        print("\n=== PRUEBA COMPLETADA ===")
        
    except Exception as e:
        print(f"Error durante la prueba: {e}")

if __name__ == "__main__":
    test_endpoint_with_date()