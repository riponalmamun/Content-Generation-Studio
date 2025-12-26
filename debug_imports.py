#!/usr/bin/env python3
"""
Debug script to check all imports and routers
"""

import sys
import traceback

def check_import(module_path, attribute=None):
    """Check if a module and its attribute can be imported"""
    try:
        module = __import__(module_path, fromlist=[''])
        print(f"✅ {module_path} imported successfully")
        
        if attribute:
            if hasattr(module, attribute):
                print(f"   ✅ {attribute} found")
                return True
            else:
                print(f"   ❌ {attribute} NOT FOUND")
                print(f"   Available: {[x for x in dir(module) if not x.startswith('_')]}")
                return False
        return True
    except Exception as e:
        print(f"❌ {module_path} import failed: {e}")
        if '--verbose' in sys.argv:
            traceback.print_exc()
        return False

def main():
    print("=" * 70)
    print("🔍 DEBUGGING IMPORTS")
    print("=" * 70)
    print()
    
    # Check core modules
    print("📦 Core Modules:")
    check_import('app.core.config')
    check_import('app.core.security')
    check_import('app.db.session')
    check_import('app.db.base')
    print()
    
    # Check models
    print("📦 Models:")
    check_import('app.models.user')
    print()
    
    # Check schemas
    print("📦 Schemas:")
    check_import('app.schemas.user')
    print()
    
    # Check API modules
    print("📦 API Routers:")
    auth_ok = check_import('app.api.auth', 'router')
    
    if auth_ok:
        print("\n✅ All checks passed! Server should start.")
    else:
        print("\n❌ Issues found. Fix the errors above.")
        print("\nTip: Run with --verbose for full traceback:")
        print("     python debug_imports.py --verbose")
    
    print("=" * 70)

if __name__ == "__main__":
    main()