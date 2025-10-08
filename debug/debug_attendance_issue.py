#!/usr/bin/env python3
"""
Debug script to check attendance records and technician data
"""

import mysql.connector
from datetime import datetime

def debug_attendance_issue():
    """Debug the attendance issue for technician 1030545270"""
    
    try:
        # Database connection
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Fenix2024*',
            database='synapsis'
        )

        cursor = connection.cursor(dictionary=True)

        # Check if technician exists
        print('=== Checking technician 1030545270 ===')
        cursor.execute('SELECT * FROM usuarios WHERE cedula = %s', ('1030545270',))
        user = cursor.fetchone()
        if user:
            print(f'✓ User found: {user["nombre"]} - Role: {user["rol_id"]} - Status: {user["estado"]}')
        else:
            print('✗ User not found')

        # Check attendance records for today
        print('\n=== Checking attendance records for today ===')
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT * FROM asistencia WHERE cedula = %s AND DATE(fecha_asistencia) = %s', ('1030545270', today))
        attendance = cursor.fetchall()

        if attendance:
            print(f'✓ Found {len(attendance)} attendance records for today:')
            for record in attendance:
                print(f'  - ID: {record["id_asistencia"]}, Estado: {record["estado"]}, Hora inicio: {record["hora_inicio"]}, Novedad: {record["novedad"]}')
        else:
            print('✗ No attendance records found for today')

        # Check recent attendance records
        print('\n=== Checking recent attendance records (last 7 days) ===')
        cursor.execute('SELECT * FROM asistencia WHERE cedula = %s AND fecha_asistencia >= DATE_SUB(NOW(), INTERVAL 7 DAY) ORDER BY fecha_asistencia DESC', ('1030545270',))
        recent = cursor.fetchall()

        if recent:
            print(f'✓ Found {len(recent)} recent attendance records:')
            for record in recent[:5]:  # Show only first 5
                print(f'  - Date: {record["fecha_asistencia"]}, Estado: {record["estado"]}, Hora inicio: {record["hora_inicio"]}')
        else:
            print('✗ No recent attendance records found')

        # Check if there are any attendance records at all for this user
        print('\n=== Checking all attendance records for this user ===')
        cursor.execute('SELECT COUNT(*) as total FROM asistencia WHERE cedula = %s', ('1030545270',))
        total_count = cursor.fetchone()
        print(f'Total attendance records for this user: {total_count["total"]}')

        # Check the asistencia table structure
        print('\n=== Checking asistencia table structure ===')
        cursor.execute('DESCRIBE asistencia')
        columns = cursor.fetchall()
        print('Table columns:')
        for col in columns:
            print(f'  - {col["Field"]}: {col["Type"]} (Null: {col["Null"]}, Key: {col["Key"]})')

        cursor.close()
        connection.close()
        
        return True

    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == "__main__":
    print("🔍 Debugging attendance issue for technician 1030545270")
    print("=" * 60)
    
    success = debug_attendance_issue()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Debug completed successfully")
    else:
        print("❌ Debug failed")