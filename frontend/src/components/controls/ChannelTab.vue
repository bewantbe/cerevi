<template>
  <div class="channel-tab">
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading">
        <Loading />
      </el-icon>
      <span>Loading channels...</span>
    </div>

    <div v-else class="channel-content">
      <!-- Channel Selection -->
      <div class="control-section">
        <h4 class="section-title">Active Channel</h4>
        <div class="channel-selector">
          <el-radio-group 
            v-model="selectedChannel" 
            @change="onChannelChange"
            class="channel-radio-group"
          >
            <el-radio 
              v-for="(name, channel) in availableChannels" 
              :key="channel" 
              :label="Number(channel)"
              class="channel-radio"
            >
              <div class="channel-option">
                <div 
                  class="channel-color-indicator" 
                  :style="{ backgroundColor: getChannelColor(Number(channel)) }"
                ></div>
                <div class="channel-info">
                  <span class="channel-name">{{ name }}</span>
                  <span class="channel-wavelength">{{ getWavelength(Number(channel)) }}</span>
                </div>
              </div>
            </el-radio>
          </el-radio-group>
        </div>
      </div>

      <!-- Brightness Control -->
      <div class="control-section">
        <h4 class="section-title">Brightness</h4>
        <div class="slider-container">
          <el-slider
            v-model="brightness"
            :min="0"
            :max="100"
            :step="1"
            show-input
            @change="onBrightnessChange"
          />
        </div>
        <div class="preset-buttons">
          <el-button size="small" @click="setBrightness(25)">25%</el-button>
          <el-button size="small" @click="setBrightness(50)">50%</el-button>
          <el-button size="small" @click="setBrightness(75)">75%</el-button>
          <el-button size="small" @click="setBrightness(100)">100%</el-button>
        </div>
      </div>

      <!-- Contrast Control -->
      <div class="control-section">
        <h4 class="section-title">Contrast</h4>
        <div class="slider-container">
          <el-slider
            v-model="contrast"
            :min="0"
            :max="100"
            :step="1"
            show-input
            @change="onContrastChange"
          />
        </div>
        <div class="preset-buttons">
          <el-button size="small" @click="setContrast(25)">25%</el-button>
          <el-button size="small" @click="setContrast(50)">50%</el-button>
          <el-button size="small" @click="setContrast(75)">75%</el-button>
          <el-button size="small" @click="setContrast(100)">100%</el-button>
        </div>
      </div>

      <!-- Multi-Channel Blending (Future Feature) -->
      <div class="control-section">
        <h4 class="section-title">Multi-Channel Blending</h4>
        <div class="blending-info">
          <el-alert
            title="Coming Soon"
            type="info"
            :closable="false"
            show-icon
          >
            Multi-channel blending and composite visualization will be available in a future update.
          </el-alert>
        </div>
      </div>

      <!-- Channel Statistics -->
      <div class="control-section">
        <h4 class="section-title">Channel Statistics</h4>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-label">Current Channel:</span>
            <span class="stat-value">{{ getCurrentChannelName() }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Data Type:</span>
            <span class="stat-value">{{ imageInfo?.data_type || 'Unknown' }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Bit Depth:</span>
            <span class="stat-value">{{ getBitDepth() }}</span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="control-section">
        <h4 class="section-title">Quick Actions</h4>
        <div class="action-buttons">
          <el-button size="small" @click="resetChannelSettings">
            <el-icon><Refresh /></el-icon>
            Reset Settings
          </el-button>
          <el-button size="small" @click="autoAdjust">
            <el-icon><MagicStick /></el-icon>
            Auto Adjust
          </el-button>
          <el-button size="small" @click="cycleChannels">
            <el-icon><Switch /></el-icon>
            Cycle Channels
          </el-button>
        </div>
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
  ElRadioGroup,
  ElRadio,
  ElAlert,
  ElMessage
} from 'element-plus'
import { 
  Loading, 
  Refresh, 
  MagicStick, 
  Switch 
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
const brightness = ref(50)
const contrast = ref(50)

// Computed
const availableChannels = computed(() => visorStore.availableChannels)
const selectedChannel = computed({
  get: () => visorStore.currentChannel,
  set: (value: number) => visorStore.setCurrentChannel(value)
})
const imageInfo = computed(() => visorStore.imageInfo)

// Methods
const getChannelColor = (channel: number) => {
  const colors = {
    0: '#ff6b6b',  // Red (405nm)
    1: '#4ecdc4',  // Cyan (488nm)
    2: '#45b7d1',  // Blue (561nm)
    3: '#96ceb4'   // Green (640nm)
  }
  return colors[channel as keyof typeof colors] || '#666'
}

const getWavelength = (channel: number) => {
  const wavelengths = {
    0: '405nm',
    1: '488nm', 
    2: '561nm',
    3: '640nm'
  }
  return wavelengths[channel as keyof typeof wavelengths] || 'Unknown'
}

const getCurrentChannelName = () => {
  const channels = availableChannels.value
  return channels[selectedChannel.value] || 'Unknown'
}

const getBitDepth = () => {
  const dataType = imageInfo.value?.data_type
  if (dataType === 'uint16') return '16-bit'
  if (dataType === 'uint8') return '8-bit'
  if (dataType === 'float32') return '32-bit float'
  return 'Unknown'
}

const onChannelChange = (val: string | number | boolean | undefined) => {
  const channel = Number(val)
  visorStore.setCurrentChannel(channel)
  ElMessage.success(`Switched to ${getCurrentChannelName()}`)
}

const onBrightnessChange = (value: number | number[]) => {
  const val = Array.isArray(value) ? value[0] : value
  // TODO: Implement brightness adjustment in viewers
  console.log('Brightness changed to:', val)
}

const onContrastChange = (value: number | number[]) => {
  const val = Array.isArray(value) ? value[0] : value
  // TODO: Implement contrast adjustment in viewers
  console.log('Contrast changed to:', val)
}

const setBrightness = (value: number) => {
  brightness.value = value
  onBrightnessChange(value)
}

const setContrast = (value: number) => {
  contrast.value = value
  onContrastChange(value)
}

const resetChannelSettings = () => {
  brightness.value = 50
  contrast.value = 50
  selectedChannel.value = 0
  ElMessage.success('Channel settings reset')
}

const autoAdjust = () => {
  // TODO: Implement auto-adjustment algorithm
  brightness.value = 60
  contrast.value = 70
  ElMessage.success('Auto-adjustment applied')
}

const cycleChannels = () => {
  const channels = Object.keys(availableChannels.value).map(Number)
  if (channels.length === 0) return
  
  const currentIndex = channels.indexOf(selectedChannel.value)
  const nextIndex = (currentIndex + 1) % channels.length
  selectedChannel.value = channels[nextIndex]
}

// Watch for specimen changes
watch(
  () => props.specimenId,
  () => {
    // Reset to defaults when specimen changes
    brightness.value = 50
    contrast.value = 50
  }
)
</script>

<style scoped>
.channel-tab {
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

.channel-content {
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

.channel-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.channel-radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.channel-radio {
  margin: 0;
  padding: 8px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e9ecef;
  transition: all 0.2s ease;
}

.channel-radio:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.channel-radio.is-checked {
  border-color: #409eff;
  background: #e6f7ff;
}

.channel-option {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.channel-color-indicator {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 2px solid #fff;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1);
}

.channel-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.channel-name {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
}

.channel-wavelength {
  font-size: 11px;
  color: #909399;
  font-family: monospace;
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

.blending-info {
  margin-top: 8px;
}

.stats-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.stat-label {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.stat-value {
  font-size: 12px;
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

/* Custom radio button styling */
.channel-radio :deep(.el-radio__input) {
  margin-right: 8px;
}

.channel-radio :deep(.el-radio__label) {
  padding-left: 0;
  width: 100%;
}

/* Custom scrollbar */
.channel-tab::-webkit-scrollbar {
  width: 6px;
}

.channel-tab::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.channel-tab::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.channel-tab::-webkit-scrollbar-thumb:hover {
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
  
  .channel-name {
    font-size: 12px;
  }
  
  .channel-wavelength {
    font-size: 10px;
  }
}
</style>
