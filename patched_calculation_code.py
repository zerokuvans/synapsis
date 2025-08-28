
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
