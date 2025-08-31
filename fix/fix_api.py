import re
import sys
import os
from datetime import datetime

def backup_file(filepath):
    """Crea una copia de respaldo del archivo"""
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"main_backup_{timestamp}.py")
    
    with open(filepath, 'r', encoding='utf-8') as src:
        with open(backup_file, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
    
    print(f"✅ Copia de seguridad creada: {backup_file}")
    return backup_file

def replace_function(filepath):
    """Reemplaza la función obtener_indicadores_cumplimiento en el archivo"""
    
    # Crear copia de seguridad
    backup_filepath = backup_file(filepath)
    
    # Leer el archivo
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón para encontrar la función completa
    pattern = re.compile(
        r'@app\.route\(\'/api/indicadores/cumplimiento\'\).*?'
        r'@login_required\(role=\'administrativo\'\).*?'
        r'def obtener_indicadores_cumplimiento\(\):.*?'
        r'try:.*?'
        r'except Exception as e:.*?'
        r'return jsonify\(\{.*?\'success\': False,.*?\'error\': str\(e\).*?\}\), 500',
        re.DOTALL
    )
    
    # Nueva implementación de la función
    new_function = '''@app.route('/api/indicadores/cumplimiento')
@login_required(role='administrativo')
def obtener_indicadores_cumplimiento():
    try:
        # Obtener los parámetros de fecha
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        supervisor_filtro = request.args.get('supervisor')
        
        # Para compatibilidad con versiones anteriores
        fecha = request.args.get('fecha')
        
        # Mostrar información de debug sobre parámetros recibidos
        print(f"Parámetros recibidos en API:")
        print(f"- fecha_inicio: {fecha_inicio}")
        print(f"- fecha_fin: {fecha_fin}")
        print(f"- supervisor: {supervisor_filtro}")
        print(f"- fecha (compatibilidad): {fecha}")
        
        # Validar fechas
        if fecha:
            # Modo compatibilidad - una sola fecha
            try:
                fecha_inicio = fecha_fin = datetime.strptime(fecha, '%Y-%m-%d').date()
                print(f"Usando modo compatibilidad con fecha: {fecha_inicio}")
            except ValueError:
                print(f"Error: Formato de fecha inválido: {fecha}")
                return jsonify({
                    'success': False,
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }), 400
        elif fecha_inicio and fecha_fin:
            # Nuevo modo - rango de fechas
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                print(f"Usando rango de fechas: {fecha_inicio} a {fecha_fin}")
            except ValueError:
                print(f"Error: Formato de fecha inválido en rango: {fecha_inicio} - {fecha_fin}")
                return jsonify({
                    'success': False,
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }), 400
        else:
            # Si no se proporcionan fechas, usar la fecha actual
            fecha_actual = get_bogota_datetime().date()
            fecha_inicio = fecha_fin = fecha_actual
            print(f"Usando fecha actual: {fecha_actual}")
        
        connection = get_db_connection()
        if connection is None:
            print("Error: No se pudo establecer conexión a la base de datos")
            return jsonify({
                'success': False,
                'error': 'Error de conexión a la base de datos'
            }), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Verificar datos para el rango de fechas
        cursor.execute("SELECT COUNT(*) as total FROM asistencia WHERE DATE(fecha_asistencia) BETWEEN %s AND %s", 
                      (fecha_inicio, fecha_fin))
        total_asistencia = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM preoperacional WHERE DATE(fecha) BETWEEN %s AND %s", 
                      (fecha_inicio, fecha_fin))
        total_preop = cursor.fetchone()['total']
        
        print(f"Datos encontrados en el rango {fecha_inicio} a {fecha_fin}:")
        print(f"- Total asistencia: {total_asistencia}")
        print(f"- Total preoperacional: {total_preop}")
        
        if total_asistencia == 0 and total_preop == 0:
            print("No hay datos para el rango de fechas")
            return jsonify({
                'success': True,
                'indicadores': [],
                'mensaje': f'No hay datos para el período {fecha_inicio} - {fecha_fin}'
            })
        
        # Obtener asistencia válida por supervisor
        query_asistencia = """
            SELECT a.super as supervisor, COUNT(*) as total_asistencia 
            FROM asistencia a 
            JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
            WHERE DATE(a.fecha_asistencia) BETWEEN %s AND %s AND t.valor = '1'
            GROUP BY a.super
        """
        params_asistencia = [fecha_inicio, fecha_fin]
        
        # Obtener preoperacionales por supervisor
        query_preoperacional = """
            SELECT supervisor, COUNT(*) as total_preoperacional
            FROM preoperacional 
            WHERE DATE(fecha) BETWEEN %s AND %s
            GROUP BY supervisor
        """
        params_preoperacional = [fecha_inicio, fecha_fin]
        
        # Aplicar filtro por supervisor si existe
        if supervisor_filtro:
            print(f"Aplicando filtro por supervisor: {supervisor_filtro}")
            query_asistencia += " HAVING a.super = %s"
            params_asistencia.append(supervisor_filtro)
            
            query_preoperacional += " HAVING supervisor = %s"
            params_preoperacional.append(supervisor_filtro)
        
        print(f"Ejecutando consulta de asistencia: {query_asistencia}")
        print(f"Parámetros: {params_asistencia}")
        
        # Ejecutar consultas
        cursor.execute(query_asistencia, tuple(params_asistencia))
        asistencia_por_supervisor = {row['supervisor']: row['total_asistencia'] for row in cursor.fetchall()}
        
        print(f"Ejecutando consulta de preoperacional: {query_preoperacional}")
        print(f"Parámetros: {params_preoperacional}")
        
        cursor.execute(query_preoperacional, tuple(params_preoperacional))
        preop_por_supervisor = {row['supervisor']: row['total_preoperacional'] for row in cursor.fetchall()}
        
        print(f"Asistencia por supervisor: {asistencia_por_supervisor}")
        print(f"Preoperacional por supervisor: {preop_por_supervisor}")
        
        # Calcular indicadores
        indicadores = []
        supervisores = set(list(asistencia_por_supervisor.keys()) + list(preop_por_supervisor.keys()))
        
        for supervisor in supervisores:
            if supervisor:  # Ignorar supervisores nulos
                total_asistencia = asistencia_por_supervisor.get(supervisor, 0)
                total_preoperacional = preop_por_supervisor.get(supervisor, 0)
                porcentaje = (total_preoperacional * 100) / total_asistencia if total_asistencia > 0 else 0
                
                indicador = {
                    'supervisor': supervisor,
                    'total_asistencia': total_asistencia,
                    'total_preoperacional': total_preoperacional,
                    'porcentaje_cumplimiento': porcentaje
                }
                indicadores.append(indicador)
        
        # Ordenar por porcentaje de cumplimiento descendente
        indicadores.sort(key=lambda x: x['porcentaje_cumplimiento'], reverse=True)
        
        print(f"Se calcularon {len(indicadores)} indicadores")
        
        cursor.close()
        connection.close()
        
        # Incluir información del período consultado en la respuesta
        return jsonify({
            'success': True,
            'indicadores': indicadores,
            'periodo': {
                'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
                'fecha_fin': fecha_fin.strftime('%Y-%m-%d')
            }
        })
        
    except Exception as e:
        import traceback
        print(f"Error en indicadores de cumplimiento: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500'''
    
    # Reemplazar la función en el contenido
    modified_content, replacements = pattern.subn(new_function, content)
    
    if replacements == 0:
        print("❌ No se encontró la función. Comprobando enfoque alternativo...")
        
        # Si no funciona el enfoque de regex, intentar localizar la función y cortarla
        function_start = content.find("@app.route('/api/indicadores/cumplimiento')")
        
        if function_start == -1:
            print("❌ No se pudo encontrar el inicio de la función. Abortando.")
            return False
        
        # Encontrar la siguiente ruta para marcar el final de la función
        next_route = content.find("@app.route", function_start + 10)
        
        if next_route == -1:
            print("❌ No se pudo encontrar el final de la función. Abortando.")
            return False
        
        # Reemplazar la función
        modified_content = (
            content[:function_start] + 
            new_function + 
            content[next_route:]
        )
        
        print("✅ Función reemplazada con enfoque alternativo.")
    else:
        print(f"✅ Función reemplazada con éxito ({replacements} reemplazos).")
    
    # Escribir el contenido modificado
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"✅ Archivo modificado guardado: {filepath}")
    return True

def main():
    filepath = "main.py"
    
    if not os.path.exists(filepath):
        print(f"❌ El archivo {filepath} no existe.")
        return 1
    
    print(f"📝 Modificando el archivo {filepath}...")
    
    try:
        if replace_function(filepath):
            print("✅ Proceso completado exitosamente.")
            return 0
        else:
            print("❌ Error al reemplazar la función.")
            return 1
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 