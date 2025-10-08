#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analizar el orden correcto de TRUNCATE
basado en las relaciones de claves foráneas
"""

import mysql.connector
from mysql.connector import Error
from collections import defaultdict, deque
import json

class AnalizadorOrdenTruncate:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '732137A031E4b@',
            'database': 'capired'
        }
        self.tablas_sistema = [
            'asignaciones_equipos_dotaciones',
            'auditoria_estados_devolucion',
            'cambios_dotacion',
            'cambios_dotaciones',
            'cambios_dotaciones_detalle',
            'devolucion_detalles',
            'devolucion_dotaciones',
            'devoluciones_dotacion',
            'devoluciones_elementos',
            'devoluciones_historial',
            'dotaciones',
            'equipos_dotaciones',
            'historial_cambios_dotaciones',
            'historial_notificaciones',
            'historial_vencimientos',
            'ingresos_dotaciones',
            'movimientos_equipos_dotaciones'
        ]
        self.relaciones = {}
        self.dependencias = defaultdict(set)
        self.tablas_maestras = set()
        
    def conectar(self):
        """Establece conexión con la base de datos"""
        try:
            self.conexion = mysql.connector.connect(**self.config)
            self.cursor = self.conexion.cursor(dictionary=True)
            return True
        except Error as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def obtener_relaciones_fk(self):
        """Obtiene todas las relaciones de claves foráneas del sistema"""
        print("\n=== ANALIZANDO RELACIONES DE CLAVES FORÁNEAS ===")
        
        try:
            # Obtener todas las FK que involucran tablas del sistema
            self.cursor.execute("""
                SELECT 
                    kcu.TABLE_NAME as tabla_origen,
                    kcu.COLUMN_NAME as columna_origen,
                    kcu.REFERENCED_TABLE_NAME as tabla_destino,
                    kcu.REFERENCED_COLUMN_NAME as columna_destino,
                    kcu.CONSTRAINT_NAME as nombre_constraint,
                    rc.UPDATE_RULE as regla_update,
                    rc.DELETE_RULE as regla_delete
                FROM information_schema.KEY_COLUMN_USAGE kcu
                JOIN information_schema.REFERENTIAL_CONSTRAINTS rc 
                    ON kcu.CONSTRAINT_NAME = rc.CONSTRAINT_NAME 
                    AND kcu.CONSTRAINT_SCHEMA = rc.CONSTRAINT_SCHEMA
                WHERE kcu.table_schema = 'capired' 
                AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
                AND (kcu.TABLE_NAME IN ({}) OR kcu.REFERENCED_TABLE_NAME IN ({}))
                ORDER BY kcu.TABLE_NAME, kcu.COLUMN_NAME
            """.format(
                ','.join([f"'{t}'" for t in self.tablas_sistema]),
                ','.join([f"'{t}'" for t in self.tablas_sistema])
            ))
            
            relaciones = self.cursor.fetchall()
            
            print(f"\n📋 RELACIONES ENCONTRADAS: {len(relaciones)}")
            print("-" * 100)
            print(f"{'Tabla Origen':<30} {'Columna':<20} {'Tabla Destino':<30} {'Regla Delete':<15}")
            print("-" * 100)
            
            for rel in relaciones:
                tabla_origen = rel['tabla_origen']
                tabla_destino = rel['tabla_destino']
                
                print(f"{tabla_origen:<30} {rel['columna_origen']:<20} {tabla_destino:<30} {rel['regla_delete']:<15}")
                
                # Guardar relación
                if tabla_origen not in self.relaciones:
                    self.relaciones[tabla_origen] = []
                
                self.relaciones[tabla_origen].append({
                    'tabla_destino': tabla_destino,
                    'columna_origen': rel['columna_origen'],
                    'columna_destino': rel['columna_destino'],
                    'constraint': rel['nombre_constraint'],
                    'delete_rule': rel['regla_delete']
                })
                
                # Si ambas tablas están en nuestro sistema, crear dependencia
                if tabla_origen in self.tablas_sistema and tabla_destino in self.tablas_sistema:
                    # tabla_origen depende de tabla_destino
                    self.dependencias[tabla_origen].add(tabla_destino)
                
                # Identificar tablas maestras (que son referenciadas pero no referencian a otras del sistema)
                if tabla_destino in self.tablas_sistema:
                    self.tablas_maestras.add(tabla_destino)
            
            return relaciones
            
        except Error as e:
            print(f"❌ Error obteniendo relaciones: {e}")
            return []
    
    def identificar_tablas_maestras(self):
        """Identifica tablas maestras que no dependen de otras del sistema"""
        print("\n=== IDENTIFICANDO TABLAS MAESTRAS ===")
        
        # Remover de maestras las que tienen dependencias dentro del sistema
        tablas_maestras_reales = self.tablas_maestras.copy()
        
        for tabla in self.tablas_maestras:
            if tabla in self.dependencias and self.dependencias[tabla]:
                # Verificar si las dependencias son dentro del sistema
                deps_sistema = self.dependencias[tabla].intersection(set(self.tablas_sistema))
                if deps_sistema:
                    tablas_maestras_reales.discard(tabla)
        
        print(f"\n📌 TABLAS MAESTRAS IDENTIFICADAS: {len(tablas_maestras_reales)}")
        for tabla in sorted(tablas_maestras_reales):
            print(f"  ✓ {tabla}")
        
        return tablas_maestras_reales
    
    def calcular_orden_truncate(self):
        """Calcula el orden correcto para TRUNCATE usando ordenamiento topológico"""
        print("\n=== CALCULANDO ORDEN DE TRUNCATE ===")
        
        # Solo considerar tablas del sistema que tienen relaciones
        tablas_con_relaciones = set()
        for tabla in self.tablas_sistema:
            if tabla in self.dependencias or any(tabla in deps for deps in self.dependencias.values()):
                tablas_con_relaciones.add(tabla)
        
        # Tablas sin relaciones pueden truncarse en cualquier momento
        tablas_sin_relaciones = set(self.tablas_sistema) - tablas_con_relaciones
        
        print(f"\n📊 ANÁLISIS DE DEPENDENCIAS:")
        print(f"  Tablas con relaciones: {len(tablas_con_relaciones)}")
        print(f"  Tablas sin relaciones: {len(tablas_sin_relaciones)}")
        
        # Algoritmo de ordenamiento topológico (Kahn's algorithm)
        # Para TRUNCATE, necesitamos el orden inverso (dependientes primero)
        
        # Calcular grado de entrada (cuántas tablas dependen de esta)
        grado_entrada = defaultdict(int)
        grafo_inverso = defaultdict(set)
        
        for tabla_origen, dependencias in self.dependencias.items():
            if tabla_origen in tablas_con_relaciones:
                for tabla_destino in dependencias:
                    if tabla_destino in tablas_con_relaciones:
                        # Para truncate, invertimos la relación
                        grafo_inverso[tabla_destino].add(tabla_origen)
                        grado_entrada[tabla_origen] += 1
        
        # Inicializar con tablas que no tienen dependencias (grado 0)
        cola = deque()
        for tabla in tablas_con_relaciones:
            if grado_entrada[tabla] == 0:
                cola.append(tabla)
        
        orden_truncate = []
        
        while cola:
            tabla_actual = cola.popleft()
            orden_truncate.append(tabla_actual)
            
            # Reducir grado de entrada de tablas que dependen de la actual
            for tabla_dependiente in grafo_inverso[tabla_actual]:
                grado_entrada[tabla_dependiente] -= 1
                if grado_entrada[tabla_dependiente] == 0:
                    cola.append(tabla_dependiente)
        
        # Verificar si hay ciclos
        if len(orden_truncate) != len(tablas_con_relaciones):
            print("\n⚠️ ADVERTENCIA: Se detectaron dependencias circulares")
            tablas_restantes = tablas_con_relaciones - set(orden_truncate)
            print(f"   Tablas con posibles ciclos: {tablas_restantes}")
            # Agregar las restantes al final
            orden_truncate.extend(sorted(tablas_restantes))
        
        # Agregar tablas sin relaciones al final
        orden_truncate.extend(sorted(tablas_sin_relaciones))
        
        return orden_truncate, tablas_sin_relaciones
    
    def validar_orden_truncate(self, orden):
        """Valida que el orden de truncate sea correcto"""
        print("\n=== VALIDANDO ORDEN DE TRUNCATE ===")
        
        errores = []
        posiciones = {tabla: i for i, tabla in enumerate(orden)}
        
        for tabla_origen, relaciones in self.relaciones.items():
            if tabla_origen in posiciones:
                for rel in relaciones:
                    tabla_destino = rel['tabla_destino']
                    if tabla_destino in posiciones:
                        # tabla_origen debe truncarse ANTES que tabla_destino
                        if posiciones[tabla_origen] > posiciones[tabla_destino]:
                            errores.append({
                                'tabla_origen': tabla_origen,
                                'tabla_destino': tabla_destino,
                                'constraint': rel['constraint'],
                                'problema': f"{tabla_origen} debe truncarse antes que {tabla_destino}"
                            })
        
        if errores:
            print(f"\n❌ ERRORES EN EL ORDEN ({len(errores)}):")
            for error in errores:
                print(f"  ⚠️ {error['problema']} (FK: {error['constraint']})")
            return False
        else:
            print("\n✅ ORDEN DE TRUNCATE VÁLIDO")
            return True
    
    def generar_reporte_orden(self, orden, tablas_sin_relaciones):
        """Genera reporte detallado del orden de truncate"""
        reporte = {
            'timestamp': self.cursor.execute("SELECT NOW() as now") or self.cursor.fetchone()['now'].isoformat(),
            'total_tablas': len(self.tablas_sistema),
            'tablas_con_relaciones': len(orden) - len(tablas_sin_relaciones),
            'tablas_sin_relaciones': len(tablas_sin_relaciones),
            'orden_truncate': orden,
            'tablas_independientes': sorted(tablas_sin_relaciones),
            'relaciones_analizadas': len(self.relaciones),
            'dependencias': {k: list(v) for k, v in self.dependencias.items()}
        }
        
        try:
            with open('orden_truncate_reporte.json', 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n✓ Reporte guardado: orden_truncate_reporte.json")
        except Exception as e:
            print(f"❌ Error guardando reporte: {e}")
        
        return reporte
    
    def ejecutar_analisis_completo(self):
        """Ejecuta el análisis completo del orden de truncate"""
        print("\n" + "=" * 80)
        print("         ANÁLISIS DE ORDEN DE TRUNCATE - SISTEMA DOTACIONES")
        print("=" * 80)
        
        if not self.conectar():
            return None
        
        try:
            # Obtener relaciones
            relaciones = self.obtener_relaciones_fk()
            
            if not relaciones:
                print("\n⚠️ No se encontraron relaciones FK. Todas las tablas pueden truncarse independientemente.")
                return sorted(self.tablas_sistema)
            
            # Identificar tablas maestras
            tablas_maestras = self.identificar_tablas_maestras()
            
            # Calcular orden
            orden, tablas_sin_rel = self.calcular_orden_truncate()
            
            # Validar orden
            orden_valido = self.validar_orden_truncate(orden)
            
            # Mostrar resultado
            print("\n" + "=" * 80)
            print("                    ORDEN DE TRUNCATE RECOMENDADO")
            print("=" * 80)
            
            print(f"\n📋 ORDEN DE EJECUCIÓN ({len(orden)} tablas):")
            print("-" * 50)
            
            for i, tabla in enumerate(orden, 1):
                estado = "🔗" if tabla not in tablas_sin_rel else "🔓"
                print(f"{i:2d}. {estado} {tabla}")
            
            print("\n📝 LEYENDA:")
            print("   🔗 = Tabla con relaciones FK")
            print("   🔓 = Tabla independiente (sin FK)")
            
            if not orden_valido:
                print("\n⚠️ ADVERTENCIA: El orden calculado tiene conflictos.")
                print("   Revisar manualmente las dependencias circulares.")
            
            # Generar reporte
            self.generar_reporte_orden(orden, tablas_sin_rel)
            
            return orden
            
        except Exception as e:
            print(f"❌ Error en análisis: {e}")
            return None
            
        finally:
            if hasattr(self, 'cursor'):
                self.cursor.close()
            if hasattr(self, 'conexion'):
                self.conexion.close()

def main():
    analizador = AnalizadorOrdenTruncate()
    orden = analizador.ejecutar_analisis_completo()
    
    if orden:
        print("\n✅ Análisis completado exitosamente.")
        print("   Revisar 'orden_truncate_reporte.json' para detalles completos.")
        return 0
    else:
        print("\n❌ Error en el análisis del orden de truncate.")
        return 1

if __name__ == "__main__":
    exit(main())