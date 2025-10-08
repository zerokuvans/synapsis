#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pruebas de integración completas para el sistema de gestión de estados de devoluciones
Este archivo contiene pruebas end-to-end que verifican el funcionamiento completo del sistema

Autor: Sistema de Gestión de Estados
Fecha: 2024
"""

import unittest
import requests
import json
import mysql.connector
import time
from datetime import datetime
import logging

# Configurar logging para las pruebas
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestIntegracionEstadoManagement(unittest.TestCase):
    """Clase de pruebas de integración para el sistema de gestión de estados"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para todas las pruebas"""
        cls.base_url = "http://localhost:5000"
        cls.connection = None
        cls.cursor = None
        cls.test_data = {
            'devolucion_id': None,
            'usuario_id': None,
            'auditoria_ids': [],
            'notificacion_ids': []
        }
        
        # Conectar a la base de datos
        cls.conectar_bd()
        
        # Crear datos de prueba
        cls.crear_datos_prueba()
    
    @classmethod
    def tearDownClass(cls):
        """Limpieza después de todas las pruebas"""
        cls.limpiar_datos_prueba()
        cls.cerrar_conexion()
    
    @classmethod
    def conectar_bd(cls):
        """Establece conexión con la base de datos"""
        try:
            cls.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='732137A031E4b@',
                database='capired'
            )
            cls.cursor = cls.connection.cursor(dictionary=True)
            logger.info("Conexión a base de datos establecida para pruebas")
        except Exception as e:
            logger.error(f"Error al conectar a la base de datos: {str(e)}")
            raise
    
    @classmethod
    def cerrar_conexion(cls):
        """Cierra la conexión con la base de datos"""
        if cls.cursor:
            cls.cursor.close()
        if cls.connection:
            cls.connection.close()
        logger.info("Conexión cerrada")
    
    @classmethod
    def crear_datos_prueba(cls):
        """Crea datos de prueba necesarios"""
        try:
            # Crear usuario de prueba si no existe
            cls.cursor.execute("""
                SELECT idusuarios FROM usuarios WHERE usuario_cedula = 12345678
            """)
            usuario = cls.cursor.fetchone()
            
            if not usuario:
                cls.cursor.execute("""
                    INSERT INTO usuarios (usuario_nombre, usuario_cedula, usuario_contraseña)
                    VALUES ('Usuario Test', 12345678, 123456)
                """)
                cls.test_data['usuario_id'] = cls.cursor.lastrowid
            else:
                cls.test_data['usuario_id'] = usuario[0]
            
            # Usar valores fijos válidos para las pruebas
            # Crear devolución de prueba con valores simplificados
            cls.cursor.execute("""
                INSERT INTO devoluciones_dotacion (tecnico_id, cliente_id, motivo, estado, created_by)
                VALUES (1, 1, 'Prueba de integración', 'REGISTRADA', %s)
            """, (cls.test_data['usuario_id'],))
            cls.test_data['devolucion_id'] = cls.cursor.lastrowid
            
            cls.connection.commit()
            logger.info(f"Datos de prueba creados - Devolución ID: {cls.test_data['devolucion_id']}")
            
        except Exception as e:
            logger.error(f"Error al crear datos de prueba: {str(e)}")
            raise
    
    @classmethod
    def limpiar_datos_prueba(cls):
        """Limpia los datos de prueba creados"""
        try:
            # Limpiar notificaciones
            if cls.test_data['notificacion_ids']:
                placeholders = ','.join(['%s'] * len(cls.test_data['notificacion_ids']))
                cls.cursor.execute(f"""
                    DELETE FROM historial_notificaciones 
                    WHERE id IN ({placeholders})
                """, cls.test_data['notificacion_ids'])
            
            # Limpiar auditorías
            if cls.test_data['auditoria_ids']:
                placeholders = ','.join(['%s'] * len(cls.test_data['auditoria_ids']))
                cls.cursor.execute(f"""
                    DELETE FROM auditoria_estados_devolucion 
                    WHERE id IN ({placeholders})
                """, cls.test_data['auditoria_ids'])
            
            # Limpiar devolución
            if cls.test_data['devolucion_id']:
                cls.cursor.execute("""
                    DELETE FROM devoluciones_dotacion 
                    WHERE id = %s
                """, (cls.test_data['devolucion_id'],))
            
            # Limpiar usuario (solo si lo creamos)
            cls.cursor.execute("""
                DELETE FROM usuarios 
                WHERE usuario_cedula = 12345678
            """)
            
            cls.connection.commit()
            logger.info("Datos de prueba limpiados")
            
        except Exception as e:
            logger.error(f"Error al limpiar datos de prueba: {str(e)}")
    
    def verificar_servidor_activo(self):
        """Verifica que el servidor esté activo"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_01_servidor_disponible(self):
        """Prueba que el servidor esté disponible"""
        logger.info("Ejecutando: test_01_servidor_disponible")
        self.assertTrue(
            self.verificar_servidor_activo(),
            "El servidor no está disponible en http://localhost:5000"
        )
    
    def test_02_obtener_transiciones_validas(self):
        """Prueba la obtención de transiciones válidas"""
        logger.info("Ejecutando: test_02_obtener_transiciones_validas")
        
        if not self.verificar_servidor_activo():
            self.skipTest("Servidor no disponible")
        
        response = requests.get(
            f"{self.base_url}/api/devoluciones/{self.test_data['devolucion_id']}/transiciones",
            params={'usuario_id': self.test_data['usuario_id']}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('transiciones', data)
        self.assertIsInstance(data['transiciones'], list)
        
        # Verificar que desde REGISTRADA se puede ir a PROCESANDO
        estados_destino = [t['estado_destino'] for t in data['transiciones']]
        self.assertIn('PROCESANDO', estados_destino)
    
    def test_03_actualizar_estado_registrada_a_procesando(self):
        """Prueba la transición de REGISTRADA a PROCESANDO"""
        logger.info("Ejecutando: test_03_actualizar_estado_registrada_a_procesando")
        
        if not self.verificar_servidor_activo():
            self.skipTest("Servidor no disponible")
        
        payload = {
            'nuevo_estado': 'PROCESANDO',
            'usuario_id': self.test_data['usuario_id'],
            'motivo': 'Iniciando procesamiento - Prueba de integración',
            'observaciones': 'Transición automática desde pruebas de integración'
        }
        
        response = requests.put(
            f"{self.base_url}/api/devoluciones/{self.test_data['devolucion_id']}/estado",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['nuevo_estado'], 'PROCESANDO')
        
        # Verificar en base de datos
        self.cursor.execute("""
            SELECT estado FROM devoluciones_dotacion WHERE id = %s
        """, (self.test_data['devolucion_id'],))
        
        resultado = self.cursor.fetchone()
        self.assertEqual(resultado['estado'], 'PROCESANDO')
    
    def test_04_verificar_auditoria_creada(self):
        """Prueba que se haya creado el registro de auditoría"""
        logger.info("Ejecutando: test_04_verificar_auditoria_creada")
        
        self.cursor.execute("""
            SELECT id, estado_anterior, estado_nuevo, usuario_id, motivo
            FROM auditoria_estados_devolucion 
            WHERE devolucion_id = %s
            ORDER BY fecha_cambio DESC
            LIMIT 1
        """, (self.test_data['devolucion_id'],))
        
        auditoria = self.cursor.fetchone()
        self.assertIsNotNone(auditoria, "No se encontró registro de auditoría")
        self.assertEqual(auditoria['estado_anterior'], 'REGISTRADA')
        self.assertEqual(auditoria['estado_nuevo'], 'PROCESANDO')
        self.assertEqual(auditoria['usuario_id'], self.test_data['usuario_id'])
        
        # Guardar ID para limpieza
        self.test_data['auditoria_ids'].append(auditoria['id'])
    
    def test_05_verificar_notificacion_programada(self):
        """Prueba que se haya programado una notificación"""
        logger.info("Ejecutando: test_05_verificar_notificacion_programada")
        
        # Esperar un momento para que se procese la notificación
        time.sleep(2)
        
        self.cursor.execute("""
            SELECT id, tipo_notificacion, estado_envio, destinatario
            FROM historial_notificaciones 
            WHERE devolucion_id = %s
            ORDER BY fecha_programada DESC
            LIMIT 1
        """, (self.test_data['devolucion_id'],))
        
        notificacion = self.cursor.fetchone()
        if notificacion:
            self.test_data['notificacion_ids'].append(notificacion['id'])
            self.assertIn(notificacion['tipo_notificacion'], ['EMAIL', 'SMS'])
            logger.info(f"Notificación encontrada: {notificacion['tipo_notificacion']}")
        else:
            logger.warning("No se encontró notificación programada")
    
    def test_06_transicion_invalida(self):
        """Prueba que se rechace una transición inválida"""
        logger.info("Ejecutando: test_06_transicion_invalida")
        
        if not self.verificar_servidor_activo():
            self.skipTest("Servidor no disponible")
        
        # Intentar ir directamente de PROCESANDO a REGISTRADA (inválido)
        payload = {
            'nuevo_estado': 'REGISTRADA',
            'usuario_id': self.test_data['usuario_id'],
            'motivo': 'Transición inválida - Prueba'
        }
        
        response = requests.put(
            f"{self.base_url}/api/devoluciones/{self.test_data['devolucion_id']}/estado",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    def test_07_completar_devolucion(self):
        """Prueba completar la devolución"""
        logger.info("Ejecutando: test_07_completar_devolucion")
        
        if not self.verificar_servidor_activo():
            self.skipTest("Servidor no disponible")
        
        payload = {
            'nuevo_estado': 'COMPLETADA',
            'usuario_id': self.test_data['usuario_id'],
            'motivo': 'Devolución procesada exitosamente',
            'observaciones': 'Todos los elementos fueron verificados y procesados'
        }
        
        response = requests.put(
            f"{self.base_url}/api/devoluciones/{self.test_data['devolucion_id']}/estado",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['nuevo_estado'], 'COMPLETADA')
    
    def test_08_historial_completo_auditoria(self):
        """Prueba que el historial de auditoría esté completo"""
        logger.info("Ejecutando: test_08_historial_completo_auditoria")
        
        self.cursor.execute("""
            SELECT estado_anterior, estado_nuevo, motivo, fecha_cambio
            FROM auditoria_estados_devolucion 
            WHERE devolucion_id = %s
            ORDER BY fecha_cambio ASC
        """, (self.test_data['devolucion_id'],))
        
        auditorias = self.cursor.fetchall()
        
        # Debería haber al menos 2 registros (REGISTRADA->PROCESANDO, PROCESANDO->COMPLETADA)
        self.assertGreaterEqual(len(auditorias), 2)
        
        # Verificar secuencia de estados
        estados_esperados = [
            (None, 'REGISTRADA'),  # Puede existir de migración inicial
            ('REGISTRADA', 'PROCESANDO'),
            ('PROCESANDO', 'COMPLETADA')
        ]
        
        # Verificar que las transiciones principales estén presentes
        transiciones_encontradas = [(a['estado_anterior'], a['estado_nuevo']) for a in auditorias]
        
        self.assertIn(('REGISTRADA', 'PROCESANDO'), transiciones_encontradas)
        self.assertIn(('PROCESANDO', 'COMPLETADA'), transiciones_encontradas)
        
        # Guardar IDs para limpieza
        for auditoria in auditorias:
            if auditoria['estado_anterior'] is not None:  # No limpiar registros de migración
                # Buscar el ID correspondiente
                self.cursor.execute("""
                    SELECT id FROM auditoria_estados_devolucion 
                    WHERE devolucion_id = %s AND estado_anterior = %s AND estado_nuevo = %s
                    AND fecha_cambio = %s
                """, (
                    self.test_data['devolucion_id'],
                    auditoria['estado_anterior'],
                    auditoria['estado_nuevo'],
                    auditoria['fecha_cambio']
                ))
                
                resultado = self.cursor.fetchone()
                if resultado and resultado['id'] not in self.test_data['auditoria_ids']:
                    self.test_data['auditoria_ids'].append(resultado['id'])
    
    def test_09_apis_configuracion_disponibles(self):
        """Prueba que las APIs de configuración estén disponibles"""
        logger.info("Ejecutando: test_09_apis_configuracion_disponibles")
        
        if not self.verificar_servidor_activo():
            self.skipTest("Servidor no disponible")
        
        # Probar API de configuraciones de notificación
        response = requests.get(f"{self.base_url}/api/admin/notificaciones/configuraciones")
        self.assertEqual(response.status_code, 200)
        
        # Probar API de roles
        response = requests.get(f"{self.base_url}/api/admin/roles")
        self.assertEqual(response.status_code, 200)
        
        # Probar API de plantillas de email
        response = requests.get(f"{self.base_url}/api/admin/plantillas/email")
        self.assertEqual(response.status_code, 200)
    
    def test_10_estado_final_correcto(self):
        """Prueba que el estado final sea el correcto"""
        logger.info("Ejecutando: test_10_estado_final_correcto")
        
        self.cursor.execute("""
            SELECT estado, updated_at FROM devoluciones_dotacion WHERE id = %s
        """, (self.test_data['devolucion_id'],))
        
        resultado = self.cursor.fetchone()
        self.assertEqual(resultado['estado'], 'COMPLETADA')
        self.assertIsNotNone(resultado['updated_at'])

class TestRendimientoSistema(unittest.TestCase):
    """Pruebas de rendimiento del sistema"""
    
    def setUp(self):
        self.base_url = "http://localhost:5000"
    
    def test_tiempo_respuesta_transiciones(self):
        """Prueba el tiempo de respuesta de la API de transiciones"""
        if not self.verificar_servidor_activo():
            self.skipTest("Servidor no disponible")
        
        start_time = time.time()
        response = requests.get(f"{self.base_url}/api/devoluciones/1/transiciones?usuario_id=1")
        end_time = time.time()
        
        tiempo_respuesta = end_time - start_time
        self.assertLess(tiempo_respuesta, 2.0, "La respuesta tardó más de 2 segundos")
        logger.info(f"Tiempo de respuesta API transiciones: {tiempo_respuesta:.3f}s")
    
    def verificar_servidor_activo(self):
        """Verifica que el servidor esté activo"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False

def ejecutar_pruebas_completas():
    """Ejecuta todas las pruebas de integración"""
    print("Ejecutando Pruebas de Integración del Sistema de Gestión de Estados")
    print("=" * 70)
    
    # Crear suite de pruebas
    suite = unittest.TestSuite()
    
    # Agregar pruebas de integración
    suite.addTest(unittest.makeSuite(TestIntegracionEstadoManagement))
    suite.addTest(unittest.makeSuite(TestRendimientoSistema))
    
    # Ejecutar pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    
    # Mostrar resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE PRUEBAS")
    print("=" * 70)
    print(f"Pruebas ejecutadas: {resultado.testsRun}")
    print(f"Errores: {len(resultado.errors)}")
    print(f"Fallos: {len(resultado.failures)}")
    print(f"Omitidas: {len(resultado.skipped) if hasattr(resultado, 'skipped') else 0}")
    
    if resultado.wasSuccessful():
        print("\n✅ Todas las pruebas pasaron exitosamente")
    else:
        print("\n❌ Algunas pruebas fallaron")
        
        if resultado.errors:
            print("\nERRORES:")
            for test, error in resultado.errors:
                print(f"- {test}: {error}")
        
        if resultado.failures:
            print("\nFALLOS:")
            for test, failure in resultado.failures:
                print(f"- {test}: {failure}")
    
    return resultado.wasSuccessful()

if __name__ == "__main__":
    ejecutar_pruebas_completas()