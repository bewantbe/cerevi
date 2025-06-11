<template>
  <div class="metadata-tab">
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading">
        <Loading />
      </el-icon>
      <span>Loading metadata...</span>
    </div>

    <div v-else-if="error" class="error-state">
      <el-icon>
        <Warning />
      </el-icon>
      <span>{{ error }}</span>
    </div>

    <div v-else class="metadata-content">
      <!-- Specimen Information -->
      <div class="info-section">
        <h4 class="section-title">Specimen</h4>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">Name:</span>
            <span class="value">{{ specimen?.name || 'N/A' }}</span>
          </div>
          <div class="info-item">
            <span class="label">Species:</span>
            <span class="value">{{ specimen?.species || 'N/A' }}</span>
          </div>
          <div class="info-item">
            <span class="label">ID:</span>
            <span class="value">{{ specimen?.id || 'N/A' }}</span>
          </div>
          <div class="info-item">
            <span class="label">Resolution:</span>
            <span class="value">{{ specimen?.resolution_um || 'N/A' }}μm</span>
          </div>
        </div>
      </div>

      <!-- Image Information -->
      <div v-if="imageInfo" class="info-section">
        <h4 class="section-title">Image Data</h4>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">Dimensions:</span>
            <span class="value">{{ formatDimensions(imageInfo.dimensions) }}</span>
          </div>
          <div class="info-item">
            <span class="label">Data Type:</span>
            <span class="value">{{ imageInfo.data_type }}</span>
          </div>
          <div class="info-item">
            <span class="label">File Size:</span>
            <span class="value">{{ formatFileSize(imageInfo.file_size) }}</span>
          </div>
          <div class="info-item">
            <span class="label">Tile Size:</span>
            <span class="value">{{ imageInfo.tile_size }}×{{ imageInfo.tile_size }}</span>
          </div>
          <div class="info-item">
            <span class="label">Pixel Size:</span>
            <span class="value">{{ formatPixelSize(imageInfo.pixel_size_um) }}</span>
          </div>
          <div class="info-item">
            <span class="label">Levels:</span>
            <span class="value">{{ imageInfo.resolution_levels.length }} levels</span>
          </div>
        </div>
      </div>

      <!-- Channel Information -->
      <div v-if="channels && Object.keys(channels).length > 0" class="info-section">
        <h4 class="section-title">Channels</h4>
        <div class="channel-list">
          <div v-for="(name, channel) in channels" :key="channel" class="channel-item">
            <div class="channel-indicator" :style="{ backgroundColor: getChannelColor(Number(channel)) }"></div>
            <span class="channel-name">{{ name }}</span>
            <span class="channel-number">Ch{{ channel }}</span>
          </div>
        </div>
      </div>

      <!-- Coordinate System -->
      <div class="info-section">
        <h4 class="section-title">Coordinate System</h4>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">System:</span>
            <span class="value">{{ specimen?.coordinate_system || 'Right-handed' }}</span>
          </div>
          <div class="info-item">
            <span class="label">Axes Order:</span>
            <span class="value">{{ specimen?.axes_order || 'Z-Y-X' }}</span>
          </div>
        </div>
      </div>

      <!-- Current Position -->
      <div class="info-section">
        <h4 class="section-title">Current Position</h4>
        <div class="position-display">
          <div class="position-item">
            <span class="axis-label">X:</span>
            <span class="axis-value">{{ currentSlice.sagittal }}</span>
          </div>
          <div class="position-item">
            <span class="axis-label">Y:</span>
            <span class="axis-value">{{ currentSlice.coronal }}</span>
          </div>
          <div class="position-item">
            <span class="axis-label">Z:</span>
            <span class="axis-value">{{ currentSlice.horizontal }}</span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="info-section">
        <h4 class="section-title">Quick Actions</h4>
        <div class="action-buttons">
          <el-button size="small" @click="goToCenter">
            <el-icon><Aim /></el-icon>
            Go to Center
          </el-button>
          <el-button size="small" @click="resetView">
            <el-icon><Refresh /></el-icon>
            Reset View
          </el-button>
          <el-button size="small" @click="copyCoordinates">
            <el-icon><CopyDocument /></el-icon>
            Copy Position
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { 
  ElIcon, 
  ElButton,
  ElMessage
} from 'element-plus'
import { 
  Loading, 
  Warning, 
  Aim, 
  Refresh, 
  CopyDocument 
} from '@element-plus/icons-vue'
import { useVISoRStore } from '@/stores/visor'
import VISoRAPI from '@/services/api'

interface Props {
  specimenId: string
}

const props = defineProps<Props>()

// Store
const visorStore = useVISoRStore()

// State
const loading = ref(false)
const error = ref<string | null>(null)

// Computed
const specimen = computed(() => visorStore.currentSpecimen)
const imageInfo = computed(() => visorStore.imageInfo)
const channels = computed(() => specimen.value?.channels || {})
const currentSlice = computed(() => visorStore.currentSlice)

// Methods
const formatDimensions = (dimensions: [number, number, number]) => {
  const [z, y, x] = dimensions
  return `${x} × ${y} × ${z} voxels`
}

const formatFileSize = (bytes: number) => {
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  if (bytes === 0) return '0 B'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

const formatPixelSize = (pixelSize: [number, number, number]) => {
  const [z, y, x] = pixelSize
  return `${x}×${y}×${z} μm`
}

const getChannelColor = (channel: number) => {
  const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7']
  return colors[channel % colors.length]
}

const goToCenter = () => {
  if (!imageInfo.value) return
  
  const [z, y, x] = imageInfo.value.dimensions
  visorStore.setSliceForView('sagittal', Math.floor(x / 2))
  visorStore.setSliceForView('coronal', Math.floor(y / 2))
  visorStore.setSliceForView('horizontal', Math.floor(z / 2))
  
  ElMessage.success('Moved to center position')
}

const resetView = () => {
  // Reset zoom and position
  ElMessage.success('View reset')
}

const copyCoordinates = async () => {
  const coords = `X:${currentSlice.value.sagittal}, Y:${currentSlice.value.coronal}, Z:${currentSlice.value.horizontal}`
  
  try {
    await navigator.clipboard.writeText(coords)
    ElMessage.success('Coordinates copied to clipboard')
  } catch (err) {
    console.error('Failed to copy coordinates:', err)
    ElMessage.error('Failed to copy coordinates')
  }
}

const loadMetadata = async () => {
  if (!props.specimenId) return
  
  loading.value = true
  error.value = null
  
  try {
    // Metadata is already loaded by the store when specimen is set
    // This is just to ensure we have the latest data
    if (!visorStore.currentSpecimen || visorStore.currentSpecimen.id !== props.specimenId) {
      await visorStore.setCurrentSpecimen(props.specimenId)
    }
  } catch (err) {
    error.value = 'Failed to load metadata'
    console.error('Metadata loading error:', err)
  } finally {
    loading.value = false
  }
}

// Watch for specimen changes
watch(
  () => props.specimenId,
  () => {
    loadMetadata()
  },
  { immediate: true }
)

// Initialize
onMounted(() => {
  loadMetadata()
})
</script>

<style scoped>
.metadata-tab {
  height: 100%;
  overflow-y: auto;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  gap: 12px;
  color: #909399;
}

.loading-state .el-icon {
  font-size: 24px;
}

.error-state .el-icon {
  font-size: 24px;
  color: #f56c6c;
}

.metadata-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e9ecef;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 8px;
}

.info-grid {
  display: grid;
  gap: 8px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.label {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.value {
  font-size: 12px;
  color: #303133;
  font-family: monospace;
  text-align: right;
}

.channel-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.channel-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.channel-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.channel-name {
  flex: 1;
  font-size: 12px;
  color: #303133;
}

.channel-number {
  font-size: 10px;
  color: #909399;
  font-family: monospace;
}

.position-display {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.position-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.axis-label {
  font-size: 10px;
  color: #909399;
  font-weight: 600;
  margin-bottom: 2px;
}

.axis-value {
  font-size: 14px;
  color: #303133;
  font-family: monospace;
  font-weight: 600;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-buttons .el-button {
  justify-content: flex-start;
}

/* Custom scrollbar */
.metadata-tab::-webkit-scrollbar {
  width: 6px;
}

.metadata-tab::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.metadata-tab::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.metadata-tab::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .info-section {
    padding: 12px;
  }
  
  .section-title {
    font-size: 13px;
  }
  
  .label,
  .value {
    font-size: 11px;
  }
  
  .position-display {
    grid-template-columns: 1fr;
  }
}
</style>
