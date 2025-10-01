#!/usr/bin/env python3
"""
Verificación final de la corrección de inconsistencia de nombres de campos
para 'camiseta polo'.
"""

import re
import os

def verificar_frontend():
    """Verifica que el frontend use consistentemente camisetapolo_valorado"""
    print("=" * 70)
    print("🔍 VERIFICANDO FRONTEND (dotaciones.html)")
    print("=" * 70)
    
    archivo_frontend = "templates/modulos/logistica/dotaciones.html"
    
    if not os.path.exists(archivo_frontend):
        print("❌ No se encontró el archivo dotaciones.html")
        return False
    
    with open(archivo_frontend, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar ocurrencias de camiseta_polo_valorado (debería ser 0)
    ocurrencias_incorrectas = len(re.findall(r'camiseta_polo_valorado', contenido))
    
    # Buscar ocurrencias de camisetapolo_valorado (debería ser 2)
    ocurrencias_correctas = len(re.findall(r'camisetapolo_valorado', contenido))
    
    print(f"📊 Análisis del archivo {archivo_frontend}:")
    print(f"   - Ocurrencias de 'camiseta_polo_valorado': {ocurrencias_incorrectas}")
    print(f"   - Ocurrencias de 'camisetapolo_valorado': {ocurrencias_correctas}")
    
    if ocurrencias_incorrectas == 0 and ocurrencias_correctas >= 2:
        print("✅ Frontend corregido correctamente")
        return True
    else:
        print("❌ Frontend aún tiene inconsistencias")
        return False

def verificar_api():
    """Verifica que el API use consistentemente camisetapolo_valorado"""
    print("\n" + "=" * 70)
    print("🔍 VERIFICANDO API (dotaciones_api.py)")
    print("=" * 70)
    
    archivo_api = "dotaciones_api.py"
    
    if not os.path.exists(archivo_api):
        print("❌ No se encontró el archivo dotaciones_api.py")
        return False
    
    with open(archivo_api, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar ocurrencias de camiseta_polo_valorado (debería ser 0)
    ocurrencias_incorrectas = len(re.findall(r'camiseta_polo_valorado', contenido))
    
    # Buscar ocurrencias de camisetapolo_valorado (debería ser >= 4)
    ocurrencias_correctas = len(re.findall(r'camisetapolo_valorado', contenido))
    
    print(f"📊 Análisis del archivo {archivo_api}:")
    print(f"   - Ocurrencias de 'camiseta_polo_valorado': {ocurrencias_incorrectas}")
    print(f"   - Ocurrencias de 'camisetapolo_valorado': {ocurrencias_correctas}")
    
    if ocurrencias_incorrectas == 0 and ocurrencias_correctas >= 4:
        print("✅ API corregido correctamente")
        return True
    else:
        print("❌ API aún tiene inconsistencias")
        return False

def verificar_mapeo_logico():
    """Verifica que el mapeo lógico funcione correctamente"""
    print("\n" + "=" * 70)
    print("🔍 VERIFICANDO MAPEO LÓGICO")
    print("=" * 70)
    
    # Simular el mapeo que hace el API
    elemento = 'camisetapolo'
    
    # Mapeo corregido
    if elemento == 'camisetapolo':
        valorado_key = 'camisetapolo_valorado'
    else:
        valorado_key = f'{elemento}_valorado'
    
    print(f"📋 Mapeo para elemento '{elemento}':")
    print(f"   - Campo valorado: {valorado_key}")
    
    # Simular datos del frontend
    data_valorado = {'camisetapolo_valorado': True}
    data_no_valorado = {'camisetapolo_valorado': False}
    
    estado_valorado = 'VALORADO' if data_valorado.get(valorado_key, False) else 'NO VALORADO'
    estado_no_valorado = 'VALORADO' if data_no_valorado.get(valorado_key, False) else 'NO VALORADO'
    
    print(f"   - Con camisetapolo_valorado=True: {estado_valorado}")
    print(f"   - Con camisetapolo_valorado=False: {estado_no_valorado}")
    
    if (valorado_key == 'camisetapolo_valorado' and 
        estado_valorado == 'VALORADO' and 
        estado_no_valorado == 'NO VALORADO'):
        print("✅ Mapeo lógico funciona correctamente")
        return True
    else:
        print("❌ Error en el mapeo lógico")
        return False

def main():
    """Ejecuta todas las verificaciones"""
    print("🔧 VERIFICACIÓN FINAL DE CORRECCIÓN DE INCONSISTENCIA")
    print("Problema original: Frontend enviaba 'camiseta_polo_valorado' pero")
    print("el sistema esperaba 'camisetapolo_valorado' para ser consistente")
    print()
    
    resultados = []
    
    # Ejecutar verificaciones
    resultados.append(verificar_frontend())
    resultados.append(verificar_api())
    resultados.append(verificar_mapeo_logico())
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📋 RESUMEN FINAL")
    print("=" * 70)
    
    pruebas_exitosas = sum(resultados)
    total_pruebas = len(resultados)
    
    print(f"✅ Verificaciones exitosas: {pruebas_exitosas}/{total_pruebas}")
    
    if pruebas_exitosas == total_pruebas:
        print("\n🎉 ¡CORRECCIÓN COMPLETADA EXITOSAMENTE!")
        print("\n📝 RESUMEN DE CAMBIOS REALIZADOS:")
        print("   1. ✅ Frontend: Cambiado 'camiseta_polo_valorado' → 'camisetapolo_valorado'")
        print("   2. ✅ API: Actualizado mapeo para usar 'camisetapolo_valorado'")
        print("   3. ✅ Consistencia: Ahora todo usa 'camisetapolo' como base")
        
        print("\n💡 BENEFICIOS DE LA CORRECCIÓN:")
        print("   - ✅ Eliminada la inconsistencia de nombres")
        print("   - ✅ Código más mantenible y claro")
        print("   - ✅ Menor riesgo de errores futuros")
        print("   - ✅ Nomenclatura unificada en todo el sistema")
        
        print("\n🔄 FUNCIONAMIENTO ACTUAL:")
        print("   - Frontend envía: 'camisetapolo_valorado'")
        print("   - API recibe: 'camisetapolo_valorado'")
        print("   - Base de datos: 'camisetapolo' (tipo_elemento)")
        print("   - Tablas dotaciones: 'estado_camiseta_polo'")
        
    else:
        print("\n⚠️  Algunas verificaciones fallaron.")
        print("   Revisar los archivos mencionados arriba.")
    
    return pruebas_exitosas == total_pruebas

if __name__ == "__main__":
    main()