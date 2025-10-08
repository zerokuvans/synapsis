import mysql.connector
from mysql.connector import Error

def test_corrected_query():
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
            
            print("Probando la consulta corregida del endpoint...")
            
            # Esta es la consulta corregida
            query = """
                SELECT 
                    cd.id_cambio as id,
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
                    cd.fecha_registro as created_at
                FROM cambios_dotacion cd
                LEFT JOIN recurso_operativo ro ON cd.id_codigo_consumidor = ro.id_codigo_consumidor
                ORDER BY cd.fecha_cambio DESC, cd.fecha_registro DESC
            """
            
            try:
                cursor.execute(query)
                cambios = cursor.fetchall()
                print(f"✓ Consulta ejecutada exitosamente. Registros encontrados: {len(cambios)}")
                
                if cambios:
                    print("\n✓ Primer registro encontrado:")
                    primer_cambio = cambios[0]
                    print(f"  ID: {primer_cambio['id']}")
                    print(f"  Técnico: {primer_cambio['tecnico_nombre']}")
                    print(f"  Fecha: {primer_cambio['fecha_cambio']}")
                    print(f"  Observaciones: {primer_cambio['observaciones']}")
                    
                    # Simular el procesamiento del endpoint
                    elementos_modificados = []
                    
                    if primer_cambio['pantalon']:
                        elementos_modificados.append(f"Pantalón: {primer_cambio['pantalon']} (Talla: {primer_cambio['pantalon_talla'] or 'N/A'})")
                    if primer_cambio['camisetagris']:
                        elementos_modificados.append(f"Camiseta Gris: {primer_cambio['camisetagris']} (Talla: {primer_cambio['camiseta_gris_talla'] or 'N/A'})")
                    if primer_cambio['guerrera']:
                        elementos_modificados.append(f"Guerrera: {primer_cambio['guerrera']} (Talla: {primer_cambio['guerrera_talla'] or 'N/A'})")
                    if primer_cambio['camisetapolo']:
                        elementos_modificados.append(f"Camiseta Polo: {primer_cambio['camisetapolo']} (Talla: {primer_cambio['camiseta_polo_talla'] or 'N/A'})")
                    if primer_cambio['guantes_nitrilo']:
                        elementos_modificados.append(f"Guantes Nitrilo: {primer_cambio['guantes_nitrilo']}")
                    if primer_cambio['guantes_carnaza']:
                        elementos_modificados.append(f"Guantes Carnaza: {primer_cambio['guantes_carnaza']}")
                    if primer_cambio['gafas']:
                        elementos_modificados.append(f"Gafas: {primer_cambio['gafas']}")
                    if primer_cambio['gorra']:
                        elementos_modificados.append(f"Gorra: {primer_cambio['gorra']}")
                    if primer_cambio['casco']:
                        elementos_modificados.append(f"Casco: {primer_cambio['casco']}")
                    if primer_cambio['botas']:
                        elementos_modificados.append(f"Botas: {primer_cambio['botas']} (Talla: {primer_cambio['botas_talla'] or 'N/A'})")
                    
                    print(f"  Elementos modificados: {', '.join(elementos_modificados) if elementos_modificados else 'Sin elementos especificados'}")
                    
                    print("\n✓ El endpoint debería funcionar correctamente ahora.")
                else:
                    print("No se encontraron registros, pero la consulta es válida.")
                    
            except Error as query_error:
                print(f"✗ ERROR EN LA CONSULTA: {query_error}")
                
    except Error as e:
        print(f"✗ Error de conexión: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    test_corrected_query()