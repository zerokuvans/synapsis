#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para el endpoint /api/asistencia/resumen_agrupado
en el servidor de producción.

Objetivo: Identificar la causa exacta del error 500 en producción.
"""

import requests
import json
import logging
from datetime import datetime, timedelta
import sys
import urllib3

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_produccion.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Deshabilitar warnings de SSL si es necesario
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ProductionEndpointTester:
    def __init__(self):
        # URL del servidor de producción (ajustar según sea necesario)
        self.base_url = "https://synapsis.com.co"  # Cambiar por la URL real
        self.session = requests.Session()
        self.session.verify = False  # Solo para pruebas, ajustar según configuración SSL
        
        # Credenciales de prueba
        self.username = "80833959"
        self.password = "M4r14l4r@"
        
        logger.info("Inicializando tester para servidor de producción")
        logger.info(f"URL base: {self.base_url}")

    def test_connectivity(self):
        """Probar conectividad básica al servidor"""
        logger.info("=== PRUEBA DE CONECTIVIDAD ===")
        try:
            response = self.session.get(f"{self.base_url}/", timeout=30)
            logger.info(f"Conectividad OK - Status: {response.status_code}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conectividad: {e}")
            return False

    def test_login(self):
        """Probar autenticación con las credenciales"""
        logger.info("=== PRUEBA DE AUTENTICACIÓN ===")
        try:
            # Primero obtener la página de login para cookies/tokens
            login_page = self.session.get(f"{self.base_url}/login", timeout=30)
            logger.info(f"Página de login obtenida - Status: {login_page.status_code}")
            
            # Intentar login
            login_data = {
                'username': self.username,
                'password': self.password
            }
            
            response = self.session.post(
                f"{self.base_url}/login",
                data=login_data,
                timeout=30,
                allow_redirects=False
            )
            
            logger.info(f"Respuesta de login - Status: {response.status_code}")
            logger.info(f"Headers de respuesta: {dict(response.headers)}")
            
            # Verificar si hay redirección (típico en login exitoso)
            if response.status_code in [302, 303, 307, 308]:
                logger.info("Login exitoso - Redirección detectada")
                return True
            elif response.status_code == 200:
                # Verificar contenido para determinar si login fue exitoso
                if "dashboard" in response.text.lower() or "administrativo" in response.text.lower():
                    logger.info("Login exitoso - Contenido de dashboard detectado")
                    return True
                else:
                    logger.warning("Login posiblemente fallido - No se detectó redirección ni dashboard")
                    return False
            else:
                logger.error(f"Login fallido - Status code inesperado: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error durante login: {e}")
            return False

    def test_endpoint_basic(self):
        """Probar el endpoint básico sin parámetros"""
        logger.info("=== PRUEBA ENDPOINT BÁSICO ===")
        try:
            url = f"{self.base_url}/api/asistencia/resumen_agrupado"
            logger.info(f"Probando URL: {url}")
            
            response = self.session.get(url, timeout=30)
            
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 500:
                logger.error("ERROR 500 DETECTADO")
                logger.error(f"Contenido de respuesta: {response.text[:1000]}")
                return False
            elif response.status_code == 200:
                try:
                    data = response.json()
                    logger.info("Respuesta JSON válida recibida")
                    logger.info(f"Estructura de respuesta: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                    return True
                except json.JSONDecodeError:
                    logger.warning("Respuesta no es JSON válido")
                    logger.info(f"Contenido: {response.text[:500]}")
                    return False
            else:
                logger.warning(f"Status code inesperado: {response.status_code}")
                logger.info(f"Contenido: {response.text[:500]}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición al endpoint: {e}")
            return False

    def test_endpoint_with_dates(self):
        """Probar el endpoint con parámetros de fecha"""
        logger.info("=== PRUEBA ENDPOINT CON FECHAS ===")
        
        # Fecha actual
        today = datetime.now()
        fecha_str = today.strftime("%Y-%m-%d")
        
        try:
            url = f"{self.base_url}/api/asistencia/resumen_agrupado"
            params = {
                'fecha_inicio': fecha_str,
                'fecha_fin': fecha_str
            }
            
            logger.info(f"Probando URL: {url}")
            logger.info(f"Parámetros: {params}")
            
            response = self.session.get(url, params=params, timeout=30)
            
            logger.info(f"Status Code: {response.status_code}")
            
            if response.status_code == 500:
                logger.error("ERROR 500 CON FECHAS DETECTADO")
                logger.error(f"Contenido de respuesta: {response.text[:1000]}")
                return False
            elif response.status_code == 200:
                try:
                    data = response.json()
                    logger.info("Respuesta JSON válida con fechas")
                    logger.info(f"Datos recibidos: {json.dumps(data, indent=2, default=str)[:500]}")
                    return True
                except json.JSONDecodeError:
                    logger.warning("Respuesta con fechas no es JSON válido")
                    return False
            else:
                logger.warning(f"Status code con fechas: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición con fechas: {e}")
            return False

    def test_endpoint_with_supervisor(self):
        """Probar el endpoint con filtro de supervisor"""
        logger.info("=== PRUEBA ENDPOINT CON SUPERVISOR ===")
        
        today = datetime.now()
        fecha_str = today.strftime("%Y-%m-%d")
        
        try:
            url = f"{self.base_url}/api/asistencia/resumen_agrupado"
            params = {
                'fecha_inicio': fecha_str,
                'fecha_fin': fecha_str,
                'supervisor': '1'  # ID de supervisor de prueba
            }
            
            logger.info(f"Probando URL: {url}")
            logger.info(f"Parámetros: {params}")
            
            response = self.session.get(url, params=params, timeout=30)
            
            logger.info(f"Status Code: {response.status_code}")
            
            if response.status_code == 500:
                logger.error("ERROR 500 CON SUPERVISOR DETECTADO")
                logger.error(f"Contenido de respuesta: {response.text[:1000]}")
                return False
            elif response.status_code == 200:
                try:
                    data = response.json()
                    logger.info("Respuesta JSON válida con supervisor")
                    return True
                except json.JSONDecodeError:
                    logger.warning("Respuesta con supervisor no es JSON válido")
                    return False
            else:
                logger.warning(f"Status code con supervisor: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición con supervisor: {e}")
            return False

    def run_all_tests(self):
        """Ejecutar todas las pruebas de diagnóstico"""
        logger.info("INICIANDO DIAGNÓSTICO COMPLETO DEL ENDPOINT")
        logger.info("=" * 60)
        
        results = {}
        
        # Prueba 1: Conectividad
        results['connectivity'] = self.test_connectivity()
        
        # Prueba 2: Autenticación
        if results['connectivity']:
            results['authentication'] = self.test_login()
        else:
            logger.error("Saltando pruebas - Sin conectividad")
            return results
        
        # Prueba 3: Endpoint básico
        if results['authentication']:
            results['endpoint_basic'] = self.test_endpoint_basic()
        else:
            logger.warning("Probando endpoint sin autenticación")
            results['endpoint_basic'] = self.test_endpoint_basic()
        
        # Prueba 4: Endpoint con fechas
        results['endpoint_dates'] = self.test_endpoint_with_dates()
        
        # Prueba 5: Endpoint con supervisor
        results['endpoint_supervisor'] = self.test_endpoint_with_supervisor()
        
        # Resumen de resultados
        logger.info("=" * 60)
        logger.info("RESUMEN DE RESULTADOS:")
        for test, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"{test}: {status}")
        
        return results

def main():
    """Función principal"""
    print("Script de Diagnóstico - Endpoint Resumen Agrupado")
    print("=" * 60)
    
    # Solicitar URL del servidor si es necesario
    server_url = input("Ingresa la URL del servidor de producción (o presiona Enter para usar https://synapsis.com.co): ").strip()
    
    tester = ProductionEndpointTester()
    if server_url:
        tester.base_url = server_url.rstrip('/')
        logger.info(f"URL personalizada configurada: {tester.base_url}")
    
    try:
        results = tester.run_all_tests()
        
        # Análisis final
        if not any(results.values()):
            print("\n❌ TODOS LOS TESTS FALLARON")
            print("Posibles causas:")
            print("- Servidor no disponible")
            print("- Problemas de red/firewall")
            print("- Configuración SSL incorrecta")
        elif results.get('endpoint_basic') == False:
            print("\n❌ ENDPOINT CON ERROR 500")
            print("El problema está en el código del endpoint en main.py")
            print("Revisar logs del servidor para más detalles")
        else:
            print("\n✅ DIAGNÓSTICO COMPLETADO")
            print("Revisar logs detallados en test_produccion.log")
            
    except KeyboardInterrupt:
        logger.info("Diagnóstico interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error inesperado durante diagnóstico: {e}")

if __name__ == "__main__":
    main()