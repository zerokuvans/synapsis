#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar la versión corregida del endpoint /api/asistencia/resumen_agrupado
que funcione sin la columna 'grupo' en la tabla tipificacion_asistencia.

PROBLEMA IDENTIFICADO: 
- La tabla tipificacion_asistencia en producción no tiene la columna 'grupo'
- El endpoint actual falla con error SQL: Unknown column 't.grupo'

SOLUCIÓN:
- Modificar la consulta para usar solo columnas existentes
- Implementar la lógica de agrupación en Python basada en nombre_tipificacion
"""

def generate_fixed_endpoint():
    """Generar código corregido del endpoint"""
    
    fixed_code = '''
@app.route('/api/asistencia/resumen_agrupado', methods=['GET'])
@login_required
def api_asistencia_resumen_agrupado():
    """
    API para obtener resumen agrupado de asistencia
    VERSIÓN CORREGIDA: Sin dependencia de la columna 'grupo'
    """
    try:
        # Obtener parámetros de fecha
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        supervisor_filtro = request.args.get('supervisor')
        
        # Si no se proporcionan fechas, usar fecha actual
        if not fecha_inicio or not fecha_fin:
            from datetime import datetime
            fecha_actual = datetime.now().strftime('%Y-%m-%d')
            fecha_inicio = fecha_actual
            fecha_fin = fecha_actual
        
        # Validar formato de fechas
        try:
            datetime.strptime(fecha_inicio, '%Y-%m-%d')
            datetime.strptime(fecha_fin, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'success': False, 
                'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }), 400
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # CONSULTA CORREGIDA: Sin usar la columna 'grupo'
        # Solo usamos columnas que existen en producción
        query_base = """
            SELECT 
                t.nombre_tipificacion as carpeta,
                t.codigo_tipificacion,
                COUNT(DISTINCT a.id_codigo_consumidor) as total_tecnicos
            FROM asistencia a
            INNER JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
            WHERE DATE(a.fecha_asistencia) BETWEEN %s AND %s
                AND t.nombre_tipificacion IS NOT NULL 
                AND t.nombre_tipificacion != ''
        """
        
        params = [fecha_inicio, fecha_fin]
        
        # Agregar filtro por supervisor si se proporciona
        if supervisor_filtro:
            query_base += " AND a.super = %s"
            params.append(supervisor_filtro)
        
        query_base += """
            GROUP BY t.nombre_tipificacion, t.codigo_tipificacion
            ORDER BY t.nombre_tipificacion
        """
        
        # Ejecutar consulta principal
        cursor.execute(query_base, tuple(params))
        resultados = cursor.fetchall()
        
        # LÓGICA DE AGRUPACIÓN EN PYTHON
        # Definir grupos basados en nombre_tipificacion
        grupos_mapping = {
            # AUSENCIA INJUSTIFICADA
            'AUSENCIA INJUSTIFICADA': 'AUSENCIA INJUSTIFICADA',
            
            # AUSENCIA JUSTIFICADA
            'INCAPACIDAD ARL': 'AUSENCIA JUSTIFICADA',
            'DOMINCAL O FESTIVO': 'AUSENCIA JUSTIFICADA',
            'LICENCIA MATERNIDAD O PATERNIDAD': 'AUSENCIA JUSTIFICADA',
            'LICENCIA LUTO': 'AUSENCIA JUSTIFICADA',
            'SUSPENSION': 'AUSENCIA JUSTIFICADA',
            'VACACIONES': 'AUSENCIA JUSTIFICADA',
            'PERMISO': 'AUSENCIA JUSTIFICADA',
            
            # INSTALACIONES
            'FTTH INSTALACIONES': 'INSTALACIONES',
            'INSTALACIONES DOBLES': 'INSTALACIONES',
            'INSTALACION': 'INSTALACIONES',
            'INSTALACIONES': 'INSTALACIONES',
            
            # POSTVENTA
            'POSTVENTA': 'POSTVENTA',
            
            # ARREGLOS
            'MANTENIMIENTO FTTH': 'ARREGLOS',
            'ARREGLOS': 'ARREGLOS',
            'MANTENIMIENTO': 'ARREGLOS',
            'REPARACION': 'ARREGLOS'
        }
        
        # Agrupar resultados por grupo
        datos_agrupados = {}
        total_general = 0
        
        for resultado in resultados:
            carpeta = resultado['carpeta']
            total_tecnicos = resultado['total_tecnicos']
            
            # Determinar grupo basado en el nombre
            grupo = 'OTROS'  # Grupo por defecto
            for nombre_clave, grupo_asignado in grupos_mapping.items():
                if nombre_clave.upper() in carpeta.upper():
                    grupo = grupo_asignado
                    break
            
            # Agregar al grupo correspondiente
            if grupo not in datos_agrupados:
                datos_agrupados[grupo] = {
                    'grupo': grupo,
                    'carpetas': [],
                    'total_tecnicos': 0
                }
            
            datos_agrupados[grupo]['carpetas'].append({
                'carpeta': carpeta,
                'codigo': resultado['codigo_tipificacion'],
                'total_tecnicos': total_tecnicos
            })
            datos_agrupados[grupo]['total_tecnicos'] += total_tecnicos
            total_general += total_tecnicos
        
        # Calcular porcentajes
        for grupo_data in datos_agrupados.values():
            if total_general > 0:
                grupo_data['porcentaje'] = round((grupo_data['total_tecnicos'] / total_general) * 100, 2)
            else:
                grupo_data['porcentaje'] = 0
            
            # Calcular porcentajes para cada carpeta dentro del grupo
            for carpeta in grupo_data['carpetas']:
                if grupo_data['total_tecnicos'] > 0:
                    carpeta['porcentaje_grupo'] = round((carpeta['total_tecnicos'] / grupo_data['total_tecnicos']) * 100, 2)
                else:
                    carpeta['porcentaje_grupo'] = 0
                
                if total_general > 0:
                    carpeta['porcentaje_total'] = round((carpeta['total_tecnicos'] / total_general) * 100, 2)
                else:
                    carpeta['porcentaje_total'] = 0
        
        # Convertir a lista y ordenar
        data_final = list(datos_agrupados.values())
        data_final.sort(key=lambda x: x['total_tecnicos'], reverse=True)
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'data': data_final,
            'resumen': {
                'total_general': total_general,
                'total_grupos': len(data_final),
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'supervisor': supervisor_filtro
            }
        })
        
    except Exception as e:
        logger.error(f"Error en api_asistencia_resumen_agrupado: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
'''
    
    return fixed_code

def generate_migration_instructions():
    """Generar instrucciones para aplicar la corrección"""
    
    instructions = """
INSTRUCCIONES PARA CORREGIR EL ENDPOINT EN PRODUCCIÓN:

1. UBICAR EL ENDPOINT EN main.py:
   - Buscar la función: api_asistencia_resumen_agrupado()
   - Líneas aproximadas: 8894-9037

2. REEMPLAZAR LA CONSULTA SQL:
   - Cambiar la consulta que usa 't.grupo' 
   - Por la nueva consulta que solo usa columnas existentes

3. AGREGAR LA LÓGICA DE AGRUPACIÓN:
   - Implementar el diccionario grupos_mapping
   - Agregar el código de agrupación en Python

4. PROBAR LA CORRECCIÓN:
   - Reiniciar el servidor main.py
   - Probar el endpoint con diferentes parámetros
   - Verificar que no hay errores 500

5. VERIFICAR RESULTADOS:
   - Los datos deben estar agrupados correctamente
   - Los porcentajes deben calcularse bien
   - La respuesta debe tener la estructura esperada

ARCHIVOS A MODIFICAR:
- main.py (líneas 8894-9037 aproximadamente)

BACKUP RECOMENDADO:
- Hacer copia de seguridad de main.py antes de modificar
"""
    
    return instructions

def main():
    """Función principal"""
    print("Generador de Corrección - Endpoint Resumen Agrupado")
    print("=" * 60)
    print("PROBLEMA: Error SQL - Unknown column 't.grupo'")
    print("SOLUCIÓN: Consulta sin dependencia de columna 'grupo'")
    print("=" * 60)
    
    # Generar código corregido
    print("\\n📝 CÓDIGO CORREGIDO DEL ENDPOINT:")
    print("-" * 40)
    fixed_code = generate_fixed_endpoint()
    print(fixed_code)
    
    # Generar instrucciones
    print("\\n📋 INSTRUCCIONES DE IMPLEMENTACIÓN:")
    print("-" * 40)
    instructions = generate_migration_instructions()
    print(instructions)
    
    # Guardar en archivo
    with open('endpoint_corregido.txt', 'w', encoding='utf-8') as f:
        f.write("CÓDIGO CORREGIDO DEL ENDPOINT:\\n")
        f.write("=" * 50 + "\\n\\n")
        f.write(fixed_code)
        f.write("\\n\\n")
        f.write("INSTRUCCIONES:\\n")
        f.write("=" * 20 + "\\n\\n")
        f.write(instructions)
    
    print("\\n✅ Código corregido guardado en: endpoint_corregido.txt")
    print("\\n🔧 PRÓXIMOS PASOS:")
    print("1. Revisar el código corregido")
    print("2. Aplicar los cambios en main.py del servidor")
    print("3. Probar el endpoint corregido")

if __name__ == "__main__":
    main()