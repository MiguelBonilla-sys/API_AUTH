import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.database import engine
from src.models.user import User

async def create_tables():
    """Create all tables in the database"""
    print("🔧 Creando tablas en la base de datos...")
    
    try:
        # Import all models to ensure they are registered
        from src.models import user  # This ensures User model is imported
        
        # Create all tables
        async with engine.begin() as conn:
            from src.config.database import Base
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Tablas creadas exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(create_tables())
    if success:
        print("✅ Base de datos lista para usar")
    else:
        print("❌ Error en la configuración de base de datos")