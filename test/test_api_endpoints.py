#!/usr/bin/env python3
"""
Test script to verify maintenance API endpoints are working correctly
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_api_endpoint(endpoint, method='GET', data=None, headers=None):
    """Test an API endpoint and return the response"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        print(f"\n{method} {endpoint}")
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
        
        # Try to parse as JSON
        try:
            json_response = response.json()
            print(f"JSON Response: {json.dumps(json_response, indent=2)}")
        except:
            # If not JSON, show first 200 characters of response
            text_response = response.text[:200]
            print(f"Text Response (first 200 chars): {text_response}")
            if "<!doctype" in text_response.lower() or "<html" in text_response.lower():
                print("⚠️  WARNING: Response appears to be HTML instead of JSON!")
        
        return response
        
    except Exception as e:
        print(f"Error testing {endpoint}: {str(e)}")
        return None

def main():
    """Test all maintenance API endpoints"""
    print("Testing Maintenance API Endpoints")
    print("=" * 50)
    
    # Test endpoints that should work without authentication (if any)
    # Most likely all require authentication, so these will return 401/403
    
    # Test GET endpoints
    test_api_endpoint("/api/mpa/mantenimientos")
    test_api_endpoint("/api/mpa/mantenimientos/1")
    test_api_endpoint("/api/mpa/vehiculos/placas")
    test_api_endpoint("/api/mpa/categorias-mantenimiento/vehiculo")
    
    # Test POST endpoint (will fail without proper data and auth)
    test_data = {
        "placa": "ABC123",
        "kilometraje": 50000,
        "id_categoria_mantenimiento": 1,
        "observacion": "Test maintenance"
    }
    test_api_endpoint("/api/mpa/mantenimientos", method='POST', data=test_data)
    
    print("\n" + "=" * 50)
    print("Test completed. Check for any HTML responses that should be JSON.")

if __name__ == "__main__":
    main()