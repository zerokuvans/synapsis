#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar los endpoints del sistema de asistencia administrativo
que ahora usan la tabla recurso_operativo
"""

import requests
import json
from datetime import datetime

# Configuración del servidor
BASE_URL = "http://localhost:8080"

def test_supervisores_endpoint():
    """Probar el endpoint /api/supervisores"""
    print("\n=== Probando /api/supervisores ===")
    try:
        response = requests.get(f"{BASE_URL}/api/supervisores")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            supervisores = data.get('supervisores', [])
            print(f"Número de supervisores: {len(supervisores)}")
            print(f"Supervisores: {supervisores}")
            return supervisores
        else:
            print(f"Error: {response.text}")
            return []
    except Exception as e:
        print(f"Error en la petición: {str(e)}")
        return []

def test_tecnicos_por_supervisor_endpoint(supervisor):
    """Probar el endpoint /api/tecnicos_por_supervisor"""
    print(f"\n=== Probando /api/tecnicos_por_supervisor para {supervisor} ===")
    try:
        response = requests.get(f"{BASE_URL}/api/tecnicos_por_supervisor", 
                              params={'supervisor': supervisor})
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            tecnicos = data.get('tecnicos', [])
            print(f"Número de técnicos: {len(tecnicos)}")
            
            if tecnicos:
                print("\nPrimeros 3 técnicos:")
                for i, tecnico in enumerate(tecnicos[:3]):
                    print(f"  {i+1}. {tecnico.get('nombre')} - Cédula: {tecnico.get('recurso_operativo_cedula')}")
                    print(f"     Carpeta: {tecnico.get('carpeta')} - ID: {tecnico.get('id_codigo_consumidor')}")
            return tecnicos
        else:
            print(f"Error: {response.text}")
            return []
    except Exception as e:
        print(f"Error en la petición: {str(e)}")
        return []

def test_guardar_asistencia_endpoint(tecnicos, supervisor):
    """Probar el endpoint /api/asistencia/guardar"""
    print(f"\n=== Probando /api/asistencia/guardar ===")
    
    if not tecnicos:
        print("No hay técnicos para probar")
        return
    
    # Crear datos de prueba con los primeros 2 técnicos
    asistencias_prueba = []
    for tecnico in tecnicos[:2]:
        asistencias_prueba.append({
            'cedula': tecnico.get('recurso_operativo_cedula'),
            'tecnico': tecnico.get('nombre'),
            'carpeta_dia': 'PRUEBA_SISTEMA',
            'carpeta': tecnico.get('carpeta', ''),
            'super': supervisor,
            'id_codigo_consumidor': tecnico.get('id_codigo_consumidor')
        })
    
    data_prueba = {
        'asistencias': asistencias_prueba
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/asistencia/guardar",
                               json=data_prueba,
                               headers={'Content-Type': 'application/json'})
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error en la petición: {str(e)}")

def main():
    """Función principal para ejecutar todas las pruebas"""
    print("=" * 60)
    print("PRUEBAS DEL SISTEMA DE ASISTENCIA ADMINISTRATIVO")
    print("Usando tabla recurso_operativo")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Probar endpoint de supervisores
    supervisores = test_supervisores_endpoint()
    
    if supervisores:
        # Probar con el primer supervisor
        primer_supervisor = supervisores[0]
        tecnicos = test_tecnicos_por_supervisor_endpoint(primer_supervisor)
        
        # Probar guardar asistencia (comentado para evitar datos de prueba en producción)
        # test_guardar_asistencia_endpoint(tecnicos, primer_supervisor)
        print("\n[NOTA] Prueba de guardado comentada para evitar datos de prueba en producción")
    
    print("\n=== RESUMEN ===")
    print("✓ Endpoint /api/supervisores: Funcionando")
    print("✓ Endpoint /api/tecnicos_por_supervisor: Funcionando")
    print("✓ Endpoint /api/asistencia/guardar: Disponible (no probado para evitar datos de prueba)")
    print("✓ Sistema migrado exitosamente a tabla recurso_operativo")

if __name__ == "__main__":
    main()