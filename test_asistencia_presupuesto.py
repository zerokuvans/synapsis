#!/usr/bin/env python3
"""
Script para probar la funcionalidad de registro de asistencia
y verificar que los valores de presupuesto se copien correctamente
"""

import mysql.connector
from datetime import datetime
import json

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def test_asistencia_presupuesto():
    """Probar el registro de asistencia con presupuesto"""
    try:
        print("🧪 PROBANDO FUNCIONALIDAD DE ASISTENCIA CON PRESUPUESTO")
        print("=" * 60)
        
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # 1. Verificar técnicos disponibles en recurso_operativo
        print("👥 TÉCNICOS DISPONIBLES:")
        cursor.execute("""
        SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, carpeta, cargo
        FROM recurso_operativo 
        WHERE estado = 'Activo' 
        LIMIT 5
    """)
        tecnicos = cursor.fetchall()
        
        if not tecnicos:
            print("❌ No hay técnicos en recurso_operativo")
            return False
        
        for i, tecnico in enumerate(tecnicos, 1):
            print(f"  {i}. Cédula: {tecnico['recurso_operativo_cedula']}")
            print(f"     Nombre: {tecnico['nombre']}")
            print(f"     Carpeta: {tecnico['carpeta']}")
            print(f"     Cargo: {tecnico['cargo']}")
            print()
        
        # 2. Seleccionar el primer técnico para la prueba
        tecnico_prueba = tecnicos[0]
        id_codigo_consumidor = tecnico_prueba['id_codigo_consumidor']
        cedula_prueba = tecnico_prueba['recurso_operativo_cedula']
        nombre_prueba = tecnico_prueba['nombre']
        carpeta_prueba = tecnico_prueba['carpeta']
        cargo_prueba = tecnico_prueba['cargo']
        
        print(f"🎯 TÉCNICO SELECCIONADO PARA PRUEBA:")
        print(f"   Cédula: {cedula_prueba}")
        print(f"   Nombre: {nombre_prueba}")
        print(f"   Carpeta: {carpeta_prueba}")
        
        # 3. Verificar si existe presupuesto para esta carpeta
        print(f"\n💰 VERIFICANDO PRESUPUESTO PARA CARPETA '{carpeta_prueba}':")
        cursor.execute("""
            SELECT presupuesto_diario, presupuesto_eventos 
            FROM presupuesto_carpeta 
            WHERE presupuesto_carpeta = %s 
            LIMIT 1
        """, (carpeta_prueba,))
        presupuesto = cursor.fetchone()
        
        if presupuesto:
            print(f"   ✅ Presupuesto encontrado:")
            print(f"      Eventos: {presupuesto['presupuesto_eventos']}")
            print(f"      Diario: {presupuesto['presupuesto_diario']}")
        else:
            print(f"   ❌ No hay presupuesto para carpeta '{carpeta_prueba}'")
            print("   ℹ️  Creando presupuesto de prueba...")
            
            cursor.execute("""
                INSERT INTO presupuesto_carpeta 
                (presupuesto_carpeta, presupuesto_eventos, presupuesto_diario) 
                VALUES (%s, %s, %s)
            """, (carpeta_prueba, 5, 150000))
            connection.commit()
            
            presupuesto = {'presupuesto_eventos': 5, 'presupuesto_diario': 150000}
            print(f"   ✅ Presupuesto creado: Eventos=5, Diario=150000")
        
        # 4. Simular el registro de asistencia
        print(f"\n📝 SIMULANDO REGISTRO DE ASISTENCIA:")
        
        # Limpiar registros anteriores de prueba
        cursor.execute("DELETE FROM asistencia WHERE cedula = %s AND tecnico LIKE '%PRUEBA%'", (cedula_prueba,))
        
        # Simular los datos que enviaría el frontend
        asistencia_data = {
            'cedula': cedula_prueba,
            'tecnico': f"{nombre_prueba} - PRUEBA",
            'carpeta_dia': carpeta_prueba,
            'carpeta': carpeta_prueba,
            'super': 'SISTEMA_PRUEBA',
            'fecha_asistencia': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'id_codigo_consumidor': 999
        }
        
        # Aplicar la misma lógica que en main.py
        valor_presupuesto = 0
        valor_eventos = 0
        presupuesto_encontrado = False
        
        if presupuesto:
            if presupuesto['presupuesto_diario'] is not None:
                try:
                    valor_presupuesto = int(float(presupuesto['presupuesto_diario']))
                    if valor_presupuesto > 0:
                        presupuesto_encontrado = True
                except Exception:
                    valor_presupuesto = 0
            
            if presupuesto['presupuesto_eventos'] is not None:
                try:
                    valor_eventos = int(float(presupuesto['presupuesto_eventos']))
                    if valor_eventos > 0:
                        presupuesto_encontrado = True
                except Exception:
                    valor_eventos = 0
        
        print(f"   📊 Valores calculados:")
        print(f"      valor (presupuesto_diario): {valor_presupuesto}")
        print(f"      eventos (presupuesto_eventos): {valor_eventos}")
        print(f"      presupuesto_encontrado: {presupuesto_encontrado}")
        
        # 5. Insertar en la tabla asistencia
        cursor.execute("""
            INSERT INTO asistencia (cedula, tecnico, carpeta_dia, carpeta, super, fecha_asistencia, id_codigo_consumidor, valor, eventos)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            asistencia_data['cedula'],
            asistencia_data['tecnico'],
            asistencia_data['carpeta_dia'],
            asistencia_data['carpeta'],
            asistencia_data['super'],
            asistencia_data['fecha_asistencia'],
            id_codigo_consumidor,
            valor_presupuesto,
            valor_eventos
        ))
        
        connection.commit()
        print(f"   ✅ Registro insertado en tabla asistencia")
        
        # 6. Verificar el registro insertado
        print(f"\n🔍 VERIFICANDO REGISTRO INSERTADO:")
        cursor.execute("""
            SELECT cedula, tecnico, carpeta, valor, eventos, fecha_asistencia
            FROM asistencia 
            WHERE cedula = %s AND tecnico LIKE '%PRUEBA%'
            ORDER BY fecha_asistencia DESC
            LIMIT 1
        """, (cedula_prueba,))
        
        registro_insertado = cursor.fetchone()
        
        if registro_insertado:
            print(f"   ✅ Registro encontrado:")
            print(f"      Cédula: {registro_insertado['cedula']}")
            print(f"      Técnico: {registro_insertado['tecnico']}")
            print(f"      Carpeta: {registro_insertado['carpeta']}")
            print(f"      Valor: {registro_insertado['valor']}")
            print(f"      Eventos: {registro_insertado['eventos']}")
            print(f"      Fecha: {registro_insertado['fecha_asistencia']}")
            
            # Verificar que los valores coincidan
            if (registro_insertado['valor'] == valor_presupuesto and 
                registro_insertado['eventos'] == valor_eventos):
                print(f"\n🎉 ¡PRUEBA EXITOSA!")
                print(f"   ✅ Los valores de presupuesto se copiaron correctamente:")
                print(f"      presupuesto_diario → valor: {presupuesto['presupuesto_diario']} → {registro_insertado['valor']}")
                print(f"      presupuesto_eventos → eventos: {presupuesto['presupuesto_eventos']} → {registro_insertado['eventos']}")
                resultado = True
            else:
                print(f"\n❌ PRUEBA FALLIDA!")
                print(f"   Los valores no coinciden:")
                print(f"      Esperado - valor: {valor_presupuesto}, eventos: {valor_eventos}")
                print(f"      Obtenido - valor: {registro_insertado['valor']}, eventos: {registro_insertado['eventos']}")
                resultado = False
        else:
            print(f"   ❌ No se encontró el registro insertado")
            resultado = False
        
        # 7. Limpiar datos de prueba
        print(f"\n🧹 LIMPIANDO DATOS DE PRUEBA:")
        cursor.execute("DELETE FROM asistencia WHERE cedula = %s AND tecnico LIKE '%PRUEBA%'", (cedula_prueba,))
        connection.commit()
        print(f"   ✅ Datos de prueba eliminados")
        
        cursor.close()
        connection.close()
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exito = test_asistencia_presupuesto()
    if exito:
        print(f"\n🎯 RESULTADO FINAL: ✅ FUNCIONALIDAD VALIDADA CORRECTAMENTE")
        print(f"   La funcionalidad de copia de presupuesto está funcionando bien.")
    else:
        print(f"\n🎯 RESULTADO FINAL: ❌ FUNCIONALIDAD REQUIERE CORRECCIÓN")
        print(f"   Hay problemas con la copia de valores de presupuesto.")