import mysql.connector
from datetime import date

# Configuración de la base de datos
config = {
    'user': 'root',
    'password': '732137A031E4b@',
    'host': 'localhost',
    'database': 'capired'
}

def test_sql_query():
    """Probar la consulta SQL directamente"""
    
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        
        supervisor_actual = 'SILVA CASTRO DANIEL ALBERTO'
        fecha_consulta = date(2025, 10, 8)
        
        print("🔍 PROBANDO CONSULTA SQL DIRECTA")
        print("=" * 60)
        print(f"Supervisor: {supervisor_actual}")
        print(f"Fecha: {fecha_consulta}")
        print()
        
        # Consulta EXACTA del endpoint
        consulta = """
            SELECT 
                a.cedula,
                a.tecnico,
                a.carpeta,
                a.super,
                a.carpeta_dia,
                COALESCE(t.nombre_tipificacion, a.carpeta_dia) AS carpeta_dia_nombre,
                a.eventos AS eventos,
                COALESCE(pc.presupuesto_diario, 0) AS presupuesto_diario,
                a.valor,
                a.estado,
                a.novedad,
                a.id_asistencia
            FROM asistencia a
            LEFT JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
            LEFT JOIN presupuesto_carpeta pc ON t.nombre_tipificacion = pc.presupuesto_carpeta
            WHERE a.super = %s AND DATE(a.fecha_asistencia) = %s
            AND a.id_asistencia = (
                SELECT MAX(a2.id_asistencia)
                FROM asistencia a2
                WHERE a2.cedula = a.cedula 
                AND a2.super = %s 
                AND DATE(a2.fecha_asistencia) = %s
            )
            ORDER BY a.tecnico
        """
        
        print("📋 EJECUTANDO CONSULTA...")
        cursor.execute(consulta, (supervisor_actual, fecha_consulta, supervisor_actual, fecha_consulta))
        registros = cursor.fetchall()
        
        print(f"📊 Registros obtenidos: {len(registros)}")
        
        # Verificar duplicados por cédula
        cedulas_vistas = {}
        duplicados = []
        
        print("\n📋 REGISTROS DEVUELTOS:")
        for i, registro in enumerate(registros, 1):
            cedula = registro['cedula']
            tecnico = registro['tecnico']
            id_asistencia = registro['id_asistencia']
            
            if cedula in cedulas_vistas:
                duplicados.append({
                    'cedula': cedula,
                    'tecnico': tecnico,
                    'primera_aparicion': cedulas_vistas[cedula],
                    'segunda_aparicion': i,
                    'id_asistencia': id_asistencia
                })
                print(f"🔴 DUPLICADO #{len(duplicados)}: {cedula} - {tecnico} (ID: {id_asistencia})")
            else:
                cedulas_vistas[cedula] = i
                print(f"✅ Fila {i:2d}: {cedula} - {tecnico} (ID: {id_asistencia})")
        
        print(f"\n📊 RESUMEN:")
        print(f"   Total registros: {len(registros)}")
        print(f"   Técnicos únicos: {len(cedulas_vistas)}")
        print(f"   Duplicados encontrados: {len(duplicados)}")
        
        if duplicados:
            print(f"🔴 ¡PROBLEMA! La consulta devuelve {len(duplicados)} duplicados")
            
            # Investigar por qué hay duplicados
            print(f"\n🔍 INVESTIGANDO DUPLICADOS:")
            for dup in duplicados:
                cedula = dup['cedula']
                print(f"\n   Cédula: {cedula}")
                
                # Buscar todos los registros de esta cédula
                cursor.execute("""
                    SELECT id_asistencia, tecnico, carpeta_dia, eventos, valor, fecha_asistencia
                    FROM asistencia 
                    WHERE cedula = %s AND super = %s AND DATE(fecha_asistencia) = %s
                    ORDER BY id_asistencia DESC
                """, (cedula, supervisor_actual, fecha_consulta))
                
                todos_registros = cursor.fetchall()
                print(f"   Total registros para esta cédula: {len(todos_registros)}")
                
                for j, reg in enumerate(todos_registros):
                    print(f"     {j+1}. ID: {reg['id_asistencia']}, Técnico: {reg['tecnico']}, Eventos: {reg['eventos']}, Valor: {reg['valor']}")
                
                # Verificar qué devuelve la subquery
                cursor.execute("""
                    SELECT MAX(a2.id_asistencia) as max_id
                    FROM asistencia a2
                    WHERE a2.cedula = %s 
                    AND a2.super = %s 
                    AND DATE(a2.fecha_asistencia) = %s
                """, (cedula, supervisor_actual, fecha_consulta))
                
                max_result = cursor.fetchone()
                print(f"   MAX(id_asistencia) de subquery: {max_result['max_id']}")
        else:
            print("✅ ¡PERFECTO! La consulta no devuelve duplicados")
        
        cursor.close()
        connection.close()
        
        return len(duplicados) == 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_sql_query()