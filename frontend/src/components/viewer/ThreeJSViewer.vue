<template>
  <div class="threejs-viewer" ref="containerRef">
    <!-- Loading overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <el-icon class="is-loading">
        <Loading />
      </el-icon>
      <span>Loading 3D model...</span>
    </div>

    <!-- Error overlay -->
    <div v-if="error" class="error-overlay">
      <el-icon>
        <Warning />
      </el-icon>
      <span>{{ error }}</span>
      <el-button size="small" @click="retry">Retry</el-button>
    </div>

    <!-- Controls overlay -->
    <div class="viewer-controls">
      <!-- Camera info -->
      <div class="camera-info">
        <div class="info-row">
          <span class="info-label">Camera:</span>
          <span class="info-value">{{ cameraPosition }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Target:</span>
          <span class="info-value">{{ cameraTarget }}</span>
        </div>
        <div v-if="coordinates" class="info-row">
          <span class="info-label">Position:</span>
          <span class="info-value">{{ coordinates.x }}, {{ coordinates.y }}, {{ coordinates.z }}</span>
        </div>
      </div>

      <!-- View controls -->
      <div class="view-controls">
        <el-button-group size="small">
          <el-button @click="resetCamera" title="Reset Camera">
            <el-icon><Refresh /></el-icon>
          </el-button>
          <el-button @click="toggleWireframe" title="Toggle Wireframe">
            <el-icon><Grid /></el-icon>
          </el-button>
          <el-button @click="toggleGrid" title="Toggle Grid">
            <el-icon><Menu /></el-icon>
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- Model status -->
    <div v-if="modelLoaded" class="model-status">
      <el-icon class="status-icon">
        <Check />
      </el-icon>
      <span>3D model loaded</span>
    </div>

    <!-- No model available -->
    <div v-if="!hasModel && !isLoading" class="no-model-info">
      <el-icon class="no-model-icon">
        <Box />
      </el-icon>
      <span>No 3D model available</span>
      <small>3D brain shell model not found for this specimen</small>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { 
  ElIcon, 
  ElButton, 
  ElButtonGroup 
} from 'element-plus'
import { 
  Loading, 
  Warning, 
  Refresh, 
  Grid, 
  Menu,
  Check,
  Box
} from '@element-plus/icons-vue'
import { useThreeJS, type CoordinatePosition } from '@/composables/useThreeJS'
import { useVISoRStore } from '@/stores/visor'

interface Props {
  specimenId: string
  coordinates?: CoordinatePosition
  showCrosshair?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showCrosshair: false
})

// Emits
const emit = defineEmits<{
  'model-loaded': [loaded: boolean]
  'coordinate-update': [coordinates: CoordinatePosition]
}>()

// Refs
const containerRef = ref<HTMLElement>()

// Store
const visorStore = useVISoRStore()

// Three.js composable
const {
  scene,
  camera,
  renderer,
  controls,
  brainMesh,
  isLoading,
  error,
  cameraPosition,
  cameraTarget,
  wireframeMode,
  modelLoaded,
  crosshairPosition,
  initThreeJS,
  loadBrainModel,
  updateCrosshair,
  toggleWireframe,
  resetCamera,
  handleResize,
  cleanup
} = useThreeJS(containerRef)

// Local state
const gridVisible = ref(false)

// Computed
const hasModel = computed(() => {
  return visorStore.currentSpecimen?.has_model || false
})

// Methods
const retry = async () => {
  if (!props.specimenId || !hasModel.value) return
  
  await initializeViewer()
}

const toggleGrid = () => {
  gridVisible.value = !gridVisible.value
  // TODO: Implement grid toggle in Three.js scene
  console.log('Grid toggled:', gridVisible.value)
}

const initializeViewer = async () => {
  if (!containerRef.value) return
  
  try {
    // Initialize Three.js
    const success = await initThreeJS({
      specimenId: props.specimenId,
      enableControls: true,
      showGrid: gridVisible.value,
      backgroundColor: 0x1a1a1a
    })
    
    if (!success) return
    
    // Load brain model if available
    if (hasModel.value) {
      await loadBrainModel(props.specimenId)
      emit('model-loaded', modelLoaded.value)
    }
    
    // Update crosshair if coordinates provided
    if (props.coordinates && props.showCrosshair) {
      updateCrosshair(props.coordinates)
    }
    
  } catch (err) {
    console.error('Failed to initialize 3D viewer:', err)
  }
}

// Watch for specimen changes
watch(
  () => props.specimenId,
  async () => {
    if (props.specimenId) {
      await nextTick()
      await initializeViewer()
    }
  }
)

// Watch for coordinate changes
watch(
  () => props.coordinates,
  (newCoords) => {
    if (newCoords && props.showCrosshair && modelLoaded.value) {
      updateCrosshair(newCoords)
    }
  },
  { deep: true }
)

// Watch for crosshair toggle
watch(
  () => props.showCrosshair,
  (show) => {
    if (show && props.coordinates && modelLoaded.value) {
      updateCrosshair(props.coordinates)
    }
  }
)

// Watch for model loaded state
watch(
  () => modelLoaded.value,
  (loaded) => {
    emit('model-loaded', loaded)
  }
)

// Handle resize
const onResize = () => {
  handleResize()
}

// Lifecycle
onMounted(async () => {
  // Wait for next tick to ensure container is rendered
  await nextTick()
  
  if (props.specimenId) {
    await initializeViewer()
  }
  
  // Add resize listener
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  cleanup()
})
</script>

<style scoped>
.threejs-viewer {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 400px;
  background: #1a1a1a;
  border-radius: 4px;
  overflow: hidden;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(26, 26, 26, 0.9);
  color: white;
  z-index: 1000;
  gap: 12px;
}

.loading-overlay .el-icon {
  font-size: 32px;
  color: #409eff;
}

.error-overlay .el-icon {
  font-size: 24px;
  color: #f56c6c;
}

.viewer-controls {
  position: absolute;
  bottom: 16px;
  left: 16px;
  right: 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  z-index: 100;
  pointer-events: none;
}

.viewer-controls > * {
  pointer-events: auto;
}

.camera-info {
  background: rgba(0, 0, 0, 0.8);
  padding: 8px 12px;
  border-radius: 6px;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.info-row {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  font-size: 11px;
  color: #909399;
  font-weight: 500;
  min-width: 50px;
}

.info-value {
  font-size: 11px;
  color: #e6e6e6;
  font-family: monospace;
}

.view-controls {
  background: rgba(0, 0, 0, 0.8);
  padding: 8px;
  border-radius: 6px;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.model-status {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(103, 194, 58, 0.9);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  z-index: 100;
}

.status-icon {
  font-size: 14px;
}

.no-model-info {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  gap: 12px;
  text-align: center;
  padding: 20px;
}

.no-model-icon {
  font-size: 48px;
  opacity: 0.5;
}

.no-model-info span {
  font-size: 16px;
  font-weight: 500;
}

.no-model-info small {
  font-size: 12px;
  opacity: 0.7;
  max-width: 200px;
  line-height: 1.4;
}

/* Three.js canvas styling */
:deep(canvas) {
  display: block;
  width: 100% !important;
  height: 100% !important;
}

/* Custom button styling for dark theme */
.view-controls .el-button {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #e6e6e6;
}

.view-controls .el-button:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: #ffffff;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .viewer-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    bottom: 8px;
    left: 8px;
    right: 8px;
  }
  
  .camera-info {
    padding: 6px 8px;
  }
  
  .info-label,
  .info-value {
    font-size: 10px;
  }
  
  .view-controls {
    align-self: center;
  }
  
  .model-status {
    top: 8px;
    right: 8px;
    font-size: 11px;
    padding: 4px 8px;
  }
  
  .no-model-info {
    padding: 16px;
  }
  
  .no-model-icon {
    font-size: 36px;
  }
  
  .no-model-info span {
    font-size: 14px;
  }
  
  .no-model-info small {
    font-size: 11px;
  }
}

/* Animation for model loading */
@keyframes modelAppear {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.model-status {
  animation: modelAppear 0.5s ease-out;
}

/* Accessibility */
.threejs-viewer:focus {
  outline: 2px solid #409eff;
  outline-offset: 2px;
}

.view-controls .el-button:focus {
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.3);
}
</style>
