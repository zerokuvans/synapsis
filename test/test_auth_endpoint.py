#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script mejorado para probar el endpoint /api/asistencia/resumen_agrupado
con autenticación Flask-Login correcta.

Basado en el diagnóstico que mostró que el problema es autenticación (302 redirect).
"""

import requests
import json
import logging
from datetime import datetime
import sys
import urllib3
from bs4 import BeautifulSoup
import re

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_auth_endpoint.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AuthenticatedEndpointTester:
    def __init__(self, base_url="http://148.113.171.196:8080"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.verify = False
        
        # Credenciales
        self.username = "80833959"
        self.password = "M4r14l4r@"
        
        logger.info(f"Inicializando tester autenticado para: {self.base_url}")

    def login(self):
        """Realizar login completo con Flask-Login"""
        logger.info("=== INICIANDO PROCESO DE LOGIN ===")
        
        try:
            # 1. Obtener la página de login
            login_url = f"{self.base_url}/"
            logger.info(f"Obteniendo página de login: {login_url}")
            
            response = self.session.get(login_url, timeout=30)
            logger.info(f"Página de login obtenida - Status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"No se pudo obtener la página de login: {response.status_code}")
                return False
            
            # 2. Extraer CSRF token si existe
            csrf_token = None
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                csrf_input = soup.find('input', {'name': 'csrf_token'})
                if csrf_input:
                    csrf_token = csrf_input.get('value')
                    logger.info("CSRF token encontrado")
                else:
                    logger.info("No se encontró CSRF token")
            except Exception as e:
                logger.warning(f"Error al buscar CSRF token: {e}")
            
            # 3. Preparar datos de login
            login_data = {
                'username': self.username,
                'password': self.password
            }
            
            if csrf_token:
                login_data['csrf_token'] = csrf_token
            
            # 4. Realizar POST de login
            logger.info("Enviando credenciales de login...")
            login_response = self.session.post(
                login_url,
                data=login_data,
                timeout=30,
                allow_redirects=True  # Permitir redirecciones automáticas
            )
            
            logger.info(f"Respuesta de login - Status: {login_response.status_code}")
            logger.info(f"URL final después de login: {login_response.url}")
            
            # 5. Verificar si el login fue exitoso
            if login_response.status_code == 200:
                # Buscar indicadores de login exitoso
                content = login_response.text.lower()
                success_indicators = [
                    'dashboard', 'administrativo', 'logout', 'cerrar sesión',
                    'bienvenido', 'menu', 'sidebar'
                ]
                
                login_success = any(indicator in content for indicator in success_indicators)
                
                if login_success:
                    logger.info("✓ LOGIN EXITOSO - Indicadores de dashboard detectados")
                    return True
                else:
                    logger.warning("Login posiblemente fallido - No se detectaron indicadores de éxito")
                    # Verificar si hay mensajes de error
                    if 'error' in content or 'incorrecto' in content or 'invalid' in content:
                        logger.error("Mensaje de error detectado en la respuesta")
                    return False
            else:
                logger.error(f"Login fallido - Status code: {login_response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error durante el proceso de login: {e}")
            return False

    def test_endpoint_authenticated(self):
        """Probar el endpoint con autenticación válida"""
        logger.info("=== PROBANDO ENDPOINT AUTENTICADO ===")
        
        endpoint_url = f"{self.base_url}/api/asistencia/resumen_agrupado"
        
        # Fecha actual para las pruebas
        today = datetime.now()
        fecha_str = today.strftime("%Y-%m-%d")
        
        test_cases = [
            {
                "name": "Sin parámetros",
                "params": {}
            },
            {
                "name": "Con fechas",
                "params": {
                    'fecha_inicio': fecha_str,
                    'fecha_fin': fecha_str
                }
            },
            {
                "name": "Con supervisor",
                "params": {
                    'fecha_inicio': fecha_str,
                    'fecha_fin': fecha_str,
                    'supervisor': '1'
                }
            }
        ]
        
        results = {}
        
        for test_case in test_cases:
            logger.info(f"--- Probando: {test_case['name']} ---")
            logger.info(f"URL: {endpoint_url}")
            logger.info(f"Parámetros: {test_case['params']}")
            
            try:
                response = self.session.get(
                    endpoint_url,
                    params=test_case['params'],
                    timeout=30
                )
                
                logger.info(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        logger.info("✓ Respuesta JSON válida recibida")
                        logger.info(f"Estructura: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                        
                        # Mostrar muestra de los datos
                        if isinstance(data, dict) and 'data' in data:
                            logger.info(f"Número de registros: {len(data['data']) if isinstance(data['data'], list) else 'N/A'}")
                        
                        results[test_case['name']] = True
                        
                    except json.JSONDecodeError:
                        logger.error("✗ Respuesta no es JSON válido")
                        logger.info(f"Contenido: {response.text[:200]}...")
                        results[test_case['name']] = False
                        
                elif response.status_code == 302:
                    logger.error("✗ Redirección detectada - Autenticación perdida")
                    results[test_case['name']] = False
                    
                elif response.status_code == 500:
                    logger.error("✗ ERROR 500 DETECTADO")
                    logger.error(f"Contenido del error: {response.text[:500]}")
                    results[test_case['name']] = False
                    
                else:
                    logger.warning(f"Status code inesperado: {response.status_code}")
                    results[test_case['name']] = False
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error en petición: {e}")
                results[test_case['name']] = False
        
        return results

    def run_complete_test(self):
        """Ejecutar prueba completa con autenticación"""
        logger.info("INICIANDO PRUEBA COMPLETA CON AUTENTICACIÓN")
        logger.info("=" * 60)
        
        # 1. Intentar login
        if not self.login():
            logger.error("❌ FALLO EN LOGIN - No se puede continuar")
            return False
        
        # 2. Probar endpoint
        logger.info("\n" + "=" * 40)
        results = self.test_endpoint_authenticated()
        
        # 3. Resumen
        logger.info("\n" + "=" * 60)
        logger.info("RESUMEN DE RESULTADOS:")
        
        all_passed = True
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"{test_name}: {status}")
            if not result:
                all_passed = False
        
        if all_passed:
            logger.info("\n🎉 TODOS LOS TESTS PASARON")
            logger.info("El endpoint funciona correctamente con autenticación")
        else:
            logger.info("\n❌ ALGUNOS TESTS FALLARON")
            logger.info("Revisar logs detallados para más información")
        
        return all_passed

def main():
    """Función principal"""
    print("Script de Prueba con Autenticación - Endpoint Resumen Agrupado")
    print("=" * 70)
    
    # Permitir URL personalizada
    server_url = input("URL del servidor (Enter para usar http://148.113.171.196:8080): ").strip()
    
    tester = AuthenticatedEndpointTester()
    if server_url:
        tester.base_url = server_url.rstrip('/')
        logger.info(f"URL personalizada: {tester.base_url}")
    
    try:
        success = tester.run_complete_test()
        
        if success:
            print("\n✅ DIAGNÓSTICO EXITOSO")
            print("El endpoint funciona correctamente")
        else:
            print("\n❌ PROBLEMAS DETECTADOS")
            print("Revisar test_auth_endpoint.log para detalles")
            
    except KeyboardInterrupt:
        logger.info("Prueba interrumpida por el usuario")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()