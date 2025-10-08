#!/usr/bin/env python3
"""
Script para verificar que la aplicación funcione correctamente
después de la reorganización de archivos
"""

import os
import sys
import subprocess
import importlib.util

def verificar_archivos_criticos():
    """Verificar que los archivos críticos existan"""
    
    print("🔍 Verificando archivos críticos...")
    
    archivos_criticos = [
        'app.py',
        'main.py',
        'requirements.txt',
        '.env.example',
        'templates',
        'static',
        'migrations',
        'supabase',
        'sql',
        'backups',
        'triggers'
    ]
    
    faltantes = []
    for archivo in archivos_criticos:
        if not os.path.exists(archivo):
            faltantes.append(archivo)
    
    if faltantes:
        print(f"❌ Archivos críticos faltantes: {', '.join(faltantes)}")
        return False
    else:
        print("✅ Todos los archivos críticos están presentes")
        return True

def verificar_importaciones_python():
    """Verificar que las importaciones de Python funcionen"""
    
    print("\n🔍 Verificando importaciones de Python...")
    
    # Intentar importar app.py
    try:
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        print("✅ app.py se puede importar correctamente")
    except Exception as e:
        print(f"❌ Error importando app.py: {e}")
        return False
    
    return True

def verificar_dependencias():
    """Verificar que las dependencias estén instaladas"""
    
    print("\n🔍 Verificando dependencias...")
    
    dependencias_importantes = [
        'flask',
        'mysql.connector',
        'bcrypt',
        'pytz',
        'reportlab',
        'pandas',
        'requests'
    ]
    
    faltantes = []
    for dep in dependencias_importantes:
        try:
            if dep == 'mysql.connector':
                import mysql.connector
            elif dep == 'flask':
                import flask
            elif dep == 'bcrypt':
                import bcrypt
            elif dep == 'pytz':
                import pytz
            elif dep == 'reportlab':
                import reportlab
            elif dep == 'pandas':
                import pandas
            elif dep == 'requests':
                import requests
        except ImportError:
            faltantes.append(dep)
    
    if faltantes:
        print(f"❌ Dependencias faltantes: {', '.join(faltantes)}")
        return False
    else:
        print("✅ Todas las dependencias importantes están instaladas")
        return True

def verificar_estructura_directorios():
    """Verificar la estructura de directorios"""
    
    print("\n🔍 Verificando estructura de directorios...")
    
    # Verificar que no haya archivos .py sueltos que deberían estar organizados
    archivos_py = glob.glob('*.py')
    
    # Filtrar archivos críticos
    archivos_criticos = ['app.py', 'main.py', 'main_fixed.py', 'temp_main.py', 'reorganizar_archivos.py', 'reorganizar_archivos_seguro.py', 'verificar_despues_reorganizacion.py']
    archivos_sueltos = [f for f in archivos_py if f not in archivos_criticos]
    
    if archivos_sueltos:
        print(f"⚠️  Archivos .py sueltos encontrados: {', '.join(archivos_sueltos)}")
        print("   Estos archivos podrían necesitar ser organizados")
    else:
        print("✅ No hay archivos .py sueltos no críticos")
    
    # Verificar directorios organizados
    directorios_organizados = ['test', 'diagnosticos', 'verificar', 'fix', 'debug', 'data', 'docs']
    
    for directorio in directorios_organizados:
        if os.path.exists(directorio):
            archivos = os.listdir(directorio)
            print(f"📁 {directorio}/ contiene {len(archivos)} elementos")
        else:
            print(f"⚠️  Directorio {directorio}/ no existe")
    
    return True

def verificar_sintaxis_python():
    """Verificar la sintaxis de los archivos Python principales"""
    
    print("\n🔍 Verificando sintaxis de archivos Python...")
    
    archivos_a_verificar = ['app.py', 'main.py']
    
    for archivo in archivos_a_verificar:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                codigo = f.read()
            
            # Verificar sintaxis
            compile(codigo, archivo, 'exec')
            print(f"✅ {archivo} - sintaxis correcta")
            
        except SyntaxError as e:
            print(f"❌ Error de sintaxis en {archivo}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error verificando {archivo}: {e}")
            return False
    
    return True

def generar_reporte_final():
    """Generar reporte final de la verificación"""
    
    print("\n" + "="*60)
    print("📋 REPORTE FINAL DE VERIFICACIÓN")
    print("="*60)
    
    resultados = []
    
    # Ejecutar todas las verificaciones
    resultados.append(("Archivos críticos", verificar_archivos_criticos()))
    resultados.append(("Importaciones Python", verificar_importaciones_python()))
    resultados.append(("Dependencias", verificar_dependencias()))
    resultados.append(("Estructura directorios", verificar_estructura_directorios()))
    resultados.append(("Sintaxis Python", verificar_sintaxis_python()))
    
    print("\n📊 RESUMEN:")
    
    exitosos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        estado = "✅" if resultado else "❌"
        print(f"   {estado} {nombre}")
    
    print(f"\n🎯 Resultado: {exitosos}/{total} verificaciones pasadas")
    
    if exitosos == total:
        print("\n🎉 ¡Todo está correcto! La aplicación debería funcionar.")
        print("\n🚀 Puedes iniciar la aplicación con:")
        print("   python main.py")
        print("   o")
        print("   python app.py")
    else:
        print("\n⚠️  Hay algunos problemas que deben ser resueltos antes de iniciar la aplicación.")
        print("   Revisa los errores mostrados arriba.")
    
    return exitosos == total

def main():
    """Función principal"""
    
    print("🔍 VERIFICADOR POST-REORGANIZACIÓN")
    print("="*60)
    print("Este script verifica que la aplicación funcione correctamente")
    print("después de reorganizar los archivos.")
    print("="*60)
    
    # Generar reporte final
    exito = generar_reporte_final()
    
    if not exito:
        sys.exit(1)

if __name__ == "__main__":
    main()