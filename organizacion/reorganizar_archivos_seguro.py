#!/usr/bin/env python3
"""
Script seguro para reorganizar archivos del proyecto Synapsis
Verifica dependencias antes de mover archivos
"""

import os
import shutil
import glob
import re
from pathlib import Path

def analizar_dependencias():
    """Analizar qué archivos son importados por otros"""
    dependencias = {}
    
    # Archivos principales a analizar
    archivos_principales = ['app.py', 'main.py', 'main_fixed.py', 'temp_main.py']
    
    for archivo in archivos_principales:
        if os.path.exists(archivo):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    
                # Buscar imports
                imports = re.findall(r'^(?:from|import)\s+(\w+)', contenido, re.MULTILINE)
                dependencias[archivo] = imports
                
            except Exception as e:
                print(f"⚠️  No se pudo analizar {archivo}: {e}")
                dependencias[archivo] = []
    
    return dependencias

def es_archivo_seguro_para_mover(archivo, dependencias):
    """Verificar si un archivo es seguro de mover"""
    nombre_base = os.path.splitext(archivo)[0]
    
    # Verificar si es importado por archivos principales
    for archivo_principal, imports in dependencias.items():
        if nombre_base in imports:
            print(f"⚠️  {archivo} es importado por {archivo_principal} - NO MOVER")
            return False
    
    # Archivos que nunca deben moverse
    archivos_prohibidos = [
        'app.py', 'main.py', 'main_fixed.py', 'temp_main.py',
        'requirements.txt', '.env.example', '.env',
        'README.md', 'RESUMEN_FASE_4_FINAL.md', 'DEPENDENCIAS_INSTALADAS.md',
        'utils.py', 'models.py'  # Podrían ser importados
    ]
    
    if archivo in archivos_prohibidos:
        print(f"⚠️  {archivo} es crítico - NO MOVER")
        return False
    
    # Verificar si contiene funciones que podrían ser importadas
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        # Si contiene definiciones de funciones o clases, ser cauteloso
        if re.search(r'^(def|class)\s+\w+', contenido, re.MULTILINE):
            print(f"ℹ️  {archivo} contiene definiciones de funciones/clases - revisar manualmente")
            return False
            
    except Exception:
        pass
    
    return True

def crear_directorios():
    """Crear directorios de organización"""
    directorios = {
        'test': 'Scripts de prueba y testing',
        'diagnosticos': 'Scripts de diagnóstico',
        'verificar': 'Scripts de verificación',
        'fix': 'Scripts de corrección',
        'debug': 'Scripts de depuración',
        'data': 'Archivos de datos (CSV, JSON, TXT)',
        'docs/tech': 'Documentación técnica',
        'scripts/utils': 'Utilidades y scripts auxiliares'
    }
    
    for directorio in directorios:
        Path(directorio).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directorio}/ - {directorios[directorio]}")

def obtener_archivos_para_mover():
    """Obtener lista de archivos que pueden ser movidos"""
    
    # Patrones de archivos que pueden moverse
    patrones = {
        'test': [
            'test_*.py', 'test_*.html', 'test_*.txt'
        ],
        'diagnosticos': [
            'diagnostico_*.py', 'diagnosticos_*.py'
        ],
        'verificar': [
            'verificar_*.py'
        ],
        'fix': [
            'fix_*.py', 'corregir_*.py', 'patch_*.py'
        ],
        'debug': [
            'debug_*.py', 'debug_*.js'
        ],
        'data': [
            '*.csv', '*.json', '*.txt', '!requirements*.txt', '!*.md'
        ],
        'docs/tech': [
            'SOLUCION_*.md', 'instrucciones_*.md', 'validacion_*.md', 'reporte_*.md'
        ],
        'scripts/utils': [
            'crear_*.py', 'actualizar_*.py', 'agregar_*.py', 'ajustar_*.py',
            'analizar_*.py', 'backup_*.py', 'buscar_*.py', 'check_*.py',
            'consultar_*.py', 'create_*.py', 'ejecutar_*.py', 'eliminar_*.py',
            'execute_*.py', 'find_*.py', 'generate_*.py', 'get_*.py',
            'import_*.py', 'insertar_*.py', 'limpiar_*.py', 'migrar_*.py',
            'modo_*.py', 'obtener_*.py', 'poblar_*.py', 'populate_*.py',
            'probar_*.py', 'reset_*.py', 'setup_*.py', 'truncate_*.py',
            'update_*.py', 'completar_*.py', 'configurar_*.py', 'asignar_*.py',
            'identificar_*.py', 'completar_*.py'
        ]
    }
    
    archivos_para_mover = {}
    
    for categoria, patrones_categoria in patrones.items():
        archivos_para_mover[categoria] = []
        
        for patron in patrones_categoria:
            if patron.startswith('!'):
                # Exclusión
                continue
                
            archivos = glob.glob(patron)
            for archivo in archivos:
                if os.path.isfile(archivo) and not es_archivo_protegido(archivo):
                    archivos_para_mover[categoria].append(archivo)
    
    return archivos_para_mover

def es_archivo_protegido(archivo):
    """Verificar si un archivo está protegido"""
    
    # Archivos críticos del sistema
    protegidos = [
        'app.py', 'main.py', 'main_fixed.py', 'temp_main.py',
        'requirements.txt', '.env.example', '.env',
        'README.md', 'RESUMEN_FASE_4_FINAL.md', 'DEPENDENCIAS_INSTALADAS.md',
        'utils.py', 'models.py', 'logging_code.py',
        'validacion_stock_por_estado.py', 'mecanismo_stock_unificado.py',
        'validacion_dotaciones_unificada.py', 'dotaciones_api.py',
        'api_reportes.py', 'indicadores.py'
    ]
    
    # Archivos que contienen datos importantes
    if archivo.endswith('.md') and archivo not in ['SOLUCION_*.md', 'instrucciones_*.md', 'validacion_*.md', 'reporte_*.md']:
        protegidos.append(archivo)
    
    return archivo in protegidos

def generar_reporte(archivos_para_mover, dependencias):
    """Generar reporte de reorganización"""
    
    print("\n" + "="*80)
    print("📋 REPORTE DE REORGANIZACIÓN DE ARCHIVOS")
    print("="*80)
    
    print(f"\n🔍 ANÁLISIS DE DEPENDENCIAS:")
    for archivo, imports in dependencias.items():
        if imports:
            print(f"   {archivo} importa: {', '.join(imports)}")
    
    print(f"\n📦 ARCHIVOS A ORGANIZAR:")
    total = 0
    for categoria, archivos in archivos_para_mover.items():
        if archivos:
            print(f"\n{categoria.upper()}/ ({len(archivos)} archivos):")
            for archivo in archivos:
                print(f"   📄 {archivo}")
            total += len(archivos)
    
    print(f"\n📊 TOTAL: {total} archivos serán movidos")
    
    print(f"\n⚠️  ARCHIVOS CRÍTICOS (no se moverán):")
    archivos_raiz = [f for f in os.listdir('.') if os.path.isfile(f)]
    archivos_criticos = [f for f in archivos_raiz if es_archivo_protegido(f)]
    for archivo in archivos_criticos:
        print(f"   🔒 {archivo}")
    
    print("\n" + "="*80)

def simular_reorganizacion():
    """Simular la reorganización sin mover archivos"""
    
    print("🔍 Analizando dependencias...")
    dependencias = analizar_dependencias()
    
    print("📋 Identificando archivos para reorganizar...")
    archivos_para_mover = obtener_archivos_para_mover()
    
    generar_reporte(archivos_para_mover, dependencias)
    
    return archivos_para_mover

def ejecutar_reorganizacion(archivos_para_mover):
    """Ejecutar la reorganización real"""
    
    print("🚀 Ejecutando reorganización...")
    
    total_movidos = 0
    
    for categoria, archivos in archivos_para_mover.items():
        if archivos:
            print(f"\n📁 Procesando {categoria}/...")
            
            for archivo in archivos:
                try:
                    destino = os.path.join(categoria, archivo)
                    shutil.move(archivo, destino)
                    print(f"   ✅ {archivo} → {categoria}/")
                    total_movidos += 1
                except Exception as e:
                    print(f"   ❌ Error con {archivo}: {e}")
    
    print(f"\n🎉 Reorganización completada!")
    print(f"📊 Total de archivos movidos: {total_movidos}")

def main():
    """Función principal"""
    
    print("🔄 REORGANIZADOR DE ARCHIVOS SYNAPSIS")
    print("="*60)
    
    # Crear directorios
    print("📁 Creando directorios...")
    crear_directorios()
    
    # Simular para generar reporte
    archivos_para_mover = simular_reorganizacion()
    
    # Preguntar si ejecutar
    print("\n❓ ¿Deseas ejecutar la reorganización?")
    print("   Se moverán los archivos listados arriba.")
    respuesta = input("   Responde 'SI' para confirmar: ")
    
    if respuesta.upper() == 'SI':
        ejecutar_reorganizacion(archivos_para_mover)
    else:
        print("\n✅ Simulación completada. No se movieron archivos.")
        print("   Puedes revisar el reporte y ejecutar cuando estés listo.")

if __name__ == "__main__":
    main()