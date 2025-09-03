import mysql.connector
from datetime import datetime, timedelta

# Configuración de la base de datos
config = {
    'user': 'root',
    'password': '732137A031E4b@',
    'host': 'localhost',
    'database': 'capired',
    'raise_on_warnings': True
}

def verificar_datos_vencimientos():
    try:
        # Conectar a la base de datos
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(dictionary=True)
        
        print("=== VERIFICACIÓN DE DATOS DE VENCIMIENTOS ===")
        print()
        
        # 1. Verificar estructura de la tabla
        print("1. Estructura de la tabla parque_automotor:")
        cursor.execute("DESCRIBE parque_automotor")
        columns = cursor.fetchall()
        for col in columns:
            if 'vencimiento' in col['Field'].lower():
                print(f"   - {col['Field']}: {col['Type']} (Null: {col['Null']})")
        print()
        
        # 2. Contar total de vehículos
        cursor.execute("SELECT COUNT(*) as total FROM parque_automotor")
        total = cursor.fetchone()['total']
        print(f"2. Total de vehículos en la tabla: {total}")
        print()
        
        # 3. Verificar vehículos con fechas de vencimiento
        print("3. Vehículos con fechas de vencimiento:")
        
        # SOAT
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM parque_automotor 
            WHERE soat_vencimiento IS NOT NULL
        """)
        soat_count = cursor.fetchone()['count']
        print(f"   - Con SOAT vencimiento: {soat_count}")
        
        # Tecnomecánica
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM parque_automotor 
            WHERE tecnomecanica_vencimiento IS NOT NULL
        """)
        tecno_count = cursor.fetchone()['count']
        print(f"   - Con Tecnomecánica vencimiento: {tecno_count}")
        print()
        
        # 4. Mostrar algunos ejemplos de vehículos con vencimientos
        print("4. Ejemplos de vehículos con vencimientos:")
        cursor.execute("""
            SELECT placa, tipo_vehiculo, soat_vencimiento, tecnomecanica_vencimiento
            FROM parque_automotor 
            WHERE soat_vencimiento IS NOT NULL
               OR tecnomecanica_vencimiento IS NOT NULL
            LIMIT 10
        """)
        
        ejemplos = cursor.fetchall()
        for vehiculo in ejemplos:
            print(f"   - Placa: {vehiculo['placa']}")
            print(f"     Tipo: {vehiculo['tipo_vehiculo']}")
            print(f"     SOAT: {vehiculo['soat_vencimiento']}")
            print(f"     Tecnomecánica: {vehiculo['tecnomecanica_vencimiento']}")
            print()
        
        # 5. Verificar vencimientos próximos (próximos 30 días)
        print("5. Vencimientos próximos (próximos 30 días):")
        fecha_limite = datetime.now() + timedelta(days=30)
        
        cursor.execute("""
            SELECT placa, 'SOAT' as tipo_documento, soat_vencimiento as fecha_vencimiento,
                   DATEDIFF(soat_vencimiento, CURDATE()) as dias_restantes
            FROM parque_automotor 
            WHERE soat_vencimiento IS NOT NULL 
            AND soat_vencimiento != '0000-00-00'
            AND soat_vencimiento <= %s
            AND soat_vencimiento >= CURDATE()
            
            UNION ALL
            
            SELECT placa, 'TECNOMECANICA' as tipo_documento, tecnomecanica_vencimiento as fecha_vencimiento,
                   DATEDIFF(tecnomecanica_vencimiento, CURDATE()) as dias_restantes
            FROM parque_automotor 
            WHERE tecnomecanica_vencimiento IS NOT NULL 
            AND tecnomecanica_vencimiento != '0000-00-00'
            AND tecnomecanica_vencimiento <= %s
            AND tecnomecanica_vencimiento >= CURDATE()
            
            ORDER BY fecha_vencimiento ASC
        """, (fecha_limite.strftime('%Y-%m-%d'), fecha_limite.strftime('%Y-%m-%d')))
        
        vencimientos_proximos = cursor.fetchall()
        
        if vencimientos_proximos:
            for venc in vencimientos_proximos:
                print(f"   - {venc['placa']} - {venc['tipo_documento']}: {venc['fecha_vencimiento']} ({venc['dias_restantes']} días)")
        else:
            print("   - No hay vencimientos próximos en los próximos 30 días")
        
        print()
        print(f"Total de vencimientos próximos: {len(vencimientos_proximos)}")
        
    except mysql.connector.Error as err:
        print(f"Error de MySQL: {err}")
    except Exception as e:
        print(f"Error general: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'cnx' in locals():
            cnx.close()

if __name__ == "__main__":
    verificar_datos_vencimientos()