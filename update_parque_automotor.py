#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar la tabla parque_automotor con datos del archivo AUTOMOTOR.csv
Base de datos: CAPIRED
Usuario: ROOT
Clave: 732137A031E4b@
"""

import mysql.connector
import pandas as pd
import sys
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ParqueAutomotorUpdater:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.csv_file = r'c:\Users\vnaranjos\OneDrive\DESARROLLOS PROPIOS\synapsis\AUTOMOTOR.csv'
        
        # Configuración de la base de datos
        self.db_configs = [
            {
                'host': 'localhost',
                'user': 'root',
                'password': '732137A031E4b@',
                'database': 'CAPIRED',
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci'
            },
            {
                'host': 'localhost',
                'user': 'ROOT',
                'password': '732137A031E4b@',
                'database': 'CAPIRED',
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci'
            },
            {
                'host': '127.0.0.1',
                'user': 'root',
                'password': '732137A031E4b@',
                'database': 'CAPIRED',
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci'
            }
        ]
        
        # Mapeo de columnas CSV a columnas de la base de datos
        self.column_mapping = {
            'id_parque_automotor': 'id_vehiculo',
            'cedula_propietario': 'cedula_propietario',
            'nombre_propietario': 'nombre_propietario', 
            'placa': 'placa',
            'tipo_vehiculo': 'tipo_vehiculo',
            'supervisor': 'supervisor',
            'soat_vencimiento': 'soat_vencimiento',
            'tecnomecanica_vencimiento': 'tecnomecanica_vencimiento',
            'licencia': 'licencia',
            'vin': 'vin',
            'numero_de_motor': 'numero_de_motor',
            'fecha_de_matricula': 'fecha_de_matricula',
            'estado': 'estado',
            'marca': 'marca',
            'linea': 'linea',
            'observaciones': 'observaciones',
            'comparendos': 'comparendos',
            'total_comparendos': 'total_comparendos',
            'id_codigo_consumidor': 'id_codigo_consumidor',
            'fecha_asignacion': 'fecha_asignacion',
            'modelo': 'modelo',
            'color': 'color',
            'fecha_actualizacion': 'fecha_actualizacion',
            'kilometraje_actual': 'kilometraje_actual',
            'proximo_mantenimiento_km': 'proximo_mantenimiento_km',
            'fecha_ultimo_mantenimiento': 'fecha_ultimo_mantenimiento'
        }
    
    def connect_database(self):
        """Conectar a la base de datos MySQL"""
        for i, config in enumerate(self.db_configs):
            try:
                logger.info(f"Intentando conexión {i+1} con usuario: {config['user']} en host: {config['host']}")
                self.connection = mysql.connector.connect(**config)
                self.cursor = self.connection.cursor()
                logger.info(f"Conexión exitosa a la base de datos CAPIRED con configuración {i+1}")
                
                # Verificar estructura de la tabla
                self.check_table_structure()
                return True
            except mysql.connector.Error as err:
                logger.warning(f"Configuración {i+1} falló: {err}")
                continue
        
        logger.error("No se pudo conectar con ninguna configuración")
        return False
    
    def check_table_structure(self):
        """Verificar la estructura de la tabla parque_automotor"""
        try:
            self.cursor.execute("DESCRIBE parque_automotor")
            columns = self.cursor.fetchall()
            logger.info("Estructura de la tabla parque_automotor:")
            for column in columns:
                logger.info(f"  - {column[0]} ({column[1]})")
        except mysql.connector.Error as err:
            logger.warning(f"No se pudo verificar la estructura de la tabla: {err}")
    
    def parse_date(self, date_str):
        """Convertir string de fecha a formato MySQL"""
        if pd.isna(date_str) or str(date_str).strip() == '' or str(date_str).strip() == '0':
            return None
        
        try:
            date_str = str(date_str).strip()
            
            # Si es un número (formato de Excel), convertir desde el número de serie
            if date_str.replace('.', '').isdigit():
                try:
                    # Excel cuenta desde 1900-01-01, pero tiene un bug con 1900 como año bisiesto
                    excel_date = float(date_str)
                    if excel_date > 0:
                        # Convertir número de serie de Excel a fecha
                        base_date = datetime(1899, 12, 30)  # Excel base date
                        converted_date = base_date + timedelta(days=excel_date)
                        return converted_date.strftime('%Y-%m-%d')
                except (ValueError, OverflowError):
                    pass
            
            # Intentar diferentes formatos de fecha
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']
            
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            logger.warning(f"No se pudo parsear la fecha: {date_str}")
            return None
        except Exception as e:
            logger.warning(f"Error parseando fecha {date_str}: {e}")
            return None
    
    def clean_numeric_value(self, value):
        """Limpiar valores numéricos"""
        if pd.isna(value) or value == '' or value == 'NULL':
            return None
        
        try:
            # Remover caracteres no numéricos excepto punto y coma
            cleaned = str(value).replace('$', '').replace('€', '').replace('¢', '').replace('�', '')
            cleaned = ''.join(c for c in cleaned if c.isdigit() or c in '.-')
            
            if cleaned == '' or cleaned == '-':
                return None
                
            return int(float(cleaned))
        except (ValueError, TypeError):
            return None
    
    def read_csv_data(self):
        """Leer y procesar el archivo CSV"""
        try:
            # Intentar diferentes codificaciones
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            
            for encoding in encodings:
                try:
                    logger.info(f"Intentando leer CSV con codificación: {encoding}")
                    df = pd.read_csv(self.csv_file, sep=';', encoding=encoding)
                    logger.info(f"Archivo CSV leído exitosamente con {encoding}. Registros encontrados: {len(df)}")
                    break
                except UnicodeDecodeError:
                    logger.warning(f"Codificación {encoding} falló")
                    continue
            
            if df is None:
                raise Exception("No se pudo leer el archivo con ninguna codificación")
            
            # Limpiar datos
            processed_data = []
            
            for index, row in df.iterrows():
                # Saltar filas vacías
                if pd.isna(row['placa']) or row['placa'] == '':
                    continue
                
                record = {
                    'placa': str(row['placa']).strip(),
                    'tipo_vehiculo': str(row['tipo_vehiculo']) if pd.notna(row['tipo_vehiculo']) else None,
                    'marca': str(row['marca']) if pd.notna(row['marca']) else None,
                    'modelo': self.clean_numeric_value(row['modelo']),
                    'color': str(row['color']) if pd.notna(row['color']) else None,
                    'estado': str(row['estado']) if pd.notna(row['estado']) else 'Activo',
                    'soat_vencimiento': self.parse_date(row['soat_vencimiento']),
                    'tecnomecanica_vencimiento': self.parse_date(row['tecnomecanica_vencimiento']),
                    'observaciones': str(row['observaciones']) if pd.notna(row['observaciones']) else None,
                    'id_codigo_consumidor': self.clean_numeric_value(row['id_codigo_consumidor']),
                    'fecha_asignacion': self.parse_date(row['fecha_asignacion']),
                    'cedula_propietario': str(row['cedula_propietario']) if pd.notna(row['cedula_propietario']) else None,
                    'nombre_propietario': str(row['nombre_propietario']) if pd.notna(row['nombre_propietario']) else None,
                    'supervisor': str(row['supervisor']) if pd.notna(row['supervisor']) else None,
                    'vin': str(row['vin']) if pd.notna(row['vin']) else None,
                    'numero_de_motor': str(row['numero_de_motor']) if pd.notna(row['numero_de_motor']) else None,
                    'fecha_de_matricula': self.parse_date(row['fecha_de_matricula']),
                    'linea': str(row['linea']) if pd.notna(row['linea']) else None,
                    'comparendos': str(row['comparendos']) if pd.notna(row['comparendos']) else None,
                    'total_comparendos': self.clean_numeric_value(row['total_comparendos']),
                    'kilometraje_actual': self.clean_numeric_value(row['kilometraje_actual']),
                    'proximo_mantenimiento_km': self.clean_numeric_value(row['proximo_mantenimiento_km']),
                    'fecha_ultimo_mantenimiento': self.parse_date(row['fecha_ultimo_mantenimiento'])
                }
                
                processed_data.append(record)
            
            logger.info(f"Datos procesados exitosamente. Registros válidos: {len(processed_data)}")
            return processed_data
            
        except Exception as e:
            logger.error(f"Error al leer el archivo CSV: {e}")
            return None
    
    def update_or_insert_vehicle(self, vehicle_data):
        """Actualizar o insertar un vehículo en la base de datos"""
        try:
            # Verificar si el vehículo existe por placa
            check_query = "SELECT id_parque_automotor FROM parque_automotor WHERE placa = %s"
            self.cursor.execute(check_query, (vehicle_data['placa'],))
            existing_vehicle = self.cursor.fetchone()
            
            if existing_vehicle:
                # Actualizar vehículo existente
                update_query = """
                UPDATE parque_automotor SET 
                    cedula_propietario = %s, nombre_propietario = %s, tipo_vehiculo = %s, 
                    supervisor = %s, soat_vencimiento = %s, tecnomecanica_vencimiento = %s,
                    vin = %s, numero_de_motor = %s, fecha_de_matricula = %s, estado = %s,
                    marca = %s, linea = %s, observaciones = %s, comparendos = %s,
                    total_comparendos = %s, id_codigo_consumidor = %s, fecha_asignacion = %s,
                    modelo = %s, color = %s, fecha_actualizacion = %s, kilometraje_actual = %s,
                    proximo_mantenimiento_km = %s, fecha_ultimo_mantenimiento = %s
                WHERE placa = %s
                """
                
                update_values = (
                    vehicle_data['cedula_propietario'], vehicle_data['nombre_propietario'],
                    vehicle_data['tipo_vehiculo'], vehicle_data['supervisor'],
                    vehicle_data['soat_vencimiento'], vehicle_data['tecnomecanica_vencimiento'],
                    vehicle_data['vin'], vehicle_data['numero_de_motor'],
                    vehicle_data['fecha_de_matricula'], vehicle_data['estado'],
                    vehicle_data['marca'], vehicle_data['linea'], vehicle_data['observaciones'],
                    vehicle_data['comparendos'], vehicle_data['total_comparendos'],
                    vehicle_data['id_codigo_consumidor'], vehicle_data['fecha_asignacion'],
                    vehicle_data['modelo'], vehicle_data['color'], vehicle_data.get('fecha_actualizacion'),
                    vehicle_data['kilometraje_actual'], vehicle_data['proximo_mantenimiento_km'],
                    vehicle_data['fecha_ultimo_mantenimiento'], vehicle_data['placa']
                )
                
                self.cursor.execute(update_query, update_values)
                return 'updated'
            else:
                # Insertar nuevo vehículo
                insert_query = """
                INSERT INTO parque_automotor 
                (cedula_propietario, nombre_propietario, placa, tipo_vehiculo, supervisor,
                 soat_vencimiento, tecnomecanica_vencimiento, vin, numero_de_motor,
                 fecha_de_matricula, estado, marca, linea, observaciones, comparendos,
                 total_comparendos, id_codigo_consumidor, fecha_asignacion, modelo, color,
                 fecha_actualizacion, kilometraje_actual, proximo_mantenimiento_km,
                 fecha_ultimo_mantenimiento)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                insert_values = (
                    vehicle_data['cedula_propietario'], vehicle_data['nombre_propietario'],
                    vehicle_data['placa'], vehicle_data['tipo_vehiculo'], vehicle_data['supervisor'],
                    vehicle_data['soat_vencimiento'], vehicle_data['tecnomecanica_vencimiento'],
                    vehicle_data['vin'], vehicle_data['numero_de_motor'],
                    vehicle_data['fecha_de_matricula'], vehicle_data['estado'],
                    vehicle_data['marca'], vehicle_data['linea'], vehicle_data['observaciones'],
                    vehicle_data['comparendos'], vehicle_data['total_comparendos'],
                    vehicle_data['id_codigo_consumidor'], vehicle_data['fecha_asignacion'],
                    vehicle_data['modelo'], vehicle_data['color'], vehicle_data.get('fecha_actualizacion'),
                    vehicle_data['kilometraje_actual'], vehicle_data['proximo_mantenimiento_km'],
                    vehicle_data['fecha_ultimo_mantenimiento']
                )
                
                self.cursor.execute(insert_query, insert_values)
                return 'inserted'
                
        except mysql.connector.Error as err:
            logger.error(f"Error al procesar vehículo {vehicle_data['placa']}: {str(err)}")
            return 'error'
    
    def process_vehicles(self, vehicles_data):
        """Procesar todos los vehículos"""
        results = {
            'inserted': 0,
            'updated': 0,
            'errors': 0,
            'error_details': []
        }
        
        try:
            for vehicle in vehicles_data:
                try:
                    result = self.update_or_insert_vehicle(vehicle)
                    
                    if result == 'inserted':
                        results['inserted'] += 1
                    elif result == 'updated':
                        results['updated'] += 1
                    else:
                        results['errors'] += 1
                        results['error_details'].append(f"Error procesando vehículo {vehicle['placa']}")
                except Exception as e:
                    results['errors'] += 1
                    results['error_details'].append(f"Error procesando vehículo {vehicle['placa']}: {str(e)}")
                    logger.error(f"Error procesando vehículo {vehicle['placa']}: {str(e)}")
                    continue
            
            # Confirmar transacción
            self.connection.commit()
            logger.info("Transacción confirmada exitosamente")
            
        except Exception as e:
            # Revertir transacción en caso de error
            self.connection.rollback()
            logger.error(f"Error durante el procesamiento. Transacción revertida: {e}")
            results['errors'] = len(vehicles_data)
        
        return results
    
    def close_connection(self):
        """Cerrar conexión a la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Conexión a la base de datos cerrada")
    
    def run(self):
        """Ejecutar el proceso completo de actualización"""
        logger.info("Iniciando proceso de actualización del parque automotor")
        
        # Conectar a la base de datos
        if not self.connect_database():
            return False
        
        try:
            # Leer datos del CSV
            vehicles_data = self.read_csv_data()
            if not vehicles_data:
                logger.error("No se pudieron leer los datos del CSV")
                return False
            
            # Procesar vehículos
            results = self.process_vehicles(vehicles_data)
            
            # Mostrar resultados
            logger.info("=== RESULTADOS DEL PROCESAMIENTO ===")
            logger.info(f"Vehículos insertados: {results['inserted']}")
            logger.info(f"Vehículos actualizados: {results['updated']}")
            logger.info(f"Errores: {results['errors']}")
            
            if results['error_details']:
                logger.info("Detalles de errores:")
                for error in results['error_details']:
                    logger.error(error)
            
            return True
            
        except Exception as e:
            logger.error(f"Error durante la ejecución: {e}")
            return False
        
        finally:
            self.close_connection()

if __name__ == "__main__":
    updater = ParqueAutomotorUpdater()
    success = updater.run()
    
    if success:
        print("\n✅ Proceso completado exitosamente")
        sys.exit(0)
    else:
        print("\n❌ El proceso falló")
        sys.exit(1)