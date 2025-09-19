#!/bin/bash
# Test script para verificar Docker build y funcionamiento

echo "🐳 Testing Docker build for API_AUTH..."

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t api-auth:test .

if [ $? -eq 0 ]; then
    echo "✅ Docker build successful!"
    
    # Test that the image runs
    echo "🚀 Testing container startup..."
    docker run --rm -d --name api-auth-test -p 8001:8000 \
        -e JWT_SECRET_KEY=test-secret \
        -e DATABASE_URL=postgresql://test:test@localhost/test \
        api-auth:test
    
    # Wait a few seconds for startup
    sleep 5
    
    # Test health endpoint
    echo "🔍 Testing health endpoint..."
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health)
    
    if [ "$response" = "200" ]; then
        echo "✅ Health check passed!"
    else
        echo "❌ Health check failed (HTTP $response)"
    fi
    
    # Clean up
    echo "🧹 Cleaning up..."
    docker stop api-auth-test
    
    echo "🎉 Docker test completed!"
else
    echo "❌ Docker build failed!"
    exit 1
fi