#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debugging completo para el módulo de vencimientos
Verifica paso a paso todo el flujo desde autenticación hasta visualización de datos
"""

import requests
import mysql.connector
import json
from datetime import datetime, timedelta
import bcrypt
from bs4 import BeautifulSoup
import re

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'capired'
}

# URL base del servidor
BASE_URL = 'http://127.0.0.1:5000'

class VencimientosDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.csrf_token = None
        self.user_authenticated = False
        self.debug_log = []
        
    def log(self, message, status="INFO"):
        """Registra un mensaje en el log de debugging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {status}: {message}"
        self.debug_log.append(log_entry)
        print(log_entry)
        
    def verificar_conexion_db(self):
        """Verifica la conexión a la base de datos"""
        self.log("=== VERIFICANDO CONEXIÓN A BASE DE DATOS ===")
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            self.log(f"Conexión exitosa a MySQL versión: {version[0]}", "SUCCESS")
            
            # Verificar tablas necesarias
            cursor.execute("SHOW TABLES LIKE 'parque_automotor'")
            if cursor.fetchone():
                self.log("Tabla 'parque_automotor' encontrada", "SUCCESS")
            else:
                self.log("Tabla 'parque_automotor' NO encontrada", "ERROR")
                
            cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
            if cursor.fetchone():
                self.log("Tabla 'recurso_operativo' encontrada", "SUCCESS")
            else:
                self.log("Tabla 'recurso_operativo' NO encontrada", "ERROR")
                
            conn.close()
            return True
        except Exception as e:
            self.log(f"Error de conexión a BD: {str(e)}", "ERROR")
            return False
            
    def verificar_datos_vencimientos(self):
        """Verifica si hay datos de vencimientos en la BD"""
        self.log("=== VERIFICANDO DATOS DE VENCIMIENTOS ===")
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            
            # Contar vehículos totales
            cursor.execute("SELECT COUNT(*) as total FROM parque_automotor")
            total_vehiculos = cursor.fetchone()['total']
            self.log(f"Total de vehículos en BD: {total_vehiculos}")
            
            # Verificar vehículos con fechas de vencimiento
            query = """
            SELECT COUNT(*) as total 
            FROM parque_automotor 
            WHERE fecha_vencimiento_soat IS NOT NULL 
               OR fecha_vencimiento_tecnomecanica IS NOT NULL
            """
            cursor.execute(query)
            vehiculos_con_fechas = cursor.fetchone()['total']
            self.log(f"Vehículos con fechas de vencimiento: {vehiculos_con_fechas}")
            
            # Verificar vencimientos próximos (30 días)
            fecha_limite = datetime.now() + timedelta(days=30)
            query = """
            SELECT COUNT(*) as total 
            FROM parque_automotor 
            WHERE (fecha_vencimiento_soat IS NOT NULL AND fecha_vencimiento_soat <= %s)
               OR (fecha_vencimiento_tecnomecanica IS NOT NULL AND fecha_vencimiento_tecnomecanica <= %s)
            """
            cursor.execute(query, (fecha_limite, fecha_limite))
            vencimientos_proximos = cursor.fetchone()['total']
            self.log(f"Vencimientos próximos (30 días): {vencimientos_proximos}")
            
            # Mostrar ejemplos de datos
            query = """
            SELECT placa, fecha_vencimiento_soat, fecha_vencimiento_tecnomecanica
            FROM parque_automotor 
            WHERE fecha_vencimiento_soat IS NOT NULL 
               OR fecha_vencimiento_tecnomecanica IS NOT NULL
            LIMIT 5
            """
            cursor.execute(query)
            ejemplos = cursor.fetchall()
            
            if ejemplos:
                self.log("Ejemplos de vehículos con fechas:")
                for vehiculo in ejemplos:
                    self.log(f"  Placa: {vehiculo['placa']}, SOAT: {vehiculo['fecha_vencimiento_soat']}, Tecnomecánica: {vehiculo['fecha_vencimiento_tecnomecanica']}")
            else:
                self.log("No se encontraron vehículos con fechas de vencimiento", "WARNING")
                
            conn.close()
            return vehiculos_con_fechas > 0
            
        except Exception as e:
            self.log(f"Error verificando datos: {str(e)}", "ERROR")
            return False
            
    def verificar_usuario_logistica(self):
        """Verifica si existe un usuario con rol logística"""
        self.log("=== VERIFICANDO USUARIO LOGÍSTICA ===")
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            
            # Buscar usuarios con rol logística
            cursor.execute("""
                SELECT recurso_operativo_cedula, recurso_operativo_nombre, id_roles
                FROM recurso_operativo 
                WHERE id_roles = '5' AND recurso_operativo_estado = 'activo'
            """)
            usuarios_logistica = cursor.fetchall()
            
            if usuarios_logistica:
                self.log(f"Encontrados {len(usuarios_logistica)} usuarios con rol logística:")
                for usuario in usuarios_logistica:
                    self.log(f"  Cédula: {usuario['recurso_operativo_cedula']}, Nombre: {usuario['recurso_operativo_nombre']}")
                return usuarios_logistica[0]  # Retornar el primer usuario
            else:
                self.log("No se encontraron usuarios con rol logística", "WARNING")
                # Crear usuario de prueba
                return self.crear_usuario_prueba()
                
        except Exception as e:
            self.log(f"Error verificando usuarios: {str(e)}", "ERROR")
            return None
            
    def crear_usuario_prueba(self):
        """Crea un usuario de prueba para logística"""
        self.log("Creando usuario de prueba para logística...")
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Verificar si ya existe
            cursor.execute("""
                SELECT recurso_operativo_cedula FROM recurso_operativo 
                WHERE recurso_operativo_cedula = 'test_logistica'
            """)
            
            if cursor.fetchone():
                self.log("Usuario de prueba ya existe")
                return {'recurso_operativo_cedula': 'test_logistica', 'recurso_operativo_nombre': 'Usuario Test Logística'}
                
            # Crear usuario
            password_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("""
                INSERT INTO recurso_operativo 
                (recurso_operativo_cedula, recurso_operativo_nombre, recurso_operativo_password, 
                 id_roles, recurso_operativo_estado)
                VALUES (%s, %s, %s, %s, %s)
            """, ('test_logistica', 'Usuario Test Logística', password_hash, '5', 'activo'))
            
            conn.commit()
            conn.close()
            
            self.log("Usuario de prueba creado exitosamente", "SUCCESS")
            return {'recurso_operativo_cedula': 'test_logistica', 'recurso_operativo_nombre': 'Usuario Test Logística'}
            
        except Exception as e:
            self.log(f"Error creando usuario de prueba: {str(e)}", "ERROR")
            return None
            
    def obtener_csrf_token(self):
        """Obtiene el token CSRF del formulario de login"""
        self.log("=== OBTENIENDO TOKEN CSRF ===")
        try:
            response = self.session.get(f"{BASE_URL}/login")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                csrf_input = soup.find('input', {'name': 'csrf_token'})
                if csrf_input:
                    self.csrf_token = csrf_input.get('value')
                    self.log(f"Token CSRF obtenido: {self.csrf_token[:20]}...", "SUCCESS")
                    return True
                else:
                    self.log("No se encontró el campo csrf_token", "ERROR")
            else:
                self.log(f"Error al acceder a /login: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"Error obteniendo CSRF token: {str(e)}", "ERROR")
        return False
        
    def autenticar_usuario(self, usuario):
        """Autentica al usuario en el sistema"""
        self.log("=== AUTENTICANDO USUARIO ===")
        try:
            login_data = {
                'username': usuario['recurso_operativo_cedula'],
                'password': '123456',
                'csrf_token': self.csrf_token
            }
            
            response = self.session.post(f"{BASE_URL}/login", data=login_data)
            
            if response.status_code == 200:
                # Verificar si la respuesta contiene indicadores de éxito
                if 'dashboard' in response.url or 'success' in response.text.lower():
                    self.log("Autenticación exitosa", "SUCCESS")
                    self.user_authenticated = True
                    return True
                else:
                    self.log("Autenticación fallida - credenciales incorrectas", "ERROR")
            else:
                self.log(f"Error en autenticación: {response.status_code}", "ERROR")
                
        except Exception as e:
            self.log(f"Error durante autenticación: {str(e)}", "ERROR")
            
        return False
        
    def probar_endpoint_vencimientos(self):
        """Prueba el endpoint de vencimientos con diferentes parámetros"""
        self.log("=== PROBANDO ENDPOINT /api/vehiculos/vencimientos ===")
        
        if not self.user_authenticated:
            self.log("Usuario no autenticado, saltando prueba de endpoint", "WARNING")
            return False
            
        # Prueba básica
        try:
            response = self.session.get(f"{BASE_URL}/api/vehiculos/vencimientos")
            self.log(f"Respuesta básica - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Datos recibidos: success={data.get('success')}, total={data.get('total')}")
                
                if data.get('success'):
                    vencimientos = data.get('data', [])
                    self.log(f"Número de vencimientos: {len(vencimientos)}")
                    
                    if vencimientos:
                        self.log("Ejemplo de vencimiento:")
                        ejemplo = vencimientos[0]
                        for key, value in ejemplo.items():
                            self.log(f"  {key}: {value}")
                    else:
                        self.log("No se encontraron vencimientos", "WARNING")
                        
                else:
                    self.log(f"Endpoint retornó error: {data.get('message')}", "ERROR")
                    
            else:
                self.log(f"Error en endpoint: {response.status_code} - {response.text}", "ERROR")
                
        except Exception as e:
            self.log(f"Error probando endpoint: {str(e)}", "ERROR")
            return False
            
        # Pruebas con parámetros
        parametros_prueba = [
            {'dias': 30},
            {'dias': 60},
            {'tipo': 'soat'},
            {'tipo': 'tecnomecanica'}
        ]
        
        for params in parametros_prueba:
            try:
                response = self.session.get(f"{BASE_URL}/api/vehiculos/vencimientos", params=params)
                if response.status_code == 200:
                    data = response.json()
                    total = len(data.get('data', []))
                    self.log(f"Con parámetros {params}: {total} resultados")
                else:
                    self.log(f"Error con parámetros {params}: {response.status_code}", "ERROR")
            except Exception as e:
                self.log(f"Error con parámetros {params}: {str(e)}", "ERROR")
                
        return True
        
    def verificar_estructura_html(self):
        """Verifica la estructura HTML de la página de automotor"""
        self.log("=== VERIFICANDO ESTRUCTURA HTML ===")
        
        if not self.user_authenticated:
            self.log("Usuario no autenticado, saltando verificación HTML", "WARNING")
            return False
            
        try:
            response = self.session.get(f"{BASE_URL}/logistica/automotor")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Verificar tabla de vencimientos
                tabla_vencimientos = soup.find('table', {'id': 'tablaVencimientos'})
                if tabla_vencimientos:
                    self.log("Tabla #tablaVencimientos encontrada", "SUCCESS")
                    
                    # Verificar estructura de la tabla
                    thead = tabla_vencimientos.find('thead')
                    if thead:
                        headers = thead.find_all('th')
                        self.log(f"Número de columnas en header: {len(headers)}")
                        for i, header in enumerate(headers):
                            self.log(f"  Columna {i+1}: {header.get_text().strip()}")
                    else:
                        self.log("No se encontró thead en la tabla", "WARNING")
                        
                    tbody = tabla_vencimientos.find('tbody')
                    if tbody:
                        self.log("Tbody encontrado", "SUCCESS")
                    else:
                        self.log("No se encontró tbody en la tabla", "WARNING")
                        
                else:
                    self.log("Tabla #tablaVencimientos NO encontrada", "ERROR")
                    
                # Verificar scripts JavaScript
                scripts = soup.find_all('script')
                cargar_vencimientos_found = False
                
                for script in scripts:
                    if script.string and 'cargarVencimientos' in script.string:
                        cargar_vencimientos_found = True
                        break
                        
                if cargar_vencimientos_found:
                    self.log("Función cargarVencimientos encontrada en JavaScript", "SUCCESS")
                else:
                    self.log("Función cargarVencimientos NO encontrada", "ERROR")
                    
            else:
                self.log(f"Error accediendo a página automotor: {response.status_code}", "ERROR")
                
        except Exception as e:
            self.log(f"Error verificando estructura HTML: {str(e)}", "ERROR")
            return False
            
        return True
        
    def generar_reporte(self):
        """Genera un reporte completo del debugging"""
        self.log("=== GENERANDO REPORTE FINAL ===")
        
        reporte_file = 'reporte_debug_vencimientos.txt'
        
        try:
            with open(reporte_file, 'w', encoding='utf-8') as f:
                f.write("REPORTE DE DEBUGGING - MÓDULO DE VENCIMIENTOS\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for log_entry in self.debug_log:
                    f.write(log_entry + "\n")
                    
            self.log(f"Reporte guardado en: {reporte_file}", "SUCCESS")
            
        except Exception as e:
            self.log(f"Error generando reporte: {str(e)}", "ERROR")
            
    def ejecutar_debugging_completo(self):
        """Ejecuta todo el proceso de debugging"""
        self.log("INICIANDO DEBUGGING COMPLETO DEL MÓDULO DE VENCIMIENTOS")
        self.log("=" * 60)
        
        # 1. Verificar conexión a BD
        if not self.verificar_conexion_db():
            self.log("Debugging terminado - Error de conexión a BD", "ERROR")
            return
            
        # 2. Verificar datos de vencimientos
        self.verificar_datos_vencimientos()
        
        # 3. Verificar usuario logística
        usuario = self.verificar_usuario_logistica()
        if not usuario:
            self.log("Debugging terminado - No se pudo obtener usuario logística", "ERROR")
            return
            
        # 4. Obtener token CSRF
        if not self.obtener_csrf_token():
            self.log("Debugging terminado - No se pudo obtener token CSRF", "ERROR")
            return
            
        # 5. Autenticar usuario
        if not self.autenticar_usuario(usuario):
            self.log("Debugging terminado - Error de autenticación", "ERROR")
            return
            
        # 6. Probar endpoint
        self.probar_endpoint_vencimientos()
        
        # 7. Verificar estructura HTML
        self.verificar_estructura_html()
        
        # 8. Generar reporte
        self.generar_reporte()
        
        self.log("DEBUGGING COMPLETO FINALIZADO", "SUCCESS")
        
def main():
    debugger = VencimientosDebugger()
    debugger.ejecutar_debugging_completo()
    
if __name__ == "__main__":
    main()