#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error
import hashlib
import json
from datetime import datetime

class ValidadorStockPorEstado:
    """Validador de stock que considera el estado de valoración (VALORADO/NO VALORADO)"""
    
    def __init__(self):
        """Inicializar conexión a la base de datos"""
        try:
            self.conexion = mysql.connector.connect(
                host='localhost',
                user='root',
                password='732137A031E4b@',
                database='capired'
            )
            print("✅ Conexión establecida con la base de datos")
        except Error as e:
            print(f"❌ Error conectando a la base de datos: {e}")
            self.conexion = None
    
    def validar_stock_por_estado(self, items_dict, estados_dict):
        """Validar stock disponible considerando el estado de valoración
        
        Args:
            items_dict (dict): Diccionario con elementos y cantidades {elemento: cantidad}
            estados_dict (dict): Diccionario con estados de valoración {elemento: 'VALORADO'/'NO VALORADO'}
            
        Returns:
            tuple: (es_valido, mensaje, stock_actual)
        """
        if not self.conexion:
            return False, "Error de conexión a la base de datos", {}
        
        try:
            cursor = self.conexion.cursor(dictionary=True)
            
            stock_insuficiente = []
            stock_actual = {}
            
            for elemento, cantidad_solicitada in items_dict.items():
                if cantidad_solicitada > 0:
                    estado = estados_dict.get(elemento, 'VALORADO')  # Default a VALORADO
                    
                    # Calcular stock disponible por estado
                    stock_disponible = self._calcular_stock_por_estado(cursor, elemento, estado)
                    stock_actual[f"{elemento}_{estado}"] = stock_disponible
                    
                    if stock_disponible < cantidad_solicitada:
                        stock_insuficiente.append({
                            'elemento': elemento,
                            'estado': estado,
                            'solicitado': cantidad_solicitada,
                            'disponible': stock_disponible,
                            'faltante': cantidad_solicitada - stock_disponible
                        })
            
            cursor.close()
            
            if stock_insuficiente:
                mensaje = "Stock insuficiente para los siguientes elementos:\n"
                for item in stock_insuficiente:
                    mensaje += f"- {item['elemento']} ({item['estado']}): Solicitado {item['solicitado']}, Disponible {item['disponible']}, Faltante {item['faltante']}\n"
                return False, mensaje, stock_actual
            
            return True, "Stock suficiente para todos los elementos", stock_actual
            
        except Exception as e:
            return False, f"Error validando stock por estado: {e}", {}
    
    def _calcular_stock_por_estado(self, cursor, elemento, estado):
        """Calcular stock disponible para un elemento específico y su estado
        
        Args:
            cursor: Cursor de la base de datos
            elemento (str): Nombre del elemento
            estado (str): Estado de valoración ('VALORADO' o 'NO VALORADO')
            
        Returns:
            int: Stock disponible
        """
        try:
            # Obtener el nombre correcto de la columna para buscar en ingresos_dotaciones
            nombre_columna = self._obtener_nombre_columna(elemento)
            
            # Para camiseta polo, buscar ambas variantes: 'camisetapolo' y 'camiseta_polo'
            if elemento in ['camiseta_polo', 'camisetapolo']:
                cursor.execute("""
                    SELECT COALESCE(SUM(cantidad), 0) as stock_ingresos
                    FROM ingresos_dotaciones 
                    WHERE (tipo_elemento = 'camisetapolo' OR tipo_elemento = 'camiseta_polo') 
                    AND estado = %s
                """, (estado,))
            else:
                # Obtener ingresos por estado para otros elementos
                cursor.execute("""
                    SELECT COALESCE(SUM(cantidad), 0) as stock_ingresos
                    FROM ingresos_dotaciones 
                    WHERE tipo_elemento = %s AND estado = %s
                """, (nombre_columna, estado))
            
            ingresos_result = cursor.fetchone()
            stock_ingresos = ingresos_result['stock_ingresos'] if ingresos_result else 0
            
            # Obtener salidas por estado desde dotaciones
            campo_estado_dotaciones = self._obtener_campo_estado(elemento, 'dotaciones')
            campo_cantidad = self._obtener_nombre_columna(elemento)
            
            query_dotaciones = f"""
                SELECT COALESCE(SUM({campo_cantidad}), 0) as total_dotaciones
                FROM dotaciones 
                WHERE {campo_estado_dotaciones} = %s AND {campo_cantidad} IS NOT NULL AND {campo_cantidad} > 0
            """
            
            cursor.execute(query_dotaciones, (estado,))
            dotaciones_result = cursor.fetchone()
            stock_dotaciones = dotaciones_result['total_dotaciones'] if dotaciones_result else 0
            
            # Obtener salidas por estado desde cambios_dotacion
            campo_estado_cambios = self._obtener_campo_estado(elemento, 'cambios_dotacion')
            
            query_cambios = f"""
                SELECT COALESCE(SUM({campo_cantidad}), 0) as total_cambios
                FROM cambios_dotacion 
                WHERE {campo_estado_cambios} = %s AND {campo_cantidad} IS NOT NULL AND {campo_cantidad} > 0
            """
            
            cursor.execute(query_cambios, (estado,))
            cambios_result = cursor.fetchone()
            stock_cambios = cambios_result['total_cambios'] if cambios_result else 0
            
            # Calcular stock disponible
            stock_disponible = stock_ingresos - stock_dotaciones - stock_cambios
            
            return max(0, stock_disponible)  # No permitir stock negativo
            
        except Exception as e:
            print(f"Error calculando stock para {elemento} ({estado}): {e}")
            return 0
    
    def _obtener_campo_estado(self, elemento, tabla='dotaciones'):
        """Obtener el nombre del campo de estado para un elemento
        
        Args:
            elemento (str): Nombre del elemento
            tabla (str): Nombre de la tabla ('dotaciones' o 'cambios_dotacion')
            
        Returns:
            str: Nombre del campo de estado en la base de datos
        """
        # Mapeo para tabla dotaciones
        mapeo_dotaciones = {
            'pantalon': 'estado_pantalon',
            'camisetagris': 'estado_camisetagris',
            'camiseta_gris': 'estado_camisetagris',
            'guerrera': 'estado_guerrera',
            'camisetapolo': 'estado_camiseta_polo',
            'camiseta_polo': 'estado_camiseta_polo',
            'guantes_nitrilo': 'estado_guantes_nitrilo',
            'guantes_carnaza': 'estado_guantes_carnaza',
            'gafas': 'estado_gafas',
            'gorra': 'estado_gorra',
            'casco': 'estado_casco',
            'botas': 'estado_botas'
        }
        
        # Mapeo para tabla cambios_dotacion (tiene nombres diferentes)
        mapeo_cambios = {
            'pantalon': 'estado_pantalon',
            'camisetagris': 'estado_camiseta_gris',  # Diferente en cambios_dotacion
            'camiseta_gris': 'estado_camiseta_gris',
            'guerrera': 'estado_guerrera',
            'camisetapolo': 'estado_camiseta_polo',
            'camiseta_polo': 'estado_camiseta_polo',
            'guantes_nitrilo': 'estado_guantes_nitrilo',
            'guantes_carnaza': 'estado_guantes_carnaza',
            'gafas': 'estado_gafas',
            'gorra': 'estado_gorra',
            'casco': 'estado_casco',
            'botas': 'estado_botas'
        }
        
        if tabla == 'cambios_dotacion':
            return mapeo_cambios.get(elemento, f'estado_{elemento}')
        else:
            return mapeo_dotaciones.get(elemento, f'estado_{elemento}')
    
    def _obtener_nombre_columna(self, elemento):
        """Obtener el nombre correcto de la columna para un elemento
        
        Args:
            elemento (str): Nombre del elemento
            
        Returns:
            str: Nombre de la columna en las tablas dotaciones/cambios_dotacion
        """
        # Mapeo de elementos a nombres de columnas
        mapeo_columnas = {
            'camiseta_gris': 'camisetagris',
            'camiseta_polo': 'camisetapolo',
            'camisetagris': 'camisetagris',
            'camisetapolo': 'camisetapolo',
            'pantalon': 'pantalon',
            'guerrera': 'guerrera',
            'guantes_nitrilo': 'guantes_nitrilo',
            'guantes_carnaza': 'guantes_carnaza',
            'gafas': 'gafas',
            'gorra': 'gorra',
            'casco': 'casco',
            'botas': 'botas'
        }
        
        return mapeo_columnas.get(elemento, elemento)
    
    def validar_asignacion_con_estados(self, id_codigo_consumidor, items_dict, estados_dict):
        """Validar una asignación completa considerando estados de valoración
        
        Args:
            id_codigo_consumidor (int): ID del código consumidor
            items_dict (dict): Elementos y cantidades
            estados_dict (dict): Estados de valoración por elemento
            
        Returns:
            tuple: (es_valido, mensaje_detallado)
        """
        print(f"\n=== VALIDANDO ASIGNACIÓN CON ESTADOS ===")
        print(f"ID Código Consumidor: {id_codigo_consumidor}")
        print(f"Items: {items_dict}")
        print(f"Estados: {estados_dict}")
        
        # Validar stock por estado
        stock_valido, stock_mensaje, stock_actual = self.validar_stock_por_estado(items_dict, estados_dict)
        
        if not stock_valido:
            print(f"❌ Validación de stock: {stock_mensaje}")
            return False, stock_mensaje
        
        print(f"✅ Validación de stock: {stock_mensaje}")
        print(f"📊 Stock actual: {stock_actual}")
        
        return True, {
            'mensaje': 'Validación exitosa - Stock suficiente por estado',
            'stock_actual': stock_actual
        }
    
    def obtener_stock_detallado_por_estado(self, elemento):
        """Obtener información detallada del stock por estado para un elemento
        
        Args:
            elemento (str): Nombre del elemento
            
        Returns:
            dict: Información detallada del stock
        """
        if not self.conexion:
            return {}
        
        try:
            cursor = self.conexion.cursor(dictionary=True)
            campo_estado_dotaciones = self._obtener_campo_estado(elemento, 'dotaciones')
            campo_estado_cambios = self._obtener_campo_estado(elemento, 'cambios_dotacion')
            
            resultado = {
                'elemento': elemento,
                'valorado': {
                    'ingresos': 0,
                    'dotaciones': 0,
                    'cambios': 0,
                    'disponible': 0
                },
                'no_valorado': {
                    'ingresos': 0,
                    'dotaciones': 0,
                    'cambios': 0,
                    'disponible': 0
                }
            }
            
            for estado in ['VALORADO', 'NO VALORADO']:
                estado_key = 'valorado' if estado == 'VALORADO' else 'no_valorado'
                
                # Ingresos - Para camiseta polo, buscar ambas variantes
                if elemento in ['camiseta_polo', 'camisetapolo']:
                    query_ingresos = """
                        SELECT COALESCE(SUM(cantidad), 0)
                        FROM ingresos_dotaciones 
                        WHERE (tipo_elemento = 'camisetapolo' OR tipo_elemento = 'camiseta_polo') 
                        AND estado = %s
                    """
                    cursor.execute(query_ingresos, (estado,))
                else:
                    query_ingresos = """
                        SELECT COALESCE(SUM(cantidad), 0)
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = %s AND estado = %s
                    """
                    cursor.execute(query_ingresos, (elemento, estado))
                ingresos = cursor.fetchone()['COALESCE(SUM(cantidad), 0)'] or 0
                resultado[estado_key]['ingresos'] = ingresos
                
                # Dotaciones - usar nombre de columna correcto
                nombre_columna_tabla = self._obtener_nombre_columna(elemento)
                query_dotaciones = f"""
                    SELECT COALESCE(SUM({nombre_columna_tabla}), 0)
                    FROM dotaciones 
                    WHERE {campo_estado_dotaciones} = %s
                """
                cursor.execute(query_dotaciones, (estado,))
                dotaciones = cursor.fetchone()[f'COALESCE(SUM({nombre_columna_tabla}), 0)'] or 0
                resultado[estado_key]['dotaciones'] = dotaciones
                
                # Cambios - usar nombre de columna correcto
                query_cambios = f"""
                    SELECT COALESCE(SUM({nombre_columna_tabla}), 0)
                    FROM cambios_dotacion 
                    WHERE {campo_estado_cambios} = %s
                """
                cursor.execute(query_cambios, (estado,))
                cambios = cursor.fetchone()[f'COALESCE(SUM({nombre_columna_tabla}), 0)'] or 0
                resultado[estado_key]['cambios'] = cambios
                
                # Disponible
                disponible = max(0, ingresos - dotaciones - cambios)
                resultado[estado_key]['disponible'] = disponible
            
            cursor.close()
            return resultado
            
        except Exception as e:
            print(f"Error obteniendo stock detallado para {elemento}: {e}")
            return {}
    
    def cerrar_conexion(self):
        """Cerrar conexión a la base de datos"""
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
            print("✅ Conexión cerrada")

def test_validacion_por_estado():
    """Función de prueba para validación por estado"""
    validador = ValidadorStockPorEstado()
    
    if not validador.conexion:
        print("❌ No se pudo establecer conexión")
        return
    
    # Datos de prueba
    items_test = {
        'botas': 1,
        'pantalon': 1
    }
    
    estados_test = {
        'botas': 'NO VALORADO',
        'pantalon': 'VALORADO'
    }
    
    print("\n=== PRUEBA DE VALIDACIÓN POR ESTADO ===")
    
    # Mostrar stock actual por estado
    for elemento in items_test.keys():
        stock_detallado = validador.obtener_stock_detallado_por_estado(elemento)
        print(f"\nStock {elemento}:")
        for estado, cantidad in stock_detallado.items():
            print(f"  {estado}: {cantidad} unidades")
    
    # Probar validación
    resultado = validador.validar_asignacion_con_estados(1, items_test, estados_test)
    print(f"\nResultado validación: {resultado}")
    
    validador.cerrar_conexion()

if __name__ == "__main__":
    test_validacion_por_estado()