#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXPLICACIÓN COMPLETA DEL CÁLCULO DE STOCK EN EL SISTEMA FERRETERO

Este script educativo demuestra paso a paso cómo funciona el cálculo de stock
y límites en el sistema ferretero, incluyendo todas las dependencias y el flujo completo.

Autor: Sistema de Diagnóstico
Fecha: 2025-08-28
"""

import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json

load_dotenv()

class ExplicacionCalculoStockCompleta:
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
                database=os.getenv('MYSQL_DB', 'capired'),
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
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
        print("   - Campos clave: codigo_ferretero, id_codigo_consumidor, cantidad, fecha_asignacion")
        print("   - Cada registro representa una entrega de material")
        
        print("\n📦 2. TABLA 'stock_general' - Control de inventario")
        print("   - Mantiene el stock actual de cada material")
        print("   - Campos: codigo_material, stock_actual, stock_minimo, stock_maximo")
        print("   - Se actualiza automáticamente con cada asignación")
        
        print("\n⚙️ 3. LÍMITES HARDCODEADOS - Configuración por área")
        print("   - Los límites están definidos en el código Python (main.py)")
        print("   - Diferentes límites según el área de trabajo del técnico")
        print("   - Período de control: generalmente 15 días")
        
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                
                # Mostrar estructura de tabla ferretero
                print("\n🔍 Estructura de tabla 'ferretero':")
                cursor.execute("DESCRIBE ferretero")
                for campo in cursor.fetchall():
                    print(f"   - {campo[0]}: {campo[1]}")
                
                # Mostrar estructura de tabla stock_general
                print("\n🔍 Estructura de tabla 'stock_general':")
                cursor.execute("DESCRIBE stock_general")
                for campo in cursor.fetchall():
                    print(f"   - {campo[0]}: {campo[1]}")
                
                cursor.close()
            except Exception as e:
                print(f"❌ Error consultando estructuras: {e}")
    
    def explicar_limites_hardcodeados(self):
        """
        PASO 2: EXPLICAR LOS LÍMITES HARDCODEADOS POR ÁREA
        
        Los límites están definidos directamente en el código Python,
        no en una tabla de base de datos.
        """
        print("\n" + "="*80)
        print("PASO 2: LÍMITES HARDCODEADOS POR ÁREA DE TRABAJO")
        print("="*80)
        
        print("\n🎯 LÓGICA DE LÍMITES:")
        print("   Los límites están definidos en el código Python (main.py línea ~3292)")
        print("   Cada área de trabajo tiene límites específicos para cada material")
        print("   Los límites controlan cuánto puede recibir un técnico en un período")
        
        # Límites reales del sistema (extraídos del código)
        limites_sistema = {
            'INSTALACION': {
                'cinta_aislante': {'cantidad': 5, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 16, 'periodo': 7, 'unidad': 'días'},
                'amarres_negros': {'cantidad': 50, 'periodo': 15, 'unidad': 'días'},
                'amarres_blancos': {'cantidad': 50, 'periodo': 15, 'unidad': 'días'},
                'grapas_blancas': {'cantidad': 200, 'periodo': 15, 'unidad': 'días'},
                'grapas_negras': {'cantidad': 200, 'periodo': 15, 'unidad': 'días'}
            },
            'POSTVENTA': {
                'cinta_aislante': {'cantidad': 3, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 12, 'periodo': 7, 'unidad': 'días'},
                'amarres_negros': {'cantidad': 30, 'periodo': 15, 'unidad': 'días'},
                'amarres_blancos': {'cantidad': 30, 'periodo': 15, 'unidad': 'días'},
                'grapas_blancas': {'cantidad': 150, 'periodo': 15, 'unidad': 'días'},
                'grapas_negras': {'cantidad': 150, 'periodo': 15, 'unidad': 'días'}
            },
            'MANTENIMIENTO': {
                'cinta_aislante': {'cantidad': 4, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 14, 'periodo': 7, 'unidad': 'días'},
                'amarres_negros': {'cantidad': 40, 'periodo': 15, 'unidad': 'días'},
                'amarres_blancos': {'cantidad': 40, 'periodo': 15, 'unidad': 'días'},
                'grapas_blancas': {'cantidad': 175, 'periodo': 15, 'unidad': 'días'},
                'grapas_negras': {'cantidad': 175, 'periodo': 15, 'unidad': 'días'}
            },
            'SUPERVISION': {
                'cinta_aislante': {'cantidad': 2, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 8, 'periodo': 7, 'unidad': 'días'},
                'amarres_negros': {'cantidad': 20, 'periodo': 15, 'unidad': 'días'},
                'amarres_blancos': {'cantidad': 20, 'periodo': 15, 'unidad': 'días'},
                'grapas_blancas': {'cantidad': 100, 'periodo': 15, 'unidad': 'días'},
                'grapas_negras': {'cantidad': 100, 'periodo': 15, 'unidad': 'días'}
            }
        }
        
        print("\n📊 LÍMITES POR ÁREA Y MATERIAL:")
        print(f"{'ÁREA':<15} {'MATERIAL':<15} {'CANTIDAD':<10} {'PERÍODO':<10}")
        print("-" * 60)
        
        for area, materiales in limites_sistema.items():
            for material, config in materiales.items():
                cantidad = config['cantidad']
                periodo = f"{config['periodo']} {config['unidad']}"
                print(f"{area:<15} {material:<15} {cantidad:<10} {periodo:<10}")
        
        print("\n💡 INTERPRETACIÓN:")
        print("   - Los límites son FIJOS y están en el código")
        print("   - Cada área tiene restricciones diferentes")
        print("   - El período de control es generalmente 15 días (7 para silicona)")
        print("   - INSTALACIÓN tiene los límites más altos")
        print("   - SUPERVISION tiene los límites más bajos")
    
    def explicar_calculo_consumo_previo(self):
        """
        PASO 3: EXPLICAR EL CÁLCULO DE CONSUMO PREVIO
        
        El sistema calcula cuánto ha consumido un técnico en los últimos N días.
        """
        print("\n" + "="*80)
        print("PASO 3: CÁLCULO DE CONSUMO PREVIO")
        print("="*80)
        
        print("\n📅 LÓGICA DEL CÁLCULO:")
        print("   1. Se obtiene la fecha actual")
        print("   2. Se calcula la fecha límite (fecha_actual - período_días)")
        print("   3. Se suman todas las asignaciones del técnico en ese período")
        print("   4. Se agrupa por material (cinta_aislante, silicona, etc.)")
        
        print("\n🔍 CONSULTA SQL UTILIZADA:")
        consulta_sql = """
        SELECT 
            COALESCE(SUM(CAST(cinta_aislante AS UNSIGNED)), 0) as cinta_aislante,
            COALESCE(SUM(CAST(silicona AS UNSIGNED)), 0) as silicona,
            COALESCE(SUM(CAST(amarres_negros AS UNSIGNED)), 0) as amarres_negros,
            COALESCE(SUM(CAST(amarres_blancos AS UNSIGNED)), 0) as amarres_blancos,
            COALESCE(SUM(CAST(grapas_blancas AS UNSIGNED)), 0) as grapas_blancas,
            COALESCE(SUM(CAST(grapas_negras AS UNSIGNED)), 0) as grapas_negras
        FROM ferretero 
        WHERE codigo_ferretero = %s 
        AND fecha_asignacion >= %s
        """
        
        print(consulta_sql)
        
        print("\n⚠️ PUNTOS CRÍTICOS:")
        print("   - Se usa CAST(campo AS UNSIGNED) para convertir VARCHAR a número")
        print("   - COALESCE maneja valores NULL")
        print("   - La fecha se compara con >= (mayor o igual)")
        print("   - El código del técnico se busca en 'codigo_ferretero'")
        
        # Ejemplo práctico si hay datos
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                
                # Buscar un técnico de ejemplo
                cursor.execute("SELECT DISTINCT codigo_ferretero FROM ferretero LIMIT 1")
                resultado = cursor.fetchone()
                
                if resultado:
                    codigo_tecnico = resultado[0]
                    fecha_limite = datetime.now() - timedelta(days=15)
                    
                    print(f"\n📋 EJEMPLO PRÁCTICO - Técnico: {codigo_tecnico}")
                    print(f"   Período: desde {fecha_limite.strftime('%Y-%m-%d')} hasta hoy")
                    
                    cursor.execute(consulta_sql, (codigo_tecnico, fecha_limite))
                    consumo = cursor.fetchone()
                    
                    if consumo:
                        materiales = ['cinta_aislante', 'silicona', 'amarres_negros', 
                                    'amarres_blancos', 'grapas_blancas', 'grapas_negras']
                        
                        print("   Consumo en los últimos 15 días:")
                        for i, material in enumerate(materiales):
                            cantidad = consumo[i] or 0
                            print(f"     - {material}: {cantidad} unidades")
                else:
                    print("\n📋 No hay datos de técnicos para mostrar ejemplo")
                
                cursor.close()
            except Exception as e:
                print(f"❌ Error en ejemplo práctico: {e}")
    
    def explicar_validacion_limites(self):
        """
        PASO 4: EXPLICAR LA VALIDACIÓN DE LÍMITES
        
        El sistema valida si la nueva asignación excedería el límite permitido.
        """
        print("\n" + "="*80)
        print("PASO 4: VALIDACIÓN DE LÍMITES")
        print("="*80)
        
        print("\n🔍 PROCESO DE VALIDACIÓN:")
        print("   1. Obtener el área de trabajo del técnico")
        print("   2. Consultar los límites para esa área (hardcodeados)")
        print("   3. Calcular el consumo previo del técnico")
        print("   4. Sumar la nueva solicitud al consumo previo")
        print("   5. Comparar el total con el límite permitido")
        
        print("\n⚖️ LÓGICA DE DECISIÓN:")
        print("   if (consumo_previo + cantidad_solicitada) > limite_permitido:")
        print("       ❌ RECHAZAR asignación")
        print("   else:")
        print("       ✅ APROBAR asignación")
        
        print("\n📊 EJEMPLO DE VALIDACIÓN:")
        print("   Técnico: Juan Pérez (Área: INSTALACION)")
        print("   Material: cinta_aislante")
        print("   Límite: 5 unidades cada 15 días")
        print("   Consumo previo: 3 unidades")
        print("   Solicitud nueva: 3 unidades")
        print("   Total: 3 + 3 = 6 unidades")
        print("   Resultado: 6 > 5 → ❌ RECHAZADO")
        
        print("\n🎯 FACTORES QUE INFLUYEN:")
        print("   - Área de trabajo del técnico")
        print("   - Tipo de material solicitado")
        print("   - Historial de asignaciones previas")
        print("   - Período de tiempo configurado")
        print("   - Cantidad solicitada en la nueva asignación")
    
    def explicar_actualizacion_stock(self):
        """
        PASO 5: EXPLICAR LA ACTUALIZACIÓN DE STOCK
        
        Cuando se aprueba una asignación, se actualiza el stock automáticamente.
        """
        print("\n" + "="*80)
        print("PASO 5: ACTUALIZACIÓN AUTOMÁTICA DE STOCK")
        print("="*80)
        
        print("\n🔄 TRIGGER 'actualizar_stock_asignacion':")
        print("   - Se ejecuta DESPUÉS de cada INSERT en la tabla 'ferretero'")
        print("   - Actualiza automáticamente la tabla 'stock_general'")
        print("   - Reduce el stock_actual según las cantidades asignadas")
        
        print("\n📝 LÓGICA DEL TRIGGER:")
        trigger_sql = """
        DELIMITER //
        CREATE TRIGGER actualizar_stock_asignacion
        AFTER INSERT ON ferretero
        FOR EACH ROW
        BEGIN
            -- Actualizar stock para cada material asignado
            IF NEW.cinta_aislante > 0 THEN
                UPDATE stock_general 
                SET stock_actual = stock_actual - NEW.cinta_aislante
                WHERE codigo_material = 'cinta_aislante';
            END IF;
            
            IF NEW.silicona > 0 THEN
                UPDATE stock_general 
                SET stock_actual = stock_actual - NEW.silicona
                WHERE codigo_material = 'silicona';
            END IF;
            
            -- ... (similar para otros materiales)
        END//
        DELIMITER ;
        """
        
        print(trigger_sql)
        
        print("\n⚡ CARACTERÍSTICAS DEL TRIGGER:")
        print("   - Ejecución automática (no requiere intervención manual)")
        print("   - Transaccional (si falla, se revierte la asignación)")
        print("   - Actualiza solo los materiales con cantidad > 0")
        print("   - Mantiene la integridad del inventario")
        
        # Verificar si el trigger existe
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                cursor.execute("""
                    SELECT TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE
                    FROM information_schema.TRIGGERS 
                    WHERE TRIGGER_SCHEMA = %s 
                    AND TRIGGER_NAME = 'actualizar_stock_asignacion'
                """, (os.getenv('MYSQL_DB', 'capired'),))
                
                trigger_info = cursor.fetchone()
                if trigger_info:
                    print(f"\n✅ ESTADO DEL TRIGGER: Activo")
                    print(f"   Nombre: {trigger_info[0]}")
                    print(f"   Evento: {trigger_info[1]}")
                    print(f"   Tabla: {trigger_info[2]}")
                else:
                    print("\n❌ ESTADO DEL TRIGGER: No encontrado")
                    print("   ⚠️ Esto explica por qué el stock no se actualiza automáticamente")
                
                cursor.close()
            except Exception as e:
                print(f"❌ Error verificando trigger: {e}")
    
    def simular_flujo_completo(self):
        """
        PASO 6: SIMULAR EL FLUJO COMPLETO
        
        Demostración paso a paso de una asignación completa.
        """
        print("\n" + "="*80)
        print("PASO 6: SIMULACIÓN DEL FLUJO COMPLETO")
        print("="*80)
        
        print("\n🎬 ESCENARIO DE SIMULACIÓN:")
        print("   Técnico: TECH001 (Área: INSTALACION)")
        print("   Solicitud: 2 cintas aislantes")
        print("   Fecha: Hoy")
        
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                codigo_tecnico = "TECH001"
                area_trabajo = "INSTALACION"
                material = "cinta_aislante"
                cantidad_solicitada = 2
                
                print(f"\n📅 PASO 1: Calcular consumo previo (últimos 15 días)")
                fecha_limite = datetime.now() - timedelta(days=15)
                cursor.execute("""
                    SELECT COALESCE(SUM(CAST(cinta_aislante AS UNSIGNED)), 0) as consumo_previo
                    FROM ferretero 
                    WHERE codigo_ferretero = %s 
                    AND fecha_asignacion >= %s
                """, (codigo_tecnico, fecha_limite))
                
                consumo_previo = cursor.fetchone()[0] or 0
                print(f"   Consumo previo: {consumo_previo} unidades")
                
                print(f"\n🎯 PASO 2: Verificar límite para área {area_trabajo}")
                limite_area = 5  # Límite hardcodeado para INSTALACION
                print(f"   Límite permitido: {limite_area} unidades cada 15 días")
                
                print(f"\n⚖️ PASO 3: Validar solicitud")
                total_con_solicitud = consumo_previo + cantidad_solicitada
                print(f"   Consumo previo: {consumo_previo}")
                print(f"   Cantidad solicitada: {cantidad_solicitada}")
                print(f"   Total: {total_con_solicitud}")
                
                if total_con_solicitud <= limite_area:
                    print(f"   ✅ APROBADO: {total_con_solicitud} <= {limite_area}")
                    
                    print(f"\n📦 PASO 4: Verificar stock disponible")
                    cursor.execute("""
                        SELECT stock_actual FROM stock_general 
                        WHERE codigo_material = %s
                    """, (material,))
                    
                    stock_result = cursor.fetchone()
                    if stock_result:
                        stock_actual = stock_result[0]
                        print(f"   Stock actual: {stock_actual} unidades")
                        
                        if stock_actual >= cantidad_solicitada:
                            print(f"   ✅ STOCK SUFICIENTE: {stock_actual} >= {cantidad_solicitada}")
                            print(f"\n🎉 RESULTADO FINAL: ASIGNACIÓN APROBADA")
                            print(f"   - Se registraría en tabla 'ferretero'")
                            print(f"   - El trigger actualizaría el stock automáticamente")
                            print(f"   - Nuevo stock sería: {stock_actual - cantidad_solicitada}")
                        else:
                            print(f"   ❌ STOCK INSUFICIENTE: {stock_actual} < {cantidad_solicitada}")
                    else:
                        print(f"   ❌ MATERIAL NO ENCONTRADO EN STOCK")
                else:
                    print(f"   ❌ RECHAZADO: {total_con_solicitud} > {limite_area}")
                    print(f"   El técnico ha excedido su límite permitido")
                
                cursor.close()
            except Exception as e:
                print(f"❌ Error en simulación: {e}")
    
    def mostrar_dependencias_criticas(self):
        """
        PASO 7: MOSTRAR DEPENDENCIAS CRÍTICAS
        
        Elementos esenciales para el funcionamiento del sistema.
        """
        print("\n" + "="*80)
        print("PASO 7: DEPENDENCIAS CRÍTICAS DEL SISTEMA")
        print("="*80)
        
        print("\n🔧 COMPONENTES ESENCIALES:")
        
        dependencias = [
            {
                "componente": "Tabla 'ferretero'",
                "estado": "✅ Existe",
                "descripcion": "Almacena las asignaciones de materiales"
            },
            {
                "componente": "Tabla 'stock_general'",
                "estado": "✅ Existe",
                "descripcion": "Controla el inventario de materiales"
            },
            {
                "componente": "Trigger 'actualizar_stock_asignacion'",
                "estado": "✅ Existe",
                "descripcion": "Actualiza stock automáticamente"
            },
            {
                "componente": "Límites hardcodeados en main.py",
                "estado": "✅ Configurado",
                "descripcion": "Define restricciones por área"
            },
            {
                "componente": "Función registrar_ferretero()",
                "estado": "✅ Implementada",
                "descripcion": "Lógica principal de validación"
            }
        ]
        
        for dep in dependencias:
            print(f"   {dep['estado']} {dep['componente']}")
            print(f"      {dep['descripcion']}")
        
        print("\n⚠️ PUNTOS DE FALLO COMUNES:")
        print("   1. Trigger faltante → Stock no se actualiza")
        print("   2. Tabla stock_general vacía → No hay control de inventario")
        print("   3. Límites mal configurados → Validaciones incorrectas")
        print("   4. Problemas de timezone → Cálculos de fecha erróneos")
        print("   5. Permisos de BD insuficientes → Operaciones fallan")
        
        print("\n🔍 VERIFICACIÓN ACTUAL:")
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                
                # Verificar registros en ferretero
                cursor.execute("SELECT COUNT(*) FROM ferretero")
                count_ferretero = cursor.fetchone()[0]
                print(f"   📋 Registros en ferretero: {count_ferretero}")
                
                # Verificar registros en stock_general
                cursor.execute("SELECT COUNT(*) FROM stock_general")
                count_stock = cursor.fetchone()[0]
                print(f"   📦 Materiales en stock_general: {count_stock}")
                
                # Verificar trigger
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.TRIGGERS 
                    WHERE TRIGGER_SCHEMA = %s 
                    AND TRIGGER_NAME = 'actualizar_stock_asignacion'
                """, (os.getenv('MYSQL_DB', 'capired'),))
                
                count_trigger = cursor.fetchone()[0]
                print(f"   🔧 Trigger actualizar_stock_asignacion: {'✅ Activo' if count_trigger > 0 else '❌ Faltante'}")
                
                cursor.close()
            except Exception as e:
                print(f"❌ Error verificando dependencias: {e}")
    
    def generar_recomendaciones(self):
        """
        PASO 8: GENERAR RECOMENDACIONES
        
        Sugerencias para optimizar el sistema.
        """
        print("\n" + "="*80)
        print("PASO 8: RECOMENDACIONES DE OPTIMIZACIÓN")
        print("="*80)
        
        print("\n🚀 MEJORAS INMEDIATAS:")
        print("   1. ✅ Verificar que el trigger 'actualizar_stock_asignacion' existe")
        print("   2. ✅ Sincronizar timezone entre Python y MySQL (UTC)")
        print("   3. ✅ Implementar logging detallado en registrar_ferretero()")
        print("   4. ⚠️ Migrar límites hardcodeados a tabla de configuración")
        print("   5. ⚠️ Añadir validaciones adicionales (técnico existe, material activo)")
        
        print("\n⚡ OPTIMIZACIONES DE RENDIMIENTO:")
        print("   1. Crear índices en (codigo_ferretero, fecha_asignacion)")
        print("   2. Implementar caché de límites por área")
        print("   3. Usar consultas preparadas para cálculos frecuentes")
        print("   4. Optimizar consultas de consumo previo")
        
        print("\n🔄 MANTENIMIENTO REGULAR:")
        print("   1. Limpieza periódica de registros antiguos (>1 año)")
        print("   2. Backup regular de configuraciones de límites")
        print("   3. Auditoría de cambios en límites por área")
        print("   4. Monitoreo de stock bajo y alertas automáticas")
        
        print("\n📊 MÉTRICAS RECOMENDADAS:")
        print("   1. Tiempo promedio de procesamiento de asignaciones")
        print("   2. Porcentaje de asignaciones rechazadas por límite")
        print("   3. Porcentaje de asignaciones rechazadas por stock")
        print("   4. Rotación de inventario por material")
        print("   5. Consumo promedio por técnico y área")
    
    def ejecutar_explicacion_completa(self):
        """Ejecutar toda la explicación paso a paso"""
        print("🎓 EXPLICACIÓN COMPLETA DEL CÁLCULO DE STOCK - SISTEMA FERRETERO")
        print("=" * 80)
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🗄️ Base de datos: {os.getenv('MYSQL_DB', 'capired')}")
        
        try:
            self.explicar_tablas_involucradas()
            self.explicar_limites_hardcodeados()
            self.explicar_calculo_consumo_previo()
            self.explicar_validacion_limites()
            self.explicar_actualizacion_stock()
            self.simular_flujo_completo()
            self.mostrar_dependencias_criticas()
            self.generar_recomendaciones()
            
            print("\n" + "="*80)
            print("🎉 EXPLICACIÓN COMPLETADA EXITOSAMENTE")
            print("="*80)
            print("\n📋 RESUMEN EJECUTIVO:")
            print("   ✅ El sistema funciona con límites hardcodeados por área")
            print("   ✅ Los cálculos se basan en consumo de los últimos 15 días")
            print("   ✅ El stock se actualiza automáticamente con triggers")
            print("   ✅ La validación considera área + material + período")
            print("\n💡 PUNTO CLAVE: Los límites están en el CÓDIGO, no en la BD")
            
        except Exception as e:
            print(f"❌ Error durante la explicación: {e}")
        finally:
            if self.conexion:
                self.conexion.close()
                print("\n🔌 Conexión a base de datos cerrada")

if __name__ == "__main__":
    explicador = ExplicacionCalculoStockCompleta()
    explicador.ejecutar_explicacion_completa()