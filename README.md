# API Auth Gateway

Un API Gateway que proporciona acceso autenticado a la API de inventario de activos de información. Este servicio actúa como un proxy seguro, requiriendo autenticación JWT antes de reenviar solicitudes a la API externa.

## 🏗️ Arquitectura

- **API Gateway**: Proxy autenticado usando FastAPI
- **Base de datos**: PostgreSQL en Railway (solo para usuarios/auth)
- **API Externa**: `https://inventoryapp.usbtopia.usbbog.edu.co`
- **Deployment**: Railway con PostgreSQL integrado

## 🚀 Configuración Rápida

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus valores
```

### 3. Ejecutar la aplicación
```bash
# Desarrollo
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Railway (automático)
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## 📚 Endpoints Disponibles

### Autenticación
- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/login` - Iniciar sesión
- `POST /auth/refresh` - Renovar token
- `GET /auth/me` - Información del usuario actual

### Inventario (Requiere autenticación)
- `GET /inventario/` - Listar activos
- `POST /inventario/` - Crear activo
- `GET /inventario/{id}` - Obtener activo específico
- `PUT /inventario/{id}` - Actualizar activo
- `DELETE /inventario/{id}` - Eliminar activo

## 🔐 Autenticación

Todos los endpoints de inventario requieren un token JWT válido:

```bash
# 1. Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "tu_usuario", "password": "tu_password"}'

# 2. Usar el token en las solicitudes
curl -X GET "http://localhost:8000/inventario/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## ⚙️ Variables de Entorno

```env
# Base de datos Railway
DATABASE_URL=postgresql://username:password@hostname:port/database

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Externa
INVENTORY_API_BASE_URL=https://inventoryapp.usbtopia.usbbog.edu.co

# Opcional
SENTRY_DSN=your-sentry-dsn
DEBUG=false
```

## 🏢 Deploy en Railway

1. Conectar repositorio a Railway
2. Agregar PostgreSQL add-on
3. Configurar variables de entorno
4. Railway auto-detectará el puerto desde `$PORT`

## 📁 Estructura del Proyecto

```
API_AUTH/
├── main.py                 # Aplicación FastAPI principal
├── requirements.txt        # Dependencias
├── .env.example           # Ejemplo de variables de entorno
├── src/
│   ├── auth/              # Sistema de autenticación
│   │   ├── jwt_utils.py   # Utilidades JWT
│   │   └── dependencies.py # Dependencias de auth
│   ├── config/            # Configuración
│   │   └── database.py    # Config de base de datos
│   ├── models/            # Modelos SQLAlchemy
│   │   └── user.py        # Modelo de usuario
│   ├── routers/           # Rutas de la API
│   │   ├── auth.py        # Rutas de autenticación
│   │   └── inventory.py   # Proxy a API de inventario
│   └── schemas/           # Esquemas Pydantic
│       ├── auth.py        # Esquemas de autenticación
│       └── inventory.py   # Esquemas de inventario
└── .github/
    └── copilot-instructions.md # Instrucciones para AI
```

## 🛡️ Seguridad

- Passwords hasheados con bcrypt
- Tokens JWT con expiración
- Validación de entrada con Pydantic
- Headers CORS configurados
- Manejo seguro de errores de API externa

## 📊 Monitoreo

- Integración con Sentry para tracking de errores
- Health checks en `/` y `/health`
- Logs estructurados para debugging

## 🔧 Desarrollo

Para contribuir al proyecto:

1. Fork del repositorio
2. Crear rama de feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT.