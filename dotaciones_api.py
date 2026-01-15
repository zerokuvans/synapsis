#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de API para gestión de dotaciones
Sistema de Logística - Capired
"""

import mysql.connector
from flask import jsonify, request, render_template_string, render_template, session, redirect, url_for
from datetime import datetime
import json
import logging

# Importar sistema de validación por estado
from validacion_stock_por_estado import ValidadorStockPorEstado
from gestor_stock_con_validacion_estado import GestorStockConValidacionEstado

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
    'autocommit': True
}

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as e:
        logger.error(f"Error conectando a la base de datos: {e}")
        return None

def registrar_rutas_dotaciones(app):
    """Registrar todas las rutas del módulo de dotaciones"""
    
    def _is_authenticated():
        try:
            from flask_login import current_user  # type: ignore
            if getattr(current_user, 'is_authenticated', False):
                return True
        except Exception:
            pass
        return bool(session.get('user_id') or session.get('id_codigo_consumidor'))

    @app.route('/logistica/dotaciones')
    def dotaciones_page():
        """Página principal del módulo de dotaciones"""
        try:
            if not _is_authenticated():
                return redirect(url_for('auth.login')) if 'auth' in app.blueprints else redirect('/login')
            return render_template('modulos/logistica/dotaciones.html')
        except Exception as e:
            logger.error(f"Error cargando página de dotaciones: {e}")
            return f"<h1>Error interno del servidor: {e}</h1>", 500
    
    @app.route('/api/dotaciones', methods=['GET'])
    def obtener_dotaciones():
        """Obtener todas las dotaciones con información de técnicos"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Query para obtener dotaciones con información del técnico
            query = """
            SELECT 
                d.*,
                ro.nombre as tecnico_nombre,
                ro.recurso_operativo_cedula as tecnico_cedula,
                DATE_FORMAT(d.fecha_registro, '%Y-%m-%d %H:%i:%s') as fecha_registro
            FROM dotaciones d
            LEFT JOIN recurso_operativo ro ON d.id_codigo_consumidor = ro.id_codigo_consumidor
            ORDER BY d.id_dotacion DESC
            """
            
            cursor.execute(query)
            dotaciones = cursor.fetchall()
            
            # Convertir valores None a 0 para campos numéricos
            for dotacion in dotaciones:
                campos_numericos = [
                    'pantalon', 'camisetagris', 'guerrera', 'camisetapolo',
                    'guantes_nitrilo', 'guantes_carnaza', 'gafas', 'gorra', 'casco', 'botas'
                ]
                for campo in campos_numericos:
                    if dotacion.get(campo) is None:
                        dotacion[campo] = 0
            
            return jsonify({
                'success': True,
                'dotaciones': dotaciones,
                'total': len(dotaciones)
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo dotaciones: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/dotaciones/<int:id_dotacion>', methods=['GET'])
    def obtener_dotacion(id_dotacion):
        """Obtener una dotación específica por ID"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT 
                d.*,
                ro.nombre as tecnico_nombre,
                ro.recurso_operativo_cedula as tecnico_cedula
            FROM dotaciones d
            LEFT JOIN recurso_operativo ro ON d.id_codigo_consumidor = ro.id_codigo_consumidor
            WHERE d.id_dotacion = %s
            """
            
            cursor.execute(query, (id_dotacion,))
            dotacion = cursor.fetchone()
            
            if not dotacion:
                return jsonify({'success': False, 'message': 'Dotación no encontrada'}), 404
            
            # Convertir valores None a 0 para campos numéricos
            campos_numericos = [
                'pantalon', 'camisetagris', 'guerrera', 'camisetapolo',
                'guantes_nitrilo', 'guantes_carnaza', 'gafas', 'gorra', 'casco', 'botas'
            ]
            for campo in campos_numericos:
                if dotacion.get(campo) is None:
                    dotacion[campo] = 0
            
            return jsonify({
                'success': True,
                'dotacion': dotacion
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo dotación {id_dotacion}: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/dotacion_detalle/<int:id_dotacion>', methods=['GET'])
    def obtener_dotacion_detalle(id_dotacion):
        """Obtener detalles completos de una dotación específica para el modal de visualización"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT 
                d.*,
                ro.nombre as tecnico_nombre,
                ro.recurso_operativo_cedula as tecnico_cedula,
                d.cliente as cliente_nombre
            FROM dotaciones d
            LEFT JOIN recurso_operativo ro ON d.id_codigo_consumidor = ro.id_codigo_consumidor
            WHERE d.id_dotacion = %s
            """
            
            cursor.execute(query, (id_dotacion,))
            dotacion = cursor.fetchone()
            
            if not dotacion:
                return jsonify({'success': False, 'message': 'Dotación no encontrada'}), 404
            
            # Mapear campos para el frontend con nombres consistentes
            dotacion_detalle = {
                'id_dotacion': dotacion['id_dotacion'],
                'tecnico_nombre': dotacion['tecnico_nombre'] or 'No asignado',
                'tecnico_cedula': dotacion['tecnico_cedula'] or 'No disponible',
                'cliente_nombre': dotacion['cliente_nombre'] or 'No disponible',
                'fecha_registro': dotacion['fecha_registro'],
                
                # Elementos de ropa con cantidades, tallas y estados
                'pantalon_cantidad': dotacion.get('pantalon') or 0,
                'pantalon_talla': dotacion.get('pantalon_talla'),
                'pantalon_valorado': 1 if dotacion.get('estado_pantalon') == 'VALORADO' else 0,
                
                'camiseta_gris_cantidad': dotacion.get('camisetagris') or 0,
                'camiseta_gris_talla': dotacion.get('camiseta_gris_talla'),
                'camiseta_gris_valorado': 1 if dotacion.get('estado_camisetagris') == 'VALORADO' else 0,
                
                'guerrera_cantidad': dotacion.get('guerrera') or 0,
                'guerrera_talla': dotacion.get('guerrera_talla'),
                'guerrera_valorado': 1 if dotacion.get('estado_guerrera') == 'VALORADO' else 0,
                
                'chaqueta_cantidad': dotacion.get('chaqueta') or 0,
                'chaqueta_talla': dotacion.get('chaqueta_talla'),
                'chaqueta_valorado': 1 if dotacion.get('estado_chaqueta') == 'VALORADO' else 0,
                
                'camiseta_polo_cantidad': dotacion.get('camisetapolo') or 0,
                'camiseta_polo_talla': dotacion.get('camiseta_polo_talla'),
                'camisetapolo_valorado': 1 if dotacion.get('estado_camiseta_polo') == 'VALORADO' else 0,
                
                # EPP sin tallas
                'guantes_nitrilo_cantidad': dotacion.get('guantes_nitrilo') or 0,
                'guantes_nitrilo_valorado': 1 if dotacion.get('estado_guantes_nitrilo') == 'VALORADO' else 0,
                
                'guantes_carnaza_cantidad': dotacion.get('guantes_carnaza') or 0,
                'guantes_carnaza_valorado': 1 if dotacion.get('estado_guantes_carnaza') == 'VALORADO' else 0,
                
                'gafas_cantidad': dotacion.get('gafas') or 0,
                'gafas_valorado': 1 if dotacion.get('estado_gafas') == 'VALORADO' else 0,
                
                'gorra_cantidad': dotacion.get('gorra') or 0,
                'gorra_valorado': 1 if dotacion.get('estado_gorra') == 'VALORADO' else 0,
                
                'casco_cantidad': dotacion.get('casco') or 0,
                'casco_valorado': 1 if dotacion.get('estado_casco') == 'VALORADO' else 0,
                
                'botas_cantidad': dotacion.get('botas') or 0,
                'botas_talla': dotacion.get('botas_talla'),
                'botas_valorado': 1 if dotacion.get('estado_botas') == 'VALORADO' else 0
            }
            
            return jsonify({
                'success': True,
                'dotacion': dotacion_detalle
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo detalles de dotación {id_dotacion}: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/dotaciones', methods=['POST'])
    def crear_dotacion():
        """Crear una nueva dotación con validación por estado"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            data = request.get_json()
            
            # DEBUG: Log de los datos recibidos
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"=== DATOS RECIBIDOS EN CREAR_DOTACION [{timestamp}] ===")
            logger.info(f"Data completa: {json.dumps(data, indent=2)}")
            
            # DEBUG: Log específico de campos valorado
            valorado_fields = {k: v for k, v in data.items() if 'valorado' in k}
            logger.info(f"Campos valorado recibidos: {valorado_fields}")
            
            # Validar datos requeridos
            if not data.get('cliente'):
                return jsonify({'success': False, 'message': 'El campo cliente es requerido'}), 400
            
            # Preparar items con estados para validación
            items_con_estado = {}
            elementos = ['pantalon', 'camisetagris', 'guerrera', 'camisetapolo', 
                        'guantes_nitrilo', 'guantes_carnaza', 'gafas', 'gorra', 'casco', 'botas']
            
            for elemento in elementos:
                cantidad = data.get(elemento, 0)
                if cantidad and cantidad > 0:
                    # Mapear nombres de elementos para el validador
                    elemento_mapeado = elemento
                    if elemento == 'camisetagris':
                        elemento_mapeado = 'camiseta_gris'
                    elif elemento == 'camisetapolo':
                        elemento_mapeado = 'camiseta_polo'
                    
                    # Obtener el estado de valoración desde el campo _valorado
                    # Mapear correctamente los nombres de campos valorado
                    if elemento == 'camisetapolo':
                        valorado_key = 'camisetapolo_valorado'
                    elif elemento == 'camisetagris':
                        valorado_key = 'camiseta_gris_valorado'
                    else:
                        valorado_key = f'{elemento}_valorado'
                    
                    es_valorado = data.get(valorado_key, False)
                    estado = 'VALORADO' if es_valorado else 'NO VALORADO'
                    
                    # DEBUG: Log detallado del mapeo
                    logger.info(f"🔍 MAPEO ELEMENTO: {elemento}")
                    logger.info(f"   - Elemento mapeado: {elemento_mapeado}")
                    logger.info(f"   - Valorado key buscado: {valorado_key}")
                    logger.info(f"   - Valor encontrado: {es_valorado}")
                    logger.info(f"   - Estado final: {estado}")
                    logger.info(f"   - Cantidad: {cantidad}")
                    items_con_estado[elemento_mapeado] = (cantidad, estado)
            
            # DEBUG: Imprimir datos recibidos
            print(f"🔍 DEBUG - Datos recibidos: {data}")
            print(f"🔍 DEBUG - Items con estado: {items_con_estado}")
            
            # Validar stock por estado antes de crear la dotación
            if items_con_estado:
                validador = ValidadorStockPorEstado()
                
                # Separar items y estados para el validador
                items_dict = {k: v[0] for k, v in items_con_estado.items()}
                estados_dict = {k: v[1] for k, v in items_con_estado.items()}
                
                print(f"🔍 DEBUG - Items dict: {items_dict}")
                print(f"🔍 DEBUG - Estados dict: {estados_dict}")
                
                es_valido, resultado = validador.validar_asignacion_con_estados(
                    data.get('id_codigo_consumidor', 0), items_dict, estados_dict
                )
                
                if not es_valido:
                    return jsonify({
                        'success': False, 
                        'message': f'Stock insuficiente: {resultado}'
                    }), 400
            
            cursor = connection.cursor()
            
            # Preparar query de inserción
            query = """
            INSERT INTO dotaciones (
                cliente, id_codigo_consumidor, pantalon, pantalon_talla,
                camisetagris, camiseta_gris_talla, guerrera, guerrera_talla,
                chaqueta, chaqueta_talla, camisetapolo, camiseta_polo_talla, 
                guantes_nitrilo, guantes_carnaza, gafas, gorra, casco, botas, botas_talla,
                estado_pantalon, estado_camisetagris, estado_guerrera, estado_chaqueta,
                estado_camiseta_polo, estado_guantes_nitrilo, estado_guantes_carnaza, 
                estado_gafas, estado_gorra, estado_casco, estado_botas, fecha_registro
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
            )
            """
            
            valores = (
                data.get('cliente'),
                data.get('id_codigo_consumidor'),
                data.get('pantalon'),
                data.get('pantalon_talla'),
                data.get('camisetagris'),
                data.get('camiseta_gris_talla'),
                data.get('guerrera'),
                data.get('guerrera_talla'),
                data.get('chaqueta'),
                data.get('chaqueta_talla'),
                data.get('camisetapolo'),
                data.get('camiseta_polo_talla'),
                data.get('guantes_nitrilo'),
                data.get('guantes_carnaza'),
                data.get('gafas'),
                data.get('gorra'),
                data.get('casco'),
                data.get('botas'),
                data.get('botas_talla'),
                # Estados de valoración - convertir de _valorado a texto
                'VALORADO' if data.get('pantalon_valorado') else 'NO VALORADO',
                'VALORADO' if data.get('camiseta_gris_valorado') else 'NO VALORADO',
                'VALORADO' if data.get('guerrera_valorado') else 'NO VALORADO',
                'VALORADO' if data.get('chaqueta_valorado') else 'NO VALORADO',
                'VALORADO' if data.get('camisetapolo_valorado') else 'NO VALORADO',
                'VALORADO' if data.get('guantes_nitrilo_valorado') else 'NO VALORADO',
                'VALORADO' if data.get('guantes_carnaza_valorado') else 'NO VALORADO',
                'VALORADO' if data.get('gafas_valorado') else 'NO VALORADO',
                'VALORADO' if data.get('gorra_valorado') else 'NO VALORADO',
                'VALORADO' if data.get('casco_valorado') else 'NO VALORADO',
                'VALORADO' if data.get('botas_valorado') else 'NO VALORADO'
            )
            
            cursor.execute(query, valores)
            id_dotacion = cursor.lastrowid
            
            # Procesar stock con validación por estado después de crear la dotación
            if items_con_estado:
                try:
                    gestor = GestorStockConValidacionEstado()
                    
                    # Preparar datos para el gestor
                    items_dict = {k: v[0] for k, v in items_con_estado.items()}
                    estados_dict = {k: v[1] for k, v in items_con_estado.items()}
                    
                    # Procesar asignación con estado
                    exito_stock, mensaje_stock = gestor.procesar_asignacion_dotacion_con_estado(
                        data.get('id_codigo_consumidor', 0), items_dict, estados_dict
                    )
                    
                    if not exito_stock:
                        logger.warning(f"Advertencia en procesamiento de stock para dotación {id_dotacion}: {mensaje_stock}")
                    else:
                        logger.info(f"Stock procesado correctamente para dotación {id_dotacion}")
                        
                except Exception as e:
                    logger.error(f"Error procesando stock para dotación {id_dotacion}: {e}")
                    # No fallar la creación de la dotación por errores de stock
            
            logger.info(f"Dotación creada con ID: {id_dotacion}")
            
            return jsonify({
                'success': True,
                'message': 'Dotación creada correctamente',
                'id_dotacion': id_dotacion
            }), 201
            
        except mysql.connector.Error as e:
            logger.error(f"Error creando dotación: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/cambios_dotacion', methods=['POST'])
    def crear_cambio_dotacion():
        """Crear un nuevo cambio de dotación con validación por estado"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            data = request.get_json()
            
            # Validaciones básicas
            id_codigo_consumidor = data.get('id_codigo_consumidor')
            fecha_cambio = data.get('fecha_cambio')
            
            if not id_codigo_consumidor or not fecha_cambio:
                return jsonify({
                    'success': False, 
                    'message': 'Técnico y fecha son campos obligatorios'
                }), 400
            
            cursor = connection.cursor(dictionary=True)
            
            # Mapeo de elementos con sus datos
            elementos_dotacion = {
                'pantalon': {
                    'cantidad': data.get('pantalon'),
                    'talla': data.get('pantalon_talla'),
                    'valorado': data.get('pantalon_valorado', False)
                },
                'camisetagris': {
                    'cantidad': data.get('camisetagris'),
                    'talla': data.get('camiseta_gris_talla'),
                    'valorado': data.get('camisetagris_valorado', False)
                },
                'guerrera': {
                    'cantidad': data.get('guerrera'),
                    'talla': data.get('guerrera_talla'),
                    'valorado': data.get('guerrera_valorado', False)
                },
                'chaqueta': {
                    'cantidad': data.get('chaqueta'),
                    'talla': data.get('chaqueta_talla'),
                    'valorado': data.get('chaqueta_valorado', False)
                },
                'camisetapolo': {
                    'cantidad': data.get('camisetapolo'),
                    'talla': data.get('camiseta_polo_talla'),
                    'valorado': data.get('camisetapolo_valorado', False)
                },
                'guantes_nitrilo': {
                    'cantidad': data.get('guantes_nitrilo'),
                    'talla': None,
                    'valorado': data.get('guantes_nitrilo_valorado', False)
                },
                'guantes_carnaza': {
                    'cantidad': data.get('guantes_carnaza'),
                    'talla': None,
                    'valorado': data.get('guantes_carnaza_valorado', False)
                },
                'gafas': {
                    'cantidad': data.get('gafas'),
                    'talla': None,
                    'valorado': data.get('gafas_valorado', False)
                },
                'gorra': {
                    'cantidad': data.get('gorra'),
                    'talla': None,
                    'valorado': data.get('gorra_valorado', False)
                },
                'casco': {
                    'cantidad': data.get('casco'),
                    'talla': None,
                    'valorado': data.get('casco_valorado', False)
                },
                'botas': {
                    'cantidad': data.get('botas'),
                    'talla': data.get('botas_talla'),
                    'valorado': data.get('botas_valorado', False)
                }
            }
            
            # DEBUG: Imprimir todos los valores recibidos
            print(f"\n🔍 DEBUG CREAR_DOTACION - {datetime.now().strftime('%H:%M:%S')}")
            print("📦 ELEMENTOS RECIBIDOS:")
            for elemento, datos in elementos_dotacion.items():
                print(f"  {elemento}: cantidad={datos['cantidad']} (tipo: {type(datos['cantidad'])}), valorado={datos['valorado']}")
            
            # Validar stock disponible con lógica inteligente (usar ambos estados si es necesario)
            errores_stock = []
            elementos_con_stock_mixto = []
            
            for elemento, datos in elementos_dotacion.items():
                cantidad = datos['cantidad']
                print(f"🔍 Evaluando {elemento}: cantidad={cantidad}, tipo={type(cantidad)}, es_none={cantidad is None}, es_mayor_0={cantidad > 0 if cantidad is not None else 'N/A'}")
                if cantidad is not None and cantidad > 0:
                    
                    # Verificar stock disponible en ambos estados
                    es_valorado = datos['valorado']
                    tipo_stock_preferido = "VALORADO" if es_valorado else "NO VALORADO"
                    tipo_stock_alternativo = "NO VALORADO" if es_valorado else "VALORADO"
                    
                    # Función auxiliar para obtener stock de un estado específico
                    def obtener_stock_por_estado(tipo_estado):
                        # Obtener ingresos
                        cursor.execute("""
                            SELECT COALESCE(SUM(cantidad), 0) as stock_disponible
                            FROM ingresos_dotaciones 
                            WHERE tipo_elemento = %s AND estado = %s
                        """, (elemento, tipo_estado))
                        
                        ingresos_result = cursor.fetchone()
                        stock_ingresos = ingresos_result['stock_disponible'] if ingresos_result else 0
                        
                        # Obtener salidas
                        cursor.execute("""
                            SELECT COALESCE(SUM(
                                CASE 
                                    WHEN %s = 'pantalon' AND estado_pantalon = %s THEN pantalon
                                    WHEN %s = 'camisetagris' AND estado_camiseta_gris = %s THEN camisetagris
                                    WHEN %s = 'guerrera' AND estado_guerrera = %s THEN guerrera
                                    WHEN %s = 'chaqueta' AND estado_chaqueta = %s THEN chaqueta
                                    WHEN %s = 'camisetapolo' AND estado_camiseta_polo = %s THEN camisetapolo
                                    WHEN %s = 'guantes_nitrilo' AND estado_guantes_nitrilo = %s THEN guantes_nitrilo
                                    WHEN %s = 'guantes_carnaza' AND estado_guantes_carnaza = %s THEN guantes_carnaza
                                    WHEN %s = 'gafas' AND estado_gafas = %s THEN gafas
                                    WHEN %s = 'gorra' AND estado_gorra = %s THEN gorra
                                    WHEN %s = 'casco' AND estado_casco = %s THEN casco
                                    WHEN %s = 'botas' AND estado_botas = %s THEN botas
                                    ELSE 0
                                END
                            ), 0) as total_salidas
                            FROM cambios_dotacion
                        """, (elemento, tipo_estado, elemento, tipo_estado, elemento, tipo_estado, 
                              elemento, tipo_estado, elemento, tipo_estado, elemento, tipo_estado,
                              elemento, tipo_estado, elemento, tipo_estado, elemento, tipo_estado,
                              elemento, tipo_estado, elemento, tipo_estado))
                        
                        salidas_result = cursor.fetchone()
                        stock_salidas = salidas_result['total_salidas'] if salidas_result else 0
                        
                        return stock_ingresos - stock_salidas
                    
                    # Obtener stock de ambos estados
                    stock_preferido = obtener_stock_por_estado(tipo_stock_preferido)
                    stock_alternativo = obtener_stock_por_estado(tipo_stock_alternativo)
                    stock_total = stock_preferido + stock_alternativo
                    
                    # Lógica inteligente de validación
                    if cantidad > stock_total:
                        # No hay stock suficiente en ningún estado
                        nombre_elemento = elemento.replace('_', ' ').title()
                        errores_stock.append(
                            f"{nombre_elemento}: Stock insuficiente total. "
                            f"Solicitado: {cantidad}, Disponible: {stock_total} "
                            f"({tipo_stock_preferido}: {stock_preferido}, {tipo_stock_alternativo}: {stock_alternativo})"
                        )
                    elif cantidad > stock_preferido and stock_alternativo > 0:
                        # Usar stock mixto - registrar para logging
                        nombre_elemento = elemento.replace('_', ' ').title()
                        stock_del_preferido = min(stock_preferido, cantidad)
                        stock_del_alternativo = cantidad - stock_del_preferido
                        
                        elementos_con_stock_mixto.append({
                            'elemento': nombre_elemento,
                            'cantidad_total': cantidad,
                            'stock_preferido': stock_del_preferido,
                            'tipo_preferido': tipo_stock_preferido,
                            'stock_alternativo': stock_del_alternativo,
                            'tipo_alternativo': tipo_stock_alternativo
                        })
                        
                        logger.info(
                            f"Stock mixto para {nombre_elemento}: "
                            f"{stock_del_preferido} de {tipo_stock_preferido} + "
                            f"{stock_del_alternativo} de {tipo_stock_alternativo}"
                        )
                    else:
                        # Hay stock suficiente en el estado preferido
                        logger.info(f"Stock suficiente para {elemento.replace('_', ' ').title()}: {cantidad} de {tipo_stock_preferido}")
            
            # Si hay errores de stock total insuficiente, rechazar la operación
            if errores_stock:
                return jsonify({
                    'success': False,
                    'message': 'Stock insuficiente total',
                    'errors': errores_stock
                }), 400
            
            # Comentado: No bloquear operaciones por stock insuficiente
            # if errores_stock:
            #     return jsonify({
            #         'success': False,
            #         'message': 'Stock insuficiente',
            #         'errors': errores_stock
            #     }), 400
            
            # Procesar el cambio de dotación
            query_cambio = """
                INSERT INTO cambios_dotacion (
                    id_codigo_consumidor, fecha_cambio, pantalon, pantalon_talla, estado_pantalon,
                    camisetagris, camiseta_gris_talla, estado_camiseta_gris, guerrera, guerrera_talla, estado_guerrera,
                    camisetapolo, camiseta_polo_talla, estado_camiseta_polo, 
                    guantes_nitrilo, estado_guantes_nitrilo, guantes_carnaza, estado_guantes_carnaza, 
                    gafas, estado_gafas, gorra, estado_gorra, casco, estado_casco, botas, botas_talla, estado_botas, observaciones
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            # Función auxiliar para manejar tallas vacías
            def procesar_talla(talla):
                return None if talla == "" or talla is None else talla
            
            cursor.execute(query_cambio, (
                id_codigo_consumidor, fecha_cambio, 
                elementos_dotacion['pantalon']['cantidad'], procesar_talla(elementos_dotacion['pantalon']['talla']), 
                'VALORADO' if elementos_dotacion['pantalon']['valorado'] else 'NO VALORADO',
                elementos_dotacion['camisetagris']['cantidad'], procesar_talla(elementos_dotacion['camisetagris']['talla']),
                'VALORADO' if elementos_dotacion['camisetagris']['valorado'] else 'NO VALORADO',
                elementos_dotacion['guerrera']['cantidad'], procesar_talla(elementos_dotacion['guerrera']['talla']),
                'VALORADO' if elementos_dotacion['guerrera']['valorado'] else 'NO VALORADO',
                elementos_dotacion['camisetapolo']['cantidad'], procesar_talla(elementos_dotacion['camisetapolo']['talla']),
                'VALORADO' if elementos_dotacion['camisetapolo']['valorado'] else 'NO VALORADO',
                elementos_dotacion['guantes_nitrilo']['cantidad'], 
                'VALORADO' if elementos_dotacion['guantes_nitrilo']['valorado'] else 'NO VALORADO',
                elementos_dotacion['guantes_carnaza']['cantidad'],
                'VALORADO' if elementos_dotacion['guantes_carnaza']['valorado'] else 'NO VALORADO',
                elementos_dotacion['gafas']['cantidad'],
                'VALORADO' if elementos_dotacion['gafas']['valorado'] else 'NO VALORADO',
                elementos_dotacion['gorra']['cantidad'],
                'VALORADO' if elementos_dotacion['gorra']['valorado'] else 'NO VALORADO',
                elementos_dotacion['casco']['cantidad'],
                'VALORADO' if elementos_dotacion['casco']['valorado'] else 'NO VALORADO',
                elementos_dotacion['botas']['cantidad'], procesar_talla(elementos_dotacion['botas']['talla']),
                'VALORADO' if elementos_dotacion['botas']['valorado'] else 'NO VALORADO',
                data.get('observaciones', '')
            ))
            
            id_cambio = cursor.lastrowid
            connection.commit()
            
            # Preparar mensaje de éxito con detalles de estado valorado y stock mixto
            elementos_procesados = []
            advertencias_stock_mixto = []
            
            for elemento, datos in elementos_dotacion.items():
                cantidad = datos['cantidad']
                if cantidad is not None and cantidad > 0:
                    estado_valorado = "VALORADO" if datos['valorado'] else "NO VALORADO"
                    nombre_elemento = elemento.replace('_', ' ').title()
                    
                    # Verificar si este elemento usó stock mixto
                    elemento_mixto = next((item for item in elementos_con_stock_mixto if item['elemento'] == nombre_elemento), None)
                    
                    if elemento_mixto:
                        elementos_procesados.append(f"{nombre_elemento}: {cantidad} (Stock mixto)")
                        advertencias_stock_mixto.append(
                            f"{nombre_elemento}: {elemento_mixto['stock_preferido']} de {elemento_mixto['tipo_preferido']} + "
                            f"{elemento_mixto['stock_alternativo']} de {elemento_mixto['tipo_alternativo']}"
                        )
                    else:
                        elementos_procesados.append(f"{nombre_elemento}: {cantidad} ({estado_valorado})")
            
            # Construir mensaje final
            mensaje_base = f'Cambio de dotación registrado exitosamente. Elementos procesados: {", ".join(elementos_procesados)}'
            
            if advertencias_stock_mixto:
                mensaje_base += f'. NOTA: Se utilizó stock mixto para: {"; ".join(advertencias_stock_mixto)}'
            
            return jsonify({
                'success': True,
                'message': mensaje_base,
                'id_cambio': id_cambio,
                'stock_mixto_usado': len(elementos_con_stock_mixto) > 0,
                'detalles_stock_mixto': elementos_con_stock_mixto
            }), 201
            
        except mysql.connector.Error as e:
            logger.error(f"Error creando cambio de dotación: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/stock_por_estado', methods=['GET'])
    def obtener_stock_por_estado():
        """Obtener stock disponible por elemento y estado de valoración"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Lista de elementos de dotación
            elementos = ['pantalon', 'camisetagris', 'guerrera', 'camisetapolo', 
                        'guantes_nitrilo', 'guantes_carnaza', 'gafas', 'gorra', 'casco', 'botas', 'chaqueta']
            
            stock_por_estado = {}
            
            # Mapeo de elementos a sus columnas de estado correspondientes
            # Nota: dotaciones usa estado_camisetagris, cambios_dotacion usa estado_camiseta_gris
            estado_columns_dotaciones = {
                'pantalon': 'estado_pantalon',
                'camisetagris': 'estado_camisetagris',
                'guerrera': 'estado_guerrera',
                'camisetapolo': 'estado_camiseta_polo',
                'guantes_nitrilo': 'estado_guantes_nitrilo',
                'guantes_carnaza': 'estado_guantes_carnaza',
                'gafas': 'estado_gafas',
                'gorra': 'estado_gorra',
                'casco': 'estado_casco',
                'botas': 'estado_botas',
                'chaqueta': 'estado_chaqueta'
            }
            
            estado_columns_cambios = {
                'pantalon': 'estado_pantalon',
                'camisetagris': 'estado_camiseta_gris',
                'guerrera': 'estado_guerrera',
                'camisetapolo': 'estado_camiseta_polo',
                'guantes_nitrilo': 'estado_guantes_nitrilo',
                'guantes_carnaza': 'estado_guantes_carnaza',
                'gafas': 'estado_gafas',
                'gorra': 'estado_gorra',
                'casco': 'estado_casco',
                'botas': 'estado_botas',
                'chaqueta': 'estado_chaqueta'
            }
            
            for elemento in elementos:
                stock_por_estado[elemento] = {
                    'VALORADO': 0,
                    'NO VALORADO': 0
                }
                
                estado_column_dotaciones = estado_columns_dotaciones.get(elemento, f'estado_{elemento}')
                estado_column_cambios = estado_columns_cambios.get(elemento, f'estado_{elemento}')
                
                # Obtener ingresos por estado
                for estado in ['VALORADO', 'NO VALORADO']:
                    cursor.execute("""
                        SELECT COALESCE(SUM(cantidad), 0) as total_ingresos
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = %s AND estado = %s
                    """, (elemento, estado))
                    
                    ingresos_result = cursor.fetchone()
                    total_ingresos = ingresos_result['total_ingresos'] if ingresos_result else 0
                    
                    # Obtener salidas de dotaciones por estado
                    cursor.execute(f"""
                        SELECT COALESCE(SUM(
                            CASE WHEN {estado_column_dotaciones} = %s THEN {elemento} ELSE 0 END
                        ), 0) as total_dotaciones
                        FROM dotaciones
                        WHERE {elemento} IS NOT NULL AND {elemento} > 0
                    """, (estado,))
                    
                    dotaciones_result = cursor.fetchone()
                    total_dotaciones = dotaciones_result['total_dotaciones'] if dotaciones_result else 0
                    
                    # Obtener salidas de cambios por estado
                    cursor.execute(f"""
                        SELECT COALESCE(SUM(
                            CASE WHEN {estado_column_cambios} = %s THEN {elemento} ELSE 0 END
                        ), 0) as total_cambios
                        FROM cambios_dotacion
                        WHERE {elemento} IS NOT NULL AND {elemento} > 0
                    """, (estado,))
                    
                    cambios_result = cursor.fetchone()
                    total_cambios = cambios_result['total_cambios'] if cambios_result else 0
                    
                    # Calcular stock disponible
                    stock_disponible = total_ingresos - total_dotaciones - total_cambios
                    stock_por_estado[elemento][estado] = max(0, stock_disponible)
            
            return jsonify({
                'success': True,
                'stock_por_estado': stock_por_estado
            }), 200
            
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo stock por estado: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/dotaciones/<int:id_dotacion>', methods=['PUT'])
    def actualizar_dotacion(id_dotacion):
        """Actualizar una dotación existente con integración de stock"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            data = request.get_json()
            
            # Validar que la dotación existe y obtener datos originales
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM dotaciones WHERE id_dotacion = %s
            """, (id_dotacion,))
            dotacion_original = cursor.fetchone()
            
            if not dotacion_original:
                return jsonify({'success': False, 'message': 'Dotación no encontrada'}), 404
            
            # Calcular diferencias para gestión de stock
            elementos_stock = ['pantalon', 'camisetagris', 'guerrera', 'camisetapolo', 'chaqueta', 
                             'guantes_nitrilo', 'guantes_carnaza', 'gafas', 'gorra', 'casco', 'botas']
            
            cambios_stock = {}
            items_con_estado = {}
            
            for elemento in elementos_stock:
                cantidad_original = dotacion_original.get(elemento, 0) or 0
                cantidad_nueva = data.get(elemento, 0) or 0
                diferencia = cantidad_nueva - cantidad_original
                
                if diferencia != 0:
                    # Determinar el estado de valoración
                    campo_estado = f'estado_{elemento}' if elemento != 'camisetagris' else 'estado_camisetagris'
                    if elemento == 'camisetapolo':
                        campo_estado = 'estado_camiseta_polo'
                    elif elemento == 'camisetagris':
                        campo_estado = 'estado_camisetagris'
                    
                    # Obtener estado desde los datos enviados
                    estado_valorado = data.get(f'{elemento}_valorado', False)
                    if elemento == 'camisetagris':
                        estado_valorado = data.get('camisetagris_valorado', False)
                    elif elemento == 'camisetapolo':
                        estado_valorado = data.get('camiseta_polo_valorado', False)
                    
                    estado = 'VALORADO' if estado_valorado else 'NO VALORADO'
                    
                    cambios_stock[elemento] = {
                        'diferencia': diferencia,
                        'estado': estado,
                        'cantidad_nueva': cantidad_nueva
                    }
                    
                    # Si es un incremento, necesitamos validar stock
                    if diferencia > 0:
                        items_con_estado[elemento] = (diferencia, estado)
            
            # Validar stock para incrementos
            if items_con_estado:
                validador = ValidadorStockPorEstado()
                items_dict = {k: v[0] for k, v in items_con_estado.items()}
                estados_dict = {k: v[1] for k, v in items_con_estado.items()}
                
                es_valido, resultado = validador.validar_asignacion_con_estados(
                    data.get('id_codigo_consumidor', 0), items_dict, estados_dict
                )
                
                if not es_valido:
                    return jsonify({
                        'success': False, 
                        'message': f'Stock insuficiente para los cambios: {resultado}'
                    }), 400
            
            # Preparar query de actualización
            query = """
            UPDATE dotaciones SET
                cliente = %s,
                id_codigo_consumidor = %s,
                pantalon = %s,
                pantalon_talla = %s,
                camisetagris = %s,
                camiseta_gris_talla = %s,
                guerrera = %s,
                guerrera_talla = %s,
                camisetapolo = %s,
                camiseta_polo_talla = %s,
                chaqueta = %s,
                chaqueta_talla = %s,
                guantes_nitrilo = %s,
                guantes_carnaza = %s,
                gafas = %s,
                gorra = %s,
                casco = %s,
                botas = %s,
                botas_talla = %s,
                estado_pantalon = %s,
                estado_camisetagris = %s,
                estado_guerrera = %s,
                estado_camiseta_polo = %s,
                estado_chaqueta = %s,
                estado_guantes_nitrilo = %s,
                estado_guantes_carnaza = %s,
                estado_gafas = %s,
                estado_gorra = %s,
                estado_casco = %s,
                estado_botas = %s,
                fecha_actualizacion = NOW()
            WHERE id_dotacion = %s
            """
            
            valores = (
                data.get('cliente'),
                data.get('id_codigo_consumidor'),
                data.get('pantalon'),
                data.get('pantalon_talla'),
                data.get('camisetagris'),
                data.get('camiseta_gris_talla'),
                data.get('guerrera'),
                data.get('guerrera_talla'),
                data.get('camisetapolo'),
                data.get('camiseta_polo_talla'),
                data.get('chaqueta'),
                data.get('chaqueta_talla'),
                data.get('guantes_nitrilo'),
                data.get('guantes_carnaza'),
                data.get('gafas'),
                data.get('gorra'),
                data.get('casco'),
                data.get('botas'),
                data.get('botas_talla'),
                # Estados de valoración - respetar exactamente lo que envía el frontend
                data.get('estado_pantalon'),
                data.get('estado_camisetagris'),
                data.get('estado_guerrera'),
                data.get('estado_camiseta_polo'),
                'VALORADO' if data.get('chaqueta_valorado') else 'NO VALORADO',  # Convertir boolean a formato de estado
                data.get('estado_guantes_nitrilo'),
                data.get('estado_guantes_carnaza'),
                data.get('estado_gafas'),
                data.get('estado_gorra'),
                data.get('estado_casco'),
                data.get('estado_botas'),
                id_dotacion
            )
            
            cursor.execute(query, valores)
            connection.commit()
            
            # Procesar movimientos de stock después de actualizar la dotación
            if cambios_stock:
                try:
                    gestor = GestorStockConValidacionEstado()
                    movimientos_procesados = []
                    
                    for elemento, cambio in cambios_stock.items():
                        diferencia = cambio['diferencia']
                        estado = cambio['estado']
                        
                        # Debug logging específico para chaquetas
                        if elemento == 'chaqueta':
                            logger.info(f"🧥 PROCESANDO CHAQUETA - Dotación {id_dotacion}: diferencia={diferencia}, estado={estado}, talla={data.get('chaqueta_talla', 'N/A')}")
                        
                        if diferencia > 0:
                            # Incremento: asignar más elementos (descontar del stock)
                            if elemento == 'chaqueta':
                                logger.info(f"🧥 ASIGNANDO CHAQUETA: {diferencia} unidades {estado} para técnico {data.get('id_codigo_consumidor', 0)}")
                            
                            exito, mensaje = gestor._registrar_movimiento_con_estado(
                                elemento, diferencia, estado, 'asignacion', 
                                data.get('id_codigo_consumidor', 0), f'UPDATE_DOTACION_{id_dotacion}'
                            )
                            if exito:
                                movimientos_procesados.append(f"Asignado {diferencia} {elemento} {estado}")
                                if elemento == 'chaqueta':
                                    logger.info(f"🧥 ✅ CHAQUETA ASIGNADA EXITOSAMENTE: {mensaje}")
                            else:
                                logger.warning(f"Error procesando incremento de {elemento}: {mensaje}")
                                if elemento == 'chaqueta':
                                    logger.error(f"🧥 ❌ ERROR ASIGNANDO CHAQUETA: {mensaje}")
                        
                        elif diferencia < 0:
                            # Decremento: devolver elementos (incrementar el stock)
                            cantidad_devuelta = abs(diferencia)
                            if elemento == 'chaqueta':
                                logger.info(f"🧥 DEVOLVIENDO CHAQUETA: {cantidad_devuelta} unidades {estado}")
                            
                            exito, mensaje = gestor._registrar_movimiento_con_estado(
                                elemento, cantidad_devuelta, estado, 'devolucion', 
                                data.get('id_codigo_consumidor', 0), f'UPDATE_DOTACION_{id_dotacion}'
                            )
                            if exito:
                                movimientos_procesados.append(f"Devuelto {cantidad_devuelta} {elemento} {estado}")
                                if elemento == 'chaqueta':
                                    logger.info(f"🧥 ✅ CHAQUETA DEVUELTA EXITOSAMENTE: {mensaje}")
                            else:
                                logger.warning(f"Error procesando decremento de {elemento}: {mensaje}")
                                if elemento == 'chaqueta':
                                    logger.error(f"🧥 ❌ ERROR DEVOLVIENDO CHAQUETA: {mensaje}")
                    
                    if movimientos_procesados:
                        logger.info(f"Stock procesado para dotación {id_dotacion}: {', '.join(movimientos_procesados)}")
                    
                    gestor.cerrar_conexion()
                    
                except Exception as e:
                    logger.error(f"Error procesando stock para dotación {id_dotacion}: {e}")
                    # No fallar la actualización por errores de stock, solo registrar
            
            logger.info(f"Dotación {id_dotacion} actualizada correctamente")
            
            mensaje_respuesta = 'Dotación actualizada correctamente'
            if cambios_stock:
                mensaje_respuesta += f' con {len(cambios_stock)} cambios de stock procesados'
            
            return jsonify({
                'success': True,
                'message': mensaje_respuesta
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error actualizando dotación {id_dotacion}: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/dotaciones/<int:id_dotacion>', methods=['DELETE'])
    def eliminar_dotacion(id_dotacion):
        """Eliminar una dotación"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            cursor = connection.cursor()
            
            # Verificar que la dotación existe
            cursor.execute("SELECT id_dotacion FROM dotaciones WHERE id_dotacion = %s", (id_dotacion,))
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': 'Dotación no encontrada'}), 404
            
            # Eliminar dotación
            cursor.execute("DELETE FROM dotaciones WHERE id_dotacion = %s", (id_dotacion,))
            
            logger.info(f"Dotación {id_dotacion} eliminada")
            
            return jsonify({
                'success': True,
                'message': 'Dotación eliminada correctamente'
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error eliminando dotación {id_dotacion}: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/tecnicos', methods=['GET'])
    def obtener_tecnicos():
        """Obtener lista de técnicos disponibles con filtros opcionales"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Obtener parámetros de filtrado
            estado = request.args.get('estado')  # 'Activo' o 'Inactivo'
            cliente = request.args.get('cliente')  # Nombre del cliente
            
            # Construir query base
            query = """
            SELECT 
                id_codigo_consumidor,
                nombre,
                cargo,
                recurso_operativo_cedula,
                cliente,
                estado,
                ciudad
            FROM recurso_operativo 
            WHERE 1=1
            """
            
            params = []
            
            # Agregar filtros según parámetros
            if estado:
                query += " AND estado = %s"
                params.append(estado)
            else:
                # Por defecto, solo técnicos activos si no se especifica estado
                query += " AND estado = 'Activo'"
            
            if cliente:
                query += " AND cliente = %s"
                params.append(cliente)
            
            query += " ORDER BY nombre"
            
            cursor.execute(query, params)
            tecnicos = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'data': tecnicos
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo técnicos: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/clientes', methods=['GET'])
    def obtener_clientes():
        """Obtener lista de clientes únicos desde recurso_operativo"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT DISTINCT cliente
            FROM recurso_operativo 
            WHERE cliente IS NOT NULL 
            AND cliente != '' 
            AND estado = 'Activo'
            ORDER BY cliente
            """
            
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            # Extraer solo los nombres de clientes
            clientes = [row['cliente'] for row in resultados]
            
            return jsonify({
                'success': True,
                'data': clientes
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo clientes: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/dotaciones/estadisticas', methods=['GET'])
    def obtener_estadisticas():
        """Obtener estadísticas de dotaciones"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Estadísticas generales
            stats_query = """
            SELECT 
                COUNT(*) as total_dotaciones,
                COUNT(CASE WHEN id_codigo_consumidor IS NOT NULL THEN 1 END) as asignadas,
                COUNT(CASE WHEN id_codigo_consumidor IS NULL THEN 1 END) as disponibles
            FROM dotaciones
            """
            
            cursor.execute(stats_query)
            estadisticas = cursor.fetchone()
            
            # Estadísticas por cliente
            clientes_query = """
            SELECT 
                cliente,
                COUNT(*) as cantidad
            FROM dotaciones
            WHERE cliente IS NOT NULL
            GROUP BY cliente
            ORDER BY cantidad DESC
            LIMIT 10
            """
            
            cursor.execute(clientes_query)
            por_cliente = cursor.fetchall()
            
            # Estadísticas por mes (últimos 6 meses)
            meses_query = """
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                COUNT(*) as cantidad
            FROM dotaciones
            WHERE fecha_registro >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            ORDER BY mes
            """
            
            cursor.execute(meses_query)
            por_mes = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'estadisticas': estadisticas,
                'por_cliente': por_cliente,
                'por_mes': por_mes
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/dotaciones/export', methods=['GET'])
    def exportar_dotaciones():
        """Exportar dotaciones a CSV"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT 
                d.id_dotacion,
                d.cliente,
                ro.nombre as tecnico_nombre,
                ro.recurso_operativo_cedula as tecnico_cedula,
                d.pantalon,
                d.pantalon_talla,
                d.camisetagris,
                d.camiseta_gris_talla,
                d.guerrera,
                d.guerrera_talla,
                d.camisetapolo,
                d.camiseta_polo_talla,
                d.guantes_nitrilo,
                d.guantes_carnaza,
                d.gafas,
                d.gorra,
                d.casco,
                d.botas,
                d.botas_talla,
                DATE_FORMAT(d.fecha_registro, '%Y-%m-%d %H:%i:%s') as fecha_registro
            FROM dotaciones d
            LEFT JOIN recurso_operativo ro ON d.id_codigo_consumidor = ro.id_codigo_consumidor
            ORDER BY d.id_dotacion DESC
            """
            
            cursor.execute(query)
            dotaciones = cursor.fetchall()
            
            # Generar CSV
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=dotaciones[0].keys() if dotaciones else [])
            writer.writeheader()
            writer.writerows(dotaciones)
            
            csv_content = output.getvalue()
            output.close()
            
            from flask import Response
            return Response(
                csv_content,
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=dotaciones_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
            )
            
        except mysql.connector.Error as e:
            logger.error(f"Error exportando dotaciones: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    # ===== NUEVAS APIs PARA SISTEMA DE INGRESOS DE DOTACIONES =====
    
    @app.route('/api/ingresos-dotaciones', methods=['POST'])
    def registrar_ingreso_dotacion():
        """Registrar nuevo ingreso de dotación a bodega"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            data = request.get_json()
            
            # Validar datos requeridos
            campos_requeridos = ['tipo_elemento', 'cantidad', 'fecha_ingreso', 'usuario_registro']
            for campo in campos_requeridos:
                if not data.get(campo):
                    return jsonify({'success': False, 'message': f'El campo {campo} es requerido'}), 400
            
            # Validar que la cantidad sea positiva
            if int(data.get('cantidad', 0)) <= 0:
                return jsonify({'success': False, 'message': 'La cantidad debe ser mayor a 0'}), 400
            
            cursor = connection.cursor()
            
            # Determinar la talla correcta según el tipo de elemento
            talla_final = None
            numero_calzado_final = None
            
            # Para pantalón, usar talla_pantalon
            if data.get('tipo_elemento') == 'pantalon' and data.get('talla_pantalon'):
                talla_final = data.get('talla_pantalon')
            # Para botas, usar numero_calzado
            elif data.get('tipo_elemento') == 'botas' and data.get('numero_calzado'):
                numero_calzado_final = data.get('numero_calzado')
            # Para otros elementos con talla genérica
            elif data.get('talla'):
                talla_final = data.get('talla')
            # Para elementos con talla de guantes
            elif data.get('talla_guantes'):
                talla_final = data.get('talla_guantes')
            # Para elementos con talla única
            elif data.get('talla_unica'):
                talla_final = data.get('talla_unica')
            
            # Insertar nuevo ingreso
            query = """
            INSERT INTO ingresos_dotaciones (
                tipo_elemento, cantidad, talla, numero_calzado, proveedor, estado, fecha_ingreso, 
                observaciones, usuario_registro
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            valores = (
                data.get('tipo_elemento'),
                data.get('cantidad'),
                talla_final,
                numero_calzado_final,
                data.get('proveedor', ''),
                data.get('estado'),
                data.get('fecha_ingreso'),
                data.get('observaciones', ''),
                data.get('usuario_registro')
            )
            
            cursor.execute(query, valores)
            id_ingreso = cursor.lastrowid
            
            logger.info(f"Ingreso de dotación registrado: ID {id_ingreso}, Tipo: {data.get('tipo_elemento')}, Cantidad: {data.get('cantidad')}")
            
            return jsonify({
                'success': True,
                'message': 'Ingreso registrado exitosamente',
                'id_ingreso': id_ingreso
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error registrando ingreso: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/stock-dotaciones', methods=['GET'])
    def obtener_stock_dotaciones():
        """Obtener información de stock actual de dotaciones"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Calcular stock para cada elemento de dotación
            elementos = ['pantalon', 'camisetagris', 'guerrera', 'camisetapolo',
                        'guantes_nitrilo', 'guantes_carnaza', 'gafas', 'gorra', 'casco', 'botas', 'chaqueta']
            
            stock_data = []
            
            for elemento in elementos:
                # Obtener total de ingresos - Para camisetapolo, buscar ambas variantes
                if elemento == 'camisetapolo':
                    cursor.execute("""
                        SELECT COALESCE(SUM(cantidad), 0) as total_ingresos
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'camisetapolo' OR tipo_elemento = 'camiseta_polo'
                    """)
                else:
                    cursor.execute("""
                        SELECT COALESCE(SUM(cantidad), 0) as total_ingresos
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = %s
                    """, (elemento,))
                
                ingresos_result = cursor.fetchone()
                total_ingresos = ingresos_result['total_ingresos'] if ingresos_result else 0
                
                # Obtener total de entregas en dotaciones
                cursor.execute(f"""
                    SELECT COALESCE(SUM({elemento}), 0) as total_dotaciones
                    FROM dotaciones
                    WHERE {elemento} IS NOT NULL AND {elemento} > 0
                """, ())
                
                dotaciones_result = cursor.fetchone()
                total_dotaciones = dotaciones_result['total_dotaciones'] if dotaciones_result else 0
                
                # Obtener total de entregas en cambios
                cursor.execute(f"""
                    SELECT COALESCE(SUM({elemento}), 0) as total_cambios
                    FROM cambios_dotacion
                    WHERE {elemento} IS NOT NULL AND {elemento} > 0
                """, ())
                
                cambios_result = cursor.fetchone()
                total_cambios = cambios_result['total_cambios'] if cambios_result else 0
                
                # Calcular stock disponible
                stock_disponible = total_ingresos - total_dotaciones - total_cambios
                
                stock_data.append({
                    'tipo_elemento': elemento,
                    'cantidad_ingresada': int(total_ingresos),
                    'cantidad_entregada': int(total_dotaciones + total_cambios),
                    'stock_disponible': int(max(0, stock_disponible))
                })
            
            # Todos los elementos se procesan en el bucle principal
            
            return jsonify({
                'success': True,
                'stock': stock_data
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo stock: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/reportes-inventario', methods=['GET'])
    def obtener_reportes_inventario():
        """Obtener reportes de inventario y movimientos"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Reporte de ingresos por mes (últimos 6 meses)
            ingresos_query = """
            SELECT 
                DATE_FORMAT(fecha_ingreso, '%Y-%m') as mes,
                tipo_elemento,
                SUM(cantidad) as total_ingresado
            FROM ingresos_dotaciones
            WHERE fecha_ingreso >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(fecha_ingreso, '%Y-%m'), tipo_elemento
            ORDER BY mes DESC, tipo_elemento
            """
            
            cursor.execute(ingresos_query)
            ingresos_por_mes = cursor.fetchall()
            
            # Reporte de entregas por mes (últimos 6 meses)
            entregas_query = """
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                SUM(pantalon) as pantalon,
                SUM(camisetagris) as camisetagris,
                SUM(guerrera) as guerrera,
                SUM(camisetapolo) as camisetapolo,
                SUM(guantes_nitrilo) as guantes_nitrilo,
                SUM(guantes_carnaza) as guantes_carnaza,
                SUM(gafas) as gafas,
                SUM(gorra) as gorra,
                SUM(casco) as casco,
                SUM(botas) as botas,
                SUM(chaqueta) as chaqueta
            FROM dotaciones
            WHERE fecha_registro >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            ORDER BY mes DESC
            """
            
            cursor.execute(entregas_query)
            entregas_por_mes = cursor.fetchall()
            
            # Reporte de proveedores más frecuentes
            proveedores_query = """
            SELECT 
                proveedor,
                COUNT(*) as total_ingresos,
                SUM(cantidad) as total_cantidad
            FROM ingresos_dotaciones
            WHERE proveedor IS NOT NULL AND proveedor != ''
            GROUP BY proveedor
            ORDER BY total_cantidad DESC
            LIMIT 10
            """
            
            cursor.execute(proveedores_query)
            top_proveedores = cursor.fetchall()
            
            # Convertir Decimal a int para JSON
            for lista in [ingresos_por_mes, entregas_por_mes, top_proveedores]:
                for item in lista:
                    for key, value in item.items():
                        if hasattr(value, 'is_integer'):
                            item[key] = int(value)
            
            return jsonify({
                'success': True,
                'ingresos_por_mes': ingresos_por_mes,
                'entregas_por_mes': entregas_por_mes,
                'top_proveedores': top_proveedores
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo reportes: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/asignaciones-mensuales', methods=['GET'])
    def obtener_asignaciones_mensuales():
        """Obtener datos de asignaciones agrupados por mes y elemento para gráficas"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Parámetros de filtrado
            elemento = request.args.get('elemento')  # Filtro por elemento específico
            mes = request.args.get('mes')  # Filtro por mes específico (formato YYYY-MM)
            
            # Query base para obtener asignaciones por mes y elemento
            base_query = """
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                DATE_FORMAT(fecha_registro, '%M %Y') as mes_nombre,
                'pantalon' as elemento,
                SUM(pantalon) as cantidad
            FROM dotaciones
            WHERE pantalon > 0 AND fecha_registro >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                DATE_FORMAT(fecha_registro, '%M %Y') as mes_nombre,
                'camisetagris' as elemento,
                SUM(camisetagris) as cantidad
            FROM dotaciones
            WHERE camisetagris > 0 AND fecha_registro >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                DATE_FORMAT(fecha_registro, '%M %Y') as mes_nombre,
                'guerrera' as elemento,
                SUM(guerrera) as cantidad
            FROM dotaciones
            WHERE guerrera > 0 AND fecha_registro >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                DATE_FORMAT(fecha_registro, '%M %Y') as mes_nombre,
                'camisetapolo' as elemento,
                SUM(camisetapolo) as cantidad
            FROM dotaciones
            WHERE camisetapolo > 0 AND fecha_registro >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                DATE_FORMAT(fecha_registro, '%M %Y') as mes_nombre,
                'guantes_nitrilo' as elemento,
                SUM(guantes_nitrilo) as cantidad
            FROM dotaciones
            WHERE guantes_nitrilo > 0 AND fecha_registro >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                DATE_FORMAT(fecha_registro, '%M %Y') as mes_nombre,
                'guantes_carnaza' as elemento,
                SUM(guantes_carnaza) as cantidad
            FROM dotaciones
            WHERE guantes_carnaza > 0 AND fecha_registro >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                DATE_FORMAT(fecha_registro, '%M %Y') as mes_nombre,
                'gafas' as elemento,
                SUM(gafas) as cantidad
            FROM dotaciones
            WHERE gafas > 0 AND fecha_registro >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                DATE_FORMAT(fecha_registro, '%M %Y') as mes_nombre,
                'gorra' as elemento,
                SUM(gorra) as cantidad
            FROM dotaciones
            WHERE gorra > 0 AND fecha_registro >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                DATE_FORMAT(fecha_registro, '%M %Y') as mes_nombre,
                'casco' as elemento,
                SUM(casco) as cantidad
            FROM dotaciones
            WHERE casco > 0 AND fecha_registro >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                DATE_FORMAT(fecha_registro, '%M %Y') as mes_nombre,
                'botas' as elemento,
                SUM(botas) as cantidad
            FROM dotaciones
            WHERE botas > 0 AND fecha_registro >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                DATE_FORMAT(fecha_registro, '%M %Y') as mes_nombre,
                'chaqueta' as elemento,
                SUM(chaqueta) as cantidad
            FROM dotaciones
            WHERE chaqueta > 0 AND fecha_registro >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            """
            
            # Construir query final con filtros
            final_query = f"SELECT * FROM ({base_query}) as asignaciones WHERE 1=1"
            params = []
            
            if elemento:
                final_query += " AND elemento = %s"
                params.append(elemento)
            
            if mes:
                final_query += " AND mes = %s"
                params.append(mes)
            
            final_query += " ORDER BY mes DESC, elemento"
            
            cursor.execute(final_query, params)
            asignaciones_data = cursor.fetchall()
            
            # Obtener lista de elementos únicos para los filtros
            elementos_query = """
            SELECT DISTINCT elemento FROM (
                SELECT 'pantalon' as elemento UNION ALL
                SELECT 'camisetagris' as elemento UNION ALL
                SELECT 'guerrera' as elemento UNION ALL
                SELECT 'camisetapolo' as elemento UNION ALL
                SELECT 'guantes_nitrilo' as elemento UNION ALL
                SELECT 'guantes_carnaza' as elemento UNION ALL
                SELECT 'gafas' as elemento UNION ALL
                SELECT 'gorra' as elemento UNION ALL
                SELECT 'casco' as elemento UNION ALL
                SELECT 'botas' as elemento UNION ALL
                SELECT 'chaqueta' as elemento
            ) as elementos
            ORDER BY elemento
            """
            
            cursor.execute(elementos_query)
            elementos_disponibles = [row['elemento'] for row in cursor.fetchall()]
            
            # Obtener meses únicos de los últimos 12 meses
            meses_query = """
            SELECT DISTINCT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                DATE_FORMAT(fecha_registro, '%M %Y') as mes_nombre
            FROM dotaciones
            WHERE fecha_registro >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            ORDER BY mes DESC
            """
            
            cursor.execute(meses_query)
            meses_disponibles = cursor.fetchall()
            
            # Convertir Decimal a int para JSON
            for item in asignaciones_data:
                for key, value in item.items():
                    if hasattr(value, 'is_integer'):
                        item[key] = int(value)
            
            return jsonify({
                'success': True,
                'asignaciones': asignaciones_data,
                'elementos_disponibles': elementos_disponibles,
                'meses_disponibles': meses_disponibles
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo asignaciones mensuales: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/stock-dotaciones-tallas', methods=['GET'])
    def obtener_stock_dotaciones_tallas():
        """Obtener stock de dotaciones desglosado por tallas"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Parámetro de filtrado por tipo
            tipo_elemento = request.args.get('tipo_elemento')
            
            # Query para obtener stock por tallas de ingresos
            ingresos_query = """
            SELECT 
                tipo_elemento,
                CASE 
                    WHEN tipo_elemento = 'pantalon' THEN COALESCE(talla, 'Sin talla')
                    WHEN tipo_elemento = 'botas' THEN 'Sin talla'
                    WHEN tipo_elemento IN ('guantes_nitrilo', 'guantes_carnaza') THEN COALESCE(talla, 'Sin talla')
                    ELSE COALESCE(talla, 'Sin talla')
                END as talla,
                CASE 
                    WHEN tipo_elemento = 'pantalon' THEN COALESCE(talla, 'Sin talla')
                    WHEN tipo_elemento = 'botas' THEN COALESCE(numero_calzado, 'Sin número')
                    WHEN tipo_elemento IN ('guantes_nitrilo', 'guantes_carnaza') THEN 'Sin número'
                    ELSE 'Sin número'
                END as numero_calzado,
                SUM(cantidad) as total_ingresado
            FROM ingresos_dotaciones
            WHERE 1=1
            """
            
            params_ingresos = []
            if tipo_elemento:
                ingresos_query += " AND tipo_elemento = %s"
                params_ingresos.append(tipo_elemento)
            
            ingresos_query += " GROUP BY tipo_elemento, talla, numero_calzado"
            
            cursor.execute(ingresos_query, params_ingresos)
            ingresos_data = cursor.fetchall()
            
            # Query para obtener entregas por tallas (DOTACIONES + CAMBIOS)
            entregas_query = """
            SELECT 
                'pantalon' as tipo_elemento,
                COALESCE(pantalon_talla, 'Sin talla') as talla,
                COALESCE(pantalon_talla, 'Sin talla') as numero_calzado,
                SUM(pantalon) as total_entregado
            FROM dotaciones
            WHERE pantalon > 0
            GROUP BY pantalon_talla
            
            UNION ALL
            
            SELECT 
                'pantalon' as tipo_elemento,
                COALESCE(pantalon_talla, 'Sin talla') as talla,
                COALESCE(pantalon_talla, 'Sin talla') as numero_calzado,
                SUM(pantalon) as total_entregado
            FROM cambios_dotacion
            WHERE pantalon > 0
            GROUP BY pantalon_talla
            
            UNION ALL
            
            SELECT 
                'camisetagris' as tipo_elemento,
                COALESCE(camiseta_gris_talla, 'Sin talla') as talla,
                'Sin número' as numero_calzado,
                SUM(camisetagris) as total_entregado
            FROM dotaciones
            WHERE camisetagris > 0
            GROUP BY camiseta_gris_talla
            
            UNION ALL
            
            SELECT 
                'camisetagris' as tipo_elemento,
                COALESCE(camiseta_gris_talla, 'Sin talla') as talla,
                'Sin número' as numero_calzado,
                SUM(camisetagris) as total_entregado
            FROM cambios_dotacion
            WHERE camisetagris > 0
            GROUP BY camiseta_gris_talla
            
            UNION ALL
            
            SELECT 
                'guerrera' as tipo_elemento,
                COALESCE(guerrera_talla, 'Sin talla') as talla,
                'Sin número' as numero_calzado,
                SUM(guerrera) as total_entregado
            FROM dotaciones
            WHERE guerrera > 0
            GROUP BY guerrera_talla
            
            UNION ALL
            
            SELECT 
                'guerrera' as tipo_elemento,
                COALESCE(guerrera_talla, 'Sin talla') as talla,
                'Sin número' as numero_calzado,
                SUM(guerrera) as total_entregado
            FROM cambios_dotacion
            WHERE guerrera > 0
            GROUP BY guerrera_talla
            
            UNION ALL
            
            SELECT 
                'camisetapolo' as tipo_elemento,
                COALESCE(camiseta_polo_talla, 'Sin talla') as talla,
                'Sin número' as numero_calzado,
                SUM(camisetapolo) as total_entregado
            FROM dotaciones
            WHERE camisetapolo > 0
            GROUP BY camiseta_polo_talla
            
            UNION ALL
            
            SELECT 
                'camisetapolo' as tipo_elemento,
                COALESCE(camiseta_polo_talla, 'Sin talla') as talla,
                'Sin número' as numero_calzado,
                SUM(camisetapolo) as total_entregado
            FROM cambios_dotacion
            WHERE camisetapolo > 0
            GROUP BY camiseta_polo_talla
            
            UNION ALL
            
            SELECT 
                'botas' as tipo_elemento,
                'Sin talla' as talla,
                COALESCE(botas_talla, 'Sin número') as numero_calzado,
                SUM(botas) as total_entregado
            FROM dotaciones
            WHERE botas > 0
            GROUP BY botas_talla
            
            UNION ALL
            
            SELECT 
                'botas' as tipo_elemento,
                'Sin talla' as talla,
                COALESCE(botas_talla, 'Sin número') as numero_calzado,
                SUM(botas) as total_entregado
            FROM cambios_dotacion
            WHERE botas > 0
            GROUP BY botas_talla
            
            UNION ALL
            
            SELECT 
                'gafas' as tipo_elemento,
                'TALLA UNICA' as talla,
                'Sin número' as numero_calzado,
                COALESCE(SUM(gafas), 0) as total_entregado
            FROM dotaciones
            WHERE gafas > 0
            
            UNION ALL
            
            SELECT 
                'gafas' as tipo_elemento,
                'TALLA UNICA' as talla,
                'Sin número' as numero_calzado,
                COALESCE(SUM(gafas), 0) as total_entregado
            FROM cambios_dotacion
            WHERE gafas > 0
            
            UNION ALL
            
            SELECT 
                'gorra' as tipo_elemento,
                'TALLA UNICA' as talla,
                'Sin número' as numero_calzado,
                COALESCE(SUM(gorra), 0) as total_entregado
            FROM dotaciones
            WHERE gorra > 0
            
            UNION ALL
            
            SELECT 
                'gorra' as tipo_elemento,
                'TALLA UNICA' as talla,
                'Sin número' as numero_calzado,
                COALESCE(SUM(gorra), 0) as total_entregado
            FROM cambios_dotacion
            WHERE gorra > 0
            
            UNION ALL
            
            SELECT 
                'casco' as tipo_elemento,
                'TALLA UNICA' as talla,
                'Sin número' as numero_calzado,
                COALESCE(SUM(casco), 0) as total_entregado
            FROM dotaciones
            WHERE casco > 0
            
            UNION ALL
            
            SELECT 
                'casco' as tipo_elemento,
                'TALLA UNICA' as talla,
                'Sin número' as numero_calzado,
                COALESCE(SUM(casco), 0) as total_entregado
            FROM cambios_dotacion
            WHERE casco > 0
            
            UNION ALL
            
            SELECT 
                'chaqueta' as tipo_elemento,
                COALESCE(chaqueta_talla, 'Sin talla') as talla,
                'Sin número' as numero_calzado,
                SUM(chaqueta) as total_entregado
            FROM dotaciones
            WHERE chaqueta > 0
            GROUP BY chaqueta_talla
            
            UNION ALL
            
            SELECT 
                'chaqueta' as tipo_elemento,
                COALESCE(chaqueta_talla, 'Sin talla') as talla,
                'Sin número' as numero_calzado,
                SUM(chaqueta) as total_entregado
            FROM cambios_dotacion
            WHERE chaqueta > 0
            GROUP BY chaqueta_talla
            """
            
            # Agregar filtro por tipo si se especifica
            if tipo_elemento:
                entregas_query = f"""
                SELECT * FROM (
                {entregas_query}
                ) as entregas_union
                WHERE tipo_elemento = %s
                """
                cursor.execute(entregas_query, [tipo_elemento])
            else:
                cursor.execute(entregas_query)
            
            entregas_data = cursor.fetchall()
            
            # Combinar datos de ingresos y entregas
            stock_por_tallas = {}
            
            # Procesar ingresos
            for ingreso in ingresos_data:
                key = f"{ingreso['tipo_elemento']}_{ingreso['talla']}_{ingreso['numero_calzado']}"
                if key not in stock_por_tallas:
                    stock_por_tallas[key] = {
                        'tipo_elemento': ingreso['tipo_elemento'],
                        'talla': ingreso['talla'],
                        'numero_calzado': ingreso['numero_calzado'],
                        'total_ingresado': 0,
                        'total_entregado': 0,
                        'stock_disponible': 0
                    }
                stock_por_tallas[key]['total_ingresado'] = int(ingreso['total_ingresado'])
            
            # Procesar entregas (sumar dotaciones + cambios)
            for entrega in entregas_data:
                key = f"{entrega['tipo_elemento']}_{entrega['talla']}_{entrega['numero_calzado']}"
                if key not in stock_por_tallas:
                    stock_por_tallas[key] = {
                        'tipo_elemento': entrega['tipo_elemento'],
                        'talla': entrega['talla'],
                        'numero_calzado': entrega['numero_calzado'],
                        'total_ingresado': 0,
                        'total_entregado': 0,
                        'stock_disponible': 0
                    }
                # Sumar entregas (pueden venir de dotaciones y cambios)
                stock_por_tallas[key]['total_entregado'] += int(entrega['total_entregado'])
            
            # Calcular stock disponible
            for key in stock_por_tallas:
                item = stock_por_tallas[key]
                item['stock_disponible'] = item['total_ingresado'] - item['total_entregado']
            
            # Convertir a lista y ordenar
            resultado = list(stock_por_tallas.values())
            resultado.sort(key=lambda x: (x['tipo_elemento'], x['talla'], x['numero_calzado']))
            
            return jsonify({
                'success': True,
                'stock_tallas': resultado
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo stock por tallas: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/ingresos-dotaciones', methods=['GET'])
    def obtener_ingresos_dotaciones():
        """Obtener historial de ingresos de dotaciones"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Parámetros de filtrado
            tipo_elemento = request.args.get('tipo_elemento')
            fecha_desde = request.args.get('fecha_desde')
            fecha_hasta = request.args.get('fecha_hasta')
            limit = int(request.args.get('limit', 50))
            
            # Construir query con filtros
            query = """
            SELECT 
                id_ingreso,
                tipo_elemento,
                cantidad,
                proveedor,
                DATE_FORMAT(fecha_ingreso, '%Y-%m-%d') as fecha_ingreso,
                observaciones,
                usuario_registro,
                DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as fecha_registro
            FROM ingresos_dotaciones
            WHERE 1=1
            """
            
            params = []
            
            if tipo_elemento:
                query += " AND tipo_elemento = %s"
                params.append(tipo_elemento)
            
            if fecha_desde:
                query += " AND fecha_ingreso >= %s"
                params.append(fecha_desde)
            
            if fecha_hasta:
                query += " AND fecha_ingreso <= %s"
                params.append(fecha_hasta)
            
            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            ingresos = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'ingresos': ingresos,
                'total': len(ingresos)
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo ingresos: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()
    
    @app.route('/api/historial-movimientos-grafica', methods=['GET'])
    def obtener_historial_movimientos_grafica():
        """Obtener datos para gráfica mensual de asignaciones de dotaciones"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Parámetros de filtrado
            elemento = request.args.get('elemento', '')  # Filtro por elemento específico
            mes = request.args.get('mes', '')  # Filtro por mes específico (YYYY-MM)
            año = request.args.get('año', str(datetime.now().year))  # Año actual por defecto
            
            # Query base para obtener asignaciones por mes
            query = """
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                'pantalon' as elemento,
                SUM(pantalon) as cantidad
            FROM dotaciones 
            WHERE pantalon > 0 AND YEAR(fecha_registro) = %s
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                'camisetagris' as elemento,
                SUM(camisetagris) as cantidad
            FROM dotaciones 
            WHERE camisetagris > 0 AND YEAR(fecha_registro) = %s
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                'guerrera' as elemento,
                SUM(guerrera) as cantidad
            FROM dotaciones 
            WHERE guerrera > 0 AND YEAR(fecha_registro) = %s
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                'camisetapolo' as elemento,
                SUM(camisetapolo) as cantidad
            FROM dotaciones 
            WHERE camisetapolo > 0 AND YEAR(fecha_registro) = %s
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                'guantes_nitrilo' as elemento,
                SUM(guantes_nitrilo) as cantidad
            FROM dotaciones 
            WHERE guantes_nitrilo > 0 AND YEAR(fecha_registro) = %s
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                'guantes_carnaza' as elemento,
                SUM(guantes_carnaza) as cantidad
            FROM dotaciones 
            WHERE guantes_carnaza > 0 AND YEAR(fecha_registro) = %s
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                'gafas' as elemento,
                SUM(gafas) as cantidad
            FROM dotaciones 
            WHERE gafas > 0 AND YEAR(fecha_registro) = %s
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                'gorra' as elemento,
                SUM(gorra) as cantidad
            FROM dotaciones 
            WHERE gorra > 0 AND YEAR(fecha_registro) = %s
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                'casco' as elemento,
                SUM(casco) as cantidad
            FROM dotaciones 
            WHERE casco > 0 AND YEAR(fecha_registro) = %s
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                'botas' as elemento,
                SUM(botas) as cantidad
            FROM dotaciones 
            WHERE botas > 0 AND YEAR(fecha_registro) = %s
            GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
            
            ORDER BY mes, elemento
            """
            
            # Ejecutar query con parámetros
            params = [año] * 10  # Un parámetro por cada UNION
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            
            # Procesar datos para la gráfica
            datos_por_mes = {}
            elementos_disponibles = set()
            
            for row in resultados:
                mes_key = row['mes']
                elemento_key = row['elemento']
                cantidad = int(row['cantidad'])
                
                elementos_disponibles.add(elemento_key)
                
                if mes_key not in datos_por_mes:
                    datos_por_mes[mes_key] = {}
                
                datos_por_mes[mes_key][elemento_key] = cantidad
            
            # Aplicar filtros
            if elemento and elemento in elementos_disponibles:
                # Filtrar por elemento específico
                datos_filtrados = {}
                for mes_key, elementos in datos_por_mes.items():
                    if elemento in elementos:
                        datos_filtrados[mes_key] = {elemento: elementos[elemento]}
                datos_por_mes = datos_filtrados
                elementos_disponibles = {elemento}
            
            if mes:
                # Filtrar por mes específico
                if mes in datos_por_mes:
                    datos_por_mes = {mes: datos_por_mes[mes]}
                else:
                    datos_por_mes = {}
            
            # Generar lista de meses completa para el año
            meses_año = []
            for i in range(1, 13):
                mes_str = f"{año}-{i:02d}"
                meses_año.append(mes_str)
            
            # Preparar datos para Chart.js
            labels = []
            datasets = {}
            
            # Nombres amigables para elementos
            nombres_elementos = {
                'pantalon': 'Pantalón',
                'camisetagris': 'Camiseta Gris',
                'guerrera': 'Guerrera',
                'camisetapolo': 'Camiseta Polo',
                'guantes_nitrilo': 'Guantes Nitrilo',
                'guantes_carnaza': 'Guantes Carnaza',
                'gafas': 'Gafas',
                'gorra': 'Gorra',
                'casco': 'Casco',
                'botas': 'Botas'
            }
            
            # Colores para cada elemento
            colores_elementos = {
                'pantalon': '#FF6384',
                'camisetagris': '#36A2EB',
                'guerrera': '#FFCE56',
                'camisetapolo': '#4BC0C0',
                'guantes_nitrilo': '#9966FF',
                'guantes_carnaza': '#FF9F40',
                'gafas': '#4ECDC4',
                'gorra': '#45B7D1',
                'casco': '#96CEB4',
                'botas': '#FFEAA7'
            }
            
            for mes_str in meses_año:
                # Convertir a formato amigable para labels
                try:
                    fecha = datetime.strptime(mes_str, '%Y-%m')
                    label = fecha.strftime('%b %Y')
                    labels.append(label)
                except:
                    labels.append(mes_str)
                
                # Inicializar datasets si no existen
                for elemento_key in elementos_disponibles:
                    if elemento_key not in datasets:
                        datasets[elemento_key] = {
                            'label': nombres_elementos.get(elemento_key, elemento_key),
                            'data': [],
                            'borderColor': colores_elementos.get(elemento_key, '#999999'),
                            'backgroundColor': colores_elementos.get(elemento_key, '#999999') + '20',
                            'tension': 0.1
                        }
                
                # Agregar datos para cada elemento
                for elemento_key in elementos_disponibles:
                    cantidad = 0
                    if mes_str in datos_por_mes and elemento_key in datos_por_mes[mes_str]:
                        cantidad = datos_por_mes[mes_str][elemento_key]
                    datasets[elemento_key]['data'].append(cantidad)
            
            # Convertir datasets a lista
            datasets_list = list(datasets.values())
            
            return jsonify({
                'success': True,
                'labels': labels,
                'datasets': datasets_list,
                'elementos_disponibles': list(elementos_disponibles),
                'año': año,
                'filtros': {
                    'elemento': elemento,
                    'mes': mes
                }
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo datos de gráfica: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado en gráfica: {e}")
            return jsonify({'success': False, 'message': f'Error interno: {e}'}), 500
        finally:
            if connection:
                connection.close()

    @app.route('/api/refresh-stock-dotaciones', methods=['POST'])
    def refresh_stock_dotaciones():
        """Endpoint para refrescar y recalcular el stock de dotaciones"""
        connection = None
        try:
            logger.info("Iniciando refresh de stock de dotaciones")
            
            # Conectar a la base de datos
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            # Obtener todos los materiales únicos de stock_ferretero
            cursor.execute("""
                SELECT DISTINCT material_tipo as material 
                FROM stock_ferretero 
                ORDER BY material_tipo
            """)
            materiales = cursor.fetchall()
            
            stock_actualizado = []
            
            for material_row in materiales:
                material = material_row['material']
                
                # Calcular stock inicial (entradas)
                cursor.execute("""
                    SELECT COALESCE(SUM(cantidad_disponible), 0) as stock_inicial
                    FROM stock_ferretero 
                    WHERE material_tipo = %s
                """, (material,))
                stock_inicial = cursor.fetchone()['stock_inicial']
                
                # Calcular asignaciones por material
                cursor.execute("""
                    SELECT COALESCE(SUM(
                        CASE 
                            WHEN %s = 'pantalon' THEN pantalon
                            WHEN %s = 'camisetagris' THEN camisetagris
                            WHEN %s = 'guerrera' THEN guerrera
                            WHEN %s = 'camisetapolo' THEN camisetapolo
                            WHEN %s = 'guantes_nitrilo' THEN guantes_nitrilo
                            WHEN %s = 'guantes_carnaza' THEN guantes_carnaza
                            WHEN %s = 'gafas' THEN gafas
                            WHEN %s = 'gorra' THEN gorra
                            WHEN %s = 'casco' THEN casco
                            WHEN %s = 'botas' THEN botas
                            ELSE 0
                        END
                    ), 0) as total_asignaciones
                    FROM dotaciones
                """, (material,) * 10)
                total_asignaciones = cursor.fetchone()['total_asignaciones']
                
                # Calcular cambios por material
                cursor.execute("""
                    SELECT COALESCE(SUM(
                        CASE 
                            WHEN %s = 'pantalon' THEN pantalon
                            WHEN %s = 'camisetagris' THEN camisetagris
                            WHEN %s = 'guerrera' THEN guerrera
                            WHEN %s = 'camisetapolo' THEN camisetapolo
                            WHEN %s = 'guantes_nitrilo' THEN guantes_nitrilo
                            WHEN %s = 'guantes_carnaza' THEN guantes_carnaza
                            WHEN %s = 'gafas' THEN gafas
                            WHEN %s = 'gorra' THEN gorra
                            WHEN %s = 'casco' THEN casco
                            WHEN %s = 'botas' THEN botas
                            ELSE 0
                        END
                    ), 0) as total_cambios
                    FROM cambios_dotacion
                """, (material,) * 10)
                total_cambios = cursor.fetchone()['total_cambios']
                
                # Calcular stock actual usando la fórmula
                stock_actual = stock_inicial - total_asignaciones - total_cambios
                
                stock_actualizado.append({
                    'material': material,
                    'stock_inicial': stock_inicial,
                    'total_asignaciones': total_asignaciones,
                    'total_cambios': total_cambios,
                    'stock_actual': stock_actual
                })
                
                logger.info(f"Stock recalculado para {material}: {stock_inicial} - {total_asignaciones} - {total_cambios} = {stock_actual}")
            
            # Después del recálculo, actualizar la vista vista_stock_dotaciones
            logger.info("Actualizando vista_stock_dotaciones...")
            
            try:
                # Recrear la vista vista_stock_dotaciones para reflejar los cambios
                cursor.execute("DROP VIEW IF EXISTS vista_stock_dotaciones")
                
                create_view_query = """
                CREATE VIEW vista_stock_dotaciones AS
                SELECT 
                    'pantalon' AS tipo_elemento,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'pantalon'
                    ) AS cantidad_ingresada,
                    (
                        SELECT COALESCE(SUM(pantalon), 0) 
                        FROM dotaciones 
                        WHERE pantalon IS NOT NULL AND pantalon > 0
                    ) + (
                        SELECT COALESCE(SUM(pantalon), 0) 
                        FROM cambios_dotacion 
                        WHERE pantalon IS NOT NULL AND pantalon > 0
                    ) AS cantidad_entregada,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'pantalon'
                    ) - (
                        SELECT COALESCE(SUM(pantalon), 0) 
                        FROM dotaciones 
                        WHERE pantalon IS NOT NULL AND pantalon > 0
                    ) - (
                        SELECT COALESCE(SUM(pantalon), 0) 
                        FROM cambios_dotacion 
                        WHERE pantalon IS NOT NULL AND pantalon > 0
                    ) AS saldo_disponible
                
                UNION ALL
                
                SELECT 
                    'camisetagris' AS tipo_elemento,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'camisetagris'
                    ) AS cantidad_ingresada,
                    (
                        SELECT COALESCE(SUM(camisetagris), 0) 
                        FROM dotaciones 
                        WHERE camisetagris IS NOT NULL AND camisetagris > 0
                    ) + (
                        SELECT COALESCE(SUM(camisetagris), 0) 
                        FROM cambios_dotacion 
                        WHERE camisetagris IS NOT NULL AND camisetagris > 0
                    ) AS cantidad_entregada,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'camisetagris'
                    ) - (
                        SELECT COALESCE(SUM(camisetagris), 0) 
                        FROM dotaciones 
                        WHERE camisetagris IS NOT NULL AND camisetagris > 0
                    ) - (
                        SELECT COALESCE(SUM(camisetagris), 0) 
                        FROM cambios_dotacion 
                        WHERE camisetagris IS NOT NULL AND camisetagris > 0
                    ) AS saldo_disponible
                

                
                UNION ALL
                
                SELECT 
                    'guerrera' AS tipo_elemento,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'guerrera'
                    ) AS cantidad_ingresada,
                    (
                        SELECT COALESCE(SUM(guerrera), 0) 
                        FROM dotaciones 
                        WHERE guerrera IS NOT NULL AND guerrera > 0
                    ) + (
                        SELECT COALESCE(SUM(guerrera), 0) 
                        FROM cambios_dotacion 
                        WHERE guerrera IS NOT NULL AND guerrera > 0
                    ) AS cantidad_entregada,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'guerrera'
                    ) - (
                        SELECT COALESCE(SUM(guerrera), 0) 
                        FROM dotaciones 
                        WHERE guerrera IS NOT NULL AND guerrera > 0
                    ) - (
                        SELECT COALESCE(SUM(guerrera), 0) 
                        FROM cambios_dotacion 
                        WHERE guerrera IS NOT NULL AND guerrera > 0
                    ) AS saldo_disponible
                
                UNION ALL
                
                SELECT 
                    'camisetapolo' AS tipo_elemento,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'camisetapolo' OR tipo_elemento = 'camiseta_polo'
                    ) AS cantidad_ingresada,
                    (
                        SELECT COALESCE(SUM(camisetapolo), 0) 
                        FROM dotaciones 
                        WHERE camisetapolo IS NOT NULL AND camisetapolo > 0
                    ) + (
                        SELECT COALESCE(SUM(camisetapolo), 0) 
                        FROM cambios_dotacion 
                        WHERE camisetapolo IS NOT NULL AND camisetapolo > 0
                    ) AS cantidad_entregada,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'camisetapolo' OR tipo_elemento = 'camiseta_polo'
                    ) - (
                        SELECT COALESCE(SUM(camisetapolo), 0) 
                        FROM dotaciones 
                        WHERE camisetapolo IS NOT NULL AND camisetapolo > 0
                    ) - (
                        SELECT COALESCE(SUM(camisetapolo), 0) 
                        FROM cambios_dotacion 
                        WHERE camisetapolo IS NOT NULL AND camisetapolo > 0
                    ) AS saldo_disponible
                
                UNION ALL
                
                SELECT 
                    'botas' AS tipo_elemento,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'botas'
                    ) AS cantidad_ingresada,
                    (
                        SELECT COALESCE(SUM(botas), 0) 
                        FROM dotaciones 
                        WHERE botas IS NOT NULL AND botas > 0
                    ) + (
                        SELECT COALESCE(SUM(botas), 0) 
                        FROM cambios_dotacion 
                        WHERE botas IS NOT NULL AND botas > 0
                    ) AS cantidad_entregada,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'botas'
                    ) - (
                        SELECT COALESCE(SUM(botas), 0) 
                        FROM dotaciones 
                        WHERE botas IS NOT NULL AND botas > 0
                    ) - (
                        SELECT COALESCE(SUM(botas), 0) 
                        FROM cambios_dotacion 
                        WHERE botas IS NOT NULL AND botas > 0
                    ) AS saldo_disponible
                
                UNION ALL
                
                SELECT 
                    'guantes_nitrilo' AS tipo_elemento,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'guantes_nitrilo'
                    ) AS cantidad_ingresada,
                    (
                        SELECT COALESCE(SUM(guantes_nitrilo), 0) 
                        FROM dotaciones 
                        WHERE guantes_nitrilo IS NOT NULL AND guantes_nitrilo > 0
                    ) + (
                        SELECT COALESCE(SUM(guantes_nitrilo), 0) 
                        FROM cambios_dotacion 
                        WHERE guantes_nitrilo IS NOT NULL AND guantes_nitrilo > 0
                    ) AS cantidad_entregada,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'guantes_nitrilo'
                    ) - (
                        SELECT COALESCE(SUM(guantes_nitrilo), 0) 
                        FROM dotaciones 
                        WHERE guantes_nitrilo IS NOT NULL AND guantes_nitrilo > 0
                    ) - (
                        SELECT COALESCE(SUM(guantes_nitrilo), 0) 
                        FROM cambios_dotacion 
                        WHERE guantes_nitrilo IS NOT NULL AND guantes_nitrilo > 0
                    ) AS saldo_disponible
                
                UNION ALL
                
                SELECT 
                    'guantes_carnaza' AS tipo_elemento,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'guantes_carnaza'
                    ) AS cantidad_ingresada,
                    (
                        SELECT COALESCE(SUM(guantes_carnaza), 0) 
                        FROM dotaciones 
                        WHERE guantes_carnaza IS NOT NULL AND guantes_carnaza > 0
                    ) + (
                        SELECT COALESCE(SUM(guantes_carnaza), 0) 
                        FROM cambios_dotacion 
                        WHERE guantes_carnaza IS NOT NULL AND guantes_carnaza > 0
                    ) AS cantidad_entregada,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'guantes_carnaza'
                    ) - (
                        SELECT COALESCE(SUM(guantes_carnaza), 0) 
                        FROM dotaciones 
                        WHERE guantes_carnaza IS NOT NULL AND guantes_carnaza > 0
                    ) - (
                        SELECT COALESCE(SUM(guantes_carnaza), 0) 
                        FROM cambios_dotacion 
                        WHERE guantes_carnaza IS NOT NULL AND guantes_carnaza > 0
                    ) AS saldo_disponible
                
                UNION ALL
                
                SELECT 
                    'gafas' AS tipo_elemento,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'gafas'
                    ) AS cantidad_ingresada,
                    (
                        SELECT COALESCE(SUM(gafas), 0) 
                        FROM dotaciones 
                        WHERE gafas IS NOT NULL AND gafas > 0
                    ) + (
                        SELECT COALESCE(SUM(gafas), 0) 
                        FROM cambios_dotacion 
                        WHERE gafas IS NOT NULL AND gafas > 0
                    ) AS cantidad_entregada,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'gafas'
                    ) - (
                        SELECT COALESCE(SUM(gafas), 0) 
                        FROM dotaciones 
                        WHERE gafas IS NOT NULL AND gafas > 0
                    ) - (
                        SELECT COALESCE(SUM(gafas), 0) 
                        FROM cambios_dotacion 
                        WHERE gafas IS NOT NULL AND gafas > 0
                    ) AS saldo_disponible
                
                UNION ALL
                
                SELECT 
                    'gorra' AS tipo_elemento,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'gorra'
                    ) AS cantidad_ingresada,
                    (
                        SELECT COALESCE(SUM(gorra), 0) 
                        FROM dotaciones 
                        WHERE gorra IS NOT NULL AND gorra > 0
                    ) + (
                        SELECT COALESCE(SUM(gorra), 0) 
                        FROM cambios_dotacion 
                        WHERE gorra IS NOT NULL AND gorra > 0
                    ) AS cantidad_entregada,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'gorra'
                    ) - (
                        SELECT COALESCE(SUM(gorra), 0) 
                        FROM dotaciones 
                        WHERE gorra IS NOT NULL AND gorra > 0
                    ) - (
                        SELECT COALESCE(SUM(gorra), 0) 
                        FROM cambios_dotacion 
                        WHERE gorra IS NOT NULL AND gorra > 0
                    ) AS saldo_disponible
                
                UNION ALL
                
                SELECT 
                    'casco' AS tipo_elemento,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'casco'
                    ) AS cantidad_ingresada,
                    (
                        SELECT COALESCE(SUM(casco), 0) 
                        FROM dotaciones 
                        WHERE casco IS NOT NULL AND casco > 0
                    ) + (
                        SELECT COALESCE(SUM(casco), 0) 
                        FROM cambios_dotacion 
                        WHERE casco IS NOT NULL AND casco > 0
                    ) AS cantidad_entregada,
                    (
                        SELECT COALESCE(SUM(cantidad), 0) 
                        FROM ingresos_dotaciones 
                        WHERE tipo_elemento = 'casco'
                    ) - (
                        SELECT COALESCE(SUM(casco), 0) 
                        FROM dotaciones 
                        WHERE casco IS NOT NULL AND casco > 0
                    ) - (
                        SELECT COALESCE(SUM(casco), 0) 
                        FROM cambios_dotacion 
                        WHERE casco IS NOT NULL AND casco > 0
                    ) AS saldo_disponible
                """
                
                cursor.execute(create_view_query)
                logger.info("Vista vista_stock_dotaciones actualizada exitosamente")
                
            except Exception as view_error:
                logger.error(f"Error actualizando vista_stock_dotaciones: {view_error}")
                # No fallar el endpoint si hay error con la vista, solo registrar
            
            # Confirmar transacción
            connection.commit()
            
            logger.info(f"Stock de dotaciones refrescado exitosamente. {len(stock_actualizado)} materiales procesados")
            
            return jsonify({
                'success': True,
                'message': f'Stock refrescado exitosamente. {len(stock_actualizado)} materiales procesados.',
                'stock_actualizado': stock_actualizado,
                'vista_actualizada': True,
                'timestamp': datetime.now().isoformat()
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos al refrescar stock: {e}")
            if connection:
                connection.rollback()
            return jsonify({
                'success': False, 
                'message': f'Error de base de datos: {str(e)}'
            }), 500
        except Exception as e:
            logger.error(f"Error inesperado al refrescar stock: {e}")
            if connection:
                connection.rollback()
            return jsonify({
                'success': False, 
                'message': f'Error interno: {str(e)}'
            }), 500
        finally:
            if connection:
                connection.close()

    @app.route('/api/firmar-dotacion', methods=['POST'])
    def firmar_dotacion():
        """Endpoint para guardar la firma digital de una dotación"""
        connection = None
        try:
            # Verificar que el usuario esté logueado
            if 'user_id' not in session:
                return jsonify({
                    'success': False,
                    'message': 'Usuario no autenticado'
                }), 401
            
            # Obtener datos del request
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se recibieron datos'
                }), 400
            
            id_dotacion = data.get('id_dotacion')
            firma_base64 = data.get('firma_base64')
            
            # Validar datos requeridos
            if not id_dotacion or not firma_base64:
                return jsonify({
                    'success': False,
                    'message': 'ID de dotación y firma son requeridos'
                }), 400
            
            logger.info(f"Procesando firma para dotación {id_dotacion}")
            
            # Conectar a la base de datos
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            # Verificar que la dotación existe y obtener el técnico asignado
            cursor.execute("""
                SELECT d.id_dotacion, d.id_codigo_consumidor, d.cliente, r.nombre as tecnico_nombre
                FROM dotaciones d
                LEFT JOIN recurso_operativo r ON d.id_codigo_consumidor = r.id_codigo_consumidor
                WHERE d.id_dotacion = %s
            """, (id_dotacion,))
            dotacion = cursor.fetchone()
            
            if not dotacion:
                return jsonify({
                    'success': False,
                    'message': 'Dotación no encontrada'
                }), 404
            
            # Verificar que solo el técnico asignado pueda firmar (o un administrativo)
            user_id_session = session.get('user_id') or session.get('id_codigo_consumidor')
            user_role = session.get('user_role')
            
            # Permitir firma solo si:
            # 1. Es el técnico asignado a la dotación
            # 2. Es un usuario administrativo
            if (str(user_id_session) != str(dotacion['id_codigo_consumidor']) and 
                user_role != 'administrativo'):
                return jsonify({
                    'success': False,
                    'message': f'Solo el técnico asignado ({dotacion["tecnico_nombre"]}) puede firmar esta dotación'
                }), 403
            
            # Verificar que la dotación no esté ya firmada
            cursor.execute("""
                SELECT firmado, fecha_firma 
                FROM dotaciones 
                WHERE id_dotacion = %s AND firmado = 1
            """, (id_dotacion,))
            ya_firmada = cursor.fetchone()
            
            if ya_firmada:
                return jsonify({
                    'success': False,
                    'message': 'Esta dotación ya ha sido firmada'
                }), 400
            
            # Procesar la imagen base64 (remover el prefijo data:image/png;base64,)
            if firma_base64.startswith('data:image/png;base64,'):
                firma_base64 = firma_base64.replace('data:image/png;base64,', '')
            
            # Actualizar la dotación con la firma
            fecha_firma = datetime.now()
            cursor.execute("""
                UPDATE dotaciones 
                SET firmado = 1, 
                    fecha_firma = %s, 
                    firma_imagen = %s,
                    usuario_firma = %s
                WHERE id_dotacion = %s
            """, (fecha_firma, firma_base64, session['user_id'], id_dotacion))
            
            # Verificar que se actualizó correctamente
            if cursor.rowcount == 0:
                return jsonify({
                    'success': False,
                    'message': 'No se pudo actualizar la dotación'
                }), 500
            
            # Confirmar transacción
            connection.commit()
            
            logger.info(f"Firma guardada exitosamente para dotación {id_dotacion} por usuario {session['user_id']}")
            
            return jsonify({
                'success': True,
                'message': 'Firma guardada exitosamente',
                'id_dotacion': id_dotacion,
                'fecha_firma': fecha_firma.isoformat(),
                'firmado': True
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos al guardar firma: {e}")
            if connection:
                connection.rollback()
            return jsonify({
                'success': False,
                'message': f'Error de base de datos: {str(e)}'
            }), 500
        except Exception as e:
            logger.error(f"Error inesperado al guardar firma: {e}")
            if connection:
                connection.rollback()
            return jsonify({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }), 500
        finally:
            if connection:
                connection.close()

    @app.route('/api/obtener-firma/<int:id_dotacion>', methods=['GET'])
    def obtener_firma(id_dotacion):
        """Obtener la firma digital de una dotación"""
        connection = None
        try:
            # Nota: Sin verificación de autenticación para consistencia con dotacion_detalle
            
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            # Verificar que la dotación existe y obtener información de la firma
            cursor.execute("""
                SELECT d.id_dotacion, d.cliente, d.firmado, d.firma_imagen, 
                       d.fecha_firma, d.usuario_firma, ro.nombre as tecnico_nombre
                FROM dotaciones d
                LEFT JOIN recurso_operativo ro ON d.id_codigo_consumidor = ro.id_codigo_consumidor
                WHERE d.id_dotacion = %s
            """, (id_dotacion,))
            
            dotacion = cursor.fetchone()
            
            if not dotacion:
                return jsonify({
                    'success': False,
                    'message': 'Dotación no encontrada'
                }), 404
            
            if not dotacion['firmado'] or not dotacion['firma_imagen']:
                return jsonify({
                    'success': False,
                    'message': 'Esta dotación no tiene firma digital'
                }), 404
            
            # Formatear la fecha de firma
            fecha_firma_str = ''
            if dotacion['fecha_firma']:
                fecha_firma_str = dotacion['fecha_firma'].strftime('%d/%m/%Y %H:%M:%S')
            
            # Crear URL de la imagen base64
            firma_url = f"data:image/png;base64,{dotacion['firma_imagen']}"
            
            return jsonify({
                'success': True,
                'firma_url': firma_url,
                'fecha_firma': fecha_firma_str,
                'usuario_firma': dotacion['usuario_firma'],
                'tecnico_nombre': dotacion['tecnico_nombre'],
                'cliente': dotacion['cliente']
            })
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos al obtener firma: {e}")
            return jsonify({
                'success': False,
                'message': f'Error de base de datos: {str(e)}'
            }), 500
        except Exception as e:
            logger.error(f"Error inesperado al obtener firma: {e}")
            return jsonify({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }), 500
        finally:
            if connection:
                connection.close()

    logger.info("Rutas de dotaciones registradas correctamente")

if __name__ == '__main__':
    # Código de prueba
    from flask import Flask
    app = Flask(__name__)
    registrar_rutas_dotaciones(app)
    
    print("Módulo de dotaciones configurado correctamente")
    print("Rutas disponibles:")
    print("- GET /logistica/dotaciones - Página principal")
    print("- GET /api/dotaciones - Listar dotaciones")
    print("- POST /api/dotaciones - Crear dotación")
    print("- GET /api/dotaciones/<id> - Obtener dotación")
    print("- PUT /api/dotaciones/<id> - Actualizar dotación")
    print("- DELETE /api/dotaciones/<id> - Eliminar dotación")
    print("- GET /api/tecnicos - Listar técnicos")
    print("- GET /api/dotaciones/estadisticas - Estadísticas")
    print("- GET /api/dotaciones/export - Exportar CSV")
