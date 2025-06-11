<template>
  <div class="viewer-grid" :class="[layoutClass, { maximized: isMaximized }]">
    <!-- Grid Layout -->
    <div v-if="!isMaximized" class="grid-container">
      <!-- Sagittal View (Top Left) -->
      <div 
        class="view-panel sagittal" 
        @click="maximizeView('sagittal')"
        @dblclick="maximizeView('sagittal')"
      >
        <div class="view-header">
          <span class="view-title">Sagittal (YZ)</span>
          <div class="view-actions">
            <el-button 
              size="small" 
              type="primary" 
              circle 
              @click.stop="maximizeView('sagittal')"
            >
              <el-icon><FullScreen /></el-icon>
            </el-button>
          </div>
        </div>
        <OpenSeadragonViewer
          :specimen-id="specimenId"
          view="sagittal"
          :channel="currentChannel"
          :level="currentLevel"
        />
      </div>

      <!-- Coronal View (Top Right) -->
      <div 
        class="view-panel coronal" 
        @click="maximizeView('coronal')"
        @dblclick="maximizeView('coronal')"
      >
        <div class="view-header">
          <span class="view-title">Coronal (XZ)</span>
          <div class="view-actions">
            <el-button 
              size="small" 
              type="primary" 
              circle 
              @click.stop="maximizeView('coronal')"
            >
              <el-icon><FullScreen /></el-icon>
            </el-button>
          </div>
        </div>
        <OpenSeadragonViewer
          :specimen-id="specimenId"
          view="coronal"
          :channel="currentChannel"
          :level="currentLevel"
        />
      </div>

      <!-- Horizontal View (Bottom Left) -->
      <div 
        class="view-panel horizontal" 
        @click="maximizeView('horizontal')"
        @dblclick="maximizeView('horizontal')"
      >
        <div class="view-header">
          <span class="view-title">Horizontal (XY)</span>
          <div class="view-actions">
            <el-button 
              size="small" 
              type="primary" 
              circle 
              @click.stop="maximizeView('horizontal')"
            >
              <el-icon><FullScreen /></el-icon>
            </el-button>
          </div>
        </div>
        <OpenSeadragonViewer
          :specimen-id="specimenId"
          view="horizontal"
          :channel="currentChannel"
          :level="currentLevel"
        />
      </div>

      <!-- 3D View (Bottom Right) -->
      <div 
        class="view-panel threejs" 
        @click="maximizeView('3d')"
        @dblclick="maximizeView('3d')"
      >
        <div class="view-header">
          <span class="view-title">3D Brain Shell</span>
          <div class="view-actions">
            <el-button 
              size="small" 
              type="primary" 
              circle 
              @click.stop="maximizeView('3d')"
            >
              <el-icon><FullScreen /></el-icon>
            </el-button>
          </div>
        </div>
        <ThreeJSViewer
          :specimen-id="specimenId"
          :coordinates="currentCoordinates"
          :show-crosshair="syncEnabled"
          @model-loaded="onModelLoaded"
          @coordinate-update="onCoordinateUpdate"
        />
      </div>
    </div>

    <!-- Maximized View -->
    <div v-else class="maximized-container">
      <div class="maximized-header">
        <h3 class="maximized-title">{{ maximizedViewTitle }}</h3>
        <div class="maximized-actions">
          <el-button-group>
            <el-button 
              v-for="view in availableViews" 
              :key="view.key"
              size="small"
              :type="maximizedView === view.key ? 'primary' : 'default'"
              @click="setMaximizedView(view.key)"
            >
              {{ view.label }}
            </el-button>
          </el-button-group>
          <el-button 
            size="small" 
            @click="exitMaximized"
          >
            <el-icon><Grid /></el-icon>
            Grid View
          </el-button>
        </div>
      </div>

      <div class="maximized-content">
        <OpenSeadragonViewer
          v-if="maximizedView && maximizedView !== '3d'"
          :specimen-id="specimenId"
          :view="maximizedView as any"
          :channel="currentChannel"
          :level="currentLevel"
        />
        <ThreeJSViewer
          v-else-if="maximizedView === '3d'"
          :specimen-id="specimenId"
          :coordinates="currentCoordinates"
          :show-crosshair="syncEnabled"
          @model-loaded="onModelLoaded"
          @coordinate-update="onCoordinateUpdate"
        />
      </div>
    </div>

    <!-- Synchronization Controls -->
    <div class="sync-controls">
      <el-switch
        v-model="syncEnabled"
        active-text="Sync Views"
        inactive-text="Independent"
        @change="onSyncToggle"
      />
      <el-tooltip content="Cross-hair cursor" placement="top">
        <el-switch
          v-model="crosshairEnabled"
          active-text="Crosshair"
          @change="onCrosshairToggle"
        />
      </el-tooltip>
    </div>

    <!-- Loading overlay -->
    <div v-if="loading" class="grid-loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>Loading viewer...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { 
  ElButton, 
  ElButtonGroup, 
  ElIcon, 
  ElSwitch,
  ElTooltip 
} from 'element-plus'
import { 
  FullScreen, 
  Grid, 
  Box, 
  Loading 
} from '@element-plus/icons-vue'
import OpenSeadragonViewer from './OpenSeadragonViewer.vue'
import ThreeJSViewer from './ThreeJSViewer.vue'
import { useVISoRStore } from '@/stores/visor'
import type { CoordinatePosition } from '@/composables/useThreeJS'

interface Props {
  specimenId: string
}

const props = defineProps<Props>()

// Store
const visorStore = useVISoRStore()

// State
const maximizedView = ref<string | null>(null)
const syncEnabled = ref(true)
const crosshairEnabled = ref(false)
const loading = ref(false)

// Computed
const isMaximized = computed(() => maximizedView.value !== null)

const layoutClass = computed(() => {
  if (isMaximized.value) return 'layout-maximized'
  return 'layout-grid'
})

const currentChannel = computed(() => visorStore.currentChannel)
const currentLevel = computed(() => visorStore.currentLevel)

const maximizedViewTitle = computed(() => {
  if (!maximizedView.value) return ''
  
  const titles = {
    sagittal: 'Sagittal View (YZ Plane)',
    coronal: 'Coronal View (XZ Plane)',
    horizontal: 'Horizontal View (XY Plane)',
    '3d': '3D Brain Shell Visualization'
  }
  
  return titles[maximizedView.value as keyof typeof titles] || ''
})

const availableViews = [
  { key: 'sagittal', label: 'Sagittal' },
  { key: 'coronal', label: 'Coronal' },
  { key: 'horizontal', label: 'Horizontal' },
  { key: '3d', label: '3D' }
]

// Current coordinates for 3D viewer synchronization
const currentCoordinates = computed((): CoordinatePosition => {
  const view = visorStore.currentView
  const slice = visorStore.currentSlice[view] || 0
  const imageInfo = visorStore.imageInfo
  
  if (!imageInfo) {
    // Return safe defaults while loading
    return { x: 0, y: 0, z: 0 }
  }
  
  // Get dynamic image dimensions [z, y, x]
  const [dimZ, dimY, dimX] = imageInfo.dimensions
  const centerX = Math.floor(dimX / 2)
  const centerY = Math.floor(dimY / 2)
  const centerZ = Math.floor(dimZ / 2)
  
  // Convert based on current view to get 3D coordinates
  switch (view) {
    case 'sagittal':
      return { x: slice, y: centerY, z: centerZ } // Fix X, vary Y,Z
    case 'coronal':
      return { x: centerX, y: slice, z: centerZ } // Fix Y, vary X,Z
    case 'horizontal':
      return { x: centerX, y: centerY, z: slice } // Fix Z, vary X,Y
    default:
      return { x: centerX, y: centerY, z: centerZ } // Center coordinates
  }
})

// Methods
const maximizeView = (view: string) => {
  maximizedView.value = view
  visorStore.setCurrentView(view as any)
}

const setMaximizedView = (view: string) => {
  maximizedView.value = view
  visorStore.setCurrentView(view as any)
}

const exitMaximized = () => {
  maximizedView.value = null
}

const onSyncToggle = (val: string | number | boolean) => {
  const enabled = Boolean(val)
  syncEnabled.value = enabled
  // TODO: Implement view synchronization logic
  console.log('View sync toggled:', enabled)
}

const onCrosshairToggle = (val: string | number | boolean) => {
  const enabled = Boolean(val)
  crosshairEnabled.value = enabled
  // TODO: Implement crosshair cursor logic
  console.log('Crosshair toggled:', enabled)
}

// 3D viewer event handlers
const onModelLoaded = (loaded: boolean) => {
  console.log('3D model loaded:', loaded)
  // TODO: Update UI state or show success notification
}

const onCoordinateUpdate = (coordinates: CoordinatePosition) => {
  console.log('Coordinate update from 3D viewer:', coordinates)
  // TODO: Sync with 2D viewers if sync is enabled
  if (syncEnabled.value) {
    // Update store with new coordinates
    // This will trigger updates in other viewers
  }
}

// Keyboard shortcuts
const handleKeydown = (event: KeyboardEvent) => {
  // Only handle if not typing in an input
  if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
    return
  }

  switch (event.key) {
    case '1':
      event.preventDefault()
      maximizeView('sagittal')
      break
    case '2':
      event.preventDefault()
      maximizeView('coronal')
      break
    case '3':
      event.preventDefault()
      maximizeView('horizontal')
      break
    case '4':
      event.preventDefault()
      maximizeView('3d')
      break
    case 'Escape':
      event.preventDefault()
      exitMaximized()
      break
    case 'g':
      event.preventDefault()
      exitMaximized()
      break
    case 's':
      if (event.ctrlKey || event.metaKey) {
        event.preventDefault()
        syncEnabled.value = !syncEnabled.value
      }
      break
  }
}

// Lifecycle
import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

// Watch for specimen changes
watch(
  () => props.specimenId,
  () => {
    loading.value = true
    // Reset to grid view when specimen changes
    exitMaximized()
    
    // Simulate loading delay
    setTimeout(() => {
      loading.value = false
    }, 1000)
  },
  { immediate: true }
)
</script>

<style scoped>
.viewer-grid {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  position: relative;
  background: #f5f5f5;
}

.grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 8px;
  flex: 1;
  padding: 8px;
}

.view-panel {
  position: relative;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 200px;
}

.view-panel:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  font-size: 14px;
  font-weight: 500;
}

.view-title {
  color: #495057;
}

.view-actions {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.view-panel:hover .view-actions {
  opacity: 1;
}

.view-panel .openseadragon-viewer,
.view-panel .threejs-placeholder {
  height: calc(100% - 41px); /* Subtract header height */
}

.threejs-placeholder,
.threejs-maximized {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  background: #000;
  gap: 12px;
}

.placeholder-icon {
  font-size: 48px;
  opacity: 0.5;
}

.placeholder-icon.large {
  font-size: 96px;
}

.threejs-placeholder small,
.threejs-maximized small {
  font-size: 12px;
  opacity: 0.7;
}

/* Maximized Layout */
.maximized-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.maximized-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.maximized-title {
  margin: 0;
  color: #495057;
  font-size: 18px;
  font-weight: 500;
}

.maximized-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.maximized-content {
  flex: 1;
  padding: 8px;
}

.maximized-content .openseadragon-viewer {
  height: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Synchronization Controls */
.sync-controls {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  gap: 12px;
  background: rgba(255, 255, 255, 0.95);
  padding: 8px 12px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(4px);
  z-index: 10;
}

/* Loading Overlay */
.grid-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  z-index: 1000;
  gap: 12px;
}

.grid-loading .el-icon {
  font-size: 32px;
  color: #409eff;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .grid-container {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(4, 300px);
    gap: 4px;
    padding: 4px;
  }
  
  .sync-controls {
    position: static;
    margin: 8px;
    justify-content: center;
  }
  
  .maximized-header {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
  
  .maximized-actions {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .view-header {
    padding: 6px 8px;
    font-size: 12px;
  }
  
  .maximized-title {
    font-size: 16px;
  }
  
  .sync-controls {
    flex-direction: column;
    gap: 8px;
  }
}

/* Animation Classes */
.layout-grid {
  animation: gridAppear 0.3s ease-out;
}

.layout-maximized {
  animation: maximizeAppear 0.3s ease-out;
}

@keyframes gridAppear {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes maximizeAppear {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Accessibility */
.view-panel:focus {
  outline: 2px solid #409eff;
  outline-offset: 2px;
}

.view-panel[tabindex] {
  outline: none;
}

.view-panel[tabindex]:focus-visible {
  outline: 2px solid #409eff;
  outline-offset: 2px;
}
</style>
