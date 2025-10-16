#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para validar que los campos del formulario coincidan con la tabla parque_automotor
"""

import mysql.connector
from mysql.connector import Error
import re
import sys
from datetime import datetime

# Configuración de conexión
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

# Campos del formulario extraídos del HTML
CAMPOS_FORMULARIO = {
    # Información Básica del Vehículo
    'placa_vehiculo': {'html_id': 'placa_vehiculo', 'db_field': 'placa', 'tipo': 'text', 'requerido': True},
    'tipo_vehiculo': {'html_id': 'tipo_vehiculo', 'db_field': 'tipo_vehiculo', 'tipo': 'select', 'requerido': True},
    'vehiculo_asistio_operacion': {'html_id': 'vehiculo_asistio_operacion', 'db_field': 'vehiculo_asistio_operacion', 'tipo': 'select', 'requerido': False},
    'marca_vehiculo': {'html_id': 'marca_vehiculo', 'db_field': 'marca', 'tipo': 'text', 'requerido': True},
    'modelo_vehiculo': {'html_id': 'modelo_vehiculo', 'db_field': 'modelo', 'tipo': 'text', 'requerido': True},
    'color': {'html_id': 'color', 'db_field': 'color', 'tipo': 'text', 'requerido': True},
    
    # Información del Conductor
    'id_codigo_consumidor': {'html_id': 'id_codigo_consumidor', 'db_field': 'id_codigo_consumidor', 'tipo': 'select', 'requerido': False},
    'fecha_asignacion': {'html_id': 'fecha_asignacion', 'db_field': 'fecha_asignacion', 'tipo': 'date', 'requerido': True},
    'licencia_conduccion': {'html_id': 'licencia_conduccion', 'db_field': 'licencia_conduccion', 'tipo': 'text', 'requerido': False},
    'fecha_vencimiento_licencia': {'html_id': 'fecha_vencimiento_licencia', 'db_field': 'vencimiento_licencia', 'tipo': 'date', 'requerido': False},
    
    # Documentación del Vehículo
    'estado': {'html_id': 'estado', 'db_field': 'estado', 'tipo': 'select', 'requerido': False},
    'fecha_vencimiento_soat': {'html_id': 'fecha_vencimiento_soat', 'db_field': 'soat_vencimiento', 'tipo': 'date', 'requerido': False},
    'fecha_vencimiento_tecnomecanica': {'html_id': 'fecha_vencimiento_tecnomecanica', 'db_field': 'tecnomecanica_vencimiento', 'tipo': 'date', 'requerido': False},
    
    # Inspección Física del Vehículo
    'estado_carroceria': {'html_id': 'estado_carroceria', 'db_field': 'estado_carroceria', 'tipo': 'select', 'requerido': False},
    'estado_llantas': {'html_id': 'estado_llantas', 'db_field': 'estado_llantas', 'tipo': 'select', 'requerido': False},
    'estado_frenos': {'html_id': 'estado_frenos', 'db_field': 'estado_frenos', 'tipo': 'select', 'requerido': False},
    'estado_motor': {'html_id': 'estado_motor', 'db_field': 'estado_motor', 'tipo': 'select', 'requerido': False},
    'estado_luces': {'html_id': 'estado_luces', 'db_field': 'estado_luces', 'tipo': 'select', 'requerido': False},
    'estado_espejos': {'html_id': 'estado_espejos', 'db_field': 'estado_espejos', 'tipo': 'select', 'requerido': False},
    'estado_vidrios': {'html_id': 'estado_vidrios', 'db_field': 'estado_vidrios', 'tipo': 'select', 'requerido': False},
    'estado_asientos': {'html_id': 'estado_asientos', 'db_field': 'estado_asientos', 'tipo': 'select', 'requerido': False},
    
    # Elementos de Seguridad
    'cinturon_seguridad': {'html_id': 'cinturon_seguridad', 'db_field': 'cinturon_seguridad', 'tipo': 'select', 'requerido': False},
    'extintor': {'html_id': 'extintor', 'db_field': 'extintor', 'tipo': 'select', 'requerido': False},
    'botiquin': {'html_id': 'botiquin', 'db_field': 'botiquin', 'tipo': 'select', 'requerido': False},
    'triangulos_seguridad': {'html_id': 'triangulos_seguridad', 'db_field': 'triangulos_seguridad', 'tipo': 'select', 'requerido': False},
    'llanta_repuesto': {'html_id': 'llanta_repuesto', 'db_field': 'llanta_repuesto', 'tipo': 'select', 'requerido': False},
    'herramientas': {'html_id': 'herramientas', 'db_field': 'herramientas', 'tipo': 'select', 'requerido': False},
    'gato': {'html_id': 'gato', 'db_field': 'gato', 'tipo': 'select', 'requerido': False},
    'cruceta': {'html_id': 'cruceta', 'db_field': 'cruceta', 'tipo': 'select', 'requerido': False},
    
    # Información Operativa
    'centro_de_trabajo': {'html_id': 'centro_de_trabajo', 'db_field': 'centro_de_trabajo', 'tipo': 'text', 'requerido': False},
    'ciudad': {'html_id': 'ciudad', 'db_field': 'ciudad', 'tipo': 'text', 'requerido': False},
    'supervisor': {'html_id': 'supervisor', 'db_field': 'supervisor', 'tipo': 'select', 'requerido': False},
    'fecha': {'html_id': 'fecha', 'db_field': 'fecha', 'tipo': 'datetime-local', 'requerido': False},
    'kilometraje': {'html_id': 'kilometraje', 'db_field': 'kilometraje', 'tipo': 'number', 'requerido': False},
    'observaciones': {'html_id': 'observaciones', 'db_field': 'observaciones', 'tipo': 'textarea', 'requerido': False}
}

def imprimir_separador(titulo=""):
    """Imprime un separador visual"""
    print("\n" + "="*80)
    if titulo:
        print(f" {titulo} ".center(80, "="))
    print("="*80)

def obtener_estructura_tabla():
    """Obtiene la estructura actual de la tabla parque_automotor"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(buffered=True)
        
        cursor.execute("DESCRIBE parque_automotor;")
        campos_db = cursor.fetchall()
        
        estructura = {}
        for campo in campos_db:
            field, type_info, null, key, default, extra = campo
            estructura[field] = {
                'tipo': type_info,
                'null': null == 'YES',
                'key': key,
                'default': default,
                'extra': extra
            }
        
        cursor.close()
        connection.close()
        
        return estructura
        
    except Error as e:
        print(f"Error obteniendo estructura de tabla: {e}")
        return {}

def validar_correspondencia_campos():
    """Valida que los campos del formulario correspondan con la tabla"""
    imprimir_separador("VALIDACIÓN DE CORRESPONDENCIA DE CAMPOS")
    
    estructura_db = obtener_estructura_tabla()
    
    if not estructura_db:
        print("No se pudo obtener la estructura de la base de datos")
        return False
    
    print(f"Campos en la tabla parque_automotor: {len(estructura_db)}")
    print(f"Campos en el formulario: {len(CAMPOS_FORMULARIO)}")
    
    # Validar campos del formulario
    campos_correctos = 0
    campos_faltantes_db = []
    campos_con_problemas = []
    
    print("\nValidando campos del formulario:")
    for campo_form, config in CAMPOS_FORMULARIO.items():
        db_field = config['db_field']
        
        if db_field in estructura_db:
            print(f"  ✅ {campo_form} -> {db_field} (OK)")
            campos_correctos += 1
        else:
            print(f"  ❌ {campo_form} -> {db_field} (FALTANTE EN DB)")
            campos_faltantes_db.append(db_field)
    
    # Verificar campos en DB que no están en formulario
    campos_db_sin_formulario = []
    for campo_db in estructura_db.keys():
        encontrado = False
        for config in CAMPOS_FORMULARIO.values():
            if config['db_field'] == campo_db:
                encontrado = True
                break
        
        if not encontrado:
            # Excluir campos técnicos que no necesitan estar en formulario
            campos_tecnicos = [
                'id_parque_automotor', 'fecha_creacion', 'fecha_actualizacion',
                'kilometraje_actual', 'proximo_mantenimiento_km', 'fecha_ultimo_mantenimiento',
                'comparendos', 'total_comparendos'
            ]
            
            if campo_db not in campos_tecnicos:
                campos_db_sin_formulario.append(campo_db)
    
    # Mostrar resultados
    print(f"\n📊 RESUMEN DE VALIDACIÓN:")
    print(f"  ✅ Campos correctos: {campos_correctos}/{len(CAMPOS_FORMULARIO)}")
    print(f"  ❌ Campos faltantes en DB: {len(campos_faltantes_db)}")
    print(f"  ⚠️  Campos en DB sin formulario: {len(campos_db_sin_formulario)}")
    
    if campos_faltantes_db:
        print(f"\n❌ CAMPOS FALTANTES EN BASE DE DATOS:")
        for campo in campos_faltantes_db:
            print(f"  - {campo}")
    
    if campos_db_sin_formulario:
        print(f"\n⚠️  CAMPOS EN DB QUE NO ESTÁN EN FORMULARIO:")
        for campo in campos_db_sin_formulario:
            tipo_campo = estructura_db[campo]['tipo']
            print(f"  - {campo} ({tipo_campo})")
    
    return len(campos_faltantes_db) == 0

def validar_tipos_datos():
    """Valida que los tipos de datos sean compatibles"""
    imprimir_separador("VALIDACIÓN DE TIPOS DE DATOS")
    
    estructura_db = obtener_estructura_tabla()
    
    if not estructura_db:
        return False
    
    problemas_tipos = []
    
    for campo_form, config in CAMPOS_FORMULARIO.items():
        db_field = config['db_field']
        tipo_form = config['tipo']
        
        if db_field in estructura_db:
            tipo_db = estructura_db[db_field]['tipo'].lower()
            
            # Validar compatibilidad de tipos
            compatible = True
            
            if tipo_form in ['text', 'textarea'] and not any(t in tipo_db for t in ['varchar', 'text', 'char']):
                compatible = False
            elif tipo_form == 'number' and not any(t in tipo_db for t in ['int', 'decimal', 'float', 'double']):
                compatible = False
            elif tipo_form in ['date', 'datetime-local'] and not any(t in tipo_db for t in ['date', 'datetime', 'timestamp']):
                compatible = False
            elif tipo_form == 'select' and not any(t in tipo_db for t in ['varchar', 'enum', 'char']):
                compatible = False
            
            if compatible:
                print(f"  ✅ {campo_form}: {tipo_form} -> {tipo_db} (Compatible)")
            else:
                print(f"  ❌ {campo_form}: {tipo_form} -> {tipo_db} (INCOMPATIBLE)")
                problemas_tipos.append({
                    'campo': campo_form,
                    'tipo_form': tipo_form,
                    'tipo_db': tipo_db
                })
    
    if problemas_tipos:
        print(f"\n❌ PROBLEMAS DE COMPATIBILIDAD DE TIPOS:")
        for problema in problemas_tipos:
            print(f"  - {problema['campo']}: Formulario({problema['tipo_form']}) vs DB({problema['tipo_db']})")
    
    return len(problemas_tipos) == 0

def generar_recomendaciones():
    """Genera recomendaciones para corregir problemas"""
    imprimir_separador("RECOMENDACIONES DE CORRECCIÓN")
    
    estructura_db = obtener_estructura_tabla()
    
    # Campos que podrían faltar en el formulario
    campos_sugeridos = []
    for campo_db in estructura_db.keys():
        encontrado = False
        for config in CAMPOS_FORMULARIO.values():
            if config['db_field'] == campo_db:
                encontrado = True
                break
        
        if not encontrado:
            # Campos que podrían ser útiles en el formulario
            campos_utiles = [
                'estado_direccion', 'estado_suspension', 'estado_escape', 'estado_bateria',
                'nivel_aceite_motor', 'nivel_liquido_frenos', 'nivel_refrigerante', 'presion_llantas',
                'chaleco_reflectivo', 'linterna', 'cables_arranque', 'kit_carretera',
                'fecha_ultima_inspeccion', 'proxima_inspeccion', 'estado_general',
                'requiere_mantenimiento', 'fecha_ingreso_taller', 'fecha_salida_taller',
                'costo_ultimo_mantenimiento', 'taller_mantenimiento'
            ]
            
            if campo_db in campos_utiles:
                tipo_campo = estructura_db[campo_db]['tipo']
                campos_sugeridos.append((campo_db, tipo_campo))
    
    if campos_sugeridos:
        print("\n💡 CAMPOS SUGERIDOS PARA AGREGAR AL FORMULARIO:")
        
        # Agrupar por categorías
        inspeccion_adicional = []
        seguridad_adicional = []
        mantenimiento = []
        
        for campo, tipo in campos_sugeridos:
            if any(palabra in campo for palabra in ['estado_', 'nivel_', 'presion_']):
                inspeccion_adicional.append((campo, tipo))
            elif any(palabra in campo for palabra in ['chaleco', 'linterna', 'cables', 'kit']):
                seguridad_adicional.append((campo, tipo))
            elif any(palabra in campo for palabra in ['mantenimiento', 'taller', 'inspeccion']):
                mantenimiento.append((campo, tipo))
        
        if inspeccion_adicional:
            print("\n  📋 Inspección Física Adicional:")
            for campo, tipo in inspeccion_adicional:
                print(f"    - {campo} ({tipo})")
        
        if seguridad_adicional:
            print("\n  🛡️  Elementos de Seguridad Adicionales:")
            for campo, tipo in seguridad_adicional:
                print(f"    - {campo} ({tipo})")
        
        if mantenimiento:
            print("\n  🔧 Gestión de Mantenimiento:")
            for campo, tipo in mantenimiento:
                print(f"    - {campo} ({tipo})")
    
    # Generar código HTML sugerido
    print("\n📝 CÓDIGO HTML SUGERIDO PARA CAMPOS FALTANTES:")
    
    if campos_sugeridos:
        print("\n<!-- Campos adicionales sugeridos -->")
        for campo, tipo in campos_sugeridos[:5]:  # Mostrar solo los primeros 5
            if 'varchar' in tipo or 'char' in tipo:
                if any(palabra in campo for palabra in ['estado_', 'requiere_']):
                    print(f"""
<div class="col-md-3">
    <label for="{campo}" class="form-label">{campo.replace('_', ' ').title()}</label>
    <select class="form-select" id="{campo}" name="{campo}">
        <option value="">Seleccione...</option>
        <option value="Bueno">Bueno</option>
        <option value="Regular">Regular</option>
        <option value="Malo">Malo</option>
    </select>
</div>""")
                else:
                    print(f"""
<div class="col-md-3">
    <label for="{campo}" class="form-label">{campo.replace('_', ' ').title()}</label>
    <input type="text" class="form-control" id="{campo}" name="{campo}">
</div>""")
            elif 'date' in tipo:
                print(f"""
<div class="col-md-3">
    <label for="{campo}" class="form-label">{campo.replace('_', ' ').title()}</label>
    <input type="date" class="form-control" id="{campo}" name="{campo}">
</div>""")

def validar_mapeo_nombres():
    """Valida el mapeo de nombres entre formulario y base de datos"""
    imprimir_separador("VALIDACIÓN DE MAPEO DE NOMBRES")
    
    print("Verificando mapeo de nombres de campos:")
    
    mapeos_problematicos = []
    
    for campo_form, config in CAMPOS_FORMULARIO.items():
        html_id = config['html_id']
        db_field = config['db_field']
        
        # Verificar consistencia en el mapeo
        if html_id != campo_form:
            print(f"  ⚠️  {campo_form}: HTML ID ({html_id}) != Campo Form ({campo_form})")
            mapeos_problematicos.append(campo_form)
        
        # Verificar nombres descriptivos
        if '_vehiculo' in html_id and '_vehiculo' not in db_field:
            print(f"  ℹ️  {campo_form}: HTML tiene sufijo '_vehiculo' pero DB no")
        
        if 'fecha_vencimiento_' in html_id and '_vencimiento' in db_field:
            print(f"  ✅ {campo_form}: Mapeo de fecha consistente")
    
    if mapeos_problematicos:
        print(f"\n⚠️  MAPEOS PROBLEMÁTICOS ENCONTRADOS: {len(mapeos_problematicos)}")
    else:
        print(f"\n✅ TODOS LOS MAPEOS SON CONSISTENTES")
    
    return len(mapeos_problematicos) == 0

def main():
    """Función principal"""
    print("🔍 VALIDACIÓN DE CAMPOS DEL FORMULARIO AUTOMOTOR")
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Validar correspondencia de campos
        campos_ok = validar_correspondencia_campos()
        
        # Validar tipos de datos
        tipos_ok = validar_tipos_datos()
        
        # Validar mapeo de nombres
        mapeo_ok = validar_mapeo_nombres()
        
        # Generar recomendaciones
        generar_recomendaciones()
        
        # Resultado final
        imprimir_separador("RESULTADO FINAL")
        
        if campos_ok and tipos_ok and mapeo_ok:
            print("✅ VALIDACIÓN EXITOSA")
            print("✅ Todos los campos del formulario corresponden correctamente con la tabla")
            print("✅ Los tipos de datos son compatibles")
            print("✅ El mapeo de nombres es consistente")
            return True
        else:
            print("⚠️  VALIDACIÓN CON ADVERTENCIAS")
            if not campos_ok:
                print("❌ Algunos campos del formulario no existen en la base de datos")
            if not tipos_ok:
                print("❌ Algunos tipos de datos no son compatibles")
            if not mapeo_ok:
                print("❌ Algunos mapeos de nombres son inconsistentes")
            print("🔧 Revisar las recomendaciones anteriores")
            return False
        
    except Exception as e:
        print(f"💥 Error durante la validación: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Validación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)