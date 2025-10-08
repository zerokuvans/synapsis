#!/usr/bin/env python3
"""
Script to check attendance records for technician 1030545270
"""
import mysql.connector
import os
from datetime import datetime

# Database configuration with defaults
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

def check_attendance_records():
    try:
        print("🔍 Checking attendance records...")
        print(f"Database: {db_config['database']} at {db_config['host']}:{db_config['port']}")
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Check if asistencia table exists
        cursor.execute("SHOW TABLES LIKE 'asistencia'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ Table 'asistencia' does not exist!")
            return
        
        print("✅ Table 'asistencia' exists")
        
        # Check table structure
        cursor.execute("DESCRIBE asistencia")
        columns = cursor.fetchall()
        print("\n📋 Table structure:")
        for col in columns:
            print(f"  - {col['Field']}: {col['Type']}")
        
        # Check for technician 1030545270
        cedula = '1030545270'
        today = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n🔍 Searching for technician {cedula} on {today}...")
        
        # Check if record exists for today
        cursor.execute("""
            SELECT * FROM asistencia 
            WHERE cedula = %s AND DATE(fecha_asistencia) = %s
        """, (cedula, today))
        
        records = cursor.fetchall()
        
        if records:
            print(f"✅ Found {len(records)} record(s) for technician {cedula} today:")
            for record in records:
                print(f"  - ID: {record.get('id', 'N/A')}")
                print(f"  - Fecha: {record.get('fecha', 'N/A')}")
                print(f"  - Estado: {record.get('estado', 'N/A')}")
                print(f"  - Novedad: {record.get('novedad', 'N/A')}")
        else:
            print(f"❌ No records found for technician {cedula} today")
            
            # Check if technician exists in any date
            cursor.execute("SELECT * FROM asistencia WHERE cedula = %s LIMIT 5", (cedula,))
            all_records = cursor.fetchall()
            
            if all_records:
                print(f"📅 Found {len(all_records)} historical records for this technician:")
                for record in all_records:
                    print(f"  - Date: {record.get('fecha_asistencia', 'N/A')}, Estado: {record.get('estado', 'N/A')}")
            else:
                print(f"❌ No records found for technician {cedula} in any date")
        
        # Check if technician exists in usuarios table
        cursor.execute("SHOW TABLES LIKE 'usuarios'")
        if cursor.fetchone():
            cursor.execute("SELECT * FROM usuarios WHERE cedula = %s", (cedula,))
            user = cursor.fetchone()
            if user:
                print(f"✅ Technician {cedula} exists in usuarios table: {user.get('nombre', 'N/A')}")
            else:
                print(f"❌ Technician {cedula} not found in usuarios table")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_attendance_records()