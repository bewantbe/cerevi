<template>
  <div class="openseadragon-viewer" :class="{ loading: isLoading }">
    <!-- Loading overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <el-icon class="is-loading">
        <Loading />
      </el-icon>
      <span>Loading image...</span>
    </div>

    <!-- Error overlay -->
    <div v-if="error" class="error-overlay">
      <el-icon>
        <Warning />
      </el-icon>
      <span>{{ error }}</span>
      <el-button size="small" @click="retryLoad">Retry</el-button>
    </div>

    <!-- OpenSeadragon container -->
    <div ref="viewerContainer" class="viewer-container" />

    <!-- Control overlay -->
    <div class="viewer-controls">
      <!-- Coordinate display -->
      <div class="coordinates-display">
        <span class="coord-label">{{ viewName }}:</span>
        <span class="coord-values">
          X: {{ Math.round(coordinates.x * imageDimensions.x) }}, 
          Y: {{ Math.round(coordinates.y * imageDimensions.y) }}, 
          Z: {{ coordinates.z }}
        </span>
        <span class="zoom-level">Zoom: {{ zoom.toFixed(2) }}x</span>
      </div>

      <!-- Slice controls -->
      <div class="slice-controls">
        <el-button-group size="small">
          <el-button @click="previousSlice" :disabled="coordinates.z <= 0">
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <el-button @click="nextSlice" :disabled="coordinates.z >= maxSlice">
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </el-button-group>
        
        <el-slider
          v-model="sliceModel"
          :min="0"
          :max="maxSlice"
          :step="1"
          class="slice-slider"
          @input="onSliceChange"
        />
        
        <span class="slice-info">{{ coordinates.z + 1 }} / {{ maxSlice + 1 }}</span>
      </div>

      <!-- View controls -->
      <div class="view-controls">
        <el-button-group size="small">
          <el-button @click="zoomIn">
            <el-icon><ZoomIn /></el-icon>
          </el-button>
          <el-button @click="zoomOut">
            <el-icon><ZoomOut /></el-icon>
          </el-button>
          <el-button @click="resetView">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- Region info tooltip -->
    <div v-if="selectedRegion" class="region-tooltip" :style="tooltipStyle">
      <div class="region-name">{{ selectedRegion.name }}</div>
      <div class="region-abbrev">{{ selectedRegion.abbreviation }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { 
  ElIcon, 
  ElButton, 
  ElButtonGroup, 
  ElSlider 
} from 'element-plus'
import { 
  Loading, 
  Warning, 
  ArrowLeft, 
  ArrowRight, 
  ZoomIn, 
  ZoomOut, 
  Refresh 
} from '@element-plus/icons-vue'
import { useOpenSeadragon } from '@/composables/useOpenSeadragon'
import { useVISoRStore } from '@/stores/visor'

interface Props {
  specimenId: string
  view: 'sagittal' | 'coronal' | 'horizontal'
  channel?: number
  level?: number
}

const props = withDefaults(defineProps<Props>(), {
  channel: 0,
  level: 0
})

// Refs
const viewerContainer = ref<HTMLElement>()
const tooltipStyle = ref({})

// Store
const visorStore = useVISoRStore()

// OpenSeadragon composable
const {
  viewer,
  coordinates,
  zoom,
  isLoading,
  error,
  initViewer,
  updateSlice,
  updateChannel,
  zoomIn,
  zoomOut,
  resetView,
  goToCoordinate
} = useOpenSeadragon(viewerContainer)

// Computed properties
const viewName = computed(() => {
  const names = {
    sagittal: 'Sagittal (YZ)',
    coronal: 'Coronal (XZ)', 
    horizontal: 'Horizontal (XY)'
  }
  return names[props.view]
})

const imageDimensions = computed(() => {
  if (!visorStore.imageInfo) {
    // Return safe defaults while loading
    return { x: 1, y: 1, z: 1 }
  }
  const [z, y, x] = visorStore.imageInfo.dimensions
  return { x, y, z }
})

const maxSlice = computed(() => {
  return visorStore.maxSlices[props.view] || 0
})

const selectedRegion = computed(() => visorStore.selectedRegion)

// Slice model for two-way binding with slider
const sliceModel = computed({
  get: () => coordinates.value.z,
  set: (value: number) => updateSlice(value)
})

// Methods
const retryLoad = async () => {
  await initViewer({
    specimenId: props.specimenId,
    view: props.view,
    channel: props.channel,
    level: props.level
  })
}

const onSliceChange = (value: number | number[]) => {
  const sliceValue = Array.isArray(value) ? value[0] : value
  updateSlice(sliceValue)
  visorStore.setSliceForView(props.view, sliceValue)
}

const previousSlice = () => {
  if (coordinates.value.z > 0) {
    onSliceChange(coordinates.value.z - 1)
  }
}

const nextSlice = () => {
  if (coordinates.value.z < maxSlice.value) {
    onSliceChange(coordinates.value.z + 1)
  }
}

// Initialize viewer when component mounts
onMounted(async () => {
  await nextTick()
  if (viewerContainer.value) {
    await retryLoad()
    
    // Initialize slice position from store
    const initialSlice = visorStore.currentSlice[props.view]
    updateSlice(initialSlice)
  }
})

// Watch for external slice changes (from other views or controls)
watch(
  () => visorStore.currentSlice[props.view],
  (newSlice) => {
    if (newSlice !== coordinates.value.z) {
      updateSlice(newSlice)
    }
  }
)

// Watch for channel changes
watch(
  () => visorStore.currentChannel,
  (newChannel) => {
    updateChannel(newChannel)
  }
)

// Watch for specimen changes
watch(
  () => props.specimenId,
  async () => {
    await retryLoad()
  }
)

// Keyboard controls
const handleKeydown = (event: KeyboardEvent) => {
  switch (event.key) {
    case 'ArrowUp':
      event.preventDefault()
      nextSlice()
      break
    case 'ArrowDown':
      event.preventDefault()
      previousSlice()
      break
    case '=':
    case '+':
      event.preventDefault()
      zoomIn()
      break
    case '-':
      event.preventDefault()
      zoomOut()
      break
    case '0':
      event.preventDefault()
      resetView()
      break
  }
}

// Add keyboard event listeners
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

// Cleanup
import { onUnmounted } from 'vue'
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.openseadragon-viewer {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 400px;
  background: #000;
  border-radius: 4px;
  overflow: hidden;
}

.viewer-container {
  width: 100%;
  height: 100%;
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
  background: rgba(0, 0, 0, 0.8);
  color: white;
  z-index: 1000;
  gap: 12px;
}

.loading-overlay .el-icon {
  font-size: 32px;
}

.error-overlay .el-icon {
  font-size: 24px;
  color: #f56c6c;
}

.viewer-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  padding: 20px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 100;
}

.coordinates-display {
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  font-size: 12px;
  font-family: monospace;
}

.coord-label {
  font-weight: bold;
  color: #409eff;
}

.coord-values {
  color: #e6e6e6;
}

.zoom-level {
  color: #67c23a;
}

.slice-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.slice-slider {
  flex: 1;
  margin: 0 12px;
}

.slice-info {
  color: white;
  font-size: 12px;
  min-width: 60px;
  text-align: center;
}

.view-controls {
  align-self: flex-end;
}

.region-tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  pointer-events: none;
  z-index: 200;
  font-size: 12px;
}

.region-name {
  font-weight: bold;
  margin-bottom: 2px;
}

.region-abbrev {
  color: #67c23a;
  font-size: 10px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .viewer-controls {
    padding: 12px 8px 8px;
  }
  
  .coordinates-display {
    font-size: 10px;
    flex-wrap: wrap;
  }
  
  .slice-controls {
    flex-wrap: wrap;
  }
  
  .slice-slider {
    margin: 8px 0;
    order: 3;
    flex-basis: 100%;
  }
}

/* Loading state */
.openseadragon-viewer.loading .viewer-container {
  opacity: 0.5;
}

/* OpenSeadragon custom styling */
:deep(.openseadragon-container) {
  background: #000 !important;
}

:deep(.openseadragon-navigator) {
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  background: rgba(0, 0, 0, 0.8) !important;
}

:deep(.openseadragon-navigator .displayregion) {
  border: 2px solid #409eff !important;
}
</style>
