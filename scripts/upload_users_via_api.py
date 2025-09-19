import json
import asyncio
import httpx
from pathlib import Path
from datetime import datetime

API_BASE_URL = "http://127.0.0.1:8000"

# Lista de propietarios de activos
PROPIETARIOS_ACTIVOS = [
    "Jefe Oficina de Control Interno ",
    "Subdirección Financiera y Administrativa ",
    "Asesor de la Dirección para Comunicaciones y Servicio al Ciudadano",
    "Oficina de Control Disciplinario Interno",
    "Profesional Gestión Financiera",
    "Responsable Área de Contabilidad",
    "Responsable Área Cesantías",
    "Jefe de la Oficina Asesora de Planeación",
    "Profesional Universitario Grado 19 - AHL",
    "Jefe Oficina de Informática y Sistemas ",
    "Profesional especializado Subdirección de Prestaciones Económicas",
    "Profesional Subdirección de Prestaciones Económicas",
    "Profesional y Profesional especializado Subdirección de Prestaciones Económicas",
    "Técnico Operativo Subdirección de Prestaciones Económicas",
    "Gerencia de Pensiones",
    "Jefe Oficina Asesora de Jurídica",
    "Responsable Área Administrativa",
    "Jefe Oficina de Informática y Sistemas",
    "Responsable Área Talento Humano",
    "Responsable Área de Cartera y Jurisdicción coactiva",
    "Técnico operativo del Área de Cartera y Jurisdicción coactiva",
    "Profesional universitario y Técnico operativo del Área de Cartera y Jurisdicción coactiva",
    " Técnico operativo del Área de Cartera y Jurisdicción coactiva",
    "Profesionales Universitarios Jurisdicción coactiva",
    "Responsable Área Cesantías ",
    "Profesional Especializado Subdirección de Prestaciones Económicas",
    "Profesionales Subdirección de Prestaciones Económicas",
    "Técnico operativo Subdirección de Prestaciones Económicas",
    "Departamento de TI"
]

def create_username_from_dueno(dueno: str) -> str:
    """Create a username from the dueno_de_activo string"""
    clean_dueno = dueno.strip().lower()
    
    username = (clean_dueno
                .replace(" ", "_")
                .replace("ñ", "n")
                .replace("ó", "o")
                .replace("é", "e")
                .replace("í", "i")
                .replace("á", "a")
                .replace("ú", "u")
                .replace(".", "")
                .replace(",", "")
                .replace("-", "_"))
    
    while "__" in username:
        username = username.replace("__", "_")
    
    username = username.strip("_")
    return username

def create_email_from_username(username: str) -> str:
    """Create an email from username"""
    return f"{username}@inventario.gov.co"

async def register_user_via_api(user_data: dict) -> bool:
    """Register a user using the API endpoint"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/auth/register",
                json=user_data,
                timeout=30.0
            )
            
            if response.status_code == 201:
                print(f"✅ Usuario creado: {user_data['username']} ({user_data['email']})")
                return True
            elif response.status_code == 400:
                error_detail = response.json().get("detail", "Error desconocido")
                if "already registered" in str(error_detail).lower():
                    print(f"⚠️  Usuario ya existe: {user_data['username']}")
                    return True  # Consider existing as success
                else:
                    print(f"❌ Error registrando {user_data['username']}: {error_detail}")
                    return False
            else:
                print(f"❌ Error registrando {user_data['username']}: HTTP {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error de conexión registrando {user_data['username']}: {str(e)}")
            return False

async def check_server_availability() -> bool:
    """Check if the FastAPI server is running"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/docs", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False

async def upload_users_to_database():
    """Upload all users to database via API endpoints"""
    print("🚀 Subiendo usuarios a la base de datos vía API...")
    print("=" * 60)
    
    # Check server availability
    print(f"🌐 Verificando servidor en {API_BASE_URL}...")
    if not await check_server_availability():
        print("❌ Servidor no disponible.")
        print("   Asegúrate de que esté corriendo con: python -m uvicorn main:app --reload")
        return False
    
    print("✅ Servidor disponible")
    
    # Remove duplicates
    unique_propietarios = []
    seen = set()
    for prop in PROPIETARIOS_ACTIVOS:
        clean_prop = prop.strip()
        if clean_prop not in seen:
            seen.add(clean_prop)
            unique_propietarios.append(clean_prop)
    
    print(f"\n👥 Creando {len(unique_propietarios)} usuarios únicos + 1 admin...")
    
    # Create admin user first
    admin_data = {
        "email": "admin@inventario.gov.co",
        "username": "admin",
        "password": "admin123",
        "full_name": "Administrador Principal",
        "dueno_de_activo": None,
        "is_superuser": True,
        "is_active": True
    }
    
    print(f"\n👑 Creando usuario administrador...")
    admin_success = await register_user_via_api(admin_data)
    
    # Create regular users
    print(f"\n👤 Creando usuarios por propietario...")
    successful_users = 0
    failed_users = 0
    
    for dueno in unique_propietarios:
        try:
            username = create_username_from_dueno(dueno)
            email = create_email_from_username(username)
            
            user_data = {
                "email": email,
                "username": username,
                "password": "password123",
                "full_name": dueno,
                "dueno_de_activo": dueno,
                "is_superuser": False,
                "is_active": True
            }
            
            success = await register_user_via_api(user_data)
            if success:
                successful_users += 1
            else:
                failed_users += 1
                
        except Exception as e:
            print(f"❌ Error procesando '{dueno}': {e}")
            failed_users += 1
    
    # Summary
    total_users = successful_users + (1 if admin_success else 0)
    print(f"\n📊 Resumen de carga:")
    print(f"   ✅ Usuarios creados exitosamente: {total_users}")
    print(f"   ❌ Errores: {failed_users}")
    print(f"   📝 Total procesados: {len(unique_propietarios) + 1}")
    
    if total_users > 0:
        print(f"\n🔑 Credenciales de acceso:")
        print(f"   👑 Admin: admin@inventario.gov.co / admin123")
        print(f"   👤 Usuarios: [username]@inventario.gov.co / password123")
        
        print(f"\n⚠️  IMPORTANTE:")
        print(f"   - Los usuarios están ahora en la base de datos")
        print(f"   - Cambiar contraseñas en producción")
        print(f"   - Los usuarios solo pueden ver/editar sus propios activos")
        print(f"   - El admin puede ver/editar todos los activos")
        
        return True
    else:
        print(f"\n❌ No se pudieron crear usuarios. Verificar logs de errores.")
        return False

def save_upload_log(success: bool, details: str):
    """Save upload log to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"user_upload_{timestamp}.log"
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"=== LOG DE CARGA DE USUARIOS ===\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Estado: {'EXITOSO' if success else 'FALLÓ'}\n")
        f.write(f"Detalles:\n{details}\n")
    
    print(f"📝 Log guardado en: {log_file}")

def main():
    """Main function"""
    print("🎯 Sistema de Carga de Usuarios a Base de Datos")
    print(f"Ejecutado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        success = asyncio.run(upload_users_to_database())
        
        if success:
            print(f"\n🎉 ¡Carga completada exitosamente!")
            print(f"🧪 Ahora puedes probar con: python scripts/test_credentials.py")
        else:
            print(f"\n⚠️  Carga completada con errores. Revisar logs.")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en la carga: {str(e)}")

if __name__ == "__main__":
    main()