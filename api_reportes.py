#!/usr/bin/env python3
"""
API Routes for Advanced Reporting Module
Implements advanced filtering, consolidated reports, and data validation APIs
"""

from flask import Flask, request, jsonify, session
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import json
from functools import wraps
import os
from dotenv import load_dotenv
import pytz
from collections import defaultdict
import pandas as pd
import io
import csv

load_dotenv()

# Configuración de zona horaria
TIMEZONE = pytz.timezone('America/Bogota')

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT')),
    'time_zone': '+00:00'
}

# Roles definition
ROLES = {
    '1': 'administrativo',
    '2': 'tecnicos',
    '3': 'operativo',
    '4': 'contabilidad',
    '5': 'logistica'
}

def get_db_connection():
    """Función para obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        return None

def get_bogota_datetime():
    """Función para obtener la fecha y hora actual en Bogotá"""
    return datetime.now(TIMEZONE)

def login_required_api(role=None):
    """Decorador para requerir autenticación en APIs"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Autenticación requerida', 'code': 'AUTH_REQUIRED'}), 401
            if role:
                ur = str(session.get('user_role') or '').strip().lower()
                if isinstance(role, (list, tuple, set)):
                    roles_norm = {str(r).strip().lower() for r in role}
                    if ur not in roles_norm and ur != 'administrativo':
                        return jsonify({'error': 'Permisos insuficientes', 'code': 'INSUFFICIENT_PERMISSIONS'}), 403
                else:
                    req_role = str(role or '').strip().lower()
                    if ur != req_role and ur != 'administrativo':
                        return jsonify({'error': 'Permisos insuficientes', 'code': 'INSUFFICIENT_PERMISSIONS'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_reportes_filtros_avanzados():
    """
    API para filtros avanzados de reportes
    Endpoint: /api/reportes/filtros/avanzados
    Métodos: GET, POST
    """
    try:
        if request.method == 'GET':
            # Obtener opciones de filtros disponibles
            connection = get_db_connection()
            if connection is None:
                return jsonify({'error': 'Error de conexión a la base de datos'}), 500
                
            cursor = connection.cursor(dictionary=True)
            
            # Obtener supervisores únicos
            cursor.execute("""
                SELECT DISTINCT supervisor 
                FROM preoperacional 
                WHERE supervisor IS NOT NULL AND supervisor != ''
                ORDER BY supervisor
            """)
            supervisores = [row['supervisor'] for row in cursor.fetchall()]
            
            # Obtener centros de trabajo únicos
            cursor.execute("""
                SELECT DISTINCT centro_de_trabajo 
                FROM preoperacional 
                WHERE centro_de_trabajo IS NOT NULL AND centro_de_trabajo != ''
                ORDER BY centro_de_trabajo
            """)
            centros_trabajo = [row['centro_de_trabajo'] for row in cursor.fetchall()]
            
            # Obtener ciudades únicas
            cursor.execute("""
                SELECT DISTINCT ciudad 
                FROM preoperacional 
                WHERE ciudad IS NOT NULL AND ciudad != ''
                ORDER BY ciudad
            """)
            ciudades = [row['ciudad'] for row in cursor.fetchall()]
            
            # Obtener tipos de vehículo únicos
            cursor.execute("""
                SELECT DISTINCT tipo_vehiculo 
                FROM preoperacional 
                WHERE tipo_vehiculo IS NOT NULL AND tipo_vehiculo != ''
                ORDER BY tipo_vehiculo
            """)
            tipos_vehiculo = [row['tipo_vehiculo'] for row in cursor.fetchall()]
            
            # Obtener configuraciones de reportes del usuario
            cursor.execute("""
                SELECT * FROM reportes_configuracion 
                WHERE usuario_id = %s AND activo = 1
                ORDER BY nombre_configuracion
            """, (session.get('user_id'),))
            configuraciones = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'filtros': {
                    'supervisores': supervisores,
                    'centros_trabajo': centros_trabajo,
                    'ciudades': ciudades,
                    'tipos_vehiculo': tipos_vehiculo
                },
                'configuraciones_guardadas': configuraciones
            })
            
        elif request.method == 'POST':
            # Aplicar filtros avanzados y obtener datos
            data = request.get_json()
            
            # Validar datos de entrada
            if not data:
                return jsonify({'error': 'Datos de filtro requeridos'}), 400
            
            # Construir consulta dinámica basada en filtros
            connection = get_db_connection()
            if connection is None:
                return jsonify({'error': 'Error de conexión a la base de datos'}), 500
                
            cursor = connection.cursor(dictionary=True)
            
            # Construir WHERE clause dinámicamente
            where_conditions = []
            params = []
            
            # Filtros de fecha
            if data.get('fecha_inicio'):
                where_conditions.append('p.fecha >= %s')
                params.append(data['fecha_inicio'])
            
            if data.get('fecha_fin'):
                where_conditions.append('p.fecha <= %s')
                params.append(data['fecha_fin'])
            
            # Filtros de supervisor
            if data.get('supervisores') and len(data['supervisores']) > 0:
                placeholders = ','.join(['%s'] * len(data['supervisores']))
                where_conditions.append(f'p.supervisor IN ({placeholders})')
                params.extend(data['supervisores'])
            
            # Filtros de centro de trabajo
            if data.get('centros_trabajo') and len(data['centros_trabajo']) > 0:
                placeholders = ','.join(['%s'] * len(data['centros_trabajo']))
                where_conditions.append(f'p.centro_de_trabajo IN ({placeholders})')
                params.extend(data['centros_trabajo'])
            
            # Filtros de ciudad
            if data.get('ciudades') and len(data['ciudades']) > 0:
                placeholders = ','.join(['%s'] * len(data['ciudades']))
                where_conditions.append(f'p.ciudad IN ({placeholders})')
                params.extend(data['ciudades'])
            
            # Filtros de tipo de vehículo
            if data.get('tipos_vehiculo') and len(data['tipos_vehiculo']) > 0:
                placeholders = ','.join(['%s'] * len(data['tipos_vehiculo']))
                where_conditions.append(f'p.tipo_vehiculo IN ({placeholders})')
                params.extend(data['tipos_vehiculo'])
            
            # Filtros de estado de vehículo
            if data.get('estado_vehiculo'):
                if data['estado_vehiculo'] == 'problemas':
                    where_conditions.append("""
                        (p.estado_espejos = '0' OR p.bocina_pito = '0' OR p.frenos = '0' 
                         OR p.encendido = '0' OR p.estado_bateria = '0' OR p.estado_amortiguadores = '0' 
                         OR p.estado_llantas = '0' OR p.luces_altas_bajas = '0' 
                         OR p.direccionales_delanteras_traseras = '0')
                    """)
                elif data['estado_vehiculo'] == 'sin_problemas':
                    where_conditions.append("""
                        (p.estado_espejos != '0' AND p.bocina_pito != '0' AND p.frenos != '0' 
                         AND p.encendido != '0' AND p.estado_bateria != '0' AND p.estado_amortiguadores != '0' 
                         AND p.estado_llantas != '0' AND p.luces_altas_bajas != '0' 
                         AND p.direccionales_delanteras_traseras != '0')
                    """)
            
            # Construir consulta final
            where_sql = ' AND '.join(where_conditions) if where_conditions else '1=1'
            
            query = f"""
                SELECT 
                    p.*,
                    r.nombre as nombre_tecnico,
                    r.recurso_operativo_cedula as cedula_tecnico,
                    r.cargo as cargo_tecnico
                FROM preoperacional p
                JOIN recurso_operativo r ON p.id_codigo_consumidor = r.id_codigo_consumidor
                WHERE {where_sql}
                ORDER BY p.fecha DESC
                LIMIT 1000
            """
            
            cursor.execute(query, params)
            registros = cursor.fetchall()
            
            # Calcular estadísticas
            total_registros = len(registros)
            registros_con_problemas = 0
            problemas_por_categoria = defaultdict(int)
            
            for registro in registros:
                tiene_problemas = False
                
                # Verificar cada categoría de problemas
                categorias = {
                    'Espejos': registro.get('estado_espejos') == '0',
                    'Bocina': registro.get('bocina_pito') == '0',
                    'Frenos': registro.get('frenos') == '0',
                    'Encendido': registro.get('encendido') == '0',
                    'Batería': registro.get('estado_bateria') == '0',
                    'Amortiguadores': registro.get('estado_amortiguadores') == '0',
                    'Llantas': registro.get('estado_llantas') == '0',
                    'Luces': registro.get('luces_altas_bajas') == '0',
                    'Direccionales': registro.get('direccionales_delanteras_traseras') == '0'
                }
                
                for categoria, tiene_problema in categorias.items():
                    if tiene_problema:
                        problemas_por_categoria[categoria] += 1
                        tiene_problemas = True
                
                if tiene_problemas:
                    registros_con_problemas += 1
            
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'data': registros,
                'estadisticas': {
                    'total_registros': total_registros,
                    'registros_con_problemas': registros_con_problemas,
                    'porcentaje_problemas': round((registros_con_problemas / total_registros * 100) if total_registros > 0 else 0, 2),
                    'problemas_por_categoria': dict(problemas_por_categoria)
                },
                'filtros_aplicados': data
            })
            
    except Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

def api_reportes_consolidacion_jerarquica():
    """
    API para consolidación jerárquica de datos (folder-based filtering)
    Endpoint: /api/reportes/consolidacion/jerarquica
    Método: POST
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos de configuración requeridos'}), 400
        
        jerarquia = data.get('jerarquia', ['supervisor', 'centro_trabajo', 'ciudad'])  # Orden jerárquico
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        incluir_detalles = data.get('incluir_detalles', False)
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({'error': 'Fechas de inicio y fin son requeridas'}), 400
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Construir estructura jerárquica
        def construir_jerarquia_recursiva(nivel_actual, filtros_padre=None):
            if nivel_actual >= len(jerarquia):
                return []
            
            campo_actual = jerarquia[nivel_actual]
            
            # Mapear campos a columnas de base de datos
            campo_db = {
                'supervisor': 'p.supervisor',
                'centro_trabajo': 'p.centro_de_trabajo', 
                'ciudad': 'p.ciudad',
                'tipo_vehiculo': 'p.tipo_vehiculo'
            }.get(campo_actual, f'p.{campo_actual}')
            
            # Construir WHERE clause con filtros padre
            where_conditions = ['p.fecha >= %s', 'p.fecha <= %s']
            params = [fecha_inicio, fecha_fin]
            
            if filtros_padre:
                for filtro in filtros_padre:
                    where_conditions.append(f"{filtro['campo']} = %s")
                    params.append(filtro['valor'])
            
            where_sql = ' AND '.join(where_conditions)
            
            # Consulta para obtener valores únicos del nivel actual
            query = f"""
                SELECT 
                    {campo_db} as valor,
                    COUNT(*) as total_registros,
                    COUNT(DISTINCT p.id_codigo_consumidor) as tecnicos_unicos,
                    SUM(CASE WHEN (
                        p.estado_espejos = '0' OR p.bocina_pito = '0' OR p.frenos = '0' 
                        OR p.encendido = '0' OR p.estado_bateria = '0' OR p.estado_amortiguadores = '0' 
                        OR p.estado_llantas = '0' OR p.luces_altas_bajas = '0' 
                        OR p.direccionales_delanteras_traseras = '0'
                    ) THEN 1 ELSE 0 END) as registros_con_problemas,
                    AVG(CASE WHEN (
                        p.estado_espejos != '0' AND p.bocina_pito != '0' AND p.frenos != '0' 
                        AND p.encendido != '0' AND p.estado_bateria != '0' AND p.estado_amortiguadores != '0' 
                        AND p.estado_llantas != '0' AND p.luces_altas_bajas != '0' 
                        AND p.direccionales_delanteras_traseras != '0'
                    ) THEN 100 ELSE 0 END) as porcentaje_cumplimiento
                FROM preoperacional p
                JOIN recurso_operativo r ON p.id_codigo_consumidor = r.id_codigo_consumidor
                WHERE {where_sql}
                GROUP BY {campo_db}
                HAVING {campo_db} IS NOT NULL AND {campo_db} != ''
                ORDER BY total_registros DESC
            """
            
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            
            nodos = []
            for resultado in resultados:
                # Calcular métricas
                porcentaje_problemas = round(
                    (resultado['registros_con_problemas'] / resultado['total_registros'] * 100) 
                    if resultado['total_registros'] > 0 else 0, 2
                )
                
                nodo = {
                    'nivel': campo_actual,
                    'valor': resultado['valor'],
                    'metricas': {
                        'total_registros': resultado['total_registros'],
                        'tecnicos_unicos': resultado['tecnicos_unicos'],
                        'registros_con_problemas': resultado['registros_con_problemas'],
                        'porcentaje_problemas': porcentaje_problemas,
                        'porcentaje_cumplimiento': round(resultado['porcentaje_cumplimiento'], 2)
                    },
                    'hijos': []
                }
                
                # Construir filtros para el siguiente nivel
                nuevos_filtros = (filtros_padre or []).copy()
                nuevos_filtros.append({
                    'campo': campo_db,
                    'valor': resultado['valor']
                })
                
                # Recursión para el siguiente nivel
                if nivel_actual + 1 < len(jerarquia):
                    nodo['hijos'] = construir_jerarquia_recursiva(nivel_actual + 1, nuevos_filtros)
                
                # Agregar detalles si se solicita y es el último nivel
                if incluir_detalles and nivel_actual == len(jerarquia) - 1:
                    nodo['detalles'] = obtener_detalles_registros(nuevos_filtros, cursor)
                
                nodos.append(nodo)
            
            return nodos
        
        # Construir jerarquía completa
        estructura_jerarquica = construir_jerarquia_recursiva(0)
        
        # Calcular totales generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_general,
                COUNT(DISTINCT p.id_codigo_consumidor) as tecnicos_total,
                SUM(CASE WHEN (
                    p.estado_espejos = '0' OR p.bocina_pito = '0' OR p.frenos = '0' 
                    OR p.encendido = '0' OR p.estado_bateria = '0' OR p.estado_amortiguadores = '0' 
                    OR p.estado_llantas = '0' OR p.luces_altas_bajas = '0' 
                    OR p.direccionales_delanteras_traseras = '0'
                ) THEN 1 ELSE 0 END) as problemas_total
            FROM preoperacional p
            WHERE p.fecha >= %s AND p.fecha <= %s
        """, (fecha_inicio, fecha_fin))
        
        totales = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'jerarquia_aplicada': jerarquia,
            'periodo': {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            },
            'estructura': estructura_jerarquica,
            'resumen_general': {
                'total_registros': totales['total_general'],
                'tecnicos_participantes': totales['tecnicos_total'],
                'total_problemas': totales['problemas_total'],
                'porcentaje_problemas_general': round(
                    (totales['problemas_total'] / totales['total_general'] * 100) 
                    if totales['total_general'] > 0 else 0, 2
                )
            }
        })
        
    except Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

def obtener_detalles_registros(filtros, cursor):
    """
    Función auxiliar para obtener detalles de registros según filtros
    """
    where_conditions = ['p.fecha >= %s', 'p.fecha <= %s']
    params = []
    
    for filtro in filtros:
        where_conditions.append(f"{filtro['campo']} = %s")
        params.append(filtro['valor'])
    
    where_sql = ' AND '.join(where_conditions[2:])  # Excluir fechas que se manejan aparte
    
    query = f"""
        SELECT 
            p.id,
            p.fecha,
            r.nombre as tecnico,
            r.recurso_operativo_cedula as cedula,
            p.supervisor,
            p.centro_de_trabajo,
            p.ciudad,
            p.tipo_vehiculo,
            CASE WHEN (
                p.estado_espejos = '0' OR p.bocina_pito = '0' OR p.frenos = '0' 
                OR p.encendido = '0' OR p.estado_bateria = '0' OR p.estado_amortiguadores = '0' 
                OR p.estado_llantas = '0' OR p.luces_altas_bajas = '0' 
                OR p.direccionales_delanteras_traseras = '0'
            ) THEN 'Con problemas' ELSE 'Sin problemas' END as estado_vehiculo
        FROM preoperacional p
        JOIN recurso_operativo r ON p.id_codigo_consumidor = r.id_codigo_consumidor
        WHERE {where_sql}
        ORDER BY p.fecha DESC
        LIMIT 50
    """
    
    cursor.execute(query, params)
    return cursor.fetchall()

def api_reportes_analisis_tendencias():
    """
    API para análisis de tendencias y patrones
    Endpoint: /api/reportes/analisis/tendencias
    Método: POST
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos de configuración requeridos'}), 400
        
        tipo_analisis = data.get('tipo', 'temporal')  # temporal, comparativo, predictivo
        granularidad = data.get('granularidad', 'diario')  # diario, semanal, mensual
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({'error': 'Fechas de inicio y fin son requeridas'}), 400
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        if tipo_analisis == 'temporal':
            # Análisis temporal con granularidad especificada
            if granularidad == 'diario':
                date_format = '%Y-%m-%d'
                date_group = 'DATE(p.fecha)'
            elif granularidad == 'semanal':
                date_format = '%Y-%u'
                date_group = 'YEARWEEK(p.fecha)'
            elif granularidad == 'mensual':
                date_format = '%Y-%m'
                date_group = 'DATE_FORMAT(p.fecha, "%Y-%m")'
            else:
                return jsonify({'error': 'Granularidad no válida'}), 400
            
            query = f"""
                SELECT 
                    {date_group} as periodo,
                    COUNT(*) as total_registros,
                    COUNT(DISTINCT p.id_codigo_consumidor) as tecnicos_activos,
                    SUM(CASE WHEN (
                        p.estado_espejos = '0' OR p.bocina_pito = '0' OR p.frenos = '0' 
                        OR p.encendido = '0' OR p.estado_bateria = '0' OR p.estado_amortiguadores = '0' 
                        OR p.estado_llantas = '0' OR p.luces_altas_bajas = '0' 
                        OR p.direccionales_delanteras_traseras = '0'
                    ) THEN 1 ELSE 0 END) as registros_con_problemas,
                    AVG(CASE WHEN (
                        p.estado_espejos != '0' AND p.bocina_pito != '0' AND p.frenos != '0' 
                        AND p.encendido != '0' AND p.estado_bateria != '0' AND p.estado_amortiguadores != '0' 
                        AND p.estado_llantas != '0' AND p.luces_altas_bajas != '0' 
                        AND p.direccionales_delanteras_traseras != '0'
                    ) THEN 100 ELSE 0 END) as porcentaje_cumplimiento
                FROM preoperacional p
                WHERE p.fecha >= %s AND p.fecha <= %s
                GROUP BY {date_group}
                ORDER BY periodo
            """
            
            cursor.execute(query, (fecha_inicio, fecha_fin))
            resultados = cursor.fetchall()
            
            # Calcular tendencias
            tendencias = []
            for i, resultado in enumerate(resultados):
                porcentaje_problemas = round(
                    (resultado['registros_con_problemas'] / resultado['total_registros'] * 100) 
                    if resultado['total_registros'] > 0 else 0, 2
                )
                
                # Calcular cambio respecto al período anterior
                cambio_registros = 0
                cambio_problemas = 0
                if i > 0:
                    anterior = resultados[i-1]
                    cambio_registros = round(
                        ((resultado['total_registros'] - anterior['total_registros']) / anterior['total_registros'] * 100)
                        if anterior['total_registros'] > 0 else 0, 2
                    )
                    
                    porcentaje_anterior = round(
                        (anterior['registros_con_problemas'] / anterior['total_registros'] * 100) 
                        if anterior['total_registros'] > 0 else 0, 2
                    )
                    cambio_problemas = round(porcentaje_problemas - porcentaje_anterior, 2)
                
                tendencias.append({
                    'periodo': resultado['periodo'],
                    'total_registros': resultado['total_registros'],
                    'tecnicos_activos': resultado['tecnicos_activos'],
                    'registros_con_problemas': resultado['registros_con_problemas'],
                    'porcentaje_problemas': porcentaje_problemas,
                    'porcentaje_cumplimiento': round(resultado['porcentaje_cumplimiento'], 2),
                    'cambio_registros': cambio_registros,
                    'cambio_problemas': cambio_problemas
                })
            
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'tipo_analisis': tipo_analisis,
                'granularidad': granularidad,
                'periodo': {
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin
                },
                'tendencias': tendencias,
                'insights': generar_insights_tendencias(tendencias)
            })
            
    except Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

def generar_insights_tendencias(tendencias):
    """
    Función auxiliar para generar insights automáticos de tendencias
    """
    if not tendencias or len(tendencias) < 2:
        return []
    
    insights = []
    
    # Analizar tendencia general de problemas
    problemas_inicio = tendencias[0]['porcentaje_problemas']
    problemas_fin = tendencias[-1]['porcentaje_problemas']
    cambio_total = problemas_fin - problemas_inicio
    
    if cambio_total > 5:
        insights.append({
            'tipo': 'alerta',
            'mensaje': f'Incremento significativo en problemas: +{cambio_total:.1f}% en el período',
            'prioridad': 'alta'
        })
    elif cambio_total < -5:
        insights.append({
            'tipo': 'positivo',
            'mensaje': f'Mejora significativa en calidad: -{abs(cambio_total):.1f}% menos problemas',
            'prioridad': 'media'
        })
    
    # Detectar picos de problemas
    max_problemas = max(t['porcentaje_problemas'] for t in tendencias)
    if max_problemas > 20:
        periodo_max = next(t['periodo'] for t in tendencias if t['porcentaje_problemas'] == max_problemas)
        insights.append({
            'tipo': 'alerta',
            'mensaje': f'Pico de problemas detectado en {periodo_max}: {max_problemas:.1f}%',
            'prioridad': 'alta'
        })
    
    # Analizar consistencia de registros
    registros_promedio = sum(t['total_registros'] for t in tendencias) / len(tendencias)
    variaciones_altas = [t for t in tendencias if abs(t['total_registros'] - registros_promedio) > registros_promedio * 0.3]
    
    if variaciones_altas:
        insights.append({
            'tipo': 'informativo',
            'mensaje': f'Detectadas {len(variaciones_altas)} variaciones significativas en volumen de registros',
            'prioridad': 'media'
        })
    
    return insights

def api_reportes_generar_consolidado():
    """
    API para generar reportes consolidados
    Endpoint: /api/reportes/generar/consolidado
    Método: POST
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos de configuración requeridos'}), 400
        
        tipo_consolidacion = data.get('tipo', 'supervisor')  # supervisor, centro_trabajo, ciudad, fecha
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({'error': 'Fechas de inicio y fin son requeridas'}), 400
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Construir consulta según tipo de consolidación
        if tipo_consolidacion == 'supervisor':
            group_field = 'p.supervisor'
            group_label = 'supervisor'
        elif tipo_consolidacion == 'centro_trabajo':
            group_field = 'p.centro_de_trabajo'
            group_label = 'centro_trabajo'
        elif tipo_consolidacion == 'ciudad':
            group_field = 'p.ciudad'
            group_label = 'ciudad'
        elif tipo_consolidacion == 'fecha':
            group_field = 'DATE(p.fecha)'
            group_label = 'fecha'
        else:
            return jsonify({'error': 'Tipo de consolidación no válido'}), 400
        
        query = f"""
            SELECT 
                {group_field} as grupo,
                COUNT(*) as total_registros,
                COUNT(DISTINCT p.id_codigo_consumidor) as tecnicos_unicos,
                SUM(CASE WHEN (
                    p.estado_espejos = '0' OR p.bocina_pito = '0' OR p.frenos = '0' 
                    OR p.encendido = '0' OR p.estado_bateria = '0' OR p.estado_amortiguadores = '0' 
                    OR p.estado_llantas = '0' OR p.luces_altas_bajas = '0' 
                    OR p.direccionales_delanteras_traseras = '0'
                ) THEN 1 ELSE 0 END) as registros_con_problemas,
                AVG(CASE WHEN (
                    p.estado_espejos != '0' AND p.bocina_pito != '0' AND p.frenos != '0' 
                    AND p.encendido != '0' AND p.estado_bateria != '0' AND p.estado_amortiguadores != '0' 
                    AND p.estado_llantas != '0' AND p.luces_altas_bajas != '0' 
                    AND p.direccionales_delanteras_traseras != '0'
                ) THEN 100 ELSE 0 END) as porcentaje_cumplimiento
            FROM preoperacional p
            JOIN recurso_operativo r ON p.id_codigo_consumidor = r.id_codigo_consumidor
            WHERE p.fecha >= %s AND p.fecha <= %s
            GROUP BY {group_field}
            HAVING {group_field} IS NOT NULL AND {group_field} != ''
            ORDER BY total_registros DESC
        """
        
        cursor.execute(query, (fecha_inicio, fecha_fin))
        resultados = cursor.fetchall()
        
        # Calcular totales generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_general,
                COUNT(DISTINCT p.id_codigo_consumidor) as tecnicos_total,
                SUM(CASE WHEN (
                    p.estado_espejos = '0' OR p.bocina_pito = '0' OR p.frenos = '0' 
                    OR p.encendido = '0' OR p.estado_bateria = '0' OR p.estado_amortiguadores = '0' 
                    OR p.estado_llantas = '0' OR p.luces_altas_bajas = '0' 
                    OR p.direccionales_delanteras_traseras = '0'
                ) THEN 1 ELSE 0 END) as problemas_total
            FROM preoperacional p
            WHERE p.fecha >= %s AND p.fecha <= %s
        """, (fecha_inicio, fecha_fin))
        
        totales = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        # Formatear resultados
        datos_consolidados = []
        for resultado in resultados:
            porcentaje_problemas = round(
                (resultado['registros_con_problemas'] / resultado['total_registros'] * 100) 
                if resultado['total_registros'] > 0 else 0, 2
            )
            
            datos_consolidados.append({
                group_label: resultado['grupo'],
                'total_registros': resultado['total_registros'],
                'tecnicos_unicos': resultado['tecnicos_unicos'],
                'registros_con_problemas': resultado['registros_con_problemas'],
                'porcentaje_problemas': porcentaje_problemas,
                'porcentaje_cumplimiento': round(resultado['porcentaje_cumplimiento'], 2)
            })
        
        return jsonify({
            'success': True,
            'tipo_consolidacion': tipo_consolidacion,
            'periodo': {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            },
            'datos': datos_consolidados,
            'resumen_general': {
                'total_registros': totales['total_general'],
                'tecnicos_participantes': totales['tecnicos_total'],
                'total_problemas': totales['problemas_total'],
                'porcentaje_problemas_general': round(
                    (totales['problemas_total'] / totales['total_general'] * 100) 
                    if totales['total_general'] > 0 else 0, 2
                )
            }
        })
        
    except Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

def api_reportes_validar_consistencia():
    """
    API para validar consistencia de datos
    Endpoint: /api/reportes/validar/consistencia
    Método: GET
    """
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        inconsistencias = []
        
        # 1. Verificar registros duplicados por técnico y fecha
        cursor.execute("""
            SELECT 
                id_codigo_consumidor,
                DATE(fecha) as fecha,
                COUNT(*) as cantidad
            FROM preoperacional
            GROUP BY id_codigo_consumidor, DATE(fecha)
            HAVING COUNT(*) > 1
        """)
        duplicados = cursor.fetchall()
        
        if duplicados:
            inconsistencias.append({
                'tipo': 'registros_duplicados',
                'descripcion': 'Técnicos con múltiples registros en la misma fecha',
                'cantidad': len(duplicados),
                'detalles': duplicados
            })
        
        # 2. Verificar técnicos sin registros en los últimos 30 días
        cursor.execute("""
            SELECT 
                r.id_codigo_consumidor,
                r.nombre,
                r.recurso_operativo_cedula,
                MAX(p.fecha) as ultimo_registro
            FROM recurso_operativo r
            LEFT JOIN preoperacional p ON r.id_codigo_consumidor = p.id_codigo_consumidor
            WHERE r.estado = 'Activo' AND r.id_roles = 2
            GROUP BY r.id_codigo_consumidor
            HAVING ultimo_registro IS NULL OR ultimo_registro < DATE_SUB(NOW(), INTERVAL 30 DAY)
        """)
        tecnicos_inactivos = cursor.fetchall()
        
        if tecnicos_inactivos:
            inconsistencias.append({
                'tipo': 'tecnicos_sin_registros',
                'descripcion': 'Técnicos activos sin registros en los últimos 30 días',
                'cantidad': len(tecnicos_inactivos),
                'detalles': tecnicos_inactivos
            })
        
        # 3. Verificar registros con datos incompletos
        cursor.execute("""
            SELECT 
                p.id,
                p.fecha,
                r.nombre,
                CASE 
                    WHEN p.supervisor IS NULL OR p.supervisor = '' THEN 'supervisor_vacio'
                    WHEN p.centro_de_trabajo IS NULL OR p.centro_de_trabajo = '' THEN 'centro_trabajo_vacio'
                    WHEN p.ciudad IS NULL OR p.ciudad = '' THEN 'ciudad_vacia'
                    WHEN p.tipo_vehiculo IS NULL OR p.tipo_vehiculo = '' THEN 'tipo_vehiculo_vacio'
                    ELSE 'otros'
                END as tipo_problema
            FROM preoperacional p
            JOIN recurso_operativo r ON p.id_codigo_consumidor = r.id_codigo_consumidor
            WHERE (p.supervisor IS NULL OR p.supervisor = '')
               OR (p.centro_de_trabajo IS NULL OR p.centro_de_trabajo = '')
               OR (p.ciudad IS NULL OR p.ciudad = '')
               OR (p.tipo_vehiculo IS NULL OR p.tipo_vehiculo = '')
            ORDER BY p.fecha DESC
            LIMIT 100
        """)
        datos_incompletos = cursor.fetchall()
        
        if datos_incompletos:
            inconsistencias.append({
                'tipo': 'datos_incompletos',
                'descripcion': 'Registros con campos obligatorios vacíos',
                'cantidad': len(datos_incompletos),
                'detalles': datos_incompletos
            })
        
        # 4. Verificar fechas futuras
        cursor.execute("""
            SELECT 
                p.id,
                p.fecha,
                r.nombre
            FROM preoperacional p
            JOIN recurso_operativo r ON p.id_codigo_consumidor = r.id_codigo_consumidor
            WHERE p.fecha > NOW()
            ORDER BY p.fecha DESC
        """)
        fechas_futuras = cursor.fetchall()
        
        if fechas_futuras:
            inconsistencias.append({
                'tipo': 'fechas_futuras',
                'descripcion': 'Registros con fechas futuras',
                'cantidad': len(fechas_futuras),
                'detalles': fechas_futuras
            })
        
        cursor.close()
        connection.close()
        
        # Calcular puntuación de calidad de datos
        total_registros_query = """
            SELECT COUNT(*) as total FROM preoperacional 
            WHERE fecha >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(total_registros_query)
        total_registros = cursor.fetchone()['total']
        cursor.close()
        connection.close()
        
        total_problemas = sum(inc['cantidad'] for inc in inconsistencias)
        puntuacion_calidad = max(0, 100 - (total_problemas / max(total_registros, 1) * 100))
        
        return jsonify({
            'success': True,
            'fecha_validacion': get_bogota_datetime().isoformat(),
            'puntuacion_calidad': round(puntuacion_calidad, 2),
            'total_inconsistencias': len(inconsistencias),
            'total_problemas': total_problemas,
            'inconsistencias': inconsistencias,
            'recomendaciones': [
                'Revisar y corregir registros duplicados',
                'Contactar técnicos sin registros recientes',
                'Completar campos obligatorios faltantes',
                'Verificar y corregir fechas incorrectas'
            ]
        })
        
    except Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

def api_reportes_exportar():
    """
    API para exportar datos en diferentes formatos
    Endpoint: /api/reportes/exportar
    Método: POST
    """
    try:
        data = request.get_json()
        formato = data.get('formato', 'excel')  # excel, pdf, csv
        tipo_reporte = data.get('tipo_reporte', 'general')
        filtros = data.get('filtros', {})
        
        # Validar formato
        if formato not in ['excel', 'pdf', 'csv']:
            return jsonify({'error': 'Formato no válido'}), 400
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Construir consulta base según el tipo de reporte
        if tipo_reporte == 'general':
            query = """
                SELECT 
                    p.fecha,
                    r.nombre as tecnico,
                    p.supervisor,
                    p.centro_de_trabajo,
                    p.ciudad,
                    p.tipo_vehiculo,
                    p.placa,
                    CASE WHEN (
                        p.estado_espejos != '0' AND p.bocina_pito != '0' AND p.frenos != '0' 
                        AND p.encendido != '0' AND p.estado_bateria != '0' AND p.estado_amortiguadores != '0' 
                        AND p.estado_llantas != '0' AND p.luces_altas_bajas != '0' 
                        AND p.direccionales_delanteras_traseras != '0'
                    ) THEN 'Aprobado' ELSE 'Con Problemas' END as estado_general
                FROM preoperacional p
                JOIN recurso_operativo r ON p.id_codigo_consumidor = r.id_codigo_consumidor
                WHERE 1=1
            """
        elif tipo_reporte == 'detallado':
            query = """
                SELECT 
                    p.fecha,
                    r.nombre as tecnico,
                    p.supervisor,
                    p.centro_de_trabajo,
                    p.ciudad,
                    p.tipo_vehiculo,
                    p.placa,
                    p.estado_espejos,
                    p.bocina_pito,
                    p.frenos,
                    p.encendido,
                    p.estado_bateria,
                    p.estado_amortiguadores,
                    p.estado_llantas,
                    p.luces_altas_bajas,
                    p.direccionales_delanteras_traseras,
                    p.observaciones
                FROM preoperacional p
                JOIN recurso_operativo r ON p.id_codigo_consumidor = r.id_codigo_consumidor
                WHERE 1=1
            """
        else:
            return jsonify({'error': 'Tipo de reporte no válido'}), 400
        
        # Aplicar filtros
        params = []
        if filtros.get('fecha_inicio'):
            query += " AND p.fecha >= %s"
            params.append(filtros['fecha_inicio'])
        if filtros.get('fecha_fin'):
            query += " AND p.fecha <= %s"
            params.append(filtros['fecha_fin'])
        if filtros.get('supervisor'):
            query += " AND p.supervisor = %s"
            params.append(filtros['supervisor'])
        if filtros.get('centro_trabajo'):
            query += " AND p.centro_de_trabajo = %s"
            params.append(filtros['centro_trabajo'])
        if filtros.get('ciudad'):
            query += " AND p.ciudad = %s"
            params.append(filtros['ciudad'])
        
        query += " ORDER BY p.fecha DESC LIMIT 5000"
        
        cursor.execute(query, params)
        datos = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        if not datos:
            return jsonify({'error': 'No se encontraron datos para exportar'}), 404
        
        # Generar archivo según el formato
        import io
        import csv
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if formato == 'csv':
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=datos[0].keys())
            writer.writeheader()
            writer.writerows(datos)
            
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=reporte_{tipo_reporte}_{timestamp}.csv'
            return response
            
        elif formato == 'excel':
            try:
                import pandas as pd
                
                df = pd.DataFrame(datos)
                output = io.BytesIO()
                
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Reporte', index=False)
                
                output.seek(0)
                
                response = make_response(output.getvalue())
                response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                response.headers['Content-Disposition'] = f'attachment; filename=reporte_{tipo_reporte}_{timestamp}.xlsx'
                return response
                
            except ImportError:
                return jsonify({'error': 'Pandas no está instalado. No se puede generar Excel'}), 500
                
        elif formato == 'pdf':
            try:
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
                from reportlab.lib.styles import getSampleStyleSheet
                
                output = io.BytesIO()
                doc = SimpleDocTemplate(output, pagesize=A4)
                
                # Estilos
                styles = getSampleStyleSheet()
                
                # Título
                title = Paragraph(f"Reporte {tipo_reporte.title()} - {timestamp}", styles['Title'])
                
                # Preparar datos para la tabla
                table_data = [list(datos[0].keys())]
                for row in datos[:100]:  # Limitar a 100 registros para PDF
                    table_data.append([str(value) if value is not None else '' for value in row.values()])
                
                # Crear tabla
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTSIZE', (0, 1), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                # Construir documento
                elements = [title, table]
                doc.build(elements)
                
                output.seek(0)
                
                response = make_response(output.getvalue())
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'attachment; filename=reporte_{tipo_reporte}_{timestamp}.pdf'
                return response
                
            except ImportError:
                return jsonify({'error': 'ReportLab no está instalado. No se puede generar PDF'}), 500
        
        return jsonify({'error': 'Formato no implementado'}), 400
        
    except Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

def api_reportes_programados():
    """
    API para gestionar reportes programados
    Endpoint: /api/reportes/programados
    Métodos: GET, POST, PUT, DELETE
    """
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        if request.method == 'GET':
            # Obtener reportes programados del usuario
            usuario_id = session.get('user_id')
            
            cursor.execute("""
                SELECT 
                    id,
                    nombre,
                    descripcion,
                    tipo_reporte,
                    formato_exportacion,
                    frecuencia,
                    parametros,
                    activo,
                    proxima_ejecucion,
                    fecha_creacion
                FROM reportes_programados 
                WHERE usuario_id = %s
                ORDER BY fecha_creacion DESC
            """, (usuario_id,))
            
            reportes = cursor.fetchall()
            
            # Convertir parametros JSON string a dict
            for reporte in reportes:
                if reporte['parametros']:
                    import json
                    try:
                        reporte['parametros'] = json.loads(reporte['parametros'])
                    except:
                        reporte['parametros'] = {}
            
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'reportes': reportes
            })
            
        elif request.method == 'POST':
            # Crear nuevo reporte programado
            data = request.get_json()
            usuario_id = session.get('user_id')
            
            nombre = data.get('nombre')
            descripcion = data.get('descripcion', '')
            tipo_reporte = data.get('tipo_reporte')
            formato_exportacion = data.get('formato_exportacion', 'excel')
            frecuencia = data.get('frecuencia')  # diario, semanal, mensual
            parametros = data.get('parametros', {})
            
            if not all([nombre, tipo_reporte, frecuencia]):
                return jsonify({'error': 'Faltan campos obligatorios'}), 400
            
            # Calcular próxima ejecución
            from datetime import datetime, timedelta
            
            if frecuencia == 'diario':
                proxima_ejecucion = datetime.now() + timedelta(days=1)
            elif frecuencia == 'semanal':
                proxima_ejecucion = datetime.now() + timedelta(weeks=1)
            elif frecuencia == 'mensual':
                proxima_ejecucion = datetime.now() + timedelta(days=30)
            else:
                return jsonify({'error': 'Frecuencia no válida'}), 400
            
            import json
            
            cursor.execute("""
                INSERT INTO reportes_programados 
                (usuario_id, nombre, descripcion, tipo_reporte, formato_exportacion, 
                 frecuencia, parametros, activo, proxima_ejecucion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                usuario_id, nombre, descripcion, tipo_reporte, formato_exportacion,
                frecuencia, json.dumps(parametros), True, proxima_ejecucion
            ))
            
            reporte_id = cursor.lastrowid
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'message': 'Reporte programado creado exitosamente',
                'reporte_id': reporte_id
            })
            
        elif request.method == 'PUT':
            # Actualizar reporte programado
            data = request.get_json()
            reporte_id = data.get('id')
            usuario_id = session.get('user_id')
            
            if not reporte_id:
                return jsonify({'error': 'ID de reporte requerido'}), 400
            
            # Verificar que el reporte pertenece al usuario
            cursor.execute("""
                SELECT id FROM reportes_programados 
                WHERE id = %s AND usuario_id = %s
            """, (reporte_id, usuario_id))
            
            if not cursor.fetchone():
                return jsonify({'error': 'Reporte no encontrado'}), 404
            
            # Actualizar campos
            campos_actualizacion = []
            valores = []
            
            if 'nombre' in data:
                campos_actualizacion.append('nombre = %s')
                valores.append(data['nombre'])
            if 'descripcion' in data:
                campos_actualizacion.append('descripcion = %s')
                valores.append(data['descripcion'])
            if 'activo' in data:
                campos_actualizacion.append('activo = %s')
                valores.append(data['activo'])
            if 'parametros' in data:
                import json
                campos_actualizacion.append('parametros = %s')
                valores.append(json.dumps(data['parametros']))
            
            if campos_actualizacion:
                valores.append(reporte_id)
                query = f"UPDATE reportes_programados SET {', '.join(campos_actualizacion)} WHERE id = %s"
                cursor.execute(query, valores)
                connection.commit()
            
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'message': 'Reporte programado actualizado exitosamente'
            })
            
        elif request.method == 'DELETE':
            # Eliminar reporte programado
            reporte_id = request.args.get('id')
            usuario_id = session.get('user_id')
            
            if not reporte_id:
                return jsonify({'error': 'ID de reporte requerido'}), 400
            
            cursor.execute("""
                DELETE FROM reportes_programados 
                WHERE id = %s AND usuario_id = %s
            """, (reporte_id, usuario_id))
            
            if cursor.rowcount == 0:
                return jsonify({'error': 'Reporte no encontrado'}), 404
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'message': 'Reporte programado eliminado exitosamente'
            })
        
    except Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

def api_reportes_configuracion():
    """
    API para gestionar configuraciones de reportes
    Endpoint: /api/reportes/configuracion
    Métodos: GET, POST, PUT, DELETE
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        if request.method == 'GET':
            # Obtener configuraciones del usuario
            cursor.execute("""
                SELECT * FROM reportes_configuracion 
                WHERE usuario_id = %s 
                ORDER BY fecha_creacion DESC
            """, (user_id,))
            configuraciones = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'configuraciones': configuraciones
            })
        
        elif request.method == 'POST':
            # Crear nueva configuración
            data = request.get_json()
            
            if not data or not data.get('nombre_configuracion'):
                return jsonify({'error': 'Nombre de configuración requerido'}), 400
            
            cursor.execute("""
                INSERT INTO reportes_configuracion 
                (usuario_id, nombre_configuracion, tipo_reporte, parametros_filtro, 
                 descripcion, activo, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                data['nombre_configuracion'],
                data.get('tipo_reporte', 'personalizado'),
                json.dumps(data.get('parametros_filtro', {})),
                data.get('descripcion', ''),
                data.get('activo', True),
                get_bogota_datetime()
            ))
            
            config_id = cursor.lastrowid
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'message': 'Configuración guardada exitosamente',
                'configuracion_id': config_id
            })
        
        elif request.method == 'PUT':
            # Actualizar configuración existente
            config_id = request.args.get('id')
            data = request.get_json()
            
            if not config_id or not data:
                return jsonify({'error': 'ID de configuración y datos requeridos'}), 400
            
            cursor.execute("""
                UPDATE reportes_configuracion 
                SET nombre_configuracion = %s, tipo_reporte = %s, 
                    parametros_filtro = %s, descripcion = %s, 
                    activo = %s, fecha_modificacion = %s
                WHERE id = %s AND usuario_id = %s
            """, (
                data.get('nombre_configuracion'),
                data.get('tipo_reporte'),
                json.dumps(data.get('parametros_filtro', {})),
                data.get('descripcion', ''),
                data.get('activo', True),
                get_bogota_datetime(),
                config_id,
                user_id
            ))
            
            if cursor.rowcount == 0:
                cursor.close()
                connection.close()
                return jsonify({'error': 'Configuración no encontrada o sin permisos'}), 404
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'message': 'Configuración actualizada exitosamente'
            })
        
        elif request.method == 'DELETE':
            # Eliminar configuración
            config_id = request.args.get('id')
            
            if not config_id:
                return jsonify({'error': 'ID de configuración requerido'}), 400
            
            cursor.execute("""
                DELETE FROM reportes_configuracion 
                WHERE id = %s AND usuario_id = %s
            """, (config_id, user_id))
            
            if cursor.rowcount == 0:
                cursor.close()
                connection.close()
                return jsonify({'error': 'Configuración no encontrada o sin permisos'}), 404
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'message': 'Configuración eliminada exitosamente'
            })
            
    except Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
