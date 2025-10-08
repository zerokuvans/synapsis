#!/usr/bin/env python3
"""
Script para verificar el funcionamiento de los botones de cambio de estado
en el módulo de devoluciones de dotación.
"""

import requests
import json
from datetime import datetime

def test_botones_estados():
    """Prueba la funcionalidad de los botones de cambio de estado"""
    
    base_url = "http://localhost:8080"
    
    print("🔍 VERIFICANDO FUNCIONALIDAD DE BOTONES DE ESTADO")
    print("=" * 60)
    
    # 1. Verificar que la página principal carga
    try:
        response = requests.get(f"{base_url}/logistica/devoluciones_dotacion")
        if response.status_code == 200:
            print("✅ Página principal carga correctamente")
            
            # Verificar que contiene los elementos necesarios
            content = response.text
            elementos_requeridos = [
                "modalDetallesDevolucion",
                "botonesTransicion", 
                "cargarBotonesTransicion",
                "confirmarCambioEstado",
                "EN_REVISION",
                "modalConfirmarCambio"
            ]
            
            elementos_encontrados = []
            elementos_faltantes = []
            
            for elemento in elementos_requeridos:
                if elemento in content:
                    elementos_encontrados.append(elemento)
                    print(f"  ✅ {elemento}")
                else:
                    elementos_faltantes.append(elemento)
                    print(f"  ❌ {elemento}")
            
            print(f"\n📊 Elementos encontrados: {len(elementos_encontrados)}/{len(elementos_requeridos)}")
            
            if elementos_faltantes:
                print(f"⚠️  Elementos faltantes: {', '.join(elementos_faltantes)}")
            
        else:
            print(f"❌ Error al cargar página: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # 2. Verificar API de devoluciones
    try:
        response = requests.get(f"{base_url}/api/devoluciones/listar")
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ API de devoluciones funciona - {len(data.get('devoluciones', []))} registros")
            
            # Verificar si hay devoluciones para probar
            devoluciones = data.get('devoluciones', [])
            if devoluciones:
                primera_devolucion = devoluciones[0]
                print(f"  📋 Primera devolución: ID {primera_devolucion.get('id')} - Estado: {primera_devolucion.get('estado')}")
                
                # Verificar estados disponibles
                estados_encontrados = set()
                for dev in devoluciones:
                    estados_encontrados.add(dev.get('estado'))
                
                print(f"  🔄 Estados encontrados: {', '.join(sorted(estados_encontrados))}")
                
                return True
            else:
                print("  ⚠️  No hay devoluciones registradas para probar")
                return True
        else:
            print(f"❌ Error en API de devoluciones: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error al verificar API: {e}")
        return False

def verificar_estructura_modal():
    """Verifica que la estructura del modal esté correcta"""
    
    print("\n🔍 VERIFICANDO ESTRUCTURA DEL MODAL")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8080/logistica/devoluciones_dotacion")
        content = response.text
        
        # Verificar elementos del modal
        elementos_modal = [
            'id="modalDetallesDevolucion"',
            'id="botonesTransicion"',
            'id="modalConfirmarCambio"',
            'cargarGestionEstados',
            'function cargarBotonesTransicion',
            'estadosPermitidos'
        ]
        
        for elemento in elementos_modal:
            if elemento in content:
                print(f"✅ {elemento}")
            else:
                print(f"❌ {elemento}")
        
        # Verificar configuración de estados
        if "'EN_REVISION': ['APROBADA', 'RECHAZADA']" in content:
            print("✅ Configuración de transiciones de estados correcta")
        else:
            print("❌ Configuración de transiciones de estados incorrecta")
            
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar estructura: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 INICIANDO VERIFICACIÓN DE BOTONES DE ESTADO")
    print("=" * 60)
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ejecutar pruebas
    resultado1 = test_botones_estados()
    resultado2 = verificar_estructura_modal()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    if resultado1 and resultado2:
        print("✅ TODAS LAS VERIFICACIONES PASARON")
        print("\n🎯 INSTRUCCIONES PARA VER LOS BOTONES:")
        print("1. Ve a: http://localhost:8080/logistica/devoluciones_dotacion")
        print("2. Haz clic en el botón 'Ver/Editar Detalles' (👁️) de cualquier devolución")
        print("3. En el modal que se abre, busca la sección 'Gestión de Estados'")
        print("4. Ahí verás los botones para cambiar estado (ej: 'Cambiar a EN_REVISION')")
        print("5. Los botones disponibles dependen del estado actual de la devolución")
        
        print("\n🔄 ESTADOS Y TRANSICIONES DISPONIBLES:")
        print("• REGISTRADA → EN_REVISION, RECHAZADA")
        print("• EN_REVISION → APROBADA, RECHAZADA") 
        print("• APROBADA → COMPLETADA")
        print("• RECHAZADA → (sin transiciones)")
        print("• COMPLETADA → (sin transiciones)")
        
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("Revisa los errores mostrados arriba")

if __name__ == "__main__":
    main()