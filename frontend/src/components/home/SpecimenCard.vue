<template>
  <div class="specimen-card" @click="handleClick">
    <div class="card-header">
      <div class="specimen-thumbnail">
        <el-icon class="thumbnail-icon" size="64">
          <View />
        </el-icon>
        <div class="data-indicators">
          <el-tag v-if="specimen.has_image" size="small" type="primary">Image</el-tag>
          <el-tag v-if="specimen.has_atlas" size="small" type="success">Atlas</el-tag>
          <el-tag v-if="specimen.has_model" size="small" type="warning">3D Model</el-tag>
        </div>
      </div>
    </div>
    
    <div class="card-body">
      <h3 class="specimen-name">{{ specimen.name }}</h3>
      <p class="specimen-species">{{ specimen.species }}</p>
      <p class="specimen-description">{{ specimen.description }}</p>
      
      <div class="specimen-details">
        <div class="detail-row">
          <span class="detail-label">Channels:</span>
          <span class="detail-value">{{ channelCount }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Resolution:</span>
          <span class="detail-value">{{ specimen.resolution_um }}μm</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Coordinate System:</span>
          <span class="detail-value">{{ specimen.coordinate_system }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Axes Order:</span>
          <span class="detail-value">{{ specimen.axes_order }}</span>
        </div>
      </div>
      
      <div class="channels-info">
        <h4>Available Channels:</h4>
        <div class="channels-list">
          <div 
            v-for="(wavelength, channelId) in specimen.channels" 
            :key="channelId"
            class="channel-item"
          >
            <span class="channel-id">Ch{{ channelId }}</span>
            <span class="channel-wavelength">{{ wavelength }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="card-footer">
      <el-button type="primary" @click.stop="handleExplore">
        <el-icon><View /></el-icon>
        Explore
      </el-button>
      <el-button @click.stop="handleInfo">
        <el-icon><InfoFilled /></el-icon>
        Details
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Specimen } from '@/services/api'
import { View, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Props
interface Props {
  specimen: Specimen
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  click: [specimenId: string]
  explore: [specimenId: string]
  info: [specimenId: string]
}>()

// Computed
const channelCount = computed(() => Object.keys(props.specimen.channels).length)

// Methods
function handleClick() {
  emit('click', props.specimen.id)
}

function handleExplore() {
  emit('explore', props.specimen.id)
}

function handleInfo() {
  emit('info', props.specimen.id)
  ElMessage.info(`Detailed information for ${props.specimen.name} coming soon!`)
}
</script>

<style scoped>
.specimen-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.specimen-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  position: relative;
}

.specimen-thumbnail {
  text-align: center;
  position: relative;
}

.thumbnail-icon {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 16px;
}

.data-indicators {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.card-body {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.specimen-name {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #303133;
}

.specimen-species {
  font-size: 0.9rem;
  color: #409eff;
  font-weight: 500;
  margin: 0 0 12px 0;
  font-style: italic;
}

.specimen-description {
  color: #606266;
  line-height: 1.5;
  margin: 0 0 20px 0;
  flex: 1;
}

.specimen-details {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-size: 0.875rem;
  color: #606266;
  font-weight: 500;
}

.detail-value {
  font-size: 0.875rem;
  color: #303133;
  font-weight: 600;
}

.channels-info {
  margin-bottom: 20px;
}

.channels-info h4 {
  font-size: 0.9rem;
  color: #303133;
  margin: 0 0 12px 0;
  font-weight: 600;
}

.channels-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
}

.channel-item {
  background: #f0f9ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  padding: 8px 12px;
  text-align: center;
  font-size: 0.75rem;
}

.channel-id {
  display: block;
  font-weight: 600;
  color: #1e40af;
  margin-bottom: 2px;
}

.channel-wavelength {
  color: #3b82f6;
}

.card-footer {
  padding: 16px 20px;
  background: #f8f9fa;
  border-top: 1px solid #e4e7ed;
  display: flex;
  gap: 12px;
}

.card-footer .el-button {
  flex: 1;
}

/* Animation for loading states */
.specimen-card.loading {
  opacity: 0.7;
  pointer-events: none;
}

.specimen-card.loading .thumbnail-icon {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .channels-list {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .card-footer {
    flex-direction: column;
  }
  
  .card-footer .el-button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .card-body {
    padding: 16px;
  }
  
  .card-header {
    padding: 16px;
  }
  
  .card-footer {
    padding: 12px 16px;
  }
  
  .specimen-details {
    padding: 12px;
  }
  
  .detail-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>
