
# ===== LOGGING DE DEBUG PARA SERVIDOR =====
import logging
from datetime import datetime

# Configurar logging si no está configurado
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ferretero_debug.log'),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

def log_debug_info(message, data=None):
    """Función auxiliar para logging detallado"""
    if data:
        logger.debug(f"FERRETERO_DEBUG: {message} - {data}")
    else:
        logger.debug(f"FERRETERO_DEBUG: {message}")

def log_date_calculation(fecha_actual, fecha_asignacion, diferencia_dias, material, cantidad):
    """Log específico para cálculos de fechas"""
    logger.debug(f"CALC_DEBUG: Material={material}, Cantidad={cantidad}")
    logger.debug(f"CALC_DEBUG: fecha_actual={fecha_actual} (tipo: {type(fecha_actual)})")
    logger.debug(f"CALC_DEBUG: fecha_asignacion={fecha_asignacion} (tipo: {type(fecha_asignacion)})")
    logger.debug(f"CALC_DEBUG: diferencia_dias={diferencia_dias}")
    logger.debug(f"CALC_DEBUG: Cálculo: ({fecha_actual} - {fecha_asignacion}).days = {diferencia_dias}")
# ===== FIN LOGGING DE DEBUG =====
