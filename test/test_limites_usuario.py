import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

def test_limites_usuario():
    """Probar los límites de materiales para el usuario 1019112308"""
    connection = None
    try:
        # Configuración de la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='732137A031E4b@',
            database='capired',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Buscar el id_codigo_consumidor del usuario 1019112308
            cursor.execute("""
                SELECT id_codigo_consumidor, cargo, carpeta, nombre
                FROM recurso_operativo 
                WHERE recurso_operativo_cedula = %s
            """, ('1019112308',))
            
            usuario = cursor.fetchone()
            if not usuario:
                print("Usuario no encontrado")
                return
            
            print(f"Usuario: {usuario['nombre']}")
            print(f"Cargo: {usuario['cargo']}")
            print(f"Carpeta: {usuario['carpeta']}")
            print(f"ID: {usuario['id_codigo_consumidor']}")
            
            # Definir límites por área (copiado del código principal)
            limites_por_area = {
                'INSTALACION': {
                    'cinta_aislante': {'cantidad': 5, 'periodo': 15},
                    'silicona': {'cantidad': 16, 'periodo': 7},
                    'amarres_negros': {'cantidad': 50, 'periodo': 15},
                    'amarres_blancos': {'cantidad': 50, 'periodo': 15},
                    'grapas_blancas': {'cantidad': 200, 'periodo': 15},
                    'grapas_negras': {'cantidad': 200, 'periodo': 15}
                },
                'POSTVENTA': {
                    'cinta_aislante': {'cantidad': 3, 'periodo': 15},
                    'silicona': {'cantidad': 12, 'periodo': 7},
                    'amarres_negros': {'cantidad': 30, 'periodo': 15},
                    'amarres_blancos': {'cantidad': 30, 'periodo': 15},
                    'grapas_blancas': {'cantidad': 100, 'periodo': 15},
                    'grapas_negras': {'cantidad': 100, 'periodo': 15}
                },
                'MANTENIMIENTO': {
                    'cinta_aislante': {'cantidad': 4, 'periodo': 15},
                    'silicona': {'cantidad': 14, 'periodo': 7},
                    'amarres_negros': {'cantidad': 40, 'periodo': 15},
                    'amarres_blancos': {'cantidad': 40, 'periodo': 15},
                    'grapas_blancas': {'cantidad': 150, 'periodo': 15},
                    'grapas_negras': {'cantidad': 150, 'periodo': 15}
                },
                'SUPERVISION': {
                    'cinta_aislante': {'cantidad': 2, 'periodo': 15},
                    'silicona': {'cantidad': 8, 'periodo': 7},
                    'amarres_negros': {'cantidad': 20, 'periodo': 15},
                    'amarres_blancos': {'cantidad': 20, 'periodo': 15},
                    'grapas_blancas': {'cantidad': 50, 'periodo': 15},
                    'grapas_negras': {'cantidad': 50, 'periodo': 15}
                },
                'FTTH INSTALACIONES': {
                    'cinta_aislante': {'cantidad': 5, 'periodo': 15},
                    'silicona': {'cantidad': 16, 'periodo': 7},
                    'amarres_negros': {'cantidad': 50, 'periodo': 15},
                    'amarres_blancos': {'cantidad': 50, 'periodo': 15},
                    'grapas_blancas': {'cantidad': 200, 'periodo': 15},
                    'grapas_negras': {'cantidad': 200, 'periodo': 15}
                }
            }
            
            # Aplicar la nueva lógica de mapeo
            cargo = usuario.get('cargo', '').upper()
            carpeta = usuario.get('carpeta', '').upper()
            
            # Mapeo mejorado considerando cargo y carpeta
            if 'FTTH INSTALACIONES' in cargo:
                area_trabajo = 'FTTH INSTALACIONES'
            elif 'INSTALACION' in cargo or ('FTTH' in cargo and 'INSTALACION' in carpeta):
                area_trabajo = 'INSTALACION'
            elif 'POSTVENTA' in cargo or 'POSTVENTA' in carpeta:
                area_trabajo = 'POSTVENTA'
            elif 'MANTENIMIENTO' in cargo or 'ARREGLOS' in carpeta or 'MANTENIMIENTO' in carpeta:
                area_trabajo = 'MANTENIMIENTO'
            elif 'SUPERVISION' in cargo or 'SUPERVISOR' in cargo:
                area_trabajo = 'SUPERVISION'
            elif 'TECNICO' in cargo and 'ARREGLOS' in carpeta:
                # Caso específico: técnicos con carpeta de arreglos van a mantenimiento
                area_trabajo = 'MANTENIMIENTO'
            else:
                area_trabajo = 'INSTALACION'  # Default
            
            print(f"\nÁrea de trabajo asignada: {area_trabajo}")
            
            limite_config = limites_por_area[area_trabajo]
            
            print(f"\nLímites asignados para {area_trabajo}:")
            for material, config in limite_config.items():
                print(f"- {material}: {config['cantidad']} unidades cada {config['periodo']} días")
            
            # Calcular estado actual para cada material
            print(f"\nEstado actual de materiales:")
            id_codigo_consumidor = usuario['id_codigo_consumidor']
            
            for material, config in limite_config.items():
                limite_total = config['cantidad']
                periodo_dias = config['periodo']
                
                # Calcular fecha límite para el período
                fecha_limite = datetime.now() - timedelta(days=periodo_dias)
                
                # Obtener material asignado en el período
                cursor.execute(f"""
                    SELECT COALESCE(SUM(CAST({material} AS UNSIGNED)), 0) as total_asignadas
                    FROM ferretero 
                    WHERE id_codigo_consumidor = %s 
                    AND fecha_asignacion >= %s
                """, (id_codigo_consumidor, fecha_limite))
                
                resultado = cursor.fetchone()
                asignadas = resultado['total_asignadas'] if resultado else 0
                
                # Calcular disponible
                disponible = max(0, limite_total - asignadas)
                
                print(f"- {material}: {asignadas}/{limite_total} (disponible: {disponible})")
            
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    test_limites_usuario()