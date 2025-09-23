#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de pruebas para las APIs del Sistema de Gestión de Estados de Devoluciones
Este script valida el funcionamiento de todas las APIs implementadas
"""

import requests
import json
import sys
from datetime import datetime

# Configuración del servidor
BASE_URL = 'http://localhost:8080'
API_BASE = f'{BASE_URL}/api'

# Credenciales de prueba (ajustar según sea necesario)
TEST_USER = {
    'username': 'admin',  # Ajustar según usuario de prueba
    'password': 'admin123'  # Ajustar según contraseña de prueba
}

class TestEstadoAPIs:
    def __init__(self):
        self.session = requests.Session()
        self.test_devolucion_id = None
        self.resultados = []
        
    def log_resultado(self, test_name, success, message, details=None):
        """Registra el resultado de una prueba"""
        resultado = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.resultados.append(resultado)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
        if details and not success:
            print(f"   Detalles: {details}")
    
    def login(self):
        """Realiza login para obtener sesión autenticada"""
        try:
            login_url = f'{BASE_URL}/login'
            response = self.session.post(login_url, data=TEST_USER)
            
            if response.status_code == 200:
                self.log_resultado(
                    "Login", 
                    True, 
                    "Login exitoso"
                )
                return True
            else:
                self.log_resultado(
                    "Login", 
                    False, 
                    f"Error en login: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_resultado(
                "Login", 
                False, 
                f"Excepción en login: {str(e)}"
            )
            return False
    
    def obtener_devolucion_prueba(self):
        """Obtiene una devolución existente para pruebas"""
        try:
            url = f'{API_BASE}/devoluciones'
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('devoluciones'):
                    self.test_devolucion_id = data['devoluciones'][0]['id']
                    self.log_resultado(
                        "Obtener devolución de prueba", 
                        True, 
                        f"Devolución ID: {self.test_devolucion_id}"
                    )
                    return True
                else:
                    self.log_resultado(
                        "Obtener devolución de prueba", 
                        False, 
                        "No hay devoluciones disponibles para prueba"
                    )
                    return False
            else:
                self.log_resultado(
                    "Obtener devolución de prueba", 
                    False, 
                    f"Error al obtener devoluciones: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_resultado(
                "Obtener devolución de prueba", 
                False, 
                f"Excepción: {str(e)}"
            )
            return False
    
    def test_obtener_transiciones(self):
        """Prueba la API GET /api/devoluciones/{id}/transiciones"""
        try:
            url = f'{API_BASE}/devoluciones/{self.test_devolucion_id}/transiciones'
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_resultado(
                        "GET Transiciones", 
                        True, 
                        f"Estado actual: {data.get('estado_actual')}, Transiciones: {len(data.get('transiciones_validas', []))}",
                        data
                    )
                    return data
                else:
                    self.log_resultado(
                        "GET Transiciones", 
                        False, 
                        "Respuesta sin éxito",
                        data
                    )
            else:
                self.log_resultado(
                    "GET Transiciones", 
                    False, 
                    f"Error HTTP: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_resultado(
                "GET Transiciones", 
                False, 
                f"Excepción: {str(e)}"
            )
        
        return None
    
    def test_obtener_historial(self):
        """Prueba la API GET /api/devoluciones/{id}/historial"""
        try:
            url = f'{API_BASE}/devoluciones/{self.test_devolucion_id}/historial'
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_resultado(
                        "GET Historial", 
                        True, 
                        f"Total cambios: {data.get('total_cambios', 0)}",
                        data
                    )
                    return data
                else:
                    self.log_resultado(
                        "GET Historial", 
                        False, 
                        "Respuesta sin éxito",
                        data
                    )
            else:
                self.log_resultado(
                    "GET Historial", 
                    False, 
                    f"Error HTTP: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_resultado(
                "GET Historial", 
                False, 
                f"Excepción: {str(e)}"
            )
        
        return None
    
    def test_validar_transicion(self):
        """Prueba la API POST /api/estados/validar-transicion"""
        try:
            url = f'{API_BASE}/estados/validar-transicion'
            
            # Prueba con transición válida
            test_data = {
                'estado_actual': 'REGISTRADA',
                'estado_nuevo': 'PROCESANDO'
            }
            
            response = self.session.post(
                url, 
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    validacion = data.get('validacion', {})
                    self.log_resultado(
                        "POST Validar Transición", 
                        True, 
                        f"Transición válida: {validacion.get('valida')}",
                        data
                    )
                    return data
                else:
                    self.log_resultado(
                        "POST Validar Transición", 
                        False, 
                        "Respuesta sin éxito",
                        data
                    )
            else:
                self.log_resultado(
                    "POST Validar Transición", 
                    False, 
                    f"Error HTTP: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_resultado(
                "POST Validar Transición", 
                False, 
                f"Excepción: {str(e)}"
            )
        
        return None
    
    def test_actualizar_estado(self, transiciones_data=None):
        """Prueba la API PUT /api/devoluciones/{id}/estado"""
        try:
            url = f'{API_BASE}/devoluciones/{self.test_devolucion_id}/estado'
            
            # Determinar un estado válido para la transición
            nuevo_estado = 'PROCESANDO'  # Estado por defecto
            
            if transiciones_data and transiciones_data.get('transiciones_validas'):
                transiciones = transiciones_data['transiciones_validas']
                if transiciones:
                    nuevo_estado = transiciones[0]['estado_destino']
            
            test_data = {
                'nuevo_estado': nuevo_estado,
                'motivo': 'Prueba automatizada del sistema de gestión de estados'
            }
            
            response = self.session.put(
                url, 
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_resultado(
                        "PUT Actualizar Estado", 
                        True, 
                        f"Estado actualizado a: {data.get('estado_nuevo')}",
                        data
                    )
                    return data
                else:
                    self.log_resultado(
                        "PUT Actualizar Estado", 
                        False, 
                        f"Error: {data.get('error')}",
                        data
                    )
            else:
                self.log_resultado(
                    "PUT Actualizar Estado", 
                    False, 
                    f"Error HTTP: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_resultado(
                "PUT Actualizar Estado", 
                False, 
                f"Excepción: {str(e)}"
            )
        
        return None
    
    def test_casos_error(self):
        """Prueba casos de error y validaciones"""
        # Prueba con ID de devolución inexistente
        try:
            url = f'{API_BASE}/devoluciones/99999/estado'
            test_data = {
                'nuevo_estado': 'PROCESANDO',
                'motivo': 'Prueba con ID inexistente'
            }
            
            response = self.session.put(
                url, 
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 404:
                self.log_resultado(
                    "Error ID inexistente", 
                    True, 
                    "Correctamente devuelve 404 para ID inexistente"
                )
            else:
                self.log_resultado(
                    "Error ID inexistente", 
                    False, 
                    f"Debería devolver 404, pero devolvió: {response.status_code}"
                )
                
        except Exception as e:
            self.log_resultado(
                "Error ID inexistente", 
                False, 
                f"Excepción: {str(e)}"
            )
        
        # Prueba con datos faltantes
        try:
            url = f'{API_BASE}/devoluciones/{self.test_devolucion_id}/estado'
            test_data = {
                'nuevo_estado': 'PROCESANDO'
                # Falta el motivo
            }
            
            response = self.session.put(
                url, 
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 400:
                self.log_resultado(
                    "Error datos faltantes", 
                    True, 
                    "Correctamente valida datos obligatorios"
                )
            else:
                self.log_resultado(
                    "Error datos faltantes", 
                    False, 
                    f"Debería devolver 400, pero devolvió: {response.status_code}"
                )
                
        except Exception as e:
            self.log_resultado(
                "Error datos faltantes", 
                False, 
                f"Excepción: {str(e)}"
            )
    
    def generar_reporte(self):
        """Genera un reporte final de las pruebas"""
        total_tests = len(self.resultados)
        tests_exitosos = len([r for r in self.resultados if r['success']])
        tests_fallidos = total_tests - tests_exitosos
        
        print("\n" + "="*60)
        print("REPORTE FINAL DE PRUEBAS")
        print("="*60)
        print(f"Total de pruebas: {total_tests}")
        print(f"Pruebas exitosas: {tests_exitosos}")
        print(f"Pruebas fallidas: {tests_fallidos}")
        print(f"Porcentaje de éxito: {(tests_exitosos/total_tests)*100:.1f}%")
        
        if tests_fallidos > 0:
            print("\nPRUEBAS FALLIDAS:")
            for resultado in self.resultados:
                if not resultado['success']:
                    print(f"- {resultado['test']}: {resultado['message']}")
        
        # Guardar reporte en archivo
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total': total_tests,
                    'passed': tests_exitosos,
                    'failed': tests_fallidos,
                    'success_rate': (tests_exitosos/total_tests)*100
                },
                'results': self.resultados
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\nReporte detallado guardado en: test_results.json")
        
        return tests_fallidos == 0
    
    def ejecutar_todas_las_pruebas(self):
        """Ejecuta todas las pruebas en secuencia"""
        print("Iniciando pruebas del Sistema de Gestión de Estados...\n")
        
        # 1. Login
        if not self.login():
            print("❌ No se pudo realizar login. Abortando pruebas.")
            return False
        
        # 2. Obtener devolución de prueba
        if not self.obtener_devolucion_prueba():
            print("❌ No se pudo obtener devolución de prueba. Abortando pruebas.")
            return False
        
        # 3. Pruebas de APIs
        transiciones_data = self.test_obtener_transiciones()
        self.test_obtener_historial()
        self.test_validar_transicion()
        
        # 4. Prueba de actualización de estado (solo si hay transiciones válidas)
        if transiciones_data and transiciones_data.get('transiciones_validas'):
            self.test_actualizar_estado(transiciones_data)
            # Verificar historial después del cambio
            self.test_obtener_historial()
        
        # 5. Pruebas de casos de error
        self.test_casos_error()
        
        # 6. Generar reporte
        return self.generar_reporte()

def main():
    """Función principal"""
    print("Sistema de Pruebas - APIs de Gestión de Estados de Devoluciones")
    print("================================================================\n")
    
    # Verificar que el servidor esté disponible
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Servidor disponible en {BASE_URL}\n")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: No se puede conectar al servidor en {BASE_URL}")
        print(f"   Asegúrate de que el servidor Flask esté ejecutándose.")
        print(f"   Error: {str(e)}")
        return False
    
    # Ejecutar pruebas
    tester = TestEstadoAPIs()
    success = tester.ejecutar_todas_las_pruebas()
    
    if success:
        print("\n🎉 Todas las pruebas pasaron exitosamente!")
        return True
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa el reporte para más detalles.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)