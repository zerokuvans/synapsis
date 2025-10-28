#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re

def debug_frontend_vencimientos():
    print("🔍 Debuggeando frontend de vencimientos...")
    
    session = requests.Session()
    usuario = {'username': '80833959', 'password': 'M4r14l4r@'}
    
    # Login
    print("🔐 Iniciando sesión...")
    login_response = session.post('http://127.0.0.1:8080/', data=usuario)
    
    if login_response.status_code != 200:
        print(f"❌ ERROR LOGIN: {login_response.status_code}")
        return
    
    print("✅ Login exitoso")
    
    # Obtener la página de vencimientos
    print("📄 Obteniendo página de vencimientos...")
    page_response = session.get('http://127.0.0.1:8080/mpa/vencimientos')
    
    if page_response.status_code != 200:
        print(f"❌ ERROR PÁGINA: {page_response.status_code}")
        return
    
    print("✅ Página obtenida correctamente")
    
    # Analizar el HTML
    soup = BeautifulSoup(page_response.text, 'html.parser')
    
    # Verificar elementos clave
    print("\n📋 Verificando elementos de la página:")
    
    # Tabla de vencimientos
    tabla = soup.find('table', {'id': 'vencimientosTable'})
    if tabla:
        print("✅ Tabla de vencimientos encontrada")
        tbody = tabla.find('tbody', {'id': 'vencimientosTableBody'})
        if tbody:
            print("✅ Tbody encontrado")
            filas = tbody.find_all('tr')
            print(f"📊 Filas en tabla: {len(filas)}")
        else:
            print("❌ Tbody no encontrado")
    else:
        print("❌ Tabla de vencimientos no encontrada")
    
    # Filtros
    filtros = ['filtroTipo', 'filtroEstado', 'filtroTecnico', 'filtroPlaca']
    for filtro in filtros:
        elemento = soup.find(attrs={'id': filtro})
        if elemento:
            print(f"✅ Filtro {filtro} encontrado")
            if elemento.name == 'select':
                opciones = elemento.find_all('option')
                print(f"   📋 Opciones: {len(opciones)}")
        else:
            print(f"❌ Filtro {filtro} no encontrado")
    
    # Estadísticas
    estadisticas = ['countVencidos', 'countProximosVencer', 'countVigentes', 'countTotal']
    for stat in estadisticas:
        elemento = soup.find(attrs={'id': stat})
        if elemento:
            print(f"✅ Estadística {stat} encontrada: {elemento.text}")
        else:
            print(f"❌ Estadística {stat} no encontrada")
    
    # Buscar scripts que carguen datos
    print("\n🔧 Verificando scripts JavaScript:")
    scripts = soup.find_all('script')
    
    for i, script in enumerate(scripts):
        if script.string and 'loadVencimientos' in script.string:
            print(f"✅ Script {i+1} contiene loadVencimientos")
        if script.string and 'fetch' in script.string:
            print(f"✅ Script {i+1} contiene fetch")
        if script.string and '/api/mpa/vencimientos' in script.string:
            print(f"✅ Script {i+1} contiene URL del API")
    
    # Verificar si hay algún filtro por defecto aplicado
    print("\n🔍 Verificando filtros por defecto:")
    
    # Buscar en el JavaScript si hay filtros aplicados por defecto
    page_content = page_response.text
    
    # Buscar patrones que indiquen filtros por defecto
    if 'filtroTipo.value = ' in page_content:
        match = re.search(r'filtroTipo\.value\s*=\s*["\']([^"\']*)["\']', page_content)
        if match:
            print(f"⚠️ Filtro de tipo por defecto: {match.group(1)}")
    
    if 'filtroEstado.value = ' in page_content:
        match = re.search(r'filtroEstado\.value\s*=\s*["\']([^"\']*)["\']', page_content)
        if match:
            print(f"⚠️ Filtro de estado por defecto: {match.group(1)}")
    
    # Buscar limitaciones en el renderizado
    if '.slice(' in page_content:
        print("⚠️ Se encontró uso de .slice() que podría limitar registros")
    
    if 'pageLength' in page_content or 'pageSize' in page_content:
        print("⚠️ Se encontró configuración de paginación")
    
    # Verificar API directamente
    print("\n📡 Verificando API directamente:")
    api_response = session.get('http://127.0.0.1:8080/api/mpa/vencimientos')
    
    if api_response.status_code == 200:
        data = api_response.json()
        if data.get('success'):
            total_api = data.get('total', 0)
            vencimientos = data.get('data', [])
            print(f"✅ API funciona: {total_api} vencimientos, {len(vencimientos)} en lista")
        else:
            print(f"❌ API error: {data.get('error')}")
    else:
        print(f"❌ API error HTTP: {api_response.status_code}")
    
    print("\n" + "="*60)
    print("🎯 RESUMEN DEL DIAGNÓSTICO")
    print("="*60)
    
    if tabla and tbody:
        print("✅ La estructura HTML está correcta")
    else:
        print("❌ Problema en la estructura HTML")
    
    if total_api == 249:
        print("✅ El API devuelve los 249 vencimientos correctos")
    else:
        print(f"❌ El API no devuelve los datos esperados: {total_api}")
    
    print("\n💡 RECOMENDACIONES:")
    print("1. Verificar la consola del navegador en tiempo real")
    print("2. Revisar si hay filtros aplicados por defecto")
    print("3. Verificar si el JavaScript se ejecuta correctamente")
    print("4. Comprobar si hay errores de red en el navegador")

if __name__ == "__main__":
    debug_frontend_vencimientos()