<template>
  <div class="atlas-tab">
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading">
        <Loading />
      </el-icon>
      <span>Loading atlas...</span>
    </div>

    <div v-else class="atlas-content">
      <!-- Atlas Overlay Toggle -->
      <div class="control-section">
        <h4 class="section-title">Atlas Overlay</h4>
        <div class="overlay-controls">
          <el-switch
            v-model="atlasEnabled"
            active-text="Show Atlas"
            inactive-text="Hide Atlas"
            @change="onAtlasToggle"
            class="atlas-switch"
          />
          <div v-if="atlasEnabled" class="overlay-status">
            <el-icon class="status-icon">
              <View />
            </el-icon>
            <span>Atlas overlay active</span>
          </div>
        </div>
      </div>

      <!-- Opacity Control -->
      <div v-if="atlasEnabled" class="control-section">
        <h4 class="section-title">Opacity</h4>
        <div class="slider-container">
          <el-slider
            v-model="opacity"
            :min="0"
            :max="100"
            :step="5"
            show-input
            @change="onOpacityChange"
          />
        </div>
        <div class="preset-buttons">
          <el-button size="small" @click="setOpacity(25)">25%</el-button>
          <el-button size="small" @click="setOpacity(50)">50%</el-button>
          <el-button size="small" @click="setOpacity(75)">75%</el-button>
          <el-button size="small" @click="setOpacity(100)">100%</el-button>
        </div>
      </div>

      <!-- Blending Mode -->
      <div v-if="atlasEnabled" class="control-section">
        <h4 class="section-title">Blending Mode</h4>
        <el-select v-model="blendMode" @change="onBlendModeChange" class="blend-select">
          <el-option label="Normal" value="normal" />
          <el-option label="Multiply" value="multiply" />
          <el-option label="Overlay" value="overlay" />
          <el-option label="Screen" value="screen" />
          <el-option label="Color Burn" value="color-burn" />
        </el-select>
      </div>

      <!-- Color Mapping -->
      <div v-if="atlasEnabled" class="control-section">
        <h4 class="section-title">Color Mapping</h4>
        <div class="color-options">
          <el-radio-group v-model="colorMode" @change="onColorModeChange">
            <el-radio label="region">Region Colors</el-radio>
            <el-radio label="hierarchy">Hierarchy Colors</el-radio>
            <el-radio label="custom">Custom Palette</el-radio>
          </el-radio-group>
        </div>
        
        <div v-if="colorMode === 'custom'" class="custom-colors">
          <div class="color-picker-grid">
            <div class="color-item">
              <span class="color-label">Background:</span>
              <el-color-picker v-model="customColors.background" />
            </div>
            <div class="color-item">
              <span class="color-label">Regions:</span>
              <el-color-picker v-model="customColors.regions" />
            </div>
            <div class="color-item">
              <span class="color-label">Borders:</span>
              <el-color-picker v-model="customColors.borders" />
            </div>
          </div>
        </div>
      </div>

      <!-- Atlas Information -->
      <div class="control-section">
        <h4 class="section-title">Atlas Information</h4>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">Available:</span>
            <span class="value">{{ hasAtlas ? 'Yes' : 'No' }}</span>
          </div>
          <div v-if="hasAtlas" class="info-item">
            <span class="label">Regions:</span>
            <span class="value">{{ totalRegions }} regions</span>
          </div>
          <div v-if="hasAtlas" class="info-item">
            <span class="label">Resolution:</span>
            <span class="value">{{ atlasResolution }}</span>
          </div>
          <div v-if="hasAtlas" class="info-item">
            <span class="label">Data Type:</span>
            <span class="value">{{ atlasDataType }}</span>
          </div>
        </div>
      </div>

      <!-- Atlas Levels -->
      <div v-if="hasAtlas" class="control-section">
        <h4 class="section-title">Resolution Level</h4>
        <div class="level-selector">
          <el-select v-model="selectedLevel" @change="onLevelChange" class="level-select">
            <el-option
              v-for="level in availableLevels"
              :key="level"
              :label="`Level ${level}`"
              :value="level"
            />
          </el-select>
          <div class="level-info">
            <span class="level-description">
              Higher levels = lower resolution, faster loading
            </span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="control-section">
        <h4 class="section-title">Quick Actions</h4>
        <div class="action-buttons">
          <el-button size="small" @click="resetAtlasSettings" :disabled="!hasAtlas">
            <el-icon><Refresh /></el-icon>
            Reset Settings
          </el-button>
          <el-button size="small" @click="toggleAtlasQuick" :disabled="!hasAtlas">
            <el-icon><Switch /></el-icon>
            Toggle Overlay
          </el-button>
          <el-button size="small" @click="previewAtlas" :disabled="!hasAtlas">
            <el-icon><View /></el-icon>
            Preview Atlas
          </el-button>
        </div>
      </div>

      <!-- No Atlas Available -->
      <div v-if="!hasAtlas" class="no-atlas-info">
        <el-alert
          title="No Atlas Available"
          type="warning"
          :closable="false"
          show-icon
        >
          This specimen does not have an associated brain atlas. Atlas overlay features are not available.
        </el-alert>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { 
  ElIcon, 
  ElButton, 
  ElSlider,
  ElSwitch,
  ElSelect,
  ElOption,
  ElRadioGroup,
  ElRadio,
  ElColorPicker,
  ElAlert,
  ElMessage
} from 'element-plus'
import { 
  Loading, 
  Refresh, 
  Switch, 
  View 
} from '@element-plus/icons-vue'
import { useVISoRStore } from '@/stores/visor'

interface Props {
  specimenId: string
}

const props = defineProps<Props>()

// Store
const visorStore = useVISoRStore()

// State
const loading = ref(false)
const opacity = ref(50)
const blendMode = ref('normal')
const colorMode = ref('region')
const selectedLevel = ref(0)
const customColors = ref({
  background: '#000000',
  regions: '#ff6b6b',
  borders: '#ffffff'
})

// Computed
const atlasEnabled = computed({
  get: () => visorStore.showAtlasOverlay,
  set: (value: boolean) => visorStore.toggleAtlasOverlay()
})

const hasAtlas = computed(() => {
  return visorStore.currentSpecimen?.has_atlas || false
})

const totalRegions = computed(() => {
  return visorStore.regions.length
})

const atlasResolution = computed(() => {
  // TODO: Get from atlas metadata
  return 'Same as image'
})

const atlasDataType = computed(() => {
  // TODO: Get from atlas metadata
  return 'uint16'
})

const availableLevels = computed(() => {
  // TODO: Get from image info
  return visorStore.imageInfo?.resolution_levels || [0, 1, 2, 3, 4, 5, 6, 7]
})

// Methods
const onAtlasToggle = (val: string | number | boolean) => {
  const enabled = Boolean(val)
  if (enabled) {
    ElMessage.success('Atlas overlay enabled')
  } else {
    ElMessage.info('Atlas overlay disabled')
  }
}

const onOpacityChange = (value: number | number[]) => {
  const val = Array.isArray(value) ? value[0] : value
  visorStore.setAtlasOpacity(val / 100)
  console.log('Atlas opacity changed to:', val)
}

const setOpacity = (value: number) => {
  opacity.value = value
  onOpacityChange(value)
}

const onBlendModeChange = (val: string | number | boolean | undefined) => {
  const mode = String(val || 'normal')
  // TODO: Implement blend mode change
  console.log('Blend mode changed to:', mode)
  ElMessage.success(`Blend mode set to ${mode}`)
}

const onColorModeChange = (val: string | number | boolean | undefined) => {
  const mode = String(val || 'region')
  // TODO: Implement color mode change
  console.log('Color mode changed to:', mode)
  ElMessage.success(`Color mode set to ${mode}`)
}

const onLevelChange = (level: number) => {
  // TODO: Implement level change
  console.log('Atlas level changed to:', level)
  ElMessage.success(`Atlas resolution level set to ${level}`)
}

const resetAtlasSettings = () => {
  opacity.value = 50
  blendMode.value = 'normal'
  colorMode.value = 'region'
  selectedLevel.value = 0
  customColors.value = {
    background: '#000000',
    regions: '#ff6b6b',
    borders: '#ffffff'
  }
  visorStore.setAtlasOpacity(0.5)
  ElMessage.success('Atlas settings reset')
}

const toggleAtlasQuick = () => {
  visorStore.toggleAtlasOverlay()
}

const previewAtlas = () => {
  // TODO: Implement atlas preview
  ElMessage.info('Atlas preview functionality coming soon')
}

// Watch for specimen changes
watch(
  () => props.specimenId,
  () => {
    // Reset to defaults when specimen changes
    resetAtlasSettings()
  }
)
</script>

<style scoped>
.atlas-tab {
  height: 100%;
  overflow-y: auto;
}

.loading-state {
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

.atlas-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.control-section {
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

.overlay-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.atlas-switch {
  align-self: flex-start;
}

.overlay-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #e6f7ff;
  border-radius: 4px;
  border: 1px solid #91d5ff;
  color: #0958d9;
  font-size: 12px;
}

.status-icon {
  font-size: 14px;
}

.slider-container {
  margin-bottom: 12px;
}

.preset-buttons {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
}

.preset-buttons .el-button {
  font-size: 11px;
  padding: 6px 8px;
}

.blend-select,
.level-select {
  width: 100%;
}

.color-options {
  margin-bottom: 12px;
}

.color-options .el-radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.custom-colors {
  margin-top: 12px;
  padding: 12px;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.color-picker-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.color-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.color-label {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e9ecef;
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
  font-weight: 600;
}

.level-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.level-info {
  padding: 8px;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.level-description {
  font-size: 11px;
  color: #909399;
  font-style: italic;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-buttons .el-button {
  justify-content: flex-start;
}

.no-atlas-info {
  margin-top: 20px;
}

/* Custom scrollbar */
.atlas-tab::-webkit-scrollbar {
  width: 6px;
}

.atlas-tab::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.atlas-tab::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.atlas-tab::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .control-section {
    padding: 12px;
  }
  
  .section-title {
    font-size: 13px;
  }
  
  .preset-buttons {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .overlay-status {
    font-size: 11px;
  }
  
  .color-picker-grid {
    gap: 8px;
  }
}
</style>
