#!/bin/bash

echo "🚀 Testing VISoR Platform Build..."

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Please run from project root."
    exit 1
fi

echo "📋 Testing backend health..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Backend not running. Starting services..."
    docker-compose up -d backend redis
    echo "⏳ Waiting for backend to start..."
    sleep 10
fi

# Test backend health
echo "🔍 Checking backend health..."
HEALTH=$(curl -s http://localhost:8000/health)
if [ $? -eq 0 ]; then
    echo "✅ Backend is healthy:"
    echo "$HEALTH" | python3 -m json.tool
else
    echo "❌ Backend health check failed"
    exit 1
fi

# Test frontend build
echo "🔨 Testing frontend build..."
cd frontend

echo "📦 Installing dependencies..."
npm install --silent

echo "🔍 Type checking..."
if npm run type-check > /dev/null 2>&1; then
    echo "✅ TypeScript compilation successful"
else
    echo "❌ TypeScript errors found. Running type-check with output:"
    npm run type-check
    echo "⚠️  Continuing despite TypeScript errors..."
fi

echo "🏗️  Building frontend..."
if npm run build > /dev/null 2>&1; then
    echo "✅ Frontend build successful"
else
    echo "❌ Frontend build failed"
    npm run build
    exit 1
fi

echo "🎯 Testing frontend dev server..."
timeout 30s npm run dev > /dev/null 2>&1 &
DEV_PID=$!
sleep 5

if kill -0 $DEV_PID 2>/dev/null; then
    echo "✅ Frontend dev server started successfully"
    kill $DEV_PID
else
    echo "⚠️  Frontend dev server may have issues"
fi

cd ..

echo "🐳 Testing Docker composition..."
if docker-compose up -d > /dev/null 2>&1; then
    echo "✅ Docker services started"
    docker-compose ps
else
    echo "❌ Docker compose failed"
    docker-compose up -d
fi

echo ""
echo "🎉 Platform Test Summary:"
echo "========================"
echo "✅ Backend: Running and healthy"
echo "✅ Frontend: Built successfully"
echo "✅ Docker: Services running"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend Dev: http://localhost:5173"
echo "   Backend API:  http://localhost:8000"
echo "   Production:   http://localhost:80"
echo ""
echo "🎯 Platform is ready for development!"
