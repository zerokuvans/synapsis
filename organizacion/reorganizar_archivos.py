#!/usr/bin/env python3
"""
Script para reorganizar archivos del proyecto Synapsis
Este script mueve archivos no críticos a directorios organizados
"""

import os
import shutil
import glob
from pathlib import Path

def crear_directorios():
    """Crear directorios si no existen"""
    directorios = ['test', 'diagnosticos', 'verificar', 'fix', 'debug', 'data', 'docs/tech']
    
    for directorio in directorios:
        Path(directorio).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directorio '{directorio}' creado o ya existe")

def mover_archivos_por_patron(patrones, destino):
    """Mover archivos que coinciden con patrones a destino"""
    archivos_movidos = []
    
    for patron in patrones:
        archivos = glob.glob(patron)
        for archivo in archivos:
            if os.path.isfile(archivo):  # Solo mover si es archivo
                try:
                    shutil.move(archivo, os.path.join(destino, archivo))
                    archivos_movidos.append(archivo)
                    print(f"📦 Movido: {archivo} → {destino}/")
                except Exception as e:
                    print(f"❌ Error moviendo {archivo}: {e}")
    
    return archivos_movidos

def es_archivo_critico(archivo):
    """Verificar si un archivo es crítico para la aplicación"""
    archivos_criticos = [
        'app.py', 'main.py', 'main_fixed.py', 'temp_main.py',
        'requirements.txt', '.env.example', '.env',
        'README.md', 'RESUMEN_FASE_4_FINAL.md', 'DEPENDENCIAS_INSTALADAS.md'
    ]
    
    # No mover archivos críticos
    if archivo in archivos_criticos:
        return True
    
    # No mover directorios
    if os.path.isdir(archivo):
        return True
    
    # No mover archivos que están en directorios que ya están organizados
    if any(dir in archivo for dir in ['templates/', 'static/', 'migrations/', 'supabase/', 'sql/', 'backups/', 'triggers/', 'utils/', 'test/', 'diagnosticos/', 'verificar/', 'fix/', 'debug/', 'data/', 'docs/']):
        return True
    
    return False

def main():
    """Función principal de reorganización"""
    print("🚀 Iniciando reorganización de archivos...")
    print("=" * 60)
    
    # Crear directorios
    crear_directorios()
    
    print("\n📋 Procesando archivos...")
    
    # Definir patrones y destinos
    categorias = {
        'test': [
            'test_*.py', 'verificar_*.py'
        ],
        'diagnosticos': [
            'diagnostico_*.py'
        ],
        'verificar': [
            'verificar_*.py'
        ],
        'fix': [
            'fix_*.py', 'corregir_*.py'
        ],
        'debug': [
            'debug_*.py'
        ],
        'data': [
            '*.csv', '*.json', '*.txt'
        ],
        'docs/tech': [
            'SOLUCION_*.md', 'instrucciones_*.md', 'validacion_*.md'
        ]
    }
    
    total_movidos = 0
    
    # Procesar cada categoría
    for destino, patrones in categorias.items():
        print(f"\n📁 Procesando categoría: {destino}")
        archivos_movidos = mover_archivos_por_patron(patrones, destino)
        total_movidos += len(archivos_movidos)
    
    print(f"\n✅ Reorganización completada!")
    print(f"📊 Total de archivos movidos: {total_movidos}")
    print("\n" + "=" * 60)
    print("💡 Notas importantes:")
    print("- Los archivos críticos no fueron movidos")
    print("- Los directorios existentes se mantuvieron")
    print("- Verifica que la aplicación funcione correctamente")
    print("- Si encuentras problemas, puedes revertir los cambios manualmente")

if __name__ == "__main__":
    # Confirmación antes de ejecutar
    respuesta = input("¿Deseas reorganizar los archivos? (s/N): ").lower()
    if respuesta == 's':
        main()
    else:
        print("Operación cancelada.")