import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

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
    # Remove extra spaces and convert to lowercase
    clean_dueno = dueno.strip().lower()
    
    # Replace spaces and special characters with underscores
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
    
    # Remove multiple underscores
    while "__" in username:
        username = username.replace("__", "_")
    
    # Remove leading/trailing underscores
    username = username.strip("_")
    
    return username

def create_email_from_username(username: str) -> str:
    """Create an email from username"""
    return f"{username}@inventario.gov.co"

def generate_credentials() -> Dict:
    """Generate credentials for all users without database"""
    # Remove duplicates while preserving order
    unique_propietarios = []
    seen = set()
    for prop in PROPIETARIOS_ACTIVOS:
        clean_prop = prop.strip()
        if clean_prop not in seen:
            seen.add(clean_prop)
            unique_propietarios.append(clean_prop)
    
    print(f"Generating credentials for {len(unique_propietarios)} unique propietarios...")
    
    credentials = {
        "admin": {
            "email": "admin@inventario.gov.co",
            "username": "admin",
            "password": "admin123",
            "full_name": "Administrador Principal",
            "dueno_de_activo": None,
            "is_superuser": True,
            "role": "admin"
        },
        "users": []
    }
    
    # Create credentials for each propietario
    for idx, dueno in enumerate(unique_propietarios, 1):
        try:
            username = create_username_from_dueno(dueno)
            email = create_email_from_username(username)
            default_password = "password123"
            
            user_credential = {
                "id": idx,
                "email": email,
                "username": username,
                "password": default_password,
                "full_name": dueno,
                "dueno_de_activo": dueno,
                "is_superuser": False,
                "role": "user"
            }
            
            credentials["users"].append(user_credential)
            print(f"✓ Generated credentials for: {username} ({email}) - '{dueno}'")
            
        except Exception as e:
            print(f"✗ Error generating credentials for '{dueno}': {e}")
            continue
    
    return credentials

def save_credentials_to_files(credentials: Dict):
    """Save credentials to multiple file formats"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create credentials directory
    creds_dir = Path("credentials")
    creds_dir.mkdir(exist_ok=True)
    
    # Save as JSON
    json_file = creds_dir / f"user_credentials_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(credentials, f, indent=2, ensure_ascii=False)
    
    # Save as text for easy reading
    txt_file = creds_dir / f"user_credentials_{timestamp}.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("=== CREDENCIALES DE USUARIOS ===\n\n")
        f.write(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Admin credentials
        admin = credentials["admin"]
        f.write("ADMINISTRADOR:\n")
        f.write(f"  Email: {admin['email']}\n")
        f.write(f"  Username: {admin['username']}\n")
        f.write(f"  Password: {admin['password']}\n")
        f.write(f"  Rol: {admin['role']}\n")
        f.write("  Acceso: Todos los activos\n\n")
        
        # User credentials
        f.write("USUARIOS POR PROPIETARIO:\n")
        f.write("-" * 50 + "\n")
        for user in credentials["users"]:
            f.write(f"\nPropietario: {user['dueno_de_activo']}\n")
            f.write(f"  Email: {user['email']}\n")
            f.write(f"  Username: {user['username']}\n")
            f.write(f"  Password: {user['password']}\n")
            f.write(f"  Acceso: Solo activos de '{user['dueno_de_activo']}'\n")
    
    # Save as CSV for import into other tools
    csv_file = creds_dir / f"user_credentials_{timestamp}.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write("email,username,password,full_name,dueno_de_activo,is_superuser,role\n")
        
        # Admin row
        admin = credentials["admin"]
        f.write(f'"{admin["email"]}","{admin["username"]}","{admin["password"]}","{admin["full_name"]}","","true","admin"\n')
        
        # User rows
        for user in credentials["users"]:
            f.write(f'"{user["email"]}","{user["username"]}","{user["password"]}","{user["full_name"]}","{user["dueno_de_activo"]}","false","user"\n')
    
    print(f"\n📁 Credenciales guardadas en:")
    print(f"   - JSON: {json_file}")
    print(f"   - TXT:  {txt_file}")
    print(f"   - CSV:  {csv_file}")

def main():
    """Main function"""
    print("🔐 Generando credenciales de usuarios...")
    
    try:
        credentials = generate_credentials()
        save_credentials_to_files(credentials)
        
        print(f"\n🎉 ¡Proceso completado!")
        print(f"📊 Resumen:")
        print(f"   - 1 usuario administrador")
        print(f"   - {len(credentials['users'])} usuarios por propietario")
        print(f"   - Total: {len(credentials['users']) + 1} usuarios")
        
        print(f"\n🔑 Credenciales de acceso:")
        print(f"   Admin: admin@inventario.gov.co / admin123")
        print(f"   Usuarios: [username]@inventario.gov.co / password123")
        
        print(f"\n⚠️  IMPORTANTE:")
        print(f"   - Cambiar contraseñas en producción")
        print(f"   - Los usuarios solo pueden ver/editar sus propios activos")
        print(f"   - El admin puede ver/editar todos los activos")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()