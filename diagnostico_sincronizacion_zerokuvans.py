#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para problemas de sincronización con repositorio Zerokuvans
Identifica y reporta problemas comunes que impiden la sincronización exitosa.
"""

import os
import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime

class DiagnosticoSincronizacion:
    def __init__(self):
        self.problemas = []
        self.advertencias = []
        self.recomendaciones = []
        self.repo_path = os.getcwd()
        
    def log_problema(self, mensaje):
        """Registrar un problema crítico"""
        self.problemas.append(mensaje)
        print(f"❌ PROBLEMA: {mensaje}")
    
    def log_advertencia(self, mensaje):
        """Registrar una advertencia"""
        self.advertencias.append(mensaje)
        print(f"⚠️  ADVERTENCIA: {mensaje}")
    
    def log_recomendacion(self, mensaje):
        """Registrar una recomendación"""
        self.recomendaciones.append(mensaje)
        print(f"💡 RECOMENDACIÓN: {mensaje}")
    
    def ejecutar_comando_git(self, comando):
        """Ejecutar comando git y retornar resultado"""
        try:
            resultado = subprocess.run(
                comando, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=self.repo_path
            )
            return resultado.returncode == 0, resultado.stdout.strip(), resultado.stderr.strip()
        except Exception as e:
            return False, "", str(e)
    
    def verificar_repositorio_git(self):
        """Verificar si es un repositorio Git válido"""
        print("\n🔍 VERIFICANDO REPOSITORIO GIT")
        print("=" * 50)
        
        # Verificar si existe .git
        if not os.path.exists(os.path.join(self.repo_path, '.git')):
            self.log_problema("No es un repositorio Git válido (falta directorio .git)")
            return False
        
        # Verificar estado del repositorio
        exito, salida, error = self.ejecutar_comando_git("git status --porcelain")
        if not exito:
            self.log_problema(f"Error al verificar estado del repositorio: {error}")
            return False
        
        print("✅ Repositorio Git válido detectado")
        
        # Mostrar estado actual
        exito, salida, error = self.ejecutar_comando_git("git status")
        if exito:
            print(f"\n📋 Estado actual del repositorio:")
            print(salida)
        
        return True
    
    def verificar_remotos(self):
        """Verificar configuración de remotos"""
        print("\n🌐 VERIFICANDO REMOTOS")
        print("=" * 50)
        
        exito, salida, error = self.ejecutar_comando_git("git remote -v")
        if not exito:
            self.log_problema("No se pudieron obtener los remotos configurados")
            return
        
        if not salida:
            self.log_problema("No hay remotos configurados")
            self.log_recomendacion("Agregar remoto: git remote add origin https://github.com/zerokuvans/synapsis.git")
            return
        
        print("📡 Remotos configurados:")
        print(salida)
        
        # Verificar conectividad con origin
        if "origin" in salida:
            print("\n🔗 Verificando conectividad con origin...")
            exito, salida_fetch, error = self.ejecutar_comando_git("git ls-remote origin")
            if not exito:
                self.log_problema(f"No se puede conectar con el repositorio remoto: {error}")
                self.log_recomendacion("Verificar credenciales de GitHub y permisos de acceso")
            else:
                print("✅ Conectividad con repositorio remoto exitosa")
    
    def verificar_rama_actual(self):
        """Verificar rama actual y estado"""
        print("\n🌿 VERIFICANDO RAMA ACTUAL")
        print("=" * 50)
        
        exito, rama, error = self.ejecutar_comando_git("git branch --show-current")
        if exito:
            print(f"📍 Rama actual: {rama}")
            
            # Verificar si hay commits por delante
            exito, salida, error = self.ejecutar_comando_git("git status -b --porcelain")
            if "ahead" in salida:
                self.log_advertencia("Hay commits locales que no han sido enviados al repositorio remoto")
                self.log_recomendacion("Ejecutar: git push origin main")
        else:
            self.log_problema(f"No se pudo determinar la rama actual: {error}")
    
    def analizar_archivos_grandes(self):
        """Identificar archivos grandes que podrían causar problemas"""
        print("\n📦 ANALIZANDO ARCHIVOS GRANDES")
        print("=" * 50)
        
        archivos_grandes = []
        limite_mb = 50  # GitHub tiene límite de 100MB, pero 50MB ya es problemático
        
        for root, dirs, files in os.walk(self.repo_path):
            # Ignorar .git
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    size = os.path.getsize(filepath)
                    size_mb = size / (1024 * 1024)
                    
                    if size_mb > limite_mb:
                        rel_path = os.path.relpath(filepath, self.repo_path)
                        archivos_grandes.append((rel_path, size_mb))
                except (OSError, IOError):
                    continue
        
        if archivos_grandes:
            self.log_problema(f"Encontrados {len(archivos_grandes)} archivos grandes (>{limite_mb}MB):")
            for archivo, size in archivos_grandes:
                print(f"   📄 {archivo}: {size:.1f}MB")
            self.log_recomendacion("Considerar usar Git LFS para archivos grandes o moverlos fuera del repositorio")
        else:
            print("✅ No se encontraron archivos problemáticamente grandes")
    
    def verificar_archivos_sensibles(self):
        """Verificar archivos sensibles que no deberían estar en el repositorio"""
        print("\n🔒 VERIFICANDO ARCHIVOS SENSIBLES")
        print("=" * 50)
        
        patrones_sensibles = [
            '.env', '*.key', '*.pem', '*.p12', '*.pfx',
            'config.json', 'secrets.json', '*.secret',
            'database.db', '*.sql', 'backup.sql'
        ]
        
        archivos_sensibles = []
        
        for patron in patrones_sensibles:
            for archivo in Path(self.repo_path).rglob(patron):
                if '.git' not in str(archivo):
                    rel_path = os.path.relpath(archivo, self.repo_path)
                    archivos_sensibles.append(rel_path)
        
        if archivos_sensibles:
            self.log_problema("Encontrados archivos sensibles que podrían estar expuestos:")
            for archivo in archivos_sensibles:
                print(f"   🔐 {archivo}")
            self.log_recomendacion("Agregar estos archivos al .gitignore y removerlos del repositorio")
        else:
            print("✅ No se encontraron archivos sensibles expuestos")
    
    def verificar_gitignore(self):
        """Verificar configuración de .gitignore"""
        print("\n📝 VERIFICANDO .GITIGNORE")
        print("=" * 50)
        
        gitignore_path = os.path.join(self.repo_path, '.gitignore')
        
        if not os.path.exists(gitignore_path):
            self.log_problema("No existe archivo .gitignore")
            self.log_recomendacion("Crear archivo .gitignore con patrones básicos")
            return
        
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        patrones_recomendados = [
            '.env', '__pycache__/', '*.pyc', '*.log',
            'venv/', '.vscode/', '*.db', '*.sql'
        ]
        
        patrones_faltantes = []
        for patron in patrones_recomendados:
            if patron not in contenido:
                patrones_faltantes.append(patron)
        
        if patrones_faltantes:
            self.log_advertencia(f"Faltan {len(patrones_faltantes)} patrones recomendados en .gitignore:")
            for patron in patrones_faltantes:
                print(f"   📋 {patron}")
        else:
            print("✅ .gitignore contiene patrones básicos recomendados")
    
    def verificar_cambios_pendientes(self):
        """Verificar cambios no committeados"""
        print("\n📋 VERIFICANDO CAMBIOS PENDIENTES")
        print("=" * 50)
        
        # Verificar archivos modificados
        exito, salida, error = self.ejecutar_comando_git("git status --porcelain")
        if not exito:
            self.log_problema(f"Error al verificar cambios pendientes: {error}")
            return
        
        if salida:
            lineas = salida.split('\n')
            modificados = [l for l in lineas if l.startswith(' M')]
            nuevos = [l for l in lineas if l.startswith('??')]
            staged = [l for l in lineas if l.startswith('A ') or l.startswith('M ')]
            
            if modificados:
                self.log_advertencia(f"Hay {len(modificados)} archivos modificados sin agregar:")
                for archivo in modificados[:5]:  # Mostrar solo los primeros 5
                    print(f"   📝 {archivo[3:]}")
                if len(modificados) > 5:
                    print(f"   ... y {len(modificados) - 5} más")
            
            if nuevos:
                self.log_advertencia(f"Hay {len(nuevos)} archivos nuevos sin agregar:")
                for archivo in nuevos[:5]:
                    print(f"   📄 {archivo[3:]}")
                if len(nuevos) > 5:
                    print(f"   ... y {len(nuevos) - 5} más")
            
            if staged:
                print(f"✅ Hay {len(staged)} archivos preparados para commit")
            
            self.log_recomendacion("Revisar cambios y hacer commit antes de sincronizar")
        else:
            print("✅ No hay cambios pendientes")
    
    def verificar_conflictos(self):
        """Verificar conflictos de merge pendientes"""
        print("\n⚔️  VERIFICANDO CONFLICTOS")
        print("=" * 50)
        
        # Verificar si hay merge en progreso
        merge_head = os.path.join(self.repo_path, '.git', 'MERGE_HEAD')
        if os.path.exists(merge_head):
            self.log_problema("Hay un merge en progreso con conflictos pendientes")
            self.log_recomendacion("Resolver conflictos y completar el merge antes de sincronizar")
            return
        
        # Verificar archivos con marcadores de conflicto
        archivos_conflicto = []
        for root, dirs, files in os.walk(self.repo_path):
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                if file.endswith(('.py', '.js', '.html', '.css', '.md', '.txt')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            contenido = f.read()
                            if '<<<<<<< HEAD' in contenido or '=======' in contenido or '>>>>>>> ' in contenido:
                                rel_path = os.path.relpath(filepath, self.repo_path)
                                archivos_conflicto.append(rel_path)
                    except (OSError, IOError):
                        continue
        
        if archivos_conflicto:
            self.log_problema(f"Encontrados {len(archivos_conflicto)} archivos con marcadores de conflicto:")
            for archivo in archivos_conflicto:
                print(f"   ⚔️  {archivo}")
            self.log_recomendacion("Resolver manualmente los conflictos en estos archivos")
        else:
            print("✅ No se encontraron conflictos pendientes")
    
    def probar_push(self):
        """Probar hacer push para identificar problemas específicos"""
        print("\n🚀 PROBANDO SINCRONIZACIÓN")
        print("=" * 50)
        
        # Primero hacer fetch para obtener cambios remotos
        print("📥 Obteniendo cambios del repositorio remoto...")
        exito, salida, error = self.ejecutar_comando_git("git fetch origin")
        if not exito:
            self.log_problema(f"Error al hacer fetch: {error}")
            if "authentication" in error.lower() or "permission" in error.lower():
                self.log_recomendacion("Verificar credenciales de GitHub (token de acceso personal)")
            return
        
        # Verificar si hay cambios para enviar
        exito, salida, error = self.ejecutar_comando_git("git status -b --porcelain")
        if "ahead" not in salida:
            print("✅ No hay commits locales para enviar")
            return
        
        # Intentar push en modo dry-run
        print("🧪 Probando push (simulación)...")
        exito, salida, error = self.ejecutar_comando_git("git push --dry-run origin main")
        if not exito:
            self.log_problema(f"Error en simulación de push: {error}")
            if "non-fast-forward" in error:
                self.log_recomendacion("Hacer pull antes del push: git pull origin main")
            elif "authentication" in error.lower():
                self.log_recomendacion("Configurar autenticación con token de acceso personal")
            elif "permission" in error.lower():
                self.log_recomendacion("Verificar permisos de escritura en el repositorio")
        else:
            print("✅ Simulación de push exitosa")
            self.log_recomendacion("Ejecutar: git push origin main")
    
    def generar_reporte(self):
        """Generar reporte final con resumen y recomendaciones"""
        print("\n" + "=" * 60)
        print("📊 REPORTE FINAL DE DIAGNÓSTICO")
        print("=" * 60)
        
        print(f"\n🕒 Fecha del diagnóstico: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Repositorio: {self.repo_path}")
        
        # Resumen de problemas
        if self.problemas:
            print(f"\n❌ PROBLEMAS CRÍTICOS ({len(self.problemas)}):")
            for i, problema in enumerate(self.problemas, 1):
                print(f"   {i}. {problema}")
        else:
            print("\n✅ No se encontraron problemas críticos")
        
        # Resumen de advertencias
        if self.advertencias:
            print(f"\n⚠️  ADVERTENCIAS ({len(self.advertencias)}):")
            for i, advertencia in enumerate(self.advertencias, 1):
                print(f"   {i}. {advertencia}")
        
        # Recomendaciones
        if self.recomendaciones:
            print(f"\n💡 RECOMENDACIONES ({len(self.recomendaciones)}):")
            for i, recomendacion in enumerate(self.recomendaciones, 1):
                print(f"   {i}. {recomendacion}")
        
        # Comandos sugeridos
        print(f"\n🔧 COMANDOS SUGERIDOS PARA RESOLVER PROBLEMAS:")
        print("   1. git add .")
        print("   2. git commit -m 'Organización de archivos y correcciones'")
        print("   3. git pull origin main")
        print("   4. git push origin main")
        
        # Guardar reporte en archivo
        reporte_data = {
            'fecha': datetime.now().isoformat(),
            'repositorio': self.repo_path,
            'problemas': self.problemas,
            'advertencias': self.advertencias,
            'recomendaciones': self.recomendaciones
        }
        
        with open('reporte_diagnostico_zerokuvans.json', 'w', encoding='utf-8') as f:
            json.dump(reporte_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado en: reporte_diagnostico_zerokuvans.json")
        print("=" * 60)
    
    def ejecutar_diagnostico_completo(self):
        """Ejecutar diagnóstico completo"""
        print("🔧 DIAGNÓSTICO DE SINCRONIZACIÓN - REPOSITORIO ZEROKUVANS")
        print("=" * 60)
        print("Este script identificará problemas que impiden la sincronización exitosa")
        print("con el repositorio en GitHub (zerokuvans/synapsis)")
        
        if not self.verificar_repositorio_git():
            return
        
        self.verificar_remotos()
        self.verificar_rama_actual()
        self.analizar_archivos_grandes()
        self.verificar_archivos_sensibles()
        self.verificar_gitignore()
        self.verificar_cambios_pendientes()
        self.verificar_conflictos()
        self.probar_push()
        self.generar_reporte()

def main():
    """Función principal"""
    diagnostico = DiagnosticoSincronizacion()
    diagnostico.ejecutar_diagnostico_completo()

if __name__ == "__main__":
    main()