#!/usr/bin/env python3
"""
Test script to check Flask route registration
"""

import sys
import os

# Ensure repository root is on Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, REPO_ROOT)

try:
    # Import the Flask app
    from app import app
    
    print("🔍 Checking Flask route registration...")
    print("=" * 50)
    
    # Get all registered routes
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': rule.rule
        })
    
    # Sort routes by rule
    routes.sort(key=lambda x: x['rule'])
    
    print(f"📊 Total registered routes: {len(routes)}")
    print("\n🔍 Looking for MPA routes...")
    
    mpa_routes = [r for r in routes if 'mpa' in r['rule'].lower()]
    
    if mpa_routes:
        print(f"✅ Found {len(mpa_routes)} MPA routes:")
        for route in mpa_routes:
            print(f"  - {route['rule']} -> {route['endpoint']} {route['methods']}")
    else:
        print("❌ No MPA routes found!")
        
    print("\n🔍 Checking specific /mpa route...")
    mpa_route = next((r for r in routes if r['rule'] == '/mpa'), None)
    
    if mpa_route:
        print(f"✅ /mpa route found: {mpa_route}")
        
        # Try to get the view function
        try:
            view_func = app.view_functions.get(mpa_route['endpoint'])
            if view_func:
                print(f"✅ View function found: {view_func.__name__}")
                print(f"   Function: {view_func}")
            else:
                print("❌ View function not found!")
        except Exception as e:
            print(f"❌ Error getting view function: {e}")
    else:
        print("❌ /mpa route not found in registered routes!")
        
    print("\n🔍 All routes containing 'mpa' (case insensitive):")
    for route in routes:
        if 'mpa' in route['rule'].lower() or 'mpa' in route['endpoint'].lower():
            print(f"  - {route['rule']} -> {route['endpoint']} {route['methods']}")
            
    print("\n🔍 Sample of other routes:")
    for route in routes[:10]:
        print(f"  - {route['rule']} -> {route['endpoint']} {route['methods']}")
        
except ImportError as e:
    print(f"❌ Error importing app: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
