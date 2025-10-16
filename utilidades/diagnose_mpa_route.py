#!/usr/bin/env python3
"""
Simple diagnostic script for /mpa route issues
Tests various scenarios to identify why the route returns "Not Found"
"""

import requests
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8080"
MPA_URL = f"{BASE_URL}/mpa"
LOGIN_URL = f"{BASE_URL}/login"

def test_server_connectivity():
    """Test if the server is responding"""
    print("🔍 Testing server connectivity...")
    try:
        response = requests.get(BASE_URL, timeout=10)
        print(f"✅ Server is responding: Status {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - is it running on port 8080?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Server connection timeout")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_mpa_route_direct():
    """Test direct access to /mpa route"""
    print("\n🔍 Testing direct access to /mpa route...")
    try:
        response = requests.get(MPA_URL, timeout=10, allow_redirects=False)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
        
        if response.status_code == 404:
            print("❌ Route returns 404 - Not Found")
            print("This suggests the route is not properly registered in Flask")
            print(f"Response text: {response.text[:200]}...")
        elif response.status_code == 302:
            print("🔄 Route redirects (likely to login)")
            print(f"Redirect location: {response.headers.get('Location', 'Not specified')}")
        elif response.status_code == 401:
            print("🔒 Route requires authentication")
        elif response.status_code == 403:
            print("🚫 Route access forbidden (role issue)")
        elif response.status_code == 200:
            print("✅ Route accessible")
            print(f"Response preview: {response.text[:200]}...")
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            print(f"Response text: {response.text[:200]}...")
            
        return response
    except Exception as e:
        print(f"❌ Error testing /mpa route: {e}")
        return None

def test_available_routes():
    """Test some common routes to see what's available"""
    print("\n🔍 Testing other available routes...")
    test_routes = ["/", "/login", "/logout", "/dashboard"]
    
    for route in test_routes:
        try:
            url = f"{BASE_URL}{route}"
            response = requests.get(url, timeout=5, allow_redirects=False)
            print(f"  {route}: Status {response.status_code}")
        except Exception as e:
            print(f"  {route}: Error - {e}")

def test_with_session():
    """Test accessing /mpa with a session (simulating login)"""
    print("\n🔍 Testing /mpa access with session...")
    
    session = requests.Session()
    
    # First, try to get the login page
    try:
        login_response = session.get(LOGIN_URL, timeout=10)
        print(f"Login page status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login page accessible")
            
            # Now try to access /mpa with the session
            mpa_response = session.get(MPA_URL, timeout=10, allow_redirects=False)
            print(f"/mpa with session status: {mpa_response.status_code}")
            
            if mpa_response.status_code == 200:
                print("✅ /mpa accessible with session!")
            elif mpa_response.status_code == 404:
                print("❌ /mpa still returns 404 even with session")
            elif mpa_response.status_code == 302:
                print("🔄 /mpa redirects with session")
                print(f"Redirect to: {mpa_response.headers.get('Location', 'Not specified')}")
            else:
                print(f"⚠️ /mpa returns {mpa_response.status_code} with session")
        else:
            print("❌ Cannot access login page")
            
    except Exception as e:
        print(f"❌ Error during session test: {e}")

def check_route_variations():
    """Test variations of the MPA route"""
    print("\n🔍 Testing MPA route variations...")
    
    variations = [
        "/mpa",
        "/mpa/",
        "/MPA",
        "/mpa/dashboard",
        "/modulos/mpa"
    ]
    
    for variation in variations:
        try:
            url = f"{BASE_URL}{variation}"
            response = requests.get(url, timeout=5, allow_redirects=False)
            print(f"  {variation}: Status {response.status_code}")
        except Exception as e:
            print(f"  {variation}: Error - {e}")

def main():
    """Main diagnostic function"""
    print("🚀 Starting MPA Route Diagnostic")
    print("=" * 50)
    
    # Test 1: Server connectivity
    if not test_server_connectivity():
        print("\n❌ Cannot proceed - server is not accessible")
        return
    
    # Test 2: Direct route access
    mpa_response = test_mpa_route_direct()
    
    # Test 3: Other routes
    test_available_routes()
    
    # Test 4: Session-based access
    test_with_session()
    
    # Test 5: Route variations
    check_route_variations()
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if mpa_response:
        if mpa_response.status_code == 404:
            print("❌ ISSUE IDENTIFIED: Route /mpa is not registered in Flask")
            print("💡 POSSIBLE SOLUTIONS:")
            print("   1. Check app.py for proper route definition")
            print("   2. Verify @app.route('/mpa') exists")
            print("   3. Check for syntax errors in route definition")
            print("   4. Ensure the route function is properly defined")
            print("   5. Check if the route is commented out or disabled")
        elif mpa_response.status_code == 302:
            print("🔄 ISSUE IDENTIFIED: Route requires authentication")
            print("💡 SOLUTION: Login first, then access /mpa")
        elif mpa_response.status_code == 403:
            print("🚫 ISSUE IDENTIFIED: User lacks required role")
            print("💡 SOLUTION: Ensure user has 'administrativo' role")
        elif mpa_response.status_code == 500:
            print("💥 ISSUE IDENTIFIED: Server error in route")
            print("💡 SOLUTION: Check server logs for Python errors")
        else:
            print(f"⚠️ UNEXPECTED STATUS: {mpa_response.status_code}")
            print("💡 Check server logs for more details")
    else:
        print("❌ CRITICAL: Cannot test /mpa route due to connection issues")

if __name__ == "__main__":
    main()