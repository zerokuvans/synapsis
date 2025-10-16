#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script interactivo para configurar Git con credenciales de zerokuvans
Resuelve problemas de sincronización con el repositorio zerokuvans/synapsis
"""

import os
import subprocess
import sys
import platform
from pathlib import Path

class ConfiguradorGitZerokuvans:
    def __init__(self):
        self.repo_path = os.getcwd()
        self.sistema = platform.system().lower()
        
    def ejecutar_comando(self, comando, mostrar_salida=True):
        """Ejecutar comando y retornar resultado"""
        try:
            resultado = subprocess.run(
                comando, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=self.repo_path
            )
            if mostrar_salida and resultado.stdout:
                print(resultado.stdout.strip())
            if resultado.stderr and resultado.returncode != 0:
                print(f"⚠️  Error: {resultado.stderr.strip()}")
            return resultado.returncode == 0, resultado.stdout.strip(), resultado.stderr.strip()
        except Exception as e:
            print(f"❌ Error ejecutando comando: {e}")
            return False, "", str(e)
    
    def mostrar_titulo(self, titulo):
        """Mostrar título con formato"""
        print("\n" + "=" * 60)
        print(f"🔧 {titulo}")
        print("=" * 60)
    
    def mostrar_paso(self, numero, descripcion):
        """Mostrar paso numerado"""
        print(f"\n📋 PASO {numero}: {descripcion}")
        print("-" * 50)
    
    def solicitar_confirmacion(self, mensaje):
        """Solicitar confirmación del usuario"""
        while True:
            respuesta = input(f"\n❓ {mensaje} (s/n): ").lower().strip()
            if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
                return True
            elif respuesta in ['n', 'no']:
                return False
            else:
                print("Por favor responde 's' para sí o 'n' para no")
    
    def mostrar_configuracion_actual(self):
        """Mostrar configuración actual de Git"""
        self.mostrar_paso(1, "VERIFICANDO CONFIGURACIÓN ACTUAL DE GIT")
        
        print("📊 Configuración actual:")
        
        # Mostrar user.name
        exito, nombre, _ = self.ejecutar_comando("git config --global user.name", False)
        if exito and nombre:
            print(f"   👤 Nombre: {nombre}")
        else:
            print("   👤 Nombre: No configurado")
        
        # Mostrar user.email
        exito, email, _ = self.ejecutar_comando("git config --global user.email", False)
        if exito and email:
            print(f"   📧 Email: {email}")
        else:
            print("   📧 Email: No configurado")
        
        # Mostrar remotos
        print("\n🌐 Remotos configurados:")
        exito, remotos, _ = self.ejecutar_comando("git remote -v", False)
        if exito and remotos:
            for linea in remotos.split('\n'):
                print(f"   📡 {linea}")
        else:
            print("   📡 No hay remotos configurados")
    
    def configurar_credenciales_zerokuvans(self):
        """Configurar credenciales para zerokuvans"""
        self.mostrar_paso(2, "CONFIGURANDO CREDENCIALES DE ZEROKUVANS")
        
        # Configurar nombre de usuario
        print("🔧 Configurando user.name como 'zerokuvans'...")
        exito, _, _ = self.ejecutar_comando('git config --global user.name "zerokuvans"', False)
        if exito:
            print("✅ Nombre de usuario configurado correctamente")
        else:
            print("❌ Error configurando nombre de usuario")
            return False
        
        # Solicitar email
        print("\n📧 Necesitamos configurar el email para zerokuvans")
        print("Opciones comunes:")
        print("   1. zerokuvans@gmail.com")
        print("   2. admin@zerokuvans.com")
        print("   3. zerokuvans@zerokuvans.com")
        print("   4. Otro email personalizado")
        
        while True:
            opcion = input("\n❓ Selecciona una opción (1-4): ").strip()
            
            if opcion == "1":
                email = "zerokuvans@gmail.com"
                break
            elif opcion == "2":
                email = "admin@zerokuvans.com"
                break
            elif opcion == "3":
                email = "zerokuvans@zerokuvans.com"
                break
            elif opcion == "4":
                email = input("📧 Ingresa el email personalizado: ").strip()
                if email and "@" in email:
                    break
                else:
                    print("❌ Email inválido. Debe contener '@'")
            else:
                print("❌ Opción inválida. Selecciona 1, 2, 3 o 4")
        
        # Configurar email
        print(f"🔧 Configurando email como '{email}'...")
        exito, _, _ = self.ejecutar_comando(f'git config --global user.email "{email}"', False)
        if exito:
            print("✅ Email configurado correctamente")
        else:
            print("❌ Error configurando email")
            return False
        
        # Mostrar configuración actualizada
        print("\n📊 Nueva configuración:")
        exito, nombre, _ = self.ejecutar_comando("git config --global user.name", False)
        exito2, email_config, _ = self.ejecutar_comando("git config --global user.email", False)
        print(f"   👤 Nombre: {nombre}")
        print(f"   📧 Email: {email_config}")
        
        return True
    
    def configurar_remoto(self):
        """Configurar remoto para zerokuvans/synapsis"""
        self.mostrar_paso(3, "CONFIGURANDO REPOSITORIO REMOTO")
        
        # Verificar remoto actual
        exito, remotos, _ = self.ejecutar_comando("git remote -v", False)
        
        url_correcta = "https://github.com/zerokuvans/synapsis.git"
        
        if "zerokuvans/synapsis" in remotos:
            print("✅ El remoto ya está configurado correctamente para zerokuvans/synapsis")
        else:
            print("🔧 Configurando remoto para zerokuvans/synapsis...")
            
            # Verificar si existe origin
            if "origin" in remotos:
                print("📝 Actualizando URL del remoto origin...")
                exito, _, _ = self.ejecutar_comando(f'git remote set-url origin {url_correcta}', False)
            else:
                print("📝 Agregando remoto origin...")
                exito, _, _ = self.ejecutar_comando(f'git remote add origin {url_correcta}', False)
            
            if exito:
                print("✅ Remoto configurado correctamente")
            else:
                print("❌ Error configurando remoto")
                return False
        
        # Mostrar remotos actualizados
        print("\n🌐 Remotos actuales:")
        self.ejecutar_comando("git remote -v")
        
        return True
    
    def limpiar_credenciales_anteriores(self):
        """Limpiar credenciales almacenadas anteriores"""
        self.mostrar_paso(4, "LIMPIANDO CREDENCIALES ANTERIORES")
        
        print("🧹 Limpiando credenciales almacenadas...")
        
        if self.sistema == "windows":
            # Windows - Credential Manager
            print("🔧 Limpiando credenciales de Windows Credential Manager...")
            comandos = [
                'cmdkey /delete:git:https://github.com',
                'cmdkey /delete:github.com',
                'git config --global --unset credential.helper'
            ]
            
            for comando in comandos:
                self.ejecutar_comando(comando, False)
        
        elif self.sistema == "darwin":  # macOS
            print("🔧 Limpiando credenciales de macOS Keychain...")
            comandos = [
                'security delete-internet-password -s github.com',
                'git config --global --unset credential.helper'
            ]
            
            for comando in comandos:
                self.ejecutar_comando(comando, False)
        
        else:  # Linux
            print("🔧 Limpiando credenciales de Linux...")
            comandos = [
                'git config --global --unset credential.helper',
                'rm -f ~/.git-credentials'
            ]
            
            for comando in comandos:
                self.ejecutar_comando(comando, False)
        
        print("✅ Credenciales anteriores limpiadas")
        print("💡 En el próximo push, Git te pedirá nuevas credenciales")
    
    def mostrar_guia_token(self):
        """Mostrar guía para crear token de acceso personal"""
        self.mostrar_paso(5, "GUÍA PARA TOKEN DE ACCESO PERSONAL")
        
        print("🔑 Para autenticarte con GitHub necesitas un Token de Acceso Personal")
        print("\n📋 INSTRUCCIONES PASO A PASO:")
        print("   1. Ve a GitHub.com e inicia sesión con la cuenta zerokuvans")
        print("   2. Haz clic en tu avatar (esquina superior derecha)")
        print("   3. Selecciona 'Settings'")
        print("   4. En el menú izquierdo, busca 'Developer settings'")
        print("   5. Haz clic en 'Personal access tokens'")
        print("   6. Selecciona 'Tokens (classic)'")
        print("   7. Haz clic en 'Generate new token'")
        print("   8. Selecciona 'Generate new token (classic)'")
        
        print("\n🔧 CONFIGURACIÓN DEL TOKEN:")
        print("   📝 Note: 'Token para synapsis - acceso completo'")
        print("   ⏰ Expiration: 90 days (o No expiration si prefieres)")
        print("   ✅ Permisos necesarios:")
        print("      ☑️  repo (acceso completo a repositorios)")
        print("      ☑️  workflow (si usas GitHub Actions)")
        print("      ☑️  write:packages (si usas GitHub Packages)")
        
        print("\n💾 IMPORTANTE:")
        print("   🔴 COPIA EL TOKEN INMEDIATAMENTE - Solo se muestra una vez")
        print("   🔴 Guárdalo en un lugar seguro")
        print("   🔴 NO lo compartas con nadie")
        
        print("\n🔐 CÓMO USAR EL TOKEN:")
        print("   👤 Usuario: zerokuvans")
        print("   🔑 Contraseña: [EL TOKEN QUE COPIASTE]")
        print("   📝 Cuando Git te pida credenciales, usa el token como contraseña")
        
        if self.solicitar_confirmacion("¿Ya tienes el token listo?"):
            return True
        else:
            print("\n⏸️  Pausa aquí para crear el token")
            print("🔄 Ejecuta este script nuevamente cuando tengas el token")
            return False
    
    def verificar_conectividad(self):
        """Verificar conectividad con el repositorio"""
        self.mostrar_paso(6, "VERIFICANDO CONECTIVIDAD")
        
        print("🔗 Probando conexión con el repositorio remoto...")
        exito, salida, error = self.ejecutar_comando("git ls-remote origin", False)
        
        if exito:
            print("✅ Conectividad exitosa con zerokuvans/synapsis")
            return True
        else:
            print("❌ Error de conectividad:")
            print(f"   {error}")
            
            if "authentication" in error.lower() or "permission" in error.lower():
                print("\n💡 SOLUCIÓN:")
                print("   🔑 Necesitas configurar el token de acceso personal")
                print("   📝 Ejecuta: git push origin main")
                print("   🔐 Cuando te pida credenciales:")
                print("      👤 Usuario: zerokuvans")
                print("      🔑 Contraseña: [TU TOKEN]")
            
            return False
    
    def verificar_estado_repositorio(self):
        """Verificar estado del repositorio"""
        self.mostrar_paso(7, "VERIFICANDO ESTADO DEL REPOSITORIO")
        
        print("📊 Estado actual del repositorio:")
        self.ejecutar_comando("git status")
        
        # Verificar si hay cambios pendientes
        exito, salida, _ = self.ejecutar_comando("git status --porcelain", False)
        
        if salida:
            print("\n⚠️  HAY CAMBIOS PENDIENTES:")
            lineas = salida.split('\n')
            modificados = [l for l in lineas if l.startswith(' M')]
            nuevos = [l for l in lineas if l.startswith('??')]
            
            if modificados:
                print(f"   📝 {len(modificados)} archivos modificados")
            if nuevos:
                print(f"   📄 {len(nuevos)} archivos nuevos")
            
            print("\n💡 RECOMENDACIÓN:")
            print("   1. git add .")
            print("   2. git commit -m 'Configuración de credenciales zerokuvans'")
            print("   3. git push origin main")
        else:
            print("\n✅ No hay cambios pendientes")
    
    def mostrar_comandos_sincronizacion(self):
        """Mostrar comandos para sincronización"""
        self.mostrar_paso(8, "COMANDOS PARA SINCRONIZACIÓN")
        
        print("🚀 COMANDOS PARA SINCRONIZAR:")
        print("\n1️⃣  AGREGAR CAMBIOS:")
        print("   git add .")
        
        print("\n2️⃣  HACER COMMIT:")
        print("   git commit -m 'Configuración y organización de archivos'")
        
        print("\n3️⃣  OBTENER CAMBIOS REMOTOS:")
        print("   git pull origin main")
        
        print("\n4️⃣  ENVIAR CAMBIOS:")
        print("   git push origin main")
        
        print("\n🔐 CREDENCIALES CUANDO TE LAS PIDA:")
        print("   👤 Username: zerokuvans")
        print("   🔑 Password: [TU TOKEN DE ACCESO PERSONAL]")
        
        print("\n⚠️  SI HAY CONFLICTOS:")
        print("   📝 Edita manualmente los archivos con conflictos")
        print("   🔍 Busca marcadores: <<<<<<< ======= >>>>>>>")
        print("   ✅ Resuelve los conflictos y haz commit")
        
        if self.solicitar_confirmacion("¿Quieres que ejecute automáticamente 'git add .' y 'git commit'?"):
            return self.ejecutar_comandos_automaticos()
        
        return True
    
    def ejecutar_comandos_automaticos(self):
        """Ejecutar comandos automáticos de git"""
        print("\n🤖 EJECUTANDO COMANDOS AUTOMÁTICOS...")
        
        # Git add
        print("📝 Agregando archivos...")
        exito, _, _ = self.ejecutar_comando("git add .", False)
        if exito:
            print("✅ Archivos agregados correctamente")
        else:
            print("❌ Error agregando archivos")
            return False
        
        # Git commit
        mensaje = "Configuración de credenciales zerokuvans y organización de archivos"
        print("💾 Haciendo commit...")
        exito, _, _ = self.ejecutar_comando(f'git commit -m "{mensaje}"', False)
        if exito:
            print("✅ Commit realizado correctamente")
        else:
            print("⚠️  No hay cambios para hacer commit o ya están committeados")
        
        print("\n🚀 SIGUIENTE PASO:")
        print("   Ejecuta: git push origin main")
        print("   🔐 Usa tus credenciales de zerokuvans cuando te las pida")
        
        return True
    
    def ejecutar_configuracion_completa(self):
        """Ejecutar configuración completa paso a paso"""
        self.mostrar_titulo("CONFIGURADOR GIT ZEROKUVANS")
        print("Este script te ayudará a configurar Git para sincronizar con zerokuvans/synapsis")
        
        if not self.solicitar_confirmacion("¿Quieres continuar con la configuración?"):
            print("❌ Configuración cancelada")
            return
        
        # Paso 1: Mostrar configuración actual
        self.mostrar_configuracion_actual()
        
        # Paso 2: Configurar credenciales
        if not self.configurar_credenciales_zerokuvans():
            print("❌ Error en configuración de credenciales")
            return
        
        # Paso 3: Configurar remoto
        if not self.configurar_remoto():
            print("❌ Error en configuración de remoto")
            return
        
        # Paso 4: Limpiar credenciales anteriores
        self.limpiar_credenciales_anteriores()
        
        # Paso 5: Guía para token
        if not self.mostrar_guia_token():
            return
        
        # Paso 6: Verificar conectividad
        self.verificar_conectividad()
        
        # Paso 7: Verificar estado
        self.verificar_estado_repositorio()
        
        # Paso 8: Comandos de sincronización
        self.mostrar_comandos_sincronizacion()
        
        # Resumen final
        self.mostrar_titulo("CONFIGURACIÓN COMPLETADA")
        print("✅ Git está configurado para zerokuvans")
        print("🔑 Recuerda usar tu token como contraseña")
        print("🚀 Ya puedes sincronizar con: git push origin main")
        
        print("\n📋 RESUMEN DE CAMBIOS:")
        print("   👤 Usuario Git: zerokuvans")
        print("   🌐 Repositorio: zerokuvans/synapsis")
        print("   🧹 Credenciales anteriores limpiadas")
        print("   🔐 Listo para usar token de acceso personal")

def main():
    """Función principal"""
    configurador = ConfiguradorGitZerokuvans()
    configurador.ejecutar_configuracion_completa()

if __name__ == "__main__":
    main()