#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parche para agregar logging detallado a la función registrar_ferretero
Este parche ayudará a diagnosticar exactamente dónde fallan los cálculos en el servidor
"""

import re

def create_logging_patch():
    """Crear el código de logging que se debe agregar a registrar_ferretero"""
    
    logging_code = '''
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
'''
    
    return logging_code

def create_patched_calculation_code():
    """Crear el código parcheado para los cálculos de límites"""
    
    patched_code = '''
# CÓDIGO PARCHEADO CON LOGGING DETALLADO

# Obtener fecha actual con logging
fecha_actual = datetime.now()
log_debug_info("Fecha actual obtenida", {
    "fecha_actual": fecha_actual,
    "tipo": str(type(fecha_actual)),
    "timezone": str(fecha_actual.tzinfo) if fecha_actual.tzinfo else "naive"
})

# Obtener asignaciones previas con logging
cursor.execute("""
    SELECT 
        fecha_asignacion,
        silicona,
        amarres_negros,
        amarres_blancos,
        cinta_aislante,
        grapas_blancas,
        grapas_negras
    FROM ferretero 
    WHERE id_codigo_consumidor = %s
    ORDER BY fecha_asignacion DESC
""", (id_codigo_consumidor,))
asignaciones_previas = cursor.fetchall()

log_debug_info("Asignaciones previas obtenidas", {
    "total_asignaciones": len(asignaciones_previas),
    "id_codigo_consumidor": id_codigo_consumidor
})

# Determinar área de trabajo con logging
carpeta = tecnico.get('carpeta', '').upper() if tecnico.get('carpeta') else ''
cargo = tecnico.get('cargo', '').upper()

log_debug_info("Datos del técnico", {
    "carpeta": carpeta,
    "cargo": cargo,
    "tecnico_completo": tecnico
})

# Límites de materiales (como en el código original)
limites = {
    'FTTH INSTALACIONES': {
        'cinta_aislante': {'cantidad': 3, 'periodo': 15, 'unidad': 'días'},
        'silicona': {'cantidad': 16, 'periodo': 7, 'unidad': 'días'},
        'amarres_negros': {'cantidad': 50, 'periodo': 15, 'unidad': 'días'},
        'amarres_blancos': {'cantidad': 50, 'periodo': 15, 'unidad': 'días'},
        'grapas_blancas': {'cantidad': 200, 'periodo': 15, 'unidad': 'días'},
        'grapas_negras': {'cantidad': 200, 'periodo': 15, 'unidad': 'días'}
    },
    'POSTVENTA': {
        'cinta_aislante': {'cantidad': 3, 'periodo': 15, 'unidad': 'días'},
        'silicona': {'cantidad': 12, 'periodo': 7, 'unidad': 'días'},
        'amarres_negros': {'cantidad': 30, 'periodo': 15, 'unidad': 'días'},
        'amarres_blancos': {'cantidad': 30, 'periodo': 15, 'unidad': 'días'},
        'grapas_blancas': {'cantidad': 100, 'periodo': 15, 'unidad': 'días'},
        'grapas_negras': {'cantidad': 100, 'periodo': 15, 'unidad': 'días'}
    }
}

# Determinar área de trabajo
area_trabajo = None
if carpeta:
    for area in limites.keys():
        if area in carpeta:
            area_trabajo = area
            break

if area_trabajo is None:
    area_trabajo = 'POSTVENTA'  # Por defecto

log_debug_info("Área de trabajo determinada", {
    "area_trabajo": area_trabajo,
    "limites_aplicables": limites[area_trabajo]
})

# Calcular consumo previo con logging detallado
contadores = {
    'cinta_aislante': 0,
    'silicona': 0,
    'amarres_negros': 0,
    'amarres_blancos': 0,
    'grapas_blancas': 0,
    'grapas_negras': 0
}

log_debug_info("Iniciando cálculo de consumo previo", {
    "total_asignaciones_a_procesar": len(asignaciones_previas)
})

for i, asignacion in enumerate(asignaciones_previas):
    fecha_asignacion = asignacion['fecha_asignacion']
    
    log_debug_info(f"Procesando asignación {i+1}", {
        "fecha_asignacion": fecha_asignacion,
        "tipo_fecha_asignacion": str(type(fecha_asignacion))
    })
    
    try:
        # CÁLCULO CRÍTICO CON LOGGING DETALLADO
        diferencia_dias = (fecha_actual - fecha_asignacion).days
        
        log_debug_info(f"Cálculo de diferencia exitoso para asignación {i+1}", {
            "fecha_actual": fecha_actual,
            "fecha_asignacion": fecha_asignacion,
            "diferencia_dias": diferencia_dias,
            "calculo_completo": f"({fecha_actual} - {fecha_asignacion}).days = {diferencia_dias}"
        })
        
        # Procesar cada material
        for material in ['cinta_aislante', 'silicona', 'amarres_negros', 'amarres_blancos', 'grapas_blancas', 'grapas_negras']:
            if material in limites[area_trabajo]:
                periodo_limite = limites[area_trabajo][material]['periodo']
                
                if diferencia_dias <= periodo_limite:
                    cantidad = int(asignacion.get(material, 0) or 0)
                    contadores[material] += cantidad
                    
                    log_date_calculation(fecha_actual, fecha_asignacion, diferencia_dias, material, cantidad)
                    
                    log_debug_info(f"Material {material} sumado", {
                        "cantidad_sumada": cantidad,
                        "total_acumulado": contadores[material],
                        "periodo_limite": periodo_limite,
                        "diferencia_dias": diferencia_dias,
                        "dentro_del_limite": diferencia_dias <= periodo_limite
                    })
                else:
                    log_debug_info(f"Material {material} fuera del período", {
                        "diferencia_dias": diferencia_dias,
                        "periodo_limite": periodo_limite,
                        "cantidad_ignorada": int(asignacion.get(material, 0) or 0)
                    })
    
    except Exception as e:
        log_debug_info(f"ERROR en cálculo de diferencia para asignación {i+1}", {
            "error": str(e),
            "error_type": str(type(e)),
            "fecha_actual": fecha_actual,
            "fecha_actual_type": str(type(fecha_actual)),
            "fecha_asignacion": fecha_asignacion,
            "fecha_asignacion_type": str(type(fecha_asignacion))
        })
        # Re-lanzar el error para que el flujo original lo maneje
        raise e

log_debug_info("Consumo previo calculado", {
    "contadores_finales": contadores
})

# Validar límites con logging
errores = []
for material in ['cinta_aislante', 'silicona', 'amarres_negros', 'amarres_blancos', 'grapas_blancas', 'grapas_negras']:
    if material in limites[area_trabajo]:
        cantidad_solicitada = int(request.form.get(material, 0) or 0)
        if cantidad_solicitada > 0:
            limite_cantidad = limites[area_trabajo][material]['cantidad']
            limite_periodo = limites[area_trabajo][material]['periodo']
            consumo_previo = contadores[material]
            total_con_solicitud = consumo_previo + cantidad_solicitada
            
            log_debug_info(f"Validando límite para {material}", {
                "cantidad_solicitada": cantidad_solicitada,
                "consumo_previo": consumo_previo,
                "total_con_solicitud": total_con_solicitud,
                "limite_cantidad": limite_cantidad,
                "limite_periodo": limite_periodo,
                "excede_limite": total_con_solicitud > limite_cantidad
            })
            
            if total_con_solicitud > limite_cantidad:
                error_msg = f"Excede límite de {limite_cantidad} {material.replace('_', ' ')} cada {limite_periodo} días. Ya asignadas: {consumo_previo}"
                errores.append(error_msg)
                
                log_debug_info(f"LÍMITE EXCEDIDO para {material}", {
                    "error_message": error_msg,
                    "limite_cantidad": limite_cantidad,
                    "consumo_previo": consumo_previo,
                    "cantidad_solicitada": cantidad_solicitada,
                    "total": total_con_solicitud
                })

log_debug_info("Validación de límites completada", {
    "total_errores": len(errores),
    "errores": errores
})

# FIN DEL CÓDIGO PARCHEADO
'''
    
    return patched_code

def create_installation_instructions():
    """Crear instrucciones para instalar el parche"""
    
    instructions = '''
# INSTRUCCIONES PARA INSTALAR EL PARCHE DE LOGGING

## 1. BACKUP DEL ARCHIVO ORIGINAL
cp main.py main.py.backup.$(date +%Y%m%d_%H%M%S)

## 2. UBICAR LA FUNCIÓN registrar_ferretero
# Buscar la línea que contiene "def registrar_ferretero()" en main.py
# Aproximadamente en la línea 3200

## 3. AGREGAR EL CÓDIGO DE LOGGING
# Agregar el código de logging al inicio de la función, después de:
# def registrar_ferretero():

## 4. REEMPLAZAR EL CÓDIGO DE CÁLCULOS
# Buscar la sección donde se hace:
# fecha_actual = datetime.now()
# Y reemplazar toda la lógica de cálculo de límites con el código parcheado

## 5. VERIFICAR IMPORTS
# Asegurarse de que al inicio del archivo main.py estén estos imports:
# import logging
# from datetime import datetime

## 6. PROBAR EN DESARROLLO
# Ejecutar la aplicación en desarrollo y verificar que se genere ferretero_debug.log

## 7. DESPLEGAR AL SERVIDOR
# Subir el archivo parcheado al servidor
# Reiniciar la aplicación
# Monitorear el archivo ferretero_debug.log

## 8. ANALIZAR LOGS
# Buscar líneas que contengan "FERRETERO_DEBUG" y "CALC_DEBUG"
# Identificar exactamente dónde falla el cálculo en el servidor

## 9. REVERTIR SI ES NECESARIO
# Si hay problemas, restaurar desde el backup:
# cp main.py.backup.YYYYMMDD_HHMMSS main.py
'''
    
    return instructions

def main():
    """Generar todos los archivos del parche"""
    print("🔧 GENERANDO PARCHE DE LOGGING PARA REGISTRAR_FERRETERO")
    print("=" * 60)
    
    # Crear archivo con código de logging
    with open('logging_code.py', 'w', encoding='utf-8') as f:
        f.write(create_logging_patch())
    print("✅ Archivo 'logging_code.py' creado")
    
    # Crear archivo con código parcheado
    with open('patched_calculation_code.py', 'w', encoding='utf-8') as f:
        f.write(create_patched_calculation_code())
    print("✅ Archivo 'patched_calculation_code.py' creado")
    
    # Crear archivo con instrucciones
    with open('patch_installation_instructions.txt', 'w', encoding='utf-8') as f:
        f.write(create_installation_instructions())
    print("✅ Archivo 'patch_installation_instructions.txt' creado")
    
    print("\n📋 ARCHIVOS GENERADOS:")
    print("   - logging_code.py: Código de logging para agregar")
    print("   - patched_calculation_code.py: Código de cálculos parcheado")
    print("   - patch_installation_instructions.txt: Instrucciones de instalación")
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("   1. Revisar los archivos generados")
    print("   2. Hacer backup de main.py")
    print("   3. Aplicar el parche siguiendo las instrucciones")
    print("   4. Probar en desarrollo")
    print("   5. Desplegar al servidor")
    print("   6. Monitorear ferretero_debug.log")

if __name__ == "__main__":
    main()