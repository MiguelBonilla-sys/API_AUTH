import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_railway_connection():
    """Test direct connection to Railway PostgreSQL"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL no encontrada en variables de entorno")
        return False
    
    print(f"🔗 Probando conexión a Railway PostgreSQL...")
    print(f"   URL: {database_url[:50]}...")
    
    try:
        # Extract connection components from URL
        # Format: postgresql://user:password@host:port/database
        url_parts = database_url.replace("postgresql://", "").split("@")
        if len(url_parts) != 2:
            print("❌ Formato de DATABASE_URL inválido")
            return False
        
        user_pass = url_parts[0].split(":")
        host_port_db = url_parts[1].split("/")
        
        if len(user_pass) != 2 or len(host_port_db) != 2:
            print("❌ No se pudo parsear DATABASE_URL")
            return False
        
        user = user_pass[0]
        password = user_pass[1]
        host_port = host_port_db[0].split(":")
        database = host_port_db[1]
        
        if len(host_port) != 2:
            print("❌ No se pudo extraer host y puerto")
            return False
        
        host = host_port[0]
        port = int(host_port[1])
        
        print(f"   Host: {host}")
        print(f"   Puerto: {port}")
        print(f"   Base de datos: {database}")
        print(f"   Usuario: {user}")
        
        # Test connection
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            ssl="require"  # Railway requires SSL
        )
        
        # Test query
        result = await conn.fetchval("SELECT version()")
        print(f"✅ Conexión exitosa!")
        print(f"   PostgreSQL: {result}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

async def create_tables_railway():
    """Create tables in Railway PostgreSQL"""
    database_url = os.getenv("DATABASE_URL")
    
    try:
        # Connect directly with asyncpg
        conn = await asyncpg.connect(database_url, ssl="require")
        
        # Create users table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR UNIQUE NOT NULL,
            username VARCHAR UNIQUE NOT NULL,
            hashed_password VARCHAR NOT NULL,
            full_name VARCHAR,
            dueno_de_activo VARCHAR,
            is_active BOOLEAN DEFAULT TRUE NOT NULL,
            is_superuser BOOLEAN DEFAULT FALSE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );
        """
        
        print("🔧 Creando tabla 'users' en Railway...")
        await conn.execute(create_table_sql)
        print("✅ Tabla 'users' creada exitosamente")
        
        # Verify table creation
        table_exists = await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
        )
        
        if table_exists:
            print("✅ Tabla verificada correctamente")
        else:
            print("⚠️  No se pudo verificar la tabla")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creando tablas: {str(e)}")
        return False

async def main():
    """Main function"""
    print("🚀 Configuración de Base de Datos Railway")
    print("=" * 50)
    
    # Test connection
    if not await test_railway_connection():
        print("\n❌ No se pudo conectar a Railway. Verifica:")
        print("   1. Las credenciales en el archivo .env")
        print("   2. Que la base de datos esté activa en Railway")
        print("   3. La conectividad de red")
        return False
    
    print("\n🔧 Creando estructura de base de datos...")
    if not await create_tables_railway():
        print("❌ Error creando tablas")
        return False
    
    print("\n🎉 ¡Base de datos configurada exitosamente!")
    print("✅ Ahora puedes ejecutar: python scripts/upload_users_via_api.py")
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Proceso interrumpido")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1)