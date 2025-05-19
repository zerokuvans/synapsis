from datetime import datetime
import pytz
from flask import jsonify
from main import get_db_connection

def verificar_tabla_tipificacion_asistencia():
    """Verifica y crea si no existe la tabla tipificacion_asistencia"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'tipificacion_asistencia'")
        tabla_existe = cursor.fetchone() is not None
        
        if not tabla_existe:
            print("La tabla tipificacion_asistencia no existe. Creándola...")
            
            # Crear la tabla si no existe
            query_crear_tabla = """
                CREATE TABLE tipificacion_asistencia (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    codigo_tipificacion VARCHAR(50) NOT NULL,
                    descripcion VARCHAR(255),
                    valor VARCHAR(10) NOT NULL,
                    UNIQUE KEY (codigo_tipificacion)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            cursor.execute(query_crear_tabla)
            
            # Insertar valores por defecto
            valores_predeterminados = [
                ('A', 'Asistió', '1'),
                ('I', 'Incapacidad', '0'),
                ('F', 'Falta', '0'),
                ('V', 'Vacaciones', '0'),
                ('P', 'Permiso autorizado', '0'),
                ('C', 'Calamidad', '0'),
                ('S', 'Suspensión', '0')
            ]
            
            for valor in valores_predeterminados:
                cursor.execute(
                    "INSERT INTO tipificacion_asistencia (codigo_tipificacion, descripcion, valor) VALUES (%s, %s, %s)",
                    valor
                )
            
            conn.commit()
            print("Tabla tipificacion_asistencia creada y poblada correctamente")
            return True
        else:
            print("La tabla tipificacion_asistencia ya existe")
            return True
        
    except Exception as e:
        print(f"Error al verificar/crear tabla tipificacion_asistencia: {str(e)}")
        return False
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

def calcular_indicadores_cumplimiento(fecha=None):
    try:
        # Primero verificar que la tabla de tipificación exista
        verificar_tabla_tipificacion_asistencia()
        
        # Si no se proporciona fecha, usar la fecha actual en Bogotá
        if fecha is None:
            tz = pytz.timezone('America/Bogota')
            fecha = datetime.now(tz).date()
        
        # Establecer conexión a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar datos para la fecha
        cursor.execute("SELECT COUNT(*) as total FROM asistencia WHERE DATE(fecha_asistencia) = %s", (fecha,))
        total_asistencia = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM preoperacional WHERE DATE(fecha) = %s", (fecha,))
        total_preop = cursor.fetchone()['total']
        
        print(f"Totales para fecha {fecha}:")
        print(f"- Total asistencia: {total_asistencia}")
        print(f"- Total preoperacional: {total_preop}")
        
        if total_asistencia == 0 and total_preop == 0:
            print("No hay datos para la fecha especificada")
            return {
                'success': True,
                'indicadores': [],
                'mensaje': f'No hay datos para la fecha {fecha}'
            }
        
        # Consulta para obtener asistencia válida por supervisor
        try:
            query_asistencia = """
                SELECT a.super as supervisor, COUNT(*) as total_asistencia 
                FROM asistencia a 
                JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
                WHERE DATE(a.fecha_asistencia) = %s AND t.valor = '1'
                GROUP BY a.super
            """
            cursor.execute(query_asistencia, (fecha,))
            asistencia_por_supervisor = {row['supervisor']: row['total_asistencia'] for row in cursor.fetchall()}
        except Exception as e:
            print(f"Error en consulta de asistencia: {e}")
            # Si falla el JOIN, intentar una versión simplificada asumiendo que todo es válido
            query_asistencia_alt = """
                SELECT super as supervisor, COUNT(*) as total_asistencia 
                FROM asistencia
                WHERE DATE(fecha_asistencia) = %s
                GROUP BY super
            """
            cursor.execute(query_asistencia_alt, (fecha,))
            asistencia_por_supervisor = {row['supervisor']: row['total_asistencia'] for row in cursor.fetchall()}
        
        # Consulta para obtener preoperacionales por supervisor
        query_preoperacional = """
            SELECT supervisor, COUNT(*) as total_preoperacional
            FROM preoperacional 
            WHERE DATE(fecha) = %s
            GROUP BY supervisor
        """
        cursor.execute(query_preoperacional, (fecha,))
        preop_por_supervisor = {row['supervisor']: row['total_preoperacional'] for row in cursor.fetchall()}
        
        # Calcular indicadores
        indicadores = []
        supervisores = set(list(asistencia_por_supervisor.keys()) + list(preop_por_supervisor.keys()))
        
        for supervisor in supervisores:
            if supervisor:  # Ignorar supervisores nulos
                total_asistencia = asistencia_por_supervisor.get(supervisor, 0)
                total_preoperacional = preop_por_supervisor.get(supervisor, 0)
                
                # Calcular porcentaje de cumplimiento
                porcentaje = (total_preoperacional * 100) / total_asistencia if total_asistencia > 0 else 0
                
                indicadores.append({
                    'supervisor': supervisor,
                    'total_asistencia': total_asistencia,
                    'total_preoperacional': total_preoperacional,
                    'porcentaje_cumplimiento': porcentaje
                })
        
        # Ordenar por porcentaje de cumplimiento descendente
        indicadores.sort(key=lambda x: x['porcentaje_cumplimiento'], reverse=True)
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'indicadores': indicadores
        }
        
    except Exception as e:
        print(f"Error en indicadores: {e}")
        return {
            'success': False,
            'error': str(e)
        } 