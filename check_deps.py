#!/usr/bin/env python3
"""
Script para verificar dependencias antes del inicio
"""
import sys

def check_dependencies():
    """Verificar que todas las dependencias críticas estén instaladas"""
    required_modules = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'psycopg2',  # This is what we're checking for
        'pydantic',
        'httpx'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n🚨 Missing modules: {missing_modules}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n🎉 All dependencies are installed!")
        return True

if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)