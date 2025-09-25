#!/usr/bin/env python3
"""
Script para verificar y actualizar la tabla permisos_transicion
"""

import mysql.connector

def actualizar_permisos_transicion():
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = connection.cursor(dictionary=True)
        
        print("🔧 Actualizando estructura de permisos_transicion...")
        
        # Actualizar las columnas ENUM para incluir todos los estados
        try:
            cursor.execute("""
                ALTER TABLE permisos_transicion 
                MODIFY COLUMN estado_origen ENUM(
                    'PENDIENTE', 'REGISTRADA', 'EN_REVISION', 'APROBADA', 
                    'RECHAZADA', 'PROCESADA', 'COMPLETADA', 'CANCELADA'
                )
            """)
            print("✅ Columna estado_origen actualizada")
        except Exception as e:
            print(f"⚠️ Error actualizando estado_origen: {e}")
        
        try:
            cursor.execute("""
                ALTER TABLE permisos_transicion 
                MODIFY COLUMN estado_destino ENUM(
                    'PENDIENTE', 'REGISTRADA', 'EN_REVISION', 'APROBADA', 
                    'RECHAZADA', 'PROCESADA', 'COMPLETADA', 'CANCELADA'
                )
            """)
            print("✅ Columna estado_destino actualizada")
        except Exception as e:
            print(f"⚠️ Error actualizando estado_destino: {e}")
        
        # Verificar estructura actualizada
        cursor.execute("DESCRIBE permisos_transicion")
        estructura = cursor.fetchall()
        print("\n📋 Estructura actualizada:")
        for campo in estructura:
            print(f"  - {campo['Field']}: {campo['Type']}")
        
        # Obtener rol de logística
        cursor.execute("SELECT id_roles FROM roles WHERE nombre_rol = 'logistica'")
        rol_logistica = cursor.fetchone()
        
        if rol_logistica:
            rol_id = rol_logistica['id_roles']
            print(f"\n🔧 Configurando permisos para rol logística (ID: {rol_id})...")
            
            # Configurar permisos básicos para rol logística
            estados_transiciones = [
                ('PENDIENTE', 'EN_REVISION'),
                ('PENDIENTE', 'RECHAZADA'),
                ('EN_REVISION', 'APROBADA'),
                ('EN_REVISION', 'RECHAZADA'),
                ('APROBADA', 'COMPLETADA'),
                ('APROBADA', 'PROCESADA'),
                ('REGISTRADA', 'EN_REVISION'),
                ('REGISTRADA', 'RECHAZADA'),
            ]
            
            for estado_origen, estado_destino in estados_transiciones:
                # Verificar si ya existe
                cursor.execute("""
                    SELECT id FROM permisos_transicion 
                    WHERE rol_id = %s AND estado_origen = %s AND estado_destino = %s
                """, (rol_id, estado_origen, estado_destino))
                
                existe = cursor.fetchone()
                
                if not existe:
                    cursor.execute("""
                        INSERT INTO permisos_transicion (rol_id, estado_origen, estado_destino, permitido)
                        VALUES (%s, %s, %s, TRUE)
                    """, (rol_id, estado_origen, estado_destino))
                    print(f"  ✅ Agregado: {estado_origen} → {estado_destino}")
                else:
                    print(f"  ⚠️ Ya existe: {estado_origen} → {estado_destino}")
            
            connection.commit()
            print("✅ Permisos configurados correctamente")
        else:
            print("❌ No se encontró rol de logística")
        
        # Verificar datos finales
        cursor.execute("SELECT COUNT(*) as total FROM permisos_transicion")
        total = cursor.fetchone()['total']
        print(f"\n📊 Total de registros: {total}")
        
        # Mostrar permisos del rol logística
        if rol_logistica:
            cursor.execute("""
                SELECT estado_origen, estado_destino, permitido 
                FROM permisos_transicion 
                WHERE rol_id = %s
                ORDER BY estado_origen, estado_destino
            """, (rol_id,))
            permisos = cursor.fetchall()
            print(f"\n📝 Permisos del rol logística:")
            for permiso in permisos:
                estado = '✅' if permiso['permitido'] else '❌'
                print(f"  {estado} {permiso['estado_origen']} → {permiso['estado_destino']}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    actualizar_permisos_transicion()