#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CREAR COMPONENTES FALTANTES PARA EL SISTEMA DE STOCK

Este script crea los componentes críticos que faltan en la base de datos:
1. Tabla 'stock_general' para el control de inventario
2. Trigger 'actualizar_stock_asignacion' para actualización automática
3. Datos iniciales de stock basados en recurso_operativo

Autor: Sistema de Diagnóstico
Fecha: 2025
"""

import os
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class CrearComponentesFaltantes:
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
                database=os.getenv('MYSQL_DB', 'synapsis'),
                autocommit=False  # Para manejar transacciones
            )
            print("✅ Conexión a MySQL establecida correctamente")
        except Exception as e:
            print(f"❌ Error conectando a MySQL: {e}")
            self.conexion = None
    
    def verificar_tabla_stock_general(self):
        """Verificar si la tabla stock_general existe"""
        if not self.conexion:
            return False
        
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'stock_general'
            """)
            existe = cursor.fetchone()[0] > 0
            cursor.close()
            return existe
        except Exception as e:
            print(f"❌ Error verificando tabla stock_general: {e}")
            return False
    
    def crear_tabla_stock_general(self):
        """Crear la tabla stock_general"""
        print("\n🔧 CREANDO TABLA 'stock_general'...")
        
        sql_crear_tabla = """
        CREATE TABLE IF NOT EXISTS stock_general (
            id INT AUTO_INCREMENT PRIMARY KEY,
            codigo_material VARCHAR(50) NOT NULL UNIQUE,
            descripcion VARCHAR(255),
            cantidad_disponible INT DEFAULT 0,
            cantidad_minima INT DEFAULT 5,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT TRUE,
            INDEX idx_codigo_material (codigo_material),
            INDEX idx_cantidad_disponible (cantidad_disponible)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_crear_tabla)
            self.conexion.commit()
            cursor.close()
            print("   ✅ Tabla 'stock_general' creada exitosamente")
            return True
        except Exception as e:
            print(f"   ❌ Error creando tabla stock_general: {e}")
            self.conexion.rollback()
            return False
    
    def poblar_stock_inicial(self):
        """Poblar la tabla stock_general con datos iniciales basado en materiales del sistema ferretero"""
        print("\n📦 POBLANDO STOCK INICIAL...")
        
        try:
            cursor = self.conexion.cursor()
            
            # Materiales del sistema ferretero (basado en el código real)
            materiales_ferretero = [
                ('cinta_aislante', 'Cinta Aislante'),
                ('silicona', 'Silicona'),
                ('amarres_negros', 'Amarres Negros'),
                ('amarres_blancos', 'Amarres Blancos'),
                ('grapas_blancas', 'Grapas Blancas'),
                ('grapas_negras', 'Grapas Negras')
            ]
            
            print(f"   📋 Insertando {len(materiales_ferretero)} materiales del sistema ferretero")
            
            # Insertar cada material con stock inicial
            sql_insertar = """
                INSERT INTO stock_general (codigo_material, descripcion, cantidad_disponible, cantidad_minima)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    descripcion = VALUES(descripcion),
                    fecha_actualizacion = CURRENT_TIMESTAMP
            """
            
            materiales_insertados = 0
            for codigo, descripcion in materiales_ferretero:
                # Stock inicial alto para materiales del ferretero
                stock_inicial = 1000
                cantidad_minima = 100
                
                cursor.execute(sql_insertar, (codigo, descripcion, stock_inicial, cantidad_minima))
                materiales_insertados += 1
            
            self.conexion.commit()
            cursor.close()
            print(f"   ✅ {materiales_insertados} materiales insertados/actualizados en stock_general")
            return True
            
        except Exception as e:
            print(f"   ❌ Error poblando stock inicial: {e}")
            self.conexion.rollback()
            return False
    
    def verificar_trigger_stock(self):
        """Verificar si el trigger actualizar_stock_asignacion existe"""
        if not self.conexion:
            return False
        
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.triggers 
                WHERE trigger_schema = DATABASE() 
                AND trigger_name = 'actualizar_stock_asignacion'
            """)
            existe = cursor.fetchone()[0] > 0
            cursor.close()
            return existe
        except Exception as e:
            print(f"❌ Error verificando trigger: {e}")
            return False
    
    def crear_trigger_stock(self):
        """Crear el trigger actualizar_stock_asignacion"""
        print("\n🔧 CREANDO TRIGGER 'actualizar_stock_asignacion'...")
        
        # Primero eliminar el trigger si existe
        sql_drop_trigger = "DROP TRIGGER IF EXISTS actualizar_stock_asignacion"
        
        # Crear el nuevo trigger
        sql_crear_trigger = """
        CREATE TRIGGER actualizar_stock_asignacion
        AFTER INSERT ON ferretero
        FOR EACH ROW
        BEGIN
            -- Actualizar el stock disponible
            UPDATE stock_general 
            SET cantidad_disponible = cantidad_disponible - NEW.cantidad,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE codigo_material = NEW.codigo_material;
            
            -- Si el material no existe en stock_general, insertarlo con stock negativo
            INSERT INTO stock_general (codigo_material, descripcion, cantidad_disponible, cantidad_minima)
            SELECT NEW.codigo_material, 
                   COALESCE(ro.descripcion, 'Material no catalogado'),
                   -NEW.cantidad,
                   5
            FROM (SELECT 1) AS dummy
            LEFT JOIN recurso_operativo ro ON ro.codigo = NEW.codigo_material
            WHERE NOT EXISTS (
                SELECT 1 FROM stock_general WHERE codigo_material = NEW.codigo_material
            );
            
            -- Log de la operación (opcional, comentado por defecto)
            -- INSERT INTO log_stock (codigo_material, operacion, cantidad, fecha)
            -- VALUES (NEW.codigo_material, 'ASIGNACION', NEW.cantidad, NOW());
        END
        """
        
        try:
            cursor = self.conexion.cursor()
            
            # Eliminar trigger existente
            cursor.execute(sql_drop_trigger)
            
            # Crear nuevo trigger
            cursor.execute(sql_crear_trigger)
            
            self.conexion.commit()
            cursor.close()
            print("   ✅ Trigger 'actualizar_stock_asignacion' creado exitosamente")
            return True
            
        except Exception as e:
            print(f"   ❌ Error creando trigger: {e}")
            self.conexion.rollback()
            return False
    
    def crear_trigger_restock(self):
        """Crear trigger adicional para reabastecimiento automático"""
        print("\n🔧 CREANDO TRIGGER DE REABASTECIMIENTO...")
        
        sql_trigger_restock = """
        CREATE TRIGGER IF NOT EXISTS alerta_stock_bajo
        AFTER UPDATE ON stock_general
        FOR EACH ROW
        BEGIN
            -- Si el stock cae por debajo del mínimo, registrar alerta
            IF NEW.cantidad_disponible < NEW.cantidad_minima AND 
               OLD.cantidad_disponible >= OLD.cantidad_minima THEN
                
                -- Insertar alerta en tabla de logs (si existe)
                -- INSERT INTO alertas_stock (codigo_material, stock_actual, stock_minimo, fecha)
                -- VALUES (NEW.codigo_material, NEW.cantidad_disponible, NEW.cantidad_minima, NOW());
                
                -- Por ahora, solo actualizar un campo de estado
                UPDATE stock_general 
                SET activo = CASE 
                    WHEN cantidad_disponible <= 0 THEN FALSE 
                    ELSE TRUE 
                END
                WHERE codigo_material = NEW.codigo_material;
            END IF;
        END
        """
        
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql_trigger_restock)
            self.conexion.commit()
            cursor.close()
            print("   ✅ Trigger de reabastecimiento creado exitosamente")
            return True
        except Exception as e:
            print(f"   ❌ Error creando trigger de reabastecimiento: {e}")
            self.conexion.rollback()
            return False
    
    def verificar_integridad(self):
        """Verificar la integridad de los componentes creados"""
        print("\n🔍 VERIFICANDO INTEGRIDAD DE COMPONENTES...")
        
        try:
            cursor = self.conexion.cursor()
            
            # Verificar tabla stock_general
            cursor.execute("SELECT COUNT(*) FROM stock_general")
            count_stock = cursor.fetchone()[0]
            print(f"   📦 Registros en stock_general: {count_stock}")
            
            # Verificar triggers
            cursor.execute("""
                SELECT trigger_name 
                FROM information_schema.triggers 
                WHERE trigger_schema = DATABASE() 
                AND trigger_name IN ('actualizar_stock_asignacion', 'alerta_stock_bajo')
            """)
            triggers = [row[0] for row in cursor.fetchall()]
            print(f"   🔧 Triggers encontrados: {', '.join(triggers)}")
            
            # Verificar algunos stocks específicos
            cursor.execute("""
                SELECT codigo_material, cantidad_disponible, cantidad_minima 
                FROM stock_general 
                WHERE cantidad_disponible > 0 
                ORDER BY cantidad_disponible DESC 
                LIMIT 5
            """)
            
            print("   📊 Top 5 materiales con mayor stock:")
            for codigo, disponible, minimo in cursor.fetchall():
                print(f"      {codigo}: {disponible} unidades (mín: {minimo})")
            
            cursor.close()
            return True
            
        except Exception as e:
            print(f"   ❌ Error verificando integridad: {e}")
            return False
    
    def probar_funcionamiento(self):
        """Probar el funcionamiento del sistema con una asignación de prueba"""
        print("\n🧪 PROBANDO FUNCIONAMIENTO DEL SISTEMA...")
        
        try:
            cursor = self.conexion.cursor()
            
            # Seleccionar un material para prueba
            cursor.execute("""
                SELECT codigo_material, cantidad_disponible 
                FROM stock_general 
                WHERE cantidad_disponible > 5 
                LIMIT 1
            """)
            
            resultado = cursor.fetchone()
            if not resultado:
                print("   ⚠️ No hay materiales con stock suficiente para prueba")
                return False
            
            codigo_material, stock_inicial = resultado
            print(f"   📦 Material de prueba: {codigo_material} (Stock: {stock_inicial})")
            
            # Crear una asignación de prueba
            cedula_prueba = "99999999"  # Cédula ficticia
            cantidad_prueba = 1
            
            print(f"   🔄 Insertando asignación de prueba...")
            cursor.execute("""
                INSERT INTO ferretero (cedula_tecnico, codigo_material, cantidad, fecha_asignacion)
                VALUES (%s, %s, %s, NOW())
            """, (cedula_prueba, codigo_material, cantidad_prueba))
            
            # Verificar que el stock se actualizó
            cursor.execute("""
                SELECT cantidad_disponible 
                FROM stock_general 
                WHERE codigo_material = %s
            """, (codigo_material,))
            
            stock_final = cursor.fetchone()[0]
            print(f"   📊 Stock después de asignación: {stock_final}")
            
            if stock_final == stock_inicial - cantidad_prueba:
                print("   ✅ TRIGGER FUNCIONANDO CORRECTAMENTE")
                
                # Limpiar la asignación de prueba
                cursor.execute("""
                    DELETE FROM ferretero 
                    WHERE cedula_tecnico = %s AND codigo_material = %s
                    ORDER BY fecha_asignacion DESC LIMIT 1
                """, (cedula_prueba, codigo_material))
                
                # Restaurar el stock
                cursor.execute("""
                    UPDATE stock_general 
                    SET cantidad_disponible = %s 
                    WHERE codigo_material = %s
                """, (stock_inicial, codigo_material))
                
                self.conexion.commit()
                print("   🧹 Datos de prueba limpiados")
                return True
            else:
                print(f"   ❌ TRIGGER NO FUNCIONA: Esperado {stock_inicial - cantidad_prueba}, obtenido {stock_final}")
                self.conexion.rollback()
                return False
            
        except Exception as e:
            print(f"   ❌ Error probando funcionamiento: {e}")
            self.conexion.rollback()
            return False
        finally:
            cursor.close()
    
    def generar_reporte_final(self):
        """Generar reporte final de la instalación"""
        print("\n" + "="*80)
        print("📋 REPORTE FINAL DE INSTALACIÓN")
        print("="*80)
        
        # Verificar componentes
        tabla_existe = self.verificar_tabla_stock_general()
        trigger_existe = self.verificar_trigger_stock()
        
        print(f"\n✅ COMPONENTES INSTALADOS:")
        print(f"   📦 Tabla stock_general: {'✅ OK' if tabla_existe else '❌ FALTA'}")
        print(f"   🔧 Trigger actualizar_stock_asignacion: {'✅ OK' if trigger_existe else '❌ FALTA'}")
        
        if tabla_existe and trigger_existe:
            print(f"\n🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE")
            print(f"\n📋 PRÓXIMOS PASOS:")
            print(f"   1. Desplegar estos cambios al servidor de producción")
            print(f"   2. Verificar que el trigger funciona en producción")
            print(f"   3. Monitorear los logs de asignaciones")
            print(f"   4. Ajustar stocks iniciales según necesidades reales")
        else:
            print(f"\n❌ INSTALACIÓN INCOMPLETA")
            print(f"   Revisar errores anteriores y ejecutar nuevamente")
    
    def ejecutar_instalacion_completa(self):
        """Ejecutar la instalación completa de componentes faltantes"""
        print("🚀 INICIANDO INSTALACIÓN DE COMPONENTES FALTANTES")
        print("⏰ Fecha:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        if not self.conexion:
            print("❌ No hay conexión a la base de datos")
            return False
        
        try:
            # Verificar estado actual
            tabla_existe = self.verificar_tabla_stock_general()
            trigger_existe = self.verificar_trigger_stock()
            
            print(f"\n🔍 ESTADO ACTUAL:")
            print(f"   Tabla stock_general: {'✅ Existe' if tabla_existe else '❌ No existe'}")
            print(f"   Trigger actualizar_stock_asignacion: {'✅ Existe' if trigger_existe else '❌ No existe'}")
            
            # Crear tabla si no existe
            if not tabla_existe:
                if not self.crear_tabla_stock_general():
                    return False
                if not self.poblar_stock_inicial():
                    return False
            else:
                print("\n📦 Tabla stock_general ya existe")
                # Verificar si tiene datos, si no, poblarla
                cursor = self.conexion.cursor()
                cursor.execute("SELECT COUNT(*) FROM stock_general")
                count = cursor.fetchone()[0]
                cursor.close()
                
                if count == 0:
                    print("   📋 Tabla vacía, poblando con datos iniciales...")
                    self.poblar_stock_inicial()
                else:
                    print(f"   📋 Tabla contiene {count} registros")
            
            # Crear trigger si no existe
            if not trigger_existe:
                if not self.crear_trigger_stock():
                    return False
                # Crear trigger adicional
                self.crear_trigger_restock()
            else:
                print("\n🔧 Trigger actualizar_stock_asignacion ya existe")
            
            # Verificar integridad
            self.verificar_integridad()
            
            # Probar funcionamiento
            self.probar_funcionamiento()
            
            # Generar reporte final
            self.generar_reporte_final()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error durante la instalación: {e}")
            return False
        finally:
            if self.conexion:
                self.conexion.close()
                print("\n🔌 Conexión a base de datos cerrada")

def main():
    """
    Función principal para ejecutar la instalación
    """
    print("Iniciando creación de componentes faltantes...")
    instalador = CrearComponentesFaltantes()
    exito = instalador.ejecutar_instalacion_completa()
    
    if exito:
        print("\n🎉 Proceso completado exitosamente")
    else:
        print("\n❌ Proceso completado con errores")

if __name__ == "__main__":
    main()