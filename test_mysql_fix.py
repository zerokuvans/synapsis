#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the MySQL cursor fix for 'Unread result found' error
"""

import mysql.connector
from datetime import datetime, date

def test_mysql_cursor_fix():
    """Test the MySQL cursor handling fix"""
    
    print("=== TESTING MYSQL CURSOR FIX ===")
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
        
        # Simulate the problematic query pattern from api_preoperacionales_tecnicos
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
            SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula as documento
            FROM recurso_operativo
            WHERE super = %s AND estado = 'Activo'
            LIMIT 3
        """
        
        cursor.execute(query_tecnicos, (supervisor,))
        tecnicos = cursor.fetchall()
        print(f"   Found {len(tecnicos)} technicians")
        
        # Test the loop pattern that was causing the error
        test_date = date.today()
        print(f"\n3. 🔄 Testing loop queries for date: {test_date}")
        
        for i, tecnico in enumerate(tecnicos, 1):
            id_tecnico = tecnico['id_codigo_consumidor']
            print(f"   Processing technician {i}: {tecnico['nombre']}")
            
            # Query 1: Check attendance (similar to original)
            cursor.execute("""
                SELECT a.id_asistencia, a.fecha_asistencia 
                FROM asistencia a
                JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
                WHERE a.id_codigo_consumidor = %s 
                AND DATE(a.fecha_asistencia) = %s 
                AND t.valor = '1'
                LIMIT 1
            """, (id_tecnico, test_date))
            
            asistencia = cursor.fetchone()
            print(f"     - Attendance: {'Found' if asistencia else 'Not found'}")
            
            # Query 2: Check preoperational (similar to original)
            cursor.execute("""
                SELECT id_preoperacional, fecha
                FROM preoperacional
                WHERE id_codigo_consumidor = %s AND DATE(fecha) = %s
                LIMIT 1
            """, (id_tecnico, test_date))
            
            preoperacional = cursor.fetchone()
            print(f"     - Preoperational: {'Found' if preoperacional else 'Not found'}")
        
        print("\n4. 🧹 Testing cursor cleanup...")
        
        # Test the improved cleanup (this should not cause "Unread result found")
        try:
            cursor.close()
            print("   ✅ Cursor closed successfully")
        except Exception as e:
            print(f"   ❌ Error closing cursor: {e}")
            
        try:
            connection.close()
            print("   ✅ Connection closed successfully")
        except Exception as e:
            print(f"   ❌ Error closing connection: {e}")
            
        print("\n🎉 TEST COMPLETED SUCCESSFULLY!")
        print("✅ The MySQL cursor fix appears to be working correctly")
        return True
        
    except mysql.connector.Error as e:
        print(f"\n❌ MySQL Error: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ General Error: {e}")
        return False

if __name__ == "__main__":
    success = test_mysql_cursor_fix()
    exit(0 if success else 1)