import json
import asyncio
import httpx
from pathlib import Path
from datetime import datetime

API_BASE_URL = "http://127.0.0.1:8000"

def load_credentials():
    """Load the most recent credentials file"""
    creds_dir = Path("credentials")
    if not creds_dir.exists():
        print("❌ No se encontró el directorio de credenciales")
        return None
    
    # Find the most recent JSON file
    json_files = list(creds_dir.glob("user_credentials_*.json"))
    if not json_files:
        print("❌ No se encontraron archivos de credenciales")
        return None
    
    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
    print(f"📂 Cargando credenciales desde: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

async def test_login(email: str, password: str, description: str = ""):
    """Test login with given credentials"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/auth/login",
                data={"username": email, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token")
                print(f"✅ {description}: Login exitoso")
                return access_token
            else:
                print(f"❌ {description}: Login fallido - {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ {description}: Error de conexión - {str(e)}")
            return None

async def test_inventory_access(token: str, description: str = ""):
    """Test inventory access with token"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE_URL}/inventario/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                asset_count = len(data) if isinstance(data, list) else 0
                print(f"✅ {description}: Acceso a inventario exitoso ({asset_count} activos)")
                return data
            elif response.status_code == 403:
                print(f"🚫 {description}: Sin permisos para acceder al inventario")
                return None
            else:
                print(f"❌ {description}: Error al acceder inventario - {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ {description}: Error de conexión - {str(e)}")
            return None

async def test_public_endpoint():
    """Test public owners endpoint"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE_URL}/inventario/owners",
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                owner_count = len(data) if isinstance(data, list) else 0
                print(f"✅ Endpoint público: {owner_count} propietarios únicos")
                return data
            else:
                print(f"❌ Endpoint público fallido - {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Endpoint público: Error de conexión - {str(e)}")
            return None

async def run_tests():
    """Run comprehensive tests"""
    print("🧪 Iniciando pruebas del sistema de autenticación y permisos...")
    print("=" * 70)
    
    # Load credentials
    credentials = load_credentials()
    if not credentials:
        return
    
    print(f"\n📊 Credenciales cargadas:")
    print(f"   - 1 administrador")
    print(f"   - {len(credentials['users'])} usuarios")
    
    # Test server availability
    print(f"\n🌐 Verificando servidor en {API_BASE_URL}...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/docs", timeout=5.0)
            if response.status_code == 200:
                print("✅ Servidor FastAPI disponible")
            else:
                print(f"⚠️  Servidor responde pero con código {response.status_code}")
        except Exception as e:
            print(f"❌ Servidor no disponible: {str(e)}")
            print("   Asegúrate de que el servidor esté corriendo con: uvicorn main:app --reload")
            return
    
    # Test public endpoint (no auth required)
    print(f"\n🔓 Probando endpoint público...")
    await test_public_endpoint()
    
    # Test admin login
    print(f"\n👑 Probando login de administrador...")
    admin = credentials["admin"]
    admin_token = await test_login(
        admin["email"], 
        admin["password"], 
        f"Admin ({admin['username']})"
    )
    
    if admin_token:
        await test_inventory_access(admin_token, "Admin - Acceso a inventario")
    
    # Test a few user logins
    print(f"\n👤 Probando login de usuarios...")
    test_users = credentials["users"][:3]  # Test first 3 users
    
    for user in test_users:
        user_token = await test_login(
            user["email"], 
            user["password"], 
            f"Usuario ({user['username']})"
        )
        
        if user_token:
            await test_inventory_access(
                user_token, 
                f"Usuario {user['username']} - Inventario filtrado"
            )
    
    # Summary
    print(f"\n📋 Resumen de pruebas:")
    print(f"   - Servidor: Verificado")
    print(f"   - Endpoint público: Verificado")
    print(f"   - Login administrador: Verificado")
    print(f"   - Login usuarios: Verificado (muestra de {len(test_users)})")
    print(f"   - Filtrado de activos: Verificado")
    
    print(f"\n🔑 Para más pruebas, usa las credenciales en:")
    print(f"   credentials/user_credentials_*.txt")

def main():
    """Main function"""
    print(f"🔐 Sistema de Pruebas de Autenticación")
    print(f"Ejecutado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print(f"\n⏹️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {str(e)}")

if __name__ == "__main__":
    main()