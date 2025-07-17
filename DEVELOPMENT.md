# VISoR Platform Development Guide

A comprehensive guide for frontend and full-stack development of the VISoR Platform.

> **Note**: For backend-specific development, see [BACKEND_DEVELOPMENT.md](BACKEND_DEVELOPMENT.md)

## 🚀 Quick Start

### Frontend Development (Hot Reload)
```bash
# Start development environment with hot reloading
./scripts/start_services.sh

# Access the application
open http://localhost:3001  # Frontend with hot reload
open http://localhost:8000  # Backend API
```

### Local Frontend Development
```bash
# Install dependencies
cd frontend
npm install

# Start Vite dev server
npm run dev

# Access at http://localhost:5173
```

### Full Stack Development
```bash
# Start backend (see BACKEND_DEVELOPMENT.md for details)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Start frontend (in another terminal)
cd frontend
npm run dev

# Both services running independently
```

## 📋 Prerequisites

### Frontend Requirements
- **Node.js 18+** (recommended: LTS version)
- **npm 9+** or **yarn 1.22+**
- **Git** (for version control)

### System Setup
```bash
# Verify Node.js version
node --version  # Should be 18+

# Verify npm version  
npm --version   # Should be 9+

# Install dependencies
cd frontend
npm install
```

## 🏗️ Frontend Project Structure

```
frontend/
├── src/
│   ├── components/        # Vue components
│   │   ├── controls/      # Control panel components
│   │   ├── home/          # Home page components
│   │   ├── layout/        # Layout components (Header, Footer)
│   │   ├── region/        # Region browser components
│   │   ├── ui/            # Reusable UI components
│   │   └── viewer/        # Image/3D viewer components
│   ├── composables/       # Vue 3 composition functions
│   ├── locales/           # Internationalization files
│   ├── router/            # Vue Router configuration
│   ├── services/          # API service layer
│   ├── stores/            # Pinia state management
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   └── views/             # Page-level components
├── public/                # Static assets
├── tests/                 # Frontend tests
├── package.json           # Dependencies and scripts
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript configuration
├── Dockerfile             # Production Docker image
└── Dockerfile.dev         # Development Docker image
```

## 💻 Development Workflow

### Docker Development (Recommended)

**Hot Reloading with Docker:**
```bash
# Start development environment
./scripts/start_services.sh

# What this does:
# ✅ Stops existing containers
# ✅ Rebuilds development images
# ✅ Starts Vite dev server with HMR
# ✅ Mounts source code for live updates
```

**Backend Development without Redis:**
```bash
# For backend development when Redis is not needed or available
docker-compose -f docker-compose.yml -f docker-compose.dev-backend-no-redis.yml up backend frontend

# This configuration:
# ✅ Disables Redis dependency for backend
# ✅ Enables debug mode
# ✅ Useful for testing without cache layer
```

**Access Points:**
- **Frontend (Hot Reload)**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

**Development Features:**
- ✅ **Hot Module Replacement (HMR)**: Instant updates without page refresh
- ✅ **Vue DevTools**: Browser extension support
- ✅ **TypeScript**: Real-time type checking
- ✅ **ESLint**: Code quality checks
- ✅ **Automatic Imports**: Auto-import Vue composables

### Local Development

**Start Frontend Locally:**
```bash
cd frontend

# Install dependencies (first time)
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm run test

# Lint and format code
npm run lint
npm run format
```

**Environment Configuration:**
```bash
# frontend/.env.development
VITE_API_URL=http://localhost:8000
VITE_APP_TITLE=VISoR Platform (Dev)

# frontend/.env.production
VITE_API_URL=https://api.visor.example.com
VITE_APP_TITLE=VISoR Platform
```

## 🔧 Frontend Technology Stack

### Core Technologies
- **Vue.js 3**: Reactive frontend framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **Pinia**: State management
- **Vue Router**: Client-side routing

### UI and Visualization
- **OpenSeadragon**: High-performance image viewer
- **Three.js**: 3D brain visualization
- **Element Plus**: Vue 3 UI component library
- **CSS3**: Modern styling with grid and flexbox

### Development Tools
- **ESLint**: Code linting
- **Prettier**: Code formatting
- **Vitest**: Unit testing framework
- **Vue DevTools**: Browser development extension

## 🎨 Frontend Development Patterns

### Vue 3 Composition API
```typescript
// composables/useViewer.ts
import { ref, computed } from 'vue'
import { useVisorStore } from '@/stores/visor'

export function useViewer() {
  const store = useVisorStore()
  const isLoading = ref(false)
  
  const currentSpecimen = computed(() => store.currentSpecimen)
  
  const loadSpecimen = async (specimenId: string) => {
    isLoading.value = true
    try {
      await store.loadSpecimen(specimenId)
    } finally {
      isLoading.value = false
    }
  }
  
  return {
    isLoading,
    currentSpecimen,
    loadSpecimen
  }
}
```

### State Management with Pinia
```typescript
// stores/visor.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Specimen } from '@/types'

export const useVisorStore = defineStore('visor', () => {
  const specimens = ref<Specimen[]>([])
  const currentSpecimenId = ref<string | null>(null)
  
  const currentSpecimen = computed(() => 
    specimens.value.find(s => s.id === currentSpecimenId.value)
  )
  
  const loadSpecimens = async () => {
    const response = await fetch('/api/specimens')
    specimens.value = await response.json()
  }
  
  return {
    specimens,
    currentSpecimen,
    loadSpecimens
  }
})
```

### API Service Layer
```typescript
// services/api.ts
import axios from 'axios'
import type { Specimen, Region } from '@/types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000'
})

export const specimenApi = {
  getAll: (): Promise<Specimen[]> => 
    api.get('/api/specimens').then(res => res.data),
    
  getById: (id: string): Promise<Specimen> =>
    api.get(`/api/specimens/${id}`).then(res => res.data),
    
  getRegions: (id: string): Promise<Region[]> =>
    api.get(`/api/specimens/${id}/regions`).then(res => res.data)
}
```

## 🐳 Docker Development Deep Dive

### Development vs Production Containers

**Development Configuration** (`docker-compose.dev.yml`):
```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile.dev
  ports:
    - "3001:5173"  # Map to Vite dev server
  volumes:
    - ./frontend:/app
    - /app/node_modules
  environment:
    - VITE_API_URL=http://localhost:8000
```

**Production Configuration** (`docker-compose.yml`):
```yaml
frontend:
  build: ./frontend
  ports:
    - "3000:80"  # Map to nginx
  environment:
    - VITE_API_URL=http://localhost:8000
```

### Container Management

**Development Commands:**
```bash
# Start development environment
./scripts/start_services.sh

# Manual development startup
docker-compose -f docker-compose.yml -f docker-compose.dev-frontend.yml up --build

# View frontend logs
docker-compose logs frontend

# Rebuild frontend container
docker-compose build frontend --no-cache

# Stop and clean up
docker-compose down --remove-orphans
```

**Why Different Ports?**
- **Port 3000**: Production nginx server
- **Port 3001**: Development Vite server with HMR
- **Port 5173**: Internal Vite dev server port

## 🧪 Testing

### Running Tests
```bash
# Unit tests with Vitest
cd frontend
npm run test

# Watch mode for development
npm run test:watch

# Coverage report
npm run test:coverage

# E2E tests (if configured)
npm run test:e2e
```

### Writing Tests
```typescript
// tests/components/Header.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Header from '@/components/layout/Header.vue'

describe('Header', () => {
  it('renders title correctly', () => {
    const wrapper = mount(Header)
    expect(wrapper.find('h1').text()).toBe('VISoR Platform')
  })
})
```

## 🔍 Debugging

### Vue DevTools
1. Install Vue DevTools browser extension
2. Open developer tools in browser
3. Navigate to "Vue" tab
4. Inspect component state, events, and performance

### Development Debugging
```typescript
// Use console logging for debugging
console.log('Current specimen:', currentSpecimen.value)

// Use Vue's built-in debugging
import { watchEffect } from 'vue'

watchEffect(() => {
  console.log('Specimen changed:', currentSpecimen.value)
})
```

### Container Debugging
```bash
# View frontend container logs
docker-compose logs frontend

# Access container shell
docker-compose exec frontend sh

# Check Vite dev server status
curl http://localhost:3001

# Monitor container resources
docker stats frontend
```

## 🚀 Build and Deployment

### Production Build
```bash
# Build for production
cd frontend
npm run build

# Preview production build locally
npm run preview

# Analyze bundle size
npm run build -- --analyze
```

### Docker Production
```bash
# Build production image
docker build -t visor-frontend ./frontend

# Run production container
docker run -d -p 3000:80 visor-frontend

# Full stack production
docker-compose up --build
```

## 🔧 Configuration

### Vite Configuration
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',  // For Docker compatibility
    port: 5173,
    watch: {
      usePolling: true  // For Docker file watching
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  }
})
```

### TypeScript Configuration
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "Node",
    "strict": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

## 📚 Additional Resources

### Frontend Documentation
- **[Vue.js 3 Guide](https://vuejs.org/guide/)**
- **[Vite Documentation](https://vitejs.dev/guide/)**
- **[OpenSeadragon API](https://openseadragon.github.io/docs/)**
- **[Three.js Documentation](https://threejs.org/docs/)**

### Development Tools
- **[Vue DevTools](https://devtools.vuejs.org/)**
- **[Vite DevTools](https://github.com/webfansplz/vite-plugin-vue-devtools)**
- **[ESLint Vue Plugin](https://eslint.vuejs.org/)**

## 🛠️ Troubleshooting

### Common Issues

**1. Hot Reload Not Working**
```bash
# Check if using correct port
open http://localhost:3001  # Not 3000!

# Restart development environment
docker-compose down
./scripts/start_services.sh
```

**2. TypeScript Errors**
```bash
# Check TypeScript configuration
npx tsc --noEmit

# Update dependencies
npm update
```

**3. Build Failures**
```bash
# Clear node_modules and reinstall
rm -rf frontend/node_modules frontend/package-lock.json
cd frontend && npm install

# Clear Docker build cache
docker system prune -f
```

**4. API Connection Issues**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check CORS configuration
# Ensure backend allows frontend origin
```

### Performance Tips

1. **Use Vue 3 Composition API** for better tree-shaking
2. **Lazy load routes** with dynamic imports
3. **Optimize images** with appropriate formats and sizes
4. **Use computed properties** instead of methods for reactive data
5. **Implement virtual scrolling** for large lists

---

## 📞 Support

For frontend development questions:

1. **Check this guide** for common solutions
2. **Review Vue.js documentation** for framework-specific issues
3. **Use Vue DevTools** for component debugging
4. **Check browser console** for JavaScript errors
5. **Review container logs** for Docker-related issues

---

*This guide covers frontend and full-stack development. For backend-only development, see [BACKEND_DEVELOPMENT.md](BACKEND_DEVELOPMENT.md).*
