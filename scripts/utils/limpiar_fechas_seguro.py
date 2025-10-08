import mysql.connector
from datetime import datetime, timedelta

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'port': 3306
}

def limpiar_fechas_seguro():
    """Limpiar fechas inválidas usando comparaciones de cadenas"""
    print("=== LIMPIEZA SEGURA DE FECHAS INVÁLIDAS ===")
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        print("\n1. VERIFICANDO FECHAS INVÁLIDAS CON COMPARACIÓN DE CADENAS:")
        
        # Contar fechas inválidas usando comparación de cadenas
        cursor.execute("""
            SELECT COUNT(*) as soat_invalidos 
            FROM parque_automotor 
            WHERE CAST(soat_vencimiento AS CHAR) = '0000-00-00'
        """)
        soat_invalidos = cursor.fetchone()['soat_invalidos']
        print(f"   ✓ SOAT con fechas '0000-00-00': {soat_invalidos}")
        
        cursor.execute("""
            SELECT COUNT(*) as tecno_invalidos 
            FROM parque_automotor 
            WHERE CAST(tecnomecanica_vencimiento AS CHAR) = '0000-00-00'
        """)
        tecno_invalidos = cursor.fetchone()['tecno_invalidos']
        print(f"   ✓ Tecnomecánica con fechas '0000-00-00': {tecno_invalidos}")
        
        print("\n2. LIMPIANDO FECHAS INVÁLIDAS:")
        
        # Limpiar fechas SOAT inválidas
        if soat_invalidos > 0:
            cursor.execute("""
                UPDATE parque_automotor 
                SET soat_vencimiento = NULL 
                WHERE CAST(soat_vencimiento AS CHAR) = '0000-00-00'
            """)
            print(f"   ✓ {soat_invalidos} fechas SOAT inválidas convertidas a NULL")
        
        # Limpiar fechas Tecnomecánica inválidas
        if tecno_invalidos > 0:
            cursor.execute("""
                UPDATE parque_automotor 
                SET tecnomecanica_vencimiento = NULL 
                WHERE CAST(tecnomecanica_vencimiento AS CHAR) = '0000-00-00'
            """)
            print(f"   ✓ {tecno_invalidos} fechas Tecnomecánica inválidas convertidas a NULL")
        
        # Confirmar cambios
        connection.commit()
        print("   ✓ Cambios guardados en la base de datos")
        
        print("\n3. AGREGANDO DATOS DE PRUEBA:")
        
        # Obtener algunas placas para actualizar con fechas de prueba
        cursor.execute("SELECT placa FROM parque_automotor LIMIT 10")
        placas = cursor.fetchall()
        
        if len(placas) >= 6:
            # Fechas de prueba
            fecha_soat_proximo = (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
            fecha_tecno_proximo = (datetime.now() + timedelta(days=25)).strftime('%Y-%m-%d')
            fecha_soat_vencido = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
            fecha_tecno_vencido = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
            fecha_soat_critico = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
            fecha_tecno_critico = (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d')
            
            # Actualizar vehículos con diferentes estados
            updates = [
                (placas[0]['placa'], fecha_soat_proximo, None, "SOAT próximo"),
                (placas[1]['placa'], None, fecha_tecno_proximo, "Tecno próxima"),
                (placas[2]['placa'], fecha_soat_vencido, None, "SOAT vencido"),
                (placas[3]['placa'], None, fecha_tecno_vencido, "Tecno vencida"),
                (placas[4]['placa'], fecha_soat_critico, None, "SOAT crítico"),
                (placas[5]['placa'], None, fecha_tecno_critico, "Tecno crítica")
            ]
            
            for placa, soat, tecno, descripcion in updates:
                if soat:
                    cursor.execute("""
                        UPDATE parque_automotor 
                        SET soat_vencimiento = %s
                        WHERE placa = %s
                    """, (soat, placa))
                if tecno:
                    cursor.execute("""
                        UPDATE parque_automotor 
                        SET tecnomecanica_vencimiento = %s
                        WHERE placa = %s
                    """, (tecno, placa))
                print(f"   ✓ {descripcion}: Placa {placa}")
            
            connection.commit()
            print("   ✓ Datos de prueba agregados exitosamente")
        
        print("\n4. VERIFICANDO RESULTADOS:")
        
        # Verificar fechas válidas después de la limpieza
        cursor.execute("""
            SELECT COUNT(*) as soat_validos 
            FROM parque_automotor 
            WHERE soat_vencimiento IS NOT NULL 
            AND CAST(soat_vencimiento AS CHAR) != '0000-00-00'
        """)
        soat_validos = cursor.fetchone()['soat_validos']
        print(f"   ✓ SOAT con fechas válidas: {soat_validos}")
        
        cursor.execute("""
            SELECT COUNT(*) as tecno_validos 
            FROM parque_automotor 
            WHERE tecnomecanica_vencimiento IS NOT NULL 
            AND CAST(tecnomecanica_vencimiento AS CHAR) != '0000-00-00'
        """)
        tecno_validos = cursor.fetchone()['tecno_validos']
        print(f"   ✓ Tecnomecánica con fechas válidas: {tecno_validos}")
        
        # Mostrar ejemplos de vehículos con fechas válidas
        cursor.execute("""
            SELECT placa, soat_vencimiento, tecnomecanica_vencimiento
            FROM parque_automotor 
            WHERE (soat_vencimiento IS NOT NULL AND CAST(soat_vencimiento AS CHAR) != '0000-00-00')
               OR (tecnomecanica_vencimiento IS NOT NULL AND CAST(tecnomecanica_vencimiento AS CHAR) != '0000-00-00')
            LIMIT 8
        """)
        
        ejemplos = cursor.fetchall()
        if ejemplos:
            print("\n   Ejemplos de vehículos con fechas válidas:")
            for vehiculo in ejemplos:
                print(f"     - Placa: {vehiculo['placa']}")
                if vehiculo['soat_vencimiento'] and str(vehiculo['soat_vencimiento']) != '0000-00-00':
                    print(f"       SOAT: {vehiculo['soat_vencimiento']}")
                if vehiculo['tecnomecanica_vencimiento'] and str(vehiculo['tecnomecanica_vencimiento']) != '0000-00-00':
                    print(f"       Tecno: {vehiculo['tecnomecanica_vencimiento']}")
        
        cursor.close()
        connection.close()
        
        print("\n✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la limpieza: {str(e)}")
        if 'connection' in locals():
            connection.rollback()
        return False

if __name__ == "__main__":
    limpiar_fechas_seguro()