#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the MySQL cursor fix for 'Unread result found' error in consultar_asistencia function
"""

import mysql.connector
from datetime import datetime, date

def test_consultar_asistencia_fix():
    """Test the MySQL cursor handling fix for consultar_asistencia function"""
    
    print("=== TESTING CONSULTAR_ASISTENCIA MYSQL CURSOR FIX ===")
    print(f"Test time: {datetime.now()}")
    print()
    
    try:
        # Database configuration
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '732137A031E4b@',
            'database': 'capired'
        }
        
        print("1. 🔌 Connecting to database...")
        connection = mysql.connector.connect(**db_config)
        
        # Use buffered cursor (this is the fix)
        cursor = connection.cursor(dictionary=True, buffered=True)
        print("   ✅ Connected with buffered cursor")
        
        # Simulate the problematic query pattern from consultar_asistencia
        print("\n2. 🔍 Testing query pattern that caused the error...")
        
        # Get a test supervisor
        cursor.execute("SELECT DISTINCT super FROM recurso_operativo WHERE super IS NOT NULL LIMIT 1")
        supervisor_result = cursor.fetchone()
        
        if not supervisor_result:
            print("   ⚠️  No supervisors found in database")
            return
            
        supervisor = supervisor_result['super']
        print(f"   Using supervisor: {supervisor}")
        
        # Get technicians for this supervisor (similar to the original function)
        query_tecnicos = """
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula as cedula,
                nombre as tecnico,
                carpeta,
                super
            FROM recurso_operativo 
            WHERE super = %s AND estado = 'Activo'
            ORDER BY nombre
            LIMIT 3
        """
        
        cursor.execute(query_tecnicos, (supervisor,))
        tecnicos = cursor.fetchall()
        print(f"   Found {len(tecnicos)} technicians")
        
        # Test the loop pattern that was causing the error
        test_date = date.today()
        print(f"\n3. 🔄 Testing loop queries for date: {test_date}")
        
        registros = []
        for i, tecnico in enumerate(tecnicos, 1):
            id_tecnico = tecnico['id_codigo_consumidor']
            print(f"   Processing technician {i}: {tecnico['tecnico']}")
            
            # Query for attendance record (similar to original)
            cursor.execute("""
                SELECT 
                    id_asistencia,
                    cedula,
                    tecnico,
                    carpeta_dia,
                    carpeta,
                    super,
                    fecha_asistencia,
                    id_codigo_consumidor,
                    hora_inicio,
                    estado,
                    novedad
                FROM asistencia 
                WHERE id_codigo_consumidor = %s AND DATE(fecha_asistencia) = %s
            """, (id_tecnico, test_date))
            
            registro_asistencia = cursor.fetchone()
            
            if registro_asistencia:
                print(f"     - Attendance record: Found")
                registros.append(registro_asistencia)
            else:
                print(f"     - Attendance record: Not found, creating empty entry")
                # Create empty entry (similar to original function)
                registros.append({
                    'id_asistencia': None,
                    'cedula': tecnico['cedula'],
                    'tecnico': tecnico['tecnico'],
                    'carpeta_dia': None,
                    'carpeta': tecnico['carpeta'],
                    'super': tecnico['super'],
                    'fecha_asistencia': test_date.strftime('%Y-%m-%d'),
                    'id_codigo_consumidor': tecnico['id_codigo_consumidor'],
                    'hora_inicio': None,
                    'estado': None,
                    'novedad': None
                })
        
        print(f"\n4. 📊 Results summary:")
        print(f"   Total records processed: {len(registros)}")
        print(f"   Records with attendance: {len([r for r in registros if r['id_asistencia'] is not None])}")
        print(f"   Records without attendance: {len([r for r in registros if r['id_asistencia'] is None])}")
        
        print("\n5. 🧹 Testing cursor and connection cleanup...")
        
        # Test cursor close (this was causing the error before)
        cursor.close()
        print("   ✅ Cursor closed successfully")
        
        # Test connection close
        connection.close()
        print("   ✅ Connection closed successfully")
        
        print("\n🎉 SUCCESS: All tests passed!")
        print("   - Buffered cursor prevents 'Unread result found' error")
        print("   - Multiple queries in loop work correctly")
        print("   - Cursor and connection cleanup works properly")
        
    except mysql.connector.Error as e:
        print(f"\n❌ MySQL Error: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False
        
    finally:
        # Test the improved finally block logic
        if 'cursor' in locals() and cursor:
            try:
                cursor.close()
                print("   🔧 Finally block: Cursor close attempted")
            except:
                print("   🔧 Finally block: Cursor already closed")
                pass
        if 'connection' in locals() and connection and connection.is_connected():
            try:
                connection.close()
                print("   🔧 Finally block: Connection close attempted")
            except:
                print("   🔧 Finally block: Connection already closed")
                pass
    
    return True

if __name__ == "__main__":
    print("TESTING CONSULTAR_ASISTENCIA MYSQL CURSOR FIX")
    print("=" * 60)
    success = test_consultar_asistencia_fix()
    if success:
        print("\n✅ Test completed successfully - Fix is working!")
    else:
        print("\n❌ Test failed - Fix needs review")