from datetime import datetime
from typing import List, Dict, Any
import pytz

def get_bogota_datetime() -> datetime:
    """Obtiene la fecha y hora actual en la zona horaria de Bogotá"""
    bogota_tz = pytz.timezone('America/Bogota')
    return datetime.now(bogota_tz)

def calcular_indicadores_cumplimiento(cur, fecha: datetime.date) -> List[Dict[str, Any]]:
    """
    Calcula los indicadores de cumplimiento por supervisor para una fecha dada
    
    Args:
        cur: Cursor de la base de datos
        fecha: Fecha para la cual calcular los indicadores
        
    Returns:
        Lista de diccionarios con los indicadores por supervisor
    """
    try:
        # Obtener asistencia por supervisor
        cur.execute("""
            SELECT a.super, COUNT(*) as total_asistencia 
            FROM asistencia a 
            JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
            WHERE DATE(a.fecha) = %s AND t.valor = '1'
            GROUP BY a.super
        """, (fecha,))
        asistencia = {row['super']: row['total_asistencia'] for row in cur.fetchall()}
        
        # Obtener preoperacionales por supervisor
        cur.execute("""
            SELECT supervisor, COUNT(*) as total_preoperacional
            FROM preoperacional 
            WHERE DATE(fecha) = %s
            GROUP BY supervisor
        """, (fecha,))
        preoperacionales = {row['supervisor']: row['total_preoperacional'] for row in cur.fetchall()}
        
        # Calcular indicadores
        indicadores = []
        todos_supervisores = set(list(asistencia.keys()) + list(preoperacionales.keys()))
        
        for sup in todos_supervisores:
            if sup:  # Ignorar supervisores nulos
                total_asistencia = asistencia.get(sup, 0)
                total_preop = preoperacionales.get(sup, 0)
                porcentaje = (total_preop * 100.0 / total_asistencia) if total_asistencia > 0 else 0
                
                indicadores.append({
                    'supervisor': sup,
                    'total_asistencia': total_asistencia,
                    'total_preoperacional': total_preop,
                    'porcentaje_cumplimiento': porcentaje
                })
        
        # Ordenar por porcentaje de cumplimiento descendente
        return sorted(indicadores, key=lambda x: x['porcentaje_cumplimiento'], reverse=True)
        
    except Exception as e:
        print(f"Error al calcular indicadores: {str(e)}")
        return [] 