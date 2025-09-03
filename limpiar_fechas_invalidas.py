import mysql.connector
from datetime import datetime

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'port': 3306
}

def limpiar_fechas_invalidas():
    """Limpiar fechas inválidas '0000-00-00' de la base de datos"""
    print("=== LIMPIEZA DE FECHAS INVÁLIDAS ===")
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        print("\n1. VERIFICANDO FECHAS INVÁLIDAS:")
        
        # Contar fechas inválidas de SOAT
        cursor.execute("""
            SELECT COUNT(*) as soat_invalidos 
            FROM parque_automotor 
            WHERE soat_vencimiento = '0000-00-00'
        """)
        soat_invalidos = cursor.fetchone()['soat_invalidos']
        print(f"   ✓ SOAT con fechas '0000-00-00': {soat_invalidos}")
        
        # Contar fechas inválidas de Tecnomecánica
        cursor.execute("""
            SELECT COUNT(*) as tecno_invalidos 
            FROM parque_automotor 
            WHERE tecnomecanica_vencimiento = '0000-00-00'
        """)
        tecno_invalidos = cursor.fetchone()['tecno_invalidos']
        print(f"   ✓ Tecnomecánica con fechas '0000-00-00': {tecno_invalidos}")
        
        print("\n2. LIMPIANDO FECHAS INVÁLIDAS:")
        
        # Limpiar fechas SOAT inválidas (convertir a NULL)
        if soat_invalidos > 0:
            cursor.execute("""
                UPDATE parque_automotor 
                SET soat_vencimiento = NULL 
                WHERE soat_vencimiento = '0000-00-00'
            """)
            print(f"   ✓ {soat_invalidos} fechas SOAT inválidas convertidas a NULL")
        
        # Limpiar fechas Tecnomecánica inválidas (convertir a NULL)
        if tecno_invalidos > 0:
            cursor.execute("""
                UPDATE parque_automotor 
                SET tecnomecanica_vencimiento = NULL 
                WHERE tecnomecanica_vencimiento = '0000-00-00'
            """)
            print(f"   ✓ {tecno_invalidos} fechas Tecnomecánica inválidas convertidas a NULL")
        
        # Confirmar cambios
        connection.commit()
        print("   ✓ Cambios guardados en la base de datos")
        
        print("\n3. AGREGANDO DATOS DE PRUEBA:")
        
        # Agregar algunas fechas de vencimiento válidas para pruebas
        fecha_soat_proximo = (datetime.now() + datetime.timedelta(days=15)).strftime('%Y-%m-%d')
        fecha_tecno_proximo = (datetime.now() + datetime.timedelta(days=25)).strftime('%Y-%m-%d')
        fecha_soat_vencido = (datetime.now() - datetime.timedelta(days=5)).strftime('%Y-%m-%d')
        
        # Actualizar algunos vehículos con fechas de prueba
        cursor.execute("""
            UPDATE parque_automotor 
            SET soat_vencimiento = %s
            WHERE placa LIKE 'ABC%' OR placa LIKE 'XYZ%'
            LIMIT 3
        """, (fecha_soat_proximo,))
        
        cursor.execute("""
            UPDATE parque_automotor 
            SET tecnomecanica_vencimiento = %s
            WHERE placa LIKE 'DEF%' OR placa LIKE 'GHI%'
            LIMIT 3
        """, (fecha_tecno_proximo,))
        
        cursor.execute("""
            UPDATE parque_automotor 
            SET soat_vencimiento = %s
            WHERE placa LIKE 'JKL%' OR placa LIKE 'MNO%'
            LIMIT 2
        """, (fecha_soat_vencido,))
        
        # Obtener algunas placas reales para actualizar
        cursor.execute("SELECT placa FROM parque_automotor LIMIT 10")
        placas = cursor.fetchall()
        
        if len(placas) >= 5:
            # Actualizar las primeras 5 placas con fechas de prueba
            for i, placa_row in enumerate(placas[:5]):
                placa = placa_row['placa']
                if i < 2:
                    # SOAT próximo a vencer
                    cursor.execute("""
                        UPDATE parque_automotor 
                        SET soat_vencimiento = %s
                        WHERE placa = %s
                    """, (fecha_soat_proximo, placa))
                elif i < 4:
                    # Tecnomecánica próxima a vencer
                    cursor.execute("""
                        UPDATE parque_automotor 
                        SET tecnomecanica_vencimiento = %s
                        WHERE placa = %s
                    """, (fecha_tecno_proximo, placa))
                else:
                    # SOAT vencido
                    cursor.execute("""
                        UPDATE parque_automotor 
                        SET soat_vencimiento = %s
                        WHERE placa = %s
                    """, (fecha_soat_vencido, placa))
        
        connection.commit()
        print(f"   ✓ Datos de prueba agregados:")
        print(f"     - SOAT próximo a vencer (15 días): {fecha_soat_proximo}")
        print(f"     - Tecnomecánica próxima a vencer (25 días): {fecha_tecno_proximo}")
        print(f"     - SOAT vencido (5 días atrás): {fecha_soat_vencido}")
        
        print("\n4. VERIFICANDO RESULTADOS:")
        
        # Verificar fechas válidas después de la limpieza
        cursor.execute("""
            SELECT COUNT(*) as soat_validos 
            FROM parque_automotor 
            WHERE soat_vencimiento IS NOT NULL
        """)
        soat_validos = cursor.fetchone()['soat_validos']
        print(f"   ✓ SOAT con fechas válidas: {soat_validos}")
        
        cursor.execute("""
            SELECT COUNT(*) as tecno_validos 
            FROM parque_automotor 
            WHERE tecnomecanica_vencimiento IS NOT NULL
        """)
        tecno_validos = cursor.fetchone()['tecno_validos']
        print(f"   ✓ Tecnomecánica con fechas válidas: {tecno_validos}")
        
        # Mostrar algunos ejemplos
        cursor.execute("""
            SELECT placa, soat_vencimiento, tecnomecanica_vencimiento,
                   DATEDIFF(soat_vencimiento, CURDATE()) as dias_soat,
                   DATEDIFF(tecnomecanica_vencimiento, CURDATE()) as dias_tecno
            FROM parque_automotor 
            WHERE (soat_vencimiento IS NOT NULL OR tecnomecanica_vencimiento IS NOT NULL)
            ORDER BY 
                LEAST(
                    COALESCE(soat_vencimiento, '9999-12-31'),
                    COALESCE(tecnomecanica_vencimiento, '9999-12-31')
                ) ASC
            LIMIT 5
        """)
        
        ejemplos = cursor.fetchall()
        if ejemplos:
            print("\n   Ejemplos de vehículos con fechas válidas:")
            for vehiculo in ejemplos:
                print(f"     - Placa: {vehiculo['placa']}")
                if vehiculo['soat_vencimiento']:
                    print(f"       SOAT: {vehiculo['soat_vencimiento']} (días: {vehiculo['dias_soat']})")
                if vehiculo['tecnomecanica_vencimiento']:
                    print(f"       Tecno: {vehiculo['tecnomecanica_vencimiento']} (días: {vehiculo['dias_tecno']})")
        
        cursor.close()
        connection.close()
        
        print("\n✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la limpieza: {str(e)}")
        return False

if __name__ == "__main__":
    limpiar_fechas_invalidas()