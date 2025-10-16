#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para organizar archivos de test, debug, check, verificar y validar
en sus carpetas correspondientes para mantener el proyecto ordenado.
"""

import os
import shutil
import glob
from pathlib import Path

def crear_carpetas_si_no_existen(carpetas):
    """Crear las carpetas de destino si no existen"""
    for carpeta in carpetas:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
            print(f"✅ Carpeta creada: {carpeta}")
        else:
            print(f"📁 Carpeta ya existe: {carpeta}")

def identificar_archivos_a_mover():
    """Identificar todos los archivos que necesitan ser organizados"""
    patrones = {
        'test/': ['test_*.py'],
        'debug/': ['debug_*.py'],
        'check/': ['check_*.py'],
        'verificar/': ['verificar_*.py', 'verificacion_*.py'],
        'validacion/': ['validar_*.py', 'validacion_*.py'],
        'analisis/': ['analyze_*.py', 'analisis_*.py', 'analizar_*.py'],
        'migraciones/': ['migration_*.py', 'migrate_*.py'],
        'fix/': ['fix_*.py'],
        'documentacion/': ['*.md'],
        'utilidades/': ['temp_*.py', 'quick_*.py', 'diagnose_*.py', 'obtener_*.py', 'actualizar_*.py', 'crear_*.py', 'add_*.py', 'apply_*.py']
    }
    
    # Archivos que NO deben moverse (archivos principales del proyecto)
    archivos_excluidos = {
        'README.md', 'main.py', 'app.py', 'models.py', 'utils.py', 
        'requirements.txt', '.env.example', '.gitignore',
        'organizar_archivos.py'  # No mover este mismo script
    }
    
    archivos_por_carpeta = {}
    
    for carpeta_destino, patrones_archivo in patrones.items():
        archivos_encontrados = []
        for patron in patrones_archivo:
            archivos = glob.glob(patron)
            # Filtrar archivos excluidos
            archivos_filtrados = [archivo for archivo in archivos if archivo not in archivos_excluidos]
            archivos_encontrados.extend(archivos_filtrados)
        
        if archivos_encontrados:
            archivos_por_carpeta[carpeta_destino] = archivos_encontrados
    
    return archivos_por_carpeta

def mostrar_resumen_archivos(archivos_por_carpeta):
    """Mostrar un resumen de los archivos que se van a mover"""
    print("\n" + "="*60)
    print("📋 RESUMEN DE ARCHIVOS A ORGANIZAR")
    print("="*60)
    
    total_archivos = 0
    
    for carpeta, archivos in archivos_por_carpeta.items():
        print(f"\n📂 Destino: {carpeta}")
        print("-" * 40)
        for archivo in archivos:
            print(f"   📄 {archivo}")
            total_archivos += 1
    
    print(f"\n📊 Total de archivos a mover: {total_archivos}")
    print("="*60)
    
    return total_archivos

def crear_backup_opcional(archivos_por_carpeta):
    """Crear un backup opcional de los archivos antes de moverlos"""
    respuesta = input("\n🔄 ¿Deseas crear un backup de los archivos antes de moverlos? (s/n): ").lower().strip()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        backup_dir = "backup_organizacion"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        print(f"\n📦 Creando backup en: {backup_dir}")
        
        for carpeta, archivos in archivos_por_carpeta.items():
            for archivo in archivos:
                if os.path.exists(archivo):
                    shutil.copy2(archivo, backup_dir)
                    print(f"   ✅ Backup creado: {archivo}")
        
        print("✅ Backup completado!")
        return True
    
    return False

def mover_archivos(archivos_por_carpeta):
    """Mover los archivos a sus carpetas correspondientes"""
    print("\n🚀 Iniciando organización de archivos...")
    
    archivos_movidos = 0
    errores = []
    
    for carpeta_destino, archivos in archivos_por_carpeta.items():
        print(f"\n📂 Organizando archivos en: {carpeta_destino}")
        
        for archivo in archivos:
            try:
                if os.path.exists(archivo):
                    destino = os.path.join(carpeta_destino, archivo)
                    shutil.move(archivo, destino)
                    print(f"   ✅ Movido: {archivo} → {destino}")
                    archivos_movidos += 1
                else:
                    print(f"   ⚠️  Archivo no encontrado: {archivo}")
            except Exception as e:
                error_msg = f"Error moviendo {archivo}: {str(e)}"
                errores.append(error_msg)
                print(f"   ❌ {error_msg}")
    
    return archivos_movidos, errores

def mostrar_resultado_final(archivos_movidos, errores, backup_creado):
    """Mostrar el resultado final de la organización"""
    print("\n" + "="*60)
    print("🎉 ORGANIZACIÓN COMPLETADA")
    print("="*60)
    
    print(f"✅ Archivos movidos exitosamente: {archivos_movidos}")
    
    if backup_creado:
        print("📦 Backup creado en: backup_organizacion/")
    
    if errores:
        print(f"\n❌ Errores encontrados ({len(errores)}):")
        for error in errores:
            print(f"   • {error}")
    else:
        print("✅ No se encontraron errores")
    
    print("\n📁 Estructura de carpetas actualizada:")
    carpetas = ['test/', 'debug/', 'check/', 'verificar/', 'validacion/', 'analisis/', 'migraciones/', 'fix/', 'documentacion/', 'utilidades/']
    for carpeta in carpetas:
        if os.path.exists(carpeta):
            if carpeta == 'documentacion/':
                archivos_en_carpeta = len([f for f in os.listdir(carpeta) if f.endswith('.md')])
            else:
                archivos_en_carpeta = len([f for f in os.listdir(carpeta) if f.endswith('.py')])
            print(f"   📂 {carpeta} - {archivos_en_carpeta} archivos")
    
    print("="*60)

def main():
    """Función principal del script"""
    print("🔧 ORGANIZADOR DE ARCHIVOS - PROYECTO SYNAPSIS")
    print("="*60)
    print("Este script organizará los archivos del proyecto en carpetas temáticas:")
    print("• test/, debug/, check/ - Archivos de pruebas y depuración")
    print("• verificar/, validacion/ - Archivos de verificación y validación")
    print("• analisis/, migraciones/, fix/ - Archivos de análisis, migración y correcciones")
    print("• documentacion/, utilidades/ - Documentación y utilidades")
    print("para mantener el proyecto ordenado y profesional.")
    
    # Identificar archivos a mover
    archivos_por_carpeta = identificar_archivos_a_mover()
    
    if not archivos_por_carpeta:
        print("\n✅ No se encontraron archivos para organizar.")
        print("El proyecto ya está organizado!")
        return
    
    # Mostrar resumen
    total_archivos = mostrar_resumen_archivos(archivos_por_carpeta)
    
    # Confirmar con el usuario
    print(f"\n❓ ¿Deseas proceder con la organización de {total_archivos} archivos? (s/n): ", end="")
    confirmacion = input().lower().strip()
    
    if confirmacion not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Operación cancelada por el usuario.")
        return
    
    # Crear carpetas de destino
    carpetas_destino = list(archivos_por_carpeta.keys())
    crear_carpetas_si_no_existen(carpetas_destino)
    
    # Crear backup opcional
    backup_creado = crear_backup_opcional(archivos_por_carpeta)
    
    # Mover archivos
    archivos_movidos, errores = mover_archivos(archivos_por_carpeta)
    
    # Mostrar resultado final
    mostrar_resultado_final(archivos_movidos, errores, backup_creado)

if __name__ == "__main__":
    main()