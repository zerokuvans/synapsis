#!/usr/bin/env python3
"""
Script para depurar específicamente el problema de los botones de estado
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8080"

def verificar_api_cambio_estado():
    """Verificar que la API de cambio de estado funcione"""
    print("🌐 VERIFICANDO API DE CAMBIO DE ESTADO")
    print("=" * 50)
    
    try:
        # Hacer una petición de prueba (sin datos válidos para ver la respuesta)
        response = requests.post(f"{BASE_URL}/api/devoluciones/cambiar-estado", 
                               json={}, 
                               headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ API responde correctamente (error 400 esperado sin datos)")
            try:
                error_data = response.json()
                print(f"Respuesta: {error_data}")
            except:
                print("Respuesta no es JSON válido")
        elif response.status_code == 404:
            print("❌ API no encontrada - ruta no existe")
        elif response.status_code == 500:
            print("⚠️  Error interno del servidor")
        else:
            print(f"⚠️  Respuesta inesperada: {response.status_code}")
        
        return response.status_code in [400, 200]
        
    except Exception as e:
        print(f"❌ Error al verificar API: {e}")
        return False

def verificar_datos_devolucion():
    """Verificar que hay datos de devolución para probar"""
    print("\n📋 VERIFICANDO DATOS DE DEVOLUCIÓN")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/devoluciones/listar")
        
        if response.status_code == 200:
            data = response.json()
            if 'devoluciones' in data and len(data['devoluciones']) > 0:
                print(f"✅ Encontradas {len(data['devoluciones'])} devoluciones")
                
                # Mostrar todas las devoluciones
                for i, dev in enumerate(data['devoluciones']):
                    print(f"📄 Devolución {i+1}:")
                    print(f"   ID: {dev.get('id')}")
                    print(f"   Estado: {dev.get('estado')}")
                    print(f"   Motivo: {dev.get('motivo')}")
                    print(f"   Técnico: {dev.get('tecnico_nombre', 'N/A')}")
                    print()
                
                return True
            else:
                print("❌ No hay devoluciones en el sistema")
                return False
        else:
            print(f"❌ Error al obtener devoluciones: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verificar_contenido_html():
    """Verificar elementos clave en el HTML"""
    print("\n🔍 VERIFICANDO CONTENIDO HTML")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/logistica/devoluciones_dotacion")
        
        if response.status_code != 200:
            print(f"❌ Error al acceder a la página: {response.status_code}")
            return False
        
        html_content = response.text
        
        # Buscar elementos clave
        elementos_buscar = [
            ('id="modalDetallesDevolucion"', 'Modal de detalles'),
            ('id="botonesTransicion"', 'Contenedor de botones'),
            ('id="modalConfirmarCambio"', 'Modal de confirmación'),
            ('cargarBotonesTransicion', 'Función cargar botones'),
            ('estadosPermitidos', 'Configuración de estados'),
            ('confirmarCambioEstado', 'Función confirmar cambio'),
            ('EN_REVISION', 'Estado EN_REVISION')
        ]
        
        elementos_encontrados = 0
        for buscar, descripcion in elementos_buscar:
            if buscar in html_content:
                print(f"✅ {descripcion}: ENCONTRADO")
                elementos_encontrados += 1
            else:
                print(f"❌ {descripcion}: NO ENCONTRADO")
        
        print(f"\n📊 Elementos encontrados: {elementos_encontrados}/{len(elementos_buscar)}")
        
        return elementos_encontrados >= 5  # Al menos 5 de 7 elementos
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def generar_solucion_directa():
    """Generar una solución directa para el problema"""
    print("\n🔧 SOLUCIÓN DIRECTA")
    print("=" * 50)
    
    print("🎯 PASOS PARA SOLUCIONAR EL PROBLEMA:")
    print()
    print("1. 📱 Abre las herramientas de desarrollador en tu navegador (F12)")
    print("2. 🔍 Ve a la pestaña 'Console'")
    print("3. 📝 Ejecuta este código JavaScript:")
    print()
    
    codigo_js = """
// Código para ejecutar en la consola del navegador
console.log('🔍 Depurando botones de estado...');

// Verificar elementos
const modal = document.getElementById('modalDetallesDevolucion');
const botones = document.getElementById('botonesTransicion');

console.log('Modal:', modal);
console.log('Botones container:', botones);

// Función de prueba para agregar botón manualmente
function agregarBotonPrueba() {
    const container = document.getElementById('botonesTransicion');
    if (container) {
        container.innerHTML = `
            <button class="btn btn-warning me-2 mb-2" 
                    onclick="alert('¡Botón funcionando! Ahora implementaremos el cambio real.')"
                    title="Cambiar a EN_REVISION">
                <i class="fas fa-search me-2"></i>
                Cambiar a EN_REVISION
            </button>
        `;
        console.log('✅ Botón de prueba agregado');
    } else {
        console.error('❌ No se encontró el contenedor');
    }
}

// Ejecutar la función
agregarBotonPrueba();
"""
    
    print(codigo_js)
    print()
    print("4. ✅ Si aparece el botón 'Cambiar a EN_REVISION', el problema es de JavaScript")
    print("5. 🔄 Si no aparece, el problema es del HTML/Modal")
    print()
    print("💡 ALTERNATIVA RÁPIDA:")
    print("Puedes ejecutar directamente: agregarBotonPrueba()")

def main():
    """Función principal"""
    print("🚀 DEPURACIÓN ESPECÍFICA DE BOTONES DE ESTADO")
    print("=" * 60)
    
    resultado1 = verificar_api_cambio_estado()
    resultado2 = verificar_datos_devolucion()
    resultado3 = verificar_contenido_html()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE DEPURACIÓN")
    print("=" * 60)
    
    if all([resultado1, resultado2, resultado3]):
        print("✅ TODOS LOS COMPONENTES ESTÁN PRESENTES")
        print("🔍 El problema parece ser de JavaScript en el navegador")
    else:
        print("❌ SE DETECTARON PROBLEMAS EN LOS COMPONENTES")
    
    # Generar solución directa
    generar_solucion_directa()

if __name__ == "__main__":
    main()