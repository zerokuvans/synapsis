#!/usr/bin/env python3
"""
Test script to directly call the MPA route function
"""

import sys
import os

# Ensure repository root is on Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, REPO_ROOT)

try:
    # Import the Flask app and test context
    from app import app
    
    print("🔍 Testing MPA route directly...")
    print("=" * 50)
    
    # Create a test client
    with app.test_client() as client:
        print("📡 Testing /mpa route with test client...")
        
        # Test without authentication
        response = client.get('/mpa', follow_redirects=False)
        print(f"Without auth - Status: {response.status_code}")
        print(f"Without auth - Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print(f"Redirects to: {response.headers.get('Location', 'Unknown')}")
        elif response.status_code == 404:
            print("❌ Still getting 404 even with test client!")
            print(f"Response data: {response.get_data(as_text=True)[:200]}...")
        else:
            print(f"Response preview: {response.get_data(as_text=True)[:200]}...")
            
    print("\n🔍 Testing route registration in current app instance...")
    
    # Check if the route exists in the current app
    mpa_rule = None
    for rule in app.url_map.iter_rules():
        if rule.rule == '/mpa':
            mpa_rule = rule
            break
            
    if mpa_rule:
        print(f"✅ Route found in current app: {mpa_rule}")
        print(f"   Endpoint: {mpa_rule.endpoint}")
        print(f"   Methods: {list(mpa_rule.methods)}")
        
        # Try to get the view function
        view_func = app.view_functions.get(mpa_rule.endpoint)
        if view_func:
            print(f"✅ View function: {view_func}")
        else:
            print("❌ View function not found!")
    else:
        print("❌ Route not found in current app!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
