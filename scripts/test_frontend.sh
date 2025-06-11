#!/bin/bash

# VISoR Platform Frontend Test Script

echo "🧪 VISoR Platform Frontend Test"
echo "==============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: docker-compose.yml not found. Please run from project root.${NC}"
    exit 1
fi

echo -e "${BLUE}📁 Project structure check...${NC}"

# Check frontend directory structure
REQUIRED_DIRS=(
    "frontend/src"
    "frontend/src/components/layout"
    "frontend/src/components/home"
    "frontend/src/views"
    "frontend/src/stores"
    "frontend/src/services"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $dir"
    else
        echo -e "${RED}✗${NC} $dir (missing)"
    fi
done

echo

# Check key frontend files
REQUIRED_FILES=(
    "frontend/package.json"
    "frontend/src/main.ts"
    "frontend/src/App.vue"
    "frontend/src/router/index.ts"
    "frontend/src/stores/visor.ts"
    "frontend/src/services/api.ts"
    "frontend/src/views/HomePage.vue"
    "frontend/src/views/AtlasViewer.vue"
    "frontend/src/views/AboutView.vue"
    "frontend/src/components/layout/Header.vue"
    "frontend/src/components/layout/Footer.vue"
    "frontend/src/components/home/SpecimenCard.vue"
    "frontend/Dockerfile"
    "frontend/nginx.conf"
)

echo -e "${BLUE}📄 Required files check...${NC}"
missing_files=0

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (missing)"
        ((missing_files++))
    fi
done

echo

# Check Node.js and npm
echo -e "${BLUE}🔧 Development environment check...${NC}"

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js: $NODE_VERSION"
else
    echo -e "${RED}✗${NC} Node.js not found"
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓${NC} npm: $NPM_VERSION"
else
    echo -e "${RED}✗${NC} npm not found"
fi

echo

# Check if dependencies are installed
echo -e "${BLUE}📦 Dependencies check...${NC}"

if [ -f "frontend/package-lock.json" ]; then
    echo -e "${GREEN}✓${NC} package-lock.json exists"
    
    if [ -d "frontend/node_modules" ]; then
        echo -e "${GREEN}✓${NC} node_modules directory exists"
        
        # Count installed packages
        if [ -f "frontend/node_modules/.package-lock.json" ]; then
            echo -e "${GREEN}✓${NC} Dependencies appear to be installed"
        else
            echo -e "${YELLOW}⚠${NC} Dependencies may need to be installed"
        fi
    else
        echo -e "${YELLOW}⚠${NC} node_modules directory missing - run 'npm install'"
    fi
else
    echo -e "${RED}✗${NC} package-lock.json missing"
fi

echo

# Check Docker setup
echo -e "${BLUE}🐳 Docker configuration check...${NC}"

if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker is available"
else
    echo -e "${RED}✗${NC} Docker not found"
fi

if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker Compose is available"
else
    echo -e "${RED}✗${NC} Docker Compose not found"
fi

# Check docker-compose.yml for frontend service
if grep -q "frontend:" docker-compose.yml; then
    echo -e "${GREEN}✓${NC} Frontend service defined in docker-compose.yml"
else
    echo -e "${RED}✗${NC} Frontend service missing in docker-compose.yml"
fi

echo

# Summary
echo -e "${BLUE}📊 Test Summary${NC}"
echo "==============="

if [ $missing_files -eq 0 ]; then
    echo -e "${GREEN}✅ All required files are present${NC}"
else
    echo -e "${RED}❌ $missing_files required files are missing${NC}"
fi

# Provide next steps
echo
echo -e "${BLUE}🚀 Next Steps${NC}"
echo "============="

if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}1.${NC} Install frontend dependencies:"
    echo "   cd frontend && npm install"
    echo
fi

echo -e "${YELLOW}2.${NC} Start development servers:"
echo "   docker-compose up -d"
echo

echo -e "${YELLOW}3.${NC} Or start frontend in development mode:"
echo "   cd frontend && npm run dev"
echo

echo -e "${YELLOW}4.${NC} Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - Full stack: http://localhost:80 (nginx)"
echo

echo -e "${YELLOW}5.${NC} Test the backend API:"
echo "   curl http://localhost:8000/health"
echo

if [ $missing_files -eq 0 ]; then
    echo -e "${GREEN}🎉 Frontend setup is complete and ready for development!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Please fix missing files before proceeding.${NC}"
    exit 1
fi
