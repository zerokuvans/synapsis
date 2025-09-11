import mysql.connector
from mysql.connector import Error

def test_endpoint_query():
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            print("Probando la consulta exacta del endpoint...")
            
            # Esta es la consulta exacta del endpoint
            query = """
                SELECT 
                    cd.id,
                    cd.id_codigo_consumidor,
                    ro.nombre as tecnico_nombre,
                    cd.fecha_cambio,
                    cd.pantalon,
                    cd.pantalon_talla,
                    cd.camisetagris,
                    cd.camiseta_gris_talla,
                    cd.guerrera,
                    cd.guerrera_talla,
                    cd.camisetapolo,
                    cd.camiseta_polo_talla,
                    cd.guantes_nitrilo,
                    cd.guantes_carnaza,
                    cd.gafas,
                    cd.gorra,
                    cd.casco,
                    cd.botas,
                    cd.botas_talla,
                    cd.observaciones,
                    cd.created_at
                FROM cambios_dotacion cd
                LEFT JOIN recurso_operativo ro ON cd.id_codigo_consumidor = ro.id_codigo_consumidor
                ORDER BY cd.fecha_cambio DESC, cd.created_at DESC
            """
            
            try:
                cursor.execute(query)
                cambios = cursor.fetchall()
                print(f"Consulta ejecutada exitosamente. Registros encontrados: {len(cambios)}")
                
                if cambios:
                    print("\nPrimer registro:")
                    for key, value in cambios[0].items():
                        print(f"  {key}: {value}")
                else:
                    print("No se encontraron registros.")
                    
            except Error as query_error:
                print(f"ERROR EN LA CONSULTA: {query_error}")
                print("\nVerificando estructura de la tabla...")
                
                # Verificar qué campos existen realmente
                cursor.execute("DESCRIBE cambios_dotacion")
                columnas = cursor.fetchall()
                print("\nCampos disponibles en cambios_dotacion:")
                for columna in columnas:
                    print(f"  {columna['Field']}")
                    
                # Verificar si existe el campo 'nombre' en recurso_operativo
                cursor.execute("DESCRIBE recurso_operativo")
                columnas_ro = cursor.fetchall()
                print("\nCampos disponibles en recurso_operativo:")
                for columna in columnas_ro:
                    print(f"  {columna['Field']}")
                
    except Error as e:
        print(f"Error de conexión: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    test_endpoint_query()