#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de API para gestión de dotaciones
Sistema de Logística - Capired
"""

import mysql.connector
from flask import jsonify, request, render_template_string, render_template
from datetime import datetime
import json
import logging

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
    
    @app.route('/logistica/dotaciones')
    def dotaciones_page():
        """Página principal del módulo de dotaciones"""
        try:
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
    
    @app.route('/api/dotaciones', methods=['POST'])
    def crear_dotacion():
        """Crear una nueva dotación"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            data = request.get_json()
            
            # Validar datos requeridos
            if not data.get('cliente'):
                return jsonify({'success': False, 'message': 'El campo cliente es requerido'}), 400
            
            cursor = connection.cursor()
            
            # Preparar query de inserción
            query = """
            INSERT INTO dotaciones (
                cliente, id_codigo_consumidor, pantalon, pantalon_talla,
                camisetagris, camiseta_gris_talla, guerrera, guerrera_talla,
                camisetapolo, camiseta_polo_talla, guantes_nitrilo, guantes_carnaza,
                gafas, gorra, casco, botas, botas_talla,
                estado_pantalon, estado_camisetagris, estado_guerrera, estado_camisetapolo,
                estado_guantes_nitrilo, estado_guantes_carnaza, estado_gafas, estado_gorra,
                estado_casco, estado_botas, fecha_registro
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
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
                data.get('camisetapolo'),
                data.get('camiseta_polo_talla'),
                data.get('guantes_nitrilo'),
                data.get('guantes_carnaza'),
                data.get('gafas'),
                data.get('gorra'),
                data.get('casco'),
                data.get('botas'),
                data.get('botas_talla'),
                # Estados de valoración
                data.get('estado_pantalon', 'VALORADO'),
                data.get('estado_camisetagris', 'VALORADO'),
                data.get('estado_guerrera', 'VALORADO'),
                data.get('estado_camisetapolo', 'VALORADO'),
                data.get('estado_guantes_nitrilo', 'VALORADO'),
                data.get('estado_guantes_carnaza', 'VALORADO'),
                data.get('estado_gafas', 'VALORADO'),
                data.get('estado_gorra', 'VALORADO'),
                data.get('estado_casco', 'VALORADO'),
                data.get('estado_botas', 'VALORADO')
            )
            
            cursor.execute(query, valores)
            id_dotacion = cursor.lastrowid
            
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
    
    @app.route('/api/dotaciones/<int:id_dotacion>', methods=['PUT'])
    def actualizar_dotacion(id_dotacion):
        """Actualizar una dotación existente"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        try:
            data = request.get_json()
            
            # Validar que la dotación existe
            cursor = connection.cursor()
            cursor.execute("SELECT id_dotacion FROM dotaciones WHERE id_dotacion = %s", (id_dotacion,))
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': 'Dotación no encontrada'}), 404
            
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
                estado_camisetapolo = %s,
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
                data.get('guantes_nitrilo'),
                data.get('guantes_carnaza'),
                data.get('gafas'),
                data.get('gorra'),
                data.get('casco'),
                data.get('botas'),
                data.get('botas_talla'),
                # Estados de valoración
                data.get('estado_pantalon', 'VALORADO'),
                data.get('estado_camisetagris', 'VALORADO'),
                data.get('estado_guerrera', 'VALORADO'),
                data.get('estado_camisetapolo', 'VALORADO'),
                data.get('estado_guantes_nitrilo', 'VALORADO'),
                data.get('estado_guantes_carnaza', 'VALORADO'),
                data.get('estado_gafas', 'VALORADO'),
                data.get('estado_gorra', 'VALORADO'),
                data.get('estado_casco', 'VALORADO'),
                data.get('estado_botas', 'VALORADO'),
                id_dotacion
            )
            
            cursor.execute(query, valores)
            
            logger.info(f"Dotación {id_dotacion} actualizada")
            
            return jsonify({
                'success': True,
                'message': 'Dotación actualizada correctamente'
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
                estado
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
                data.get('talla'),
                data.get('numero_calzado'),
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
            
            # Obtener stock usando la vista creada
            query = "SELECT * FROM vista_stock_dotaciones ORDER BY tipo_elemento"
            cursor.execute(query)
            stock_data = cursor.fetchall()
            
            # Convertir Decimal a int para JSON
            for item in stock_data:
                for key, value in item.items():
                    if hasattr(value, 'is_integer'):
                        item[key] = int(value)
            
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
                SUM(botas) as botas
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
                SELECT 'botas' as elemento
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
                    WHEN tipo_elemento = 'pantalon' THEN 'Sin talla'
                    ELSE COALESCE(talla, 'Sin talla')
                END as talla,
                COALESCE(numero_calzado, 'Sin número') as numero_calzado,
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
            
            # Query para obtener entregas por tallas
            entregas_query = """
            SELECT 
                'pantalon' as tipo_elemento,
                'Sin talla' as talla,
                COALESCE(pantalon_talla, 'Sin número') as numero_calzado,
                SUM(pantalon) as total_entregado
            FROM dotaciones
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
                'guerrera' as tipo_elemento,
                COALESCE(guerrera_talla, 'Sin talla') as talla,
                'Sin número' as numero_calzado,
                SUM(guerrera) as total_entregado
            FROM dotaciones
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
                'botas' as tipo_elemento,
                'Sin talla' as talla,
                COALESCE(botas_talla, 'Sin número') as numero_calzado,
                SUM(botas) as total_entregado
            FROM dotaciones
            WHERE botas > 0
            GROUP BY botas_talla
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
            
            # Procesar entregas
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
                stock_por_tallas[key]['total_entregado'] = int(entrega['total_entregado'])
            
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