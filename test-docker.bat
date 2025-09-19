@echo off
REM Test script para verificar Docker build y funcionamiento en Windows

echo 🐳 Testing Docker build for API_AUTH...

REM Build the Docker image
echo 📦 Building Docker image...
docker build -t api-auth:test .

if %ERRORLEVEL% EQU 0 (
    echo ✅ Docker build successful!
    
    REM Test that the image runs
    echo 🚀 Testing container startup...
    docker run --rm -d --name api-auth-test -p 8001:8000 -e JWT_SECRET_KEY=test-secret -e DATABASE_URL=postgresql://test:test@localhost/test api-auth:test
    
    REM Wait a few seconds for startup
    timeout /t 5 /nobreak >nul
    
    REM Test health endpoint
    echo 🔍 Testing health endpoint...
    curl -s -o nul -w "%%{http_code}" http://localhost:8001/health > temp_response.txt
    set /p response=<temp_response.txt
    del temp_response.txt
    
    if "%response%"=="200" (
        echo ✅ Health check passed!
    ) else (
        echo ❌ Health check failed ^(HTTP %response%^)
    )
    
    REM Clean up
    echo 🧹 Cleaning up...
    docker stop api-auth-test
    
    echo 🎉 Docker test completed!
) else (
    echo ❌ Docker build failed!
    exit /b 1
)