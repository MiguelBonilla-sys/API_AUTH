# 🚀 Railway Deployment Guide - API_AUTH

## Preparación antes del deploy

### 1. Archivos verificados ✅

- ✅ `requirements.txt` - Dependencias completas
- ✅ `Procfile` - Comando de inicio
- ✅ `railway.toml` - Configuración Railway
- ✅ `.env.example` - Template de variables
- ✅ `main.py` - Configurado con PORT variable
- ✅ Configuración psycopg2 para PostgreSQL
- ✅ `Dockerfile` - Containerización opcional
- ✅ `docker-compose.yml` - Desarrollo local con PostgreSQL

## 🎯 Pasos para deploy en Railway

### 1. Crear proyecto en Railway
```bash
# Instalar Railway CLI (opcional)
npm install -g @railway/cli

# O usar la web: https://railway.app
```

### 2. Conectar repositorio
1. Ve a [railway.app](https://railway.app)
2. Click "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Conecta tu repositorio `API_AUTH`

### 3. Agregar PostgreSQL Database
1. En tu proyecto Railway, click "Add Service"
2. Selecciona "Database" > "PostgreSQL"
3. Railway auto-configurará la variable `DATABASE_URL`

### 4. Configurar Variables de Entorno

**Variables CRÍTICAS que debes configurar:**

```env
# JWT (OBLIGATORIO - genera una clave fuerte)
JWT_SECRET_KEY=tu-clave-super-secreta-256-bits

# API Externa
INVENTORY_API_BASE_URL=https://inventoryapp.usbtopia.usbbog.edu.co

# Producción
DEBUG=false

# Sentry (opcional pero recomendado)
SENTRY_DSN=tu-sentry-dsn

# CORS (especifica dominios en producción)
ALLOWED_ORIGINS=https://tu-frontend.com,https://tu-app.railway.app
```

**Variables AUTO-CONFIGURADAS por Railway:**
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Puerto automático (no configurar manualmente)

### 5. Deploy automático
- Railway auto-detecta FastAPI
- Usa el `Procfile` o `railway.toml` 
- Primer deploy puede tomar 2-5 minutos

## 🔧 Verificación Post-Deploy

### 1. Health Check
```bash
curl https://tu-app.railway.app/health
# Debe retornar: {"status": "healthy"}
```

### 2. Verificar base de datos
```bash
curl https://tu-app.railway.app/
# Debe retornar info de la API
```

### 3. Test de autenticación
```bash
# Crear usuario de prueba
curl -X POST "https://tu-app.railway.app/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@test.com", 
    "password": "test123",
    "full_name": "Admin User",
    "dueno_de_activo": "IT",
    "is_superuser": true
  }'
```

## 🐛 Troubleshooting

### Error: "Application failed to respond"
- ✅ Verifica que `PORT` no esté configurada manualmente
- ✅ Revisa logs: `railway logs`

### Error: Database connection
- ✅ Verifica que PostgreSQL service esté running
- ✅ `DATABASE_URL` debe estar auto-configurada

### Error: JWT/Auth issues
- ✅ Configura `JWT_SECRET_KEY` obligatoriamente
- ✅ Debe ser una cadena fuerte (mínimo 32 caracteres)

### Error: CORS
- ✅ Configura `ALLOWED_ORIGINS` con tu dominio
- ✅ No uses `*` en producción

## 📊 Monitoring

### Logs en tiempo real
```bash
railway logs --tail
```

### Métricas
- CPU, Memory, Network disponibles en Railway dashboard
- Sentry para error tracking si está configurado

## 🔒 Seguridad en Producción

### Variables críticas:
- ✅ `JWT_SECRET_KEY` - Única y secreta
- ✅ `ALLOWED_ORIGINS` - Solo dominios permitidos  
- ✅ `DEBUG=false` - Nunca true en producción
- ✅ Sentry DSN para monitoring de errores

### Base de datos:
- ✅ Railway PostgreSQL incluye SSL por defecto
- ✅ Conexiones encriptadas automáticamente
- ✅ Backups automáticos cada 24h

## 🎉 ¡Listo para producción!

Tu API estará disponible en: `https://tu-proyecto.railway.app`

**Endpoints disponibles:**
- `GET /` - Info de la API
- `GET /health` - Health check  
- `POST /auth/register` - Registro
- `POST /auth/login` - Login
- `GET /inventario/` - Inventario (autenticado)