#!/usr/bin/env python3
"""
Test script to verify the attendance record auto-creation fix
"""
import requests
import json

BASE_URL = "http://localhost:8080"
LOGIN_URL = f"{BASE_URL}/"
API_URL = f"{BASE_URL}/api/asistencia/actualizar-campo"

def test_attendance_fix():
    print("🧪 Testing attendance record auto-creation fix...")
    
    # Create session for login
    session = requests.Session()
    
    # Login first
    print("🔐 Logging in...")
    login_data = {
        'username': '1032402333',
        'password': 'CE1032402333'
    }
    
    login_response = session.post(LOGIN_URL, data=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    print("✅ Login successful")
    
    # Test updating a field for technician 1030545270
    print("📝 Testing field update for technician 1030545270...")
    
    test_data = {
        'cedula': '1030545270',
        'campo': 'estado',
        'valor': 'CUMPLE'
    }
    
    response = session.post(API_URL, json=test_data)
    
    print(f"📊 Response Status: {response.status_code}")
    print(f"📊 Response Content: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ SUCCESS: Attendance record created and updated successfully!")
            print(f"✅ Message: {result.get('message')}")
        else:
            print(f"❌ API returned success=false: {result.get('message')}")
    else:
        print(f"❌ API call failed with status {response.status_code}")
        try:
            error_data = response.json()
            print(f"❌ Error message: {error_data.get('message', 'Unknown error')}")
        except:
            print(f"❌ Raw response: {response.text}")
    
    # Test updating novedad field
    print("\n📝 Testing novedad field update...")
    
    novedad_data = {
        'cedula': '1030545270',
        'campo': 'novedad',
        'valor': 'Llegó temprano'
    }
    
    response2 = session.post(API_URL, json=novedad_data)
    
    print(f"📊 Response Status: {response2.status_code}")
    print(f"📊 Response Content: {response2.text}")
    
    if response2.status_code == 200:
        result2 = response2.json()
        if result2.get('success'):
            print("✅ SUCCESS: Novedad field updated successfully!")
            print(f"✅ Message: {result2.get('message')}")
        else:
            print(f"❌ API returned success=false: {result2.get('message')}")
    else:
        print(f"❌ Novedad update failed with status {response2.status_code}")

if __name__ == "__main__":
    test_attendance_fix()