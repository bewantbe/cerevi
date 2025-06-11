<template>
  <div class="atlas-viewer">
    <div v-if="!visorStore.currentSpecimen" class="loading-state">
      <el-card class="welcome-card">
        <div class="welcome-content">
          <el-icon class="welcome-icon" size="48"><View /></el-icon>
          <h2>Loading Specimen...</h2>
          <p>Preparing the atlas viewer for {{ specimenId }}</p>
          <el-button @click="goHome">Back to Home</el-button>
        </div>
      </el-card>
    </div>

    <div v-else class="viewer-content">
      <!-- Status bar -->
      <div class="status-bar">
        <div class="status-left">
          <span class="specimen-name">{{ visorStore.currentSpecimen.name }}</span>
          <span class="view-info">{{ visorStore.currentView }} view</span>
          <span class="slice-info">
            Slice {{ visorStore.currentSliceForView + 1 }} / {{ visorStore.maxSlices[visorStore.currentView] + 1 }}
          </span>
        </div>
        
        <div class="status-center">
          <el-button-group size="small">
            <el-button 
              :type="visorStore.currentView === 'sagittal' ? 'primary' : 'default'"
              @click="visorStore.setCurrentView('sagittal')"
            >
              Sagittal
            </el-button>
            <el-button 
              :type="visorStore.currentView === 'coronal' ? 'primary' : 'default'"
              @click="visorStore.setCurrentView('coronal')"
            >
              Coronal
            </el-button>
            <el-button 
              :type="visorStore.currentView === 'horizontal' ? 'primary' : 'default'"
              @click="visorStore.setCurrentView('horizontal')"
            >
              Horizontal
            </el-button>
          </el-button-group>
        </div>
        
        <div class="status-right">
          <span class="coordinates" v-if="mouseCoordinates">
            X: {{ mouseCoordinates.x }}, Y: {{ mouseCoordinates.y }}, Z: {{ mouseCoordinates.z }}
          </span>
          <span class="channel-info">
            {{ visorStore.availableChannels[visorStore.currentChannel] }}
          </span>
        </div>
      </div>

      <!-- Main viewer area with control panel -->
      <div class="viewer-main">
        <!-- Control Panel -->
        <ControlPanel :specimen-id="props.specimenId" />
        
        <!-- ViewerGrid -->
        <div class="viewer-container">
          <ViewerGrid :specimen-id="props.specimenId" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useVISoRStore } from '@/stores/visor'
import ViewerGrid from '@/components/viewer/ViewerGrid.vue'
import ControlPanel from '@/components/controls/ControlPanel.vue'
import {
  View,
  ArrowLeft,
  ArrowRight,
  ZoomIn,
  ZoomOut,
  Close,
  Menu
} from '@element-plus/icons-vue'

// Props
interface Props {
  specimenId: string
}

const props = defineProps<Props>()
const router = useRouter()
const visorStore = useVISoRStore()

// Local state
const mouseCoordinates = ref<{ x: number; y: number; z: number } | null>(null)

// Computed
const currentSliceModel = computed({
  get: () => visorStore.currentSliceForView,
  set: (value: number) => visorStore.setCurrentSlice(value)
})

// Methods
function goHome() {
  router.push('/')
}

function previousSlice() {
  const currentSlice = visorStore.currentSliceForView
  if (currentSlice > 0) {
    visorStore.setCurrentSlice(currentSlice - 1)
  }
}

function nextSlice() {
  const currentSlice = visorStore.currentSliceForView
  const maxSlice = visorStore.maxSlices[visorStore.currentView]
  if (currentSlice < maxSlice) {
    visorStore.setCurrentSlice(currentSlice + 1)
  }
}

// Keyboard shortcuts
function handleKeydown(event: KeyboardEvent) {
  switch (event.key) {
    case 'ArrowLeft':
      event.preventDefault()
      previousSlice()
      break
    case 'ArrowRight':
      event.preventDefault()
      nextSlice()
      break
    case '1':
      visorStore.setCurrentView('sagittal')
      break
    case '2':
      visorStore.setCurrentView('coronal')
      break
    case '3':
      visorStore.setCurrentView('horizontal')
      break
    case 's':
      visorStore.toggleSidebar()
      break
    case 'a':
      visorStore.toggleAtlasOverlay()
      break
  }
}

// Lifecycle
onMounted(async () => {
  // Load specimen if not already loaded
  if (!visorStore.currentSpecimen || visorStore.currentSpecimen.id !== props.specimenId) {
    await visorStore.setCurrentSpecimen(props.specimenId)
  }
  
  // Add keyboard event listeners
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.atlas-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px;
}

.welcome-card {
  max-width: 500px;
  text-align: center;
}

.welcome-content {
  padding: 40px 20px;
}

.welcome-icon {
  color: #409eff;
  margin-bottom: 20px;
}

.welcome-content h2 {
  color: #303133;
  margin-bottom: 16px;
}

.welcome-content p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 20px;
}

.viewer-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.status-bar {
  height: 40px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  font-size: 12px;
  color: #606266;
  z-index: 1001;
}

.status-left {
  display: flex;
  gap: 16px;
  align-items: center;
}

.specimen-name {
  font-weight: 600;
  color: #303133;
}

.status-center {
  display: flex;
  align-items: center;
}

.status-right {
  display: flex;
  gap: 16px;
  align-items: center;
}

.coordinates {
  font-family: 'Courier New', monospace;
  background: rgba(64, 158, 255, 0.1);
  padding: 2px 6px;
  border-radius: 3px;
}

.viewer-main {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
}

.viewer-container {
  flex: 1;
  margin-left: 360px; /* Account for control panel width */
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
}

/* Responsive design */
@media (max-width: 1024px) {
  .viewer-container {
    margin-left: 0;
  }
  
  .status-bar {
    flex-direction: column;
    height: auto;
    padding: 8px 16px;
    gap: 8px;
  }
  
  .status-left,
  .status-center,
  .status-right {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .viewer-main {
    flex-direction: column;
  }
  
  .viewer-container {
    margin-left: 0;
  }
}

/* Keyboard shortcut info */
.atlas-viewer:focus {
  outline: none;
}

/* Ensure proper stacking */
.atlas-viewer {
  position: relative;
  z-index: 1;
}

/* Loading and transition states */
.viewer-content {
  transition: all 0.3s ease;
}

.loading-state {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .status-bar {
    border-bottom: 2px solid #000;
  }
  
  .coordinates {
    border: 1px solid #000;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .viewer-container,
  .viewer-content,
  .loading-state {
    transition: none;
    animation: none;
  }
}
</style>
