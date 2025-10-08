#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la estructura de la tabla tipificacion_asistencia
en el servidor de producción y compararla con la local.
"""

import requests
import json
import logging
from datetime import datetime
import sys
import urllib3
from bs4 import BeautifulSoup

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('verificar_estructura_produccion.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ProductionTableChecker:
    def __init__(self, base_url="http://148.113.171.196:8080"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.verify = False
        
        # Credenciales
        self.username = "80833959"
        self.password = "M4r14l4r@"
        
        logger.info(f"Inicializando verificador para: {self.base_url}")

    def login(self):
        """Realizar login"""
        logger.info("=== INICIANDO LOGIN ===")
        
        try:
            # Obtener página de login
            response = self.session.get(f"{self.base_url}/", timeout=30)
            
            if response.status_code != 200:
                logger.error(f"No se pudo obtener la página de login: {response.status_code}")
                return False
            
            # Preparar datos de login
            login_data = {
                'username': self.username,
                'password': self.password
            }
            
            # Realizar login
            login_response = self.session.post(
                f"{self.base_url}/",
                data=login_data,
                timeout=30,
                allow_redirects=True
            )
            
            logger.info(f"Login response - Status: {login_response.status_code}")
            logger.info(f"URL final: {login_response.url}")
            
            # Verificar login exitoso
            if login_response.status_code == 200:
                content = login_response.text.lower()
                if any(indicator in content for indicator in ['dashboard', 'administrativo', 'logout']):
                    logger.info("✓ LOGIN EXITOSO")
                    return True
            
            logger.error("Login fallido")
            return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error durante login: {e}")
            return False

    def create_test_endpoint(self):
        """Crear un endpoint de prueba para verificar estructura de tabla"""
        logger.info("=== CREANDO ENDPOINT DE PRUEBA ===")
        
        # Este endpoint debería ser agregado temporalmente al main.py del servidor
        test_endpoint_code = '''
@app.route('/api/debug/table_structure', methods=['GET'])
@login_required
def debug_table_structure():
    """Endpoint temporal para verificar estructura de tipificacion_asistencia"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Verificar estructura de la tabla
        cursor.execute("DESCRIBE tipificacion_asistencia")
        estructura = cursor.fetchall()
        
        # Obtener algunos registros de muestra
        cursor.execute("SELECT * FROM tipificacion_asistencia LIMIT 5")
        muestra = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'estructura': estructura,
            'muestra': muestra,
            'total_columnas': len(estructura)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
'''
        
        logger.info("Código del endpoint de prueba:")
        logger.info(test_endpoint_code)
        
        return test_endpoint_code

    def test_direct_sql_query(self):
        """Probar una consulta SQL directa simplificada"""
        logger.info("=== PROBANDO CONSULTA SQL SIMPLIFICADA ===")
        
        # Crear un endpoint temporal que no use la columna 'grupo'
        test_url = f"{self.base_url}/api/asistencia/resumen_agrupado"
        
        # Probar con una consulta que solo use columnas básicas
        params = {
            'fecha_inicio': '2025-09-30',
            'fecha_fin': '2025-09-30',
            'debug': 'true'  # Parámetro para activar modo debug
        }
        
        try:
            response = self.session.get(test_url, params=params, timeout=30)
            
            logger.info(f"Status Code: {response.status_code}")
            
            if response.status_code == 500:
                try:
                    error_data = response.json()
                    logger.error(f"Error SQL: {error_data.get('message', 'Sin mensaje')}")
                    
                    # Analizar el error para entender qué columnas faltan
                    error_msg = error_data.get('message', '')
                    if 'Unknown column' in error_msg:
                        # Extraer el nombre de la columna problemática
                        import re
                        match = re.search(r"Unknown column '([^']+)'", error_msg)
                        if match:
                            columna_faltante = match.group(1)
                            logger.error(f"Columna faltante identificada: {columna_faltante}")
                            return {'columna_faltante': columna_faltante, 'error': error_msg}
                    
                except json.JSONDecodeError:
                    logger.error("Error no es JSON válido")
                    
            return {'status': response.status_code, 'response': response.text[:500]}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición: {e}")
            return {'error': str(e)}

    def suggest_fix(self, columna_faltante):
        """Sugerir solución para la columna faltante"""
        logger.info("=== SUGERENCIAS DE SOLUCIÓN ===")
        
        if columna_faltante == 't.grupo':
            logger.info("PROBLEMA: La tabla tipificacion_asistencia no tiene la columna 'grupo'")
            logger.info("SOLUCIONES POSIBLES:")
            logger.info("1. Agregar la columna 'grupo' a la tabla en producción:")
            logger.info("   ALTER TABLE tipificacion_asistencia ADD COLUMN grupo VARCHAR(100);")
            logger.info("")
            logger.info("2. Modificar la consulta para no usar la columna 'grupo':")
            logger.info("   - Usar solo 'nombre_tipificacion' para agrupar")
            logger.info("   - Crear lógica de agrupación en el código Python")
            logger.info("")
            logger.info("3. Sincronizar estructura de base de datos entre desarrollo y producción")

    def run_verification(self):
        """Ejecutar verificación completa"""
        logger.info("INICIANDO VERIFICACIÓN DE ESTRUCTURA DE TABLA")
        logger.info("=" * 60)
        
        # 1. Login
        if not self.login():
            logger.error("❌ No se pudo hacer login")
            return False
        
        # 2. Mostrar código de endpoint de prueba
        self.create_test_endpoint()
        
        # 3. Probar consulta SQL
        logger.info("\n" + "=" * 40)
        result = self.test_direct_sql_query()
        
        # 4. Analizar resultados
        if 'columna_faltante' in result:
            self.suggest_fix(result['columna_faltante'])
        
        logger.info("\n" + "=" * 60)
        logger.info("VERIFICACIÓN COMPLETADA")
        
        return True

def main():
    """Función principal"""
    print("Verificador de Estructura de Tabla - Producción vs Desarrollo")
    print("=" * 70)
    
    checker = ProductionTableChecker()
    
    try:
        checker.run_verification()
        print("\n✅ Verificación completada")
        print("Revisar verificar_estructura_produccion.log para detalles")
        
    except KeyboardInterrupt:
        logger.info("Verificación interrumpida por el usuario")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()