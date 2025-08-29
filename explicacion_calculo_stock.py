#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXPLICACIÓN DEL CÁLCULO DE STOCK Y LÍMITES EN EL SISTEMA FERRETERO

Este script educativo explica paso a paso cómo funciona el sistema de cálculo
de stock y límites para la asignación de materiales a técnicos ferreteros.

Autor: Sistema de Diagnóstico
Fecha: 2025
"""

import os
import mysql.connector
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class ExplicacionCalculoStock:
    def __init__(self):
        self.conexion = None
        self.conectar_bd()
    
    def conectar_bd(self):
        """Conectar a la base de datos MySQL"""
        try:
            self.conexion = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                port=int(os.getenv('MYSQL_PORT', 3306)),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD', ''),
                database=os.getenv('MYSQL_DB', 'synapsis')
            )
            print("✅ Conexión a MySQL establecida correctamente")
        except Exception as e:
            print(f"❌ Error conectando a MySQL: {e}")
            self.conexion = None
    
    def explicar_tablas_involucradas(self):
        """
        PASO 1: EXPLICAR LAS TABLAS INVOLUCRADAS
        
        El sistema de stock involucra principalmente 3 tablas:
        """
        print("\n" + "="*80)
        print("PASO 1: TABLAS INVOLUCRADAS EN EL CÁLCULO DE STOCK")
        print("="*80)
        
        print("\n📋 1. TABLA 'ferretero' - Registro de asignaciones")
        print("   - Almacena cada asignación de material a un técnico")
        print("   - Campos clave: cedula_tecnico, codigo_material, cantidad, fecha_asignacion")
        print("   - Cada registro representa una entrega de material")
        
        print("\n📋 2. TABLA 'recurso_operativo' - Catálogo de materiales")
        print("   - Define los materiales disponibles y sus límites")
        print("   - Campos clave: codigo, descripcion, limite_area_*")
        print("   - Los límites varían según el área de trabajo del técnico")
        
        print("\n📋 3. TABLA 'stock_general' - Inventario disponible")
        print("   - Controla la cantidad disponible de cada material")
        print("   - Campos clave: codigo_material, cantidad_disponible")
        print("   - Se actualiza automáticamente con cada asignación")
        
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                
                # Mostrar estructura de tabla ferretero
                print("\n🔍 Estructura de tabla 'ferretero':")
                cursor.execute("DESCRIBE ferretero")
                for campo in cursor.fetchall():
                    print(f"   - {campo[0]}: {campo[1]}")
                
                # Mostrar estructura de tabla recurso_operativo
                print("\n🔍 Estructura de tabla 'recurso_operativo':")
                cursor.execute("DESCRIBE recurso_operativo")
                for campo in cursor.fetchall():
                    if 'limite' in campo[0] or campo[0] in ['codigo', 'descripcion']:
                        print(f"   - {campo[0]}: {campo[1]}")
                
                cursor.close()
            except Exception as e:
                print(f"❌ Error consultando estructura: {e}")
    
    def explicar_limites_por_area(self):
        """
        PASO 2: EXPLICAR CÓMO SE DETERMINAN LOS LÍMITES POR ÁREA
        
        Los límites dependen del área de trabajo del técnico:
        - Área 1: limite_area_1
        - Área 2: limite_area_2  
        - Área 3: limite_area_3
        - Área 4: limite_area_4
        """
        print("\n" + "="*80)
        print("PASO 2: DETERMINACIÓN DE LÍMITES POR ÁREA DE TRABAJO")
        print("="*80)
        
        print("\n🎯 LÓGICA DE LÍMITES:")
        print("   El sistema asigna límites diferentes según el área de trabajo del técnico")
        print("   Cada material tiene 4 límites configurados (uno por área)")
        
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                
                # Mostrar ejemplos de límites por material
                print("\n📊 EJEMPLOS DE LÍMITES POR MATERIAL:")
                query = """
                SELECT codigo, descripcion, 
                       limite_area_1, limite_area_2, limite_area_3, limite_area_4
                FROM recurso_operativo 
                WHERE limite_area_1 IS NOT NULL 
                LIMIT 5
                """
                cursor.execute(query)
                
                print(f"{'Código':<10} {'Descripción':<30} {'Área 1':<8} {'Área 2':<8} {'Área 3':<8} {'Área 4':<8}")
                print("-" * 80)
                
                for row in cursor.fetchall():
                    codigo, desc, l1, l2, l3, l4 = row
                    desc_corta = (desc[:27] + '...') if len(desc) > 30 else desc
                    print(f"{codigo:<10} {desc_corta:<30} {l1 or 0:<8} {l2 or 0:<8} {l3 or 0:<8} {l4 or 0:<8}")
                
                print("\n💡 INTERPRETACIÓN:")
                print("   - Si un técnico trabaja en Área 1, se aplica limite_area_1")
                print("   - Si trabaja en Área 2, se aplica limite_area_2, etc.")
                print("   - El límite define cuántas unidades puede recibir en 15 días")
                
                cursor.close()
            except Exception as e:
                print(f"❌ Error consultando límites: {e}")
    
    def explicar_calculo_consumo_previo(self):
        """
        PASO 3: EXPLICAR EL CÁLCULO DE CONSUMO PREVIO
        
        El sistema calcula cuánto material ha recibido el técnico
        en los últimos 15 días para el mismo material.
        """
        print("\n" + "="*80)
        print("PASO 3: CÁLCULO DE CONSUMO PREVIO (ÚLTIMOS 15 DÍAS)")
        print("="*80)
        
        print("\n📅 LÓGICA DE CONSUMO PREVIO:")
        print("   1. Se calcula la fecha límite: fecha_actual - 15 días")
        print("   2. Se buscan todas las asignaciones del técnico para ese material")
        print("   3. Se suman las cantidades asignadas en ese período")
        print("   4. Esta suma es el 'consumo previo'")
        
        fecha_actual = datetime.now()
        fecha_limite = fecha_actual - timedelta(days=15)
        
        print(f"\n🕒 EJEMPLO DE CÁLCULO:")
        print(f"   Fecha actual: {fecha_actual.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Fecha límite: {fecha_limite.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Período de análisis: {fecha_limite.strftime('%Y-%m-%d')} a {fecha_actual.strftime('%Y-%m-%d')}")
        
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                
                # Mostrar ejemplo real de consumo previo
                print("\n📊 EJEMPLO REAL DE CONSUMO PREVIO:")
                query = """
                SELECT cedula_tecnico, codigo_material, 
                       SUM(cantidad) as consumo_total,
                       COUNT(*) as num_asignaciones,
                       MIN(fecha_asignacion) as primera_asignacion,
                       MAX(fecha_asignacion) as ultima_asignacion
                FROM ferretero 
                WHERE fecha_asignacion >= DATE_SUB(NOW(), INTERVAL 15 DAY)
                GROUP BY cedula_tecnico, codigo_material
                HAVING consumo_total > 0
                ORDER BY consumo_total DESC
                LIMIT 5
                """
                cursor.execute(query)
                
                print(f"{'Técnico':<12} {'Material':<12} {'Consumo':<8} {'Asign.':<6} {'Primera':<12} {'Última':<12}")
                print("-" * 70)
                
                for row in cursor.fetchall():
                    tecnico, material, consumo, asign, primera, ultima = row
                    print(f"{tecnico:<12} {material:<12} {consumo:<8} {asign:<6} {primera.strftime('%Y-%m-%d'):<12} {ultima.strftime('%Y-%m-%d'):<12}")
                
                cursor.close()
            except Exception as e:
                print(f"❌ Error consultando consumo previo: {e}")
    
    def explicar_validacion_limites(self):
        """
        PASO 4: EXPLICAR LA VALIDACIÓN DE LÍMITES
        
        El sistema valida si la nueva asignación excedería el límite permitido.
        """
        print("\n" + "="*80)
        print("PASO 4: VALIDACIÓN DE LÍMITES")
        print("="*80)
        
        print("\n🔍 PROCESO DE VALIDACIÓN:")
        print("   1. Obtener el límite del material para el área del técnico")
        print("   2. Calcular el consumo previo (últimos 15 días)")
        print("   3. Sumar la cantidad solicitada al consumo previo")
        print("   4. Comparar el total con el límite permitido")
        
        print("\n📐 FÓRMULA DE VALIDACIÓN:")
        print("   (consumo_previo + cantidad_solicitada) <= limite_area")
        
        print("\n✅ CASOS DE VALIDACIÓN:")
        print("   - SI el total <= límite: APROBADO")
        print("   - SI el total > límite: RECHAZADO")
        
        # Ejemplo práctico
        print("\n💡 EJEMPLO PRÁCTICO:")
        print("   Técnico: 12345678 (Área 1)")
        print("   Material: CINTA_AISLA (límite_area_1 = 3)")
        print("   Consumo previo: 2 unidades")
        print("   Cantidad solicitada: 2 unidades")
        print("   Validación: (2 + 2) = 4 > 3 → RECHAZADO")
        print("   ")
        print("   Si solicitara 1 unidad:")
        print("   Validación: (2 + 1) = 3 <= 3 → APROBADO")
    
    def explicar_actualizacion_stock(self):
        """
        PASO 5: EXPLICAR LA ACTUALIZACIÓN DE STOCK
        
        Cuando se aprueba una asignación, se actualiza el stock disponible.
        """
        print("\n" + "="*80)
        print("PASO 5: ACTUALIZACIÓN DE STOCK")
        print("="*80)
        
        print("\n📦 PROCESO DE ACTUALIZACIÓN:")
        print("   1. Se registra la asignación en tabla 'ferretero'")
        print("   2. Se activa el trigger 'actualizar_stock_asignacion'")
        print("   3. El trigger reduce el stock en tabla 'stock_general'")
        print("   4. Se verifica que el stock no quede negativo")
        
        print("\n🔧 TRIGGER 'actualizar_stock_asignacion':")
        print("   - Se ejecuta AFTER INSERT ON ferretero")
        print("   - Reduce stock_general.cantidad_disponible")
        print("   - Fórmula: cantidad_disponible = cantidad_disponible - NEW.cantidad")
        
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                
                # Verificar si existe el trigger
                print("\n🔍 VERIFICACIÓN DEL TRIGGER:")
                cursor.execute("""
                    SELECT TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE 
                    FROM information_schema.TRIGGERS 
                    WHERE TRIGGER_SCHEMA = DATABASE() 
                    AND TRIGGER_NAME = 'actualizar_stock_asignacion'
                """)
                
                trigger = cursor.fetchone()
                if trigger:
                    print(f"   ✅ Trigger encontrado: {trigger[0]}")
                    print(f"   📋 Evento: {trigger[1]} en tabla {trigger[2]}")
                else:
                    print("   ❌ TRIGGER NO ENCONTRADO - PROBLEMA CRÍTICO")
                    print("   🚨 Sin este trigger, el stock no se actualiza automáticamente")
                
                # Mostrar estado actual del stock
                print("\n📊 ESTADO ACTUAL DEL STOCK (primeros 5):")
                cursor.execute("""
                    SELECT codigo_material, cantidad_disponible 
                    FROM stock_general 
                    WHERE cantidad_disponible > 0 
                    ORDER BY cantidad_disponible DESC 
                    LIMIT 5
                """)
                
                print(f"{'Material':<15} {'Stock Disponible':<15}")
                print("-" * 30)
                
                for row in cursor.fetchall():
                    material, stock = row
                    print(f"{material:<15} {stock:<15}")
                
                cursor.close()
            except Exception as e:
                print(f"❌ Error verificando trigger/stock: {e}")
    
    def mostrar_flujo_completo(self):
        """
        PASO 6: MOSTRAR EL FLUJO COMPLETO CON EJEMPLO REAL
        
        Simular una asignación completa paso a paso.
        """
        print("\n" + "="*80)
        print("PASO 6: FLUJO COMPLETO DE ASIGNACIÓN")
        print("="*80)
        
        print("\n🔄 FLUJO PASO A PASO:")
        
        # Datos de ejemplo
        cedula_tecnico = "12345678"
        codigo_material = "CINTA_AISLA"
        cantidad_solicitada = 1
        area_trabajo = 1
        
        print(f"\n📝 DATOS DE LA SOLICITUD:")
        print(f"   Técnico: {cedula_tecnico}")
        print(f"   Material: {codigo_material}")
        print(f"   Cantidad: {cantidad_solicitada}")
        print(f"   Área de trabajo: {area_trabajo}")
        
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                
                # Paso 1: Obtener límite del material
                print(f"\n🎯 PASO 1: Obtener límite para área {area_trabajo}")
                cursor.execute(f"""
                    SELECT limite_area_{area_trabajo}, descripcion 
                    FROM recurso_operativo 
                    WHERE codigo = %s
                """, (codigo_material,))
                
                resultado = cursor.fetchone()
                if resultado:
                    limite, descripcion = resultado
                    print(f"   Material: {descripcion}")
                    print(f"   Límite para área {area_trabajo}: {limite} unidades")
                else:
                    print(f"   ❌ Material {codigo_material} no encontrado")
                    return
                
                # Paso 2: Calcular consumo previo
                print(f"\n📅 PASO 2: Calcular consumo previo (últimos 15 días)")
                cursor.execute("""
                    SELECT COALESCE(SUM(cantidad), 0) as consumo_previo
                    FROM ferretero 
                    WHERE cedula_tecnico = %s 
                    AND codigo_material = %s 
                    AND fecha_asignacion >= DATE_SUB(NOW(), INTERVAL 15 DAY)
                """, (cedula_tecnico, codigo_material))
                
                consumo_previo = cursor.fetchone()[0]
                print(f"   Consumo previo: {consumo_previo} unidades")
                
                # Paso 3: Validar límite
                print(f"\n🔍 PASO 3: Validar límite")
                total_consumo = consumo_previo + cantidad_solicitada
                print(f"   Cálculo: {consumo_previo} + {cantidad_solicitada} = {total_consumo}")
                print(f"   Límite: {limite}")
                
                if total_consumo <= limite:
                    print(f"   ✅ APROBADO: {total_consumo} <= {limite}")
                    
                    # Paso 4: Verificar stock disponible
                    print(f"\n📦 PASO 4: Verificar stock disponible")
                    cursor.execute("""
                        SELECT cantidad_disponible 
                        FROM stock_general 
                        WHERE codigo_material = %s
                    """, (codigo_material,))
                    
                    stock_resultado = cursor.fetchone()
                    if stock_resultado:
                        stock_disponible = stock_resultado[0]
                        print(f"   Stock disponible: {stock_disponible} unidades")
                        
                        if stock_disponible >= cantidad_solicitada:
                            print(f"   ✅ Stock suficiente: {stock_disponible} >= {cantidad_solicitada}")
                            print(f"\n🎉 ASIGNACIÓN APROBADA")
                            print(f"   - Se registraría en tabla 'ferretero'")
                            print(f"   - El trigger reduciría el stock a {stock_disponible - cantidad_solicitada}")
                        else:
                            print(f"   ❌ Stock insuficiente: {stock_disponible} < {cantidad_solicitada}")
                    else:
                        print(f"   ❌ Material no encontrado en stock")
                else:
                    print(f"   ❌ RECHAZADO: {total_consumo} > {limite}")
                    print(f"   💡 El técnico ya alcanzó su límite de {limite} unidades")
                
                cursor.close()
            except Exception as e:
                print(f"❌ Error en simulación: {e}")
    
    def mostrar_dependencias_criticas(self):
        """
        PASO 7: EXPLICAR DEPENDENCIAS CRÍTICAS DEL SISTEMA
        
        Identificar qué componentes son esenciales para el funcionamiento.
        """
        print("\n" + "="*80)
        print("PASO 7: DEPENDENCIAS CRÍTICAS DEL SISTEMA")
        print("="*80)
        
        print("\n🔧 COMPONENTES ESENCIALES:")
        
        print("\n1️⃣ TRIGGER 'actualizar_stock_asignacion':")
        print("   - CRÍTICO: Sin él, el stock no se actualiza")
        print("   - Ubicación: Base de datos MySQL")
        print("   - Función: Reduce stock automáticamente")
        
        print("\n2️⃣ CONFIGURACIÓN DE ZONA HORARIA:")
        print("   - IMPORTANTE: Afecta cálculos de fechas")
        print("   - Python debe coincidir con MySQL")
        print("   - Recomendación: Usar UTC")
        
        print("\n3️⃣ VARIABLES DE ENTORNO:")
        print("   - MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD")
        print("   - MYSQL_DB, MYSQL_PORT")
        print("   - Deben estar correctamente configuradas")
        
        print("\n4️⃣ PERMISOS DE BASE DE DATOS:")
        print("   - SELECT, INSERT en tabla 'ferretero'")
        print("   - SELECT, UPDATE en tabla 'stock_general'")
        print("   - SELECT en tabla 'recurso_operativo'")
        
        print("\n5️⃣ INTEGRIDAD DE DATOS:")
        print("   - Límites configurados en 'recurso_operativo'")
        print("   - Stock inicial en 'stock_general'")
        print("   - Áreas de trabajo válidas (1-4)")
        
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                
                print("\n🔍 VERIFICACIÓN DE DEPENDENCIAS:")
                
                # Verificar trigger
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.TRIGGERS 
                    WHERE TRIGGER_SCHEMA = DATABASE() 
                    AND TRIGGER_NAME = 'actualizar_stock_asignacion'
                """)
                trigger_existe = cursor.fetchone()[0] > 0
                print(f"   Trigger actualizar_stock_asignacion: {'✅ OK' if trigger_existe else '❌ FALTA'}")
                
                # Verificar tablas
                tablas = ['ferretero', 'recurso_operativo', 'stock_general']
                for tabla in tablas:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    count = cursor.fetchone()[0]
                    print(f"   Tabla {tabla}: {'✅ OK' if count > 0 else '⚠️ VACÍA'} ({count} registros)")
                
                cursor.close()
            except Exception as e:
                print(f"❌ Error verificando dependencias: {e}")
    
    def generar_recomendaciones(self):
        """
        PASO 8: GENERAR RECOMENDACIONES PARA OPTIMIZACIÓN
        
        Sugerir mejoras y verificaciones para el sistema.
        """
        print("\n" + "="*80)
        print("PASO 8: RECOMENDACIONES PARA OPTIMIZACIÓN")
        print("="*80)
        
        print("\n💡 RECOMENDACIONES INMEDIATAS:")
        
        print("\n🔧 1. VERIFICAR TRIGGER:")
        print("   - Confirmar que 'actualizar_stock_asignacion' existe")
        print("   - Verificar que se ejecuta correctamente")
        print("   - Probar con una asignación de prueba")
        
        print("\n🕒 2. SINCRONIZAR ZONA HORARIA:")
        print("   - Configurar Python y MySQL en UTC")
        print("   - Verificar que NOW() y datetime.now() coinciden")
        print("   - Usar TIMESTAMP en lugar de DATETIME")
        
        print("\n📊 3. MONITOREO Y LOGGING:")
        print("   - Implementar logging detallado en registrar_ferretero()")
        print("   - Registrar cada paso del cálculo")
        print("   - Alertas cuando se rechacen asignaciones")
        
        print("\n🔒 4. VALIDACIONES ADICIONALES:")
        print("   - Verificar que el técnico existe")
        print("   - Validar que el material está activo")
        print("   - Confirmar que el área de trabajo es válida (1-4)")
        
        print("\n⚡ 5. OPTIMIZACIÓN DE RENDIMIENTO:")
        print("   - Índices en (cedula_tecnico, codigo_material, fecha_asignacion)")
        print("   - Caché de límites por área")
        print("   - Consultas preparadas para cálculos frecuentes")
        
        print("\n🔄 6. MANTENIMIENTO:")
        print("   - Limpieza periódica de registros antiguos")
        print("   - Backup regular de configuraciones")
        print("   - Auditoría de cambios en límites")
    
    def ejecutar_explicacion_completa(self):
        """
        Ejecutar toda la explicación paso a paso
        """
        print("🎓 EXPLICACIÓN COMPLETA DEL CÁLCULO DE STOCK Y LÍMITES")
        print("📚 Sistema Ferretero - Gestión de Materiales")
        print("⏰ Fecha:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        try:
            self.explicar_tablas_involucradas()
            self.explicar_limites_por_area()
            self.explicar_calculo_consumo_previo()
            self.explicar_validacion_limites()
            self.explicar_actualizacion_stock()
            self.mostrar_flujo_completo()
            self.mostrar_dependencias_criticas()
            self.generar_recomendaciones()
            
            print("\n" + "="*80)
            print("🎉 EXPLICACIÓN COMPLETADA EXITOSAMENTE")
            print("="*80)
            print("\n📋 RESUMEN:")
            print("   ✅ Tablas y estructura explicadas")
            print("   ✅ Lógica de límites por área")
            print("   ✅ Cálculo de consumo previo")
            print("   ✅ Proceso de validación")
            print("   ✅ Actualización de stock")
            print("   ✅ Flujo completo simulado")
            print("   ✅ Dependencias críticas identificadas")
            print("   ✅ Recomendaciones generadas")
            
        except Exception as e:
            print(f"\n❌ Error durante la explicación: {e}")
        finally:
            if self.conexion:
                self.conexion.close()
                print("\n🔌 Conexión a base de datos cerrada")

def main():
    """
    Función principal para ejecutar la explicación
    """
    print("Iniciando explicación del cálculo de stock...")
    explicacion = ExplicacionCalculoStock()
    explicacion.ejecutar_explicacion_completa()

if __name__ == "__main__":
    main()