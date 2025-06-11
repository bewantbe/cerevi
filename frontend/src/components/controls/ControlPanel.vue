<template>
  <div class="control-panel" :class="{ collapsed: !isExpanded }">
    <!-- Panel Header -->
    <div class="panel-header">
      <h3 class="panel-title">Controls</h3>
      <el-button 
        type="text" 
        size="small" 
        @click="togglePanel"
        class="toggle-button"
      >
        <el-icon>
          <ArrowLeft v-if="isExpanded" />
          <ArrowRight v-else />
        </el-icon>
      </el-button>
    </div>

    <!-- Panel Content -->
    <div v-if="isExpanded" class="panel-content">
      <el-tabs v-model="activeTab" tab-position="top" class="control-tabs">
        <!-- Metadata Tab -->
        <el-tab-pane label="Info" name="metadata">
          <MetadataTab :specimen-id="specimenId" />
        </el-tab-pane>

        <!-- Channel Controls Tab -->
        <el-tab-pane label="Channels" name="channels">
          <ChannelTab :specimen-id="specimenId" />
        </el-tab-pane>

        <!-- Atlas Overlay Tab -->
        <el-tab-pane label="Atlas" name="atlas">
          <AtlasTab :specimen-id="specimenId" />
        </el-tab-pane>

        <!-- Region Browser Tab -->
        <el-tab-pane label="Regions" name="regions">
          <RegionTab :specimen-id="specimenId" />
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Collapsed State -->
    <div v-else class="collapsed-indicator">
      <el-icon class="indicator-icon">
        <Tools />
      </el-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { 
  ElButton, 
  ElIcon, 
  ElTabs, 
  ElTabPane 
} from 'element-plus'
import { 
  ArrowLeft, 
  ArrowRight, 
  Tools 
} from '@element-plus/icons-vue'
import MetadataTab from './MetadataTab.vue'
import ChannelTab from './ChannelTab.vue'
import AtlasTab from './AtlasTab.vue'
import RegionTab from './RegionTab.vue'

interface Props {
  specimenId: string
}

const props = defineProps<Props>()

// State
const isExpanded = ref(true)
const activeTab = ref('metadata')

// Methods
const togglePanel = () => {
  isExpanded.value = !isExpanded.value
}
</script>

<style scoped>
.control-panel {
  position: fixed;
  left: 0;
  top: 60px;
  bottom: 0;
  width: 360px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.control-panel.collapsed {
  width: 48px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  background: #f8f9fa;
  min-height: 60px;
}

.panel-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.toggle-button {
  padding: 8px;
  border-radius: 4px;
}

.panel-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.control-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.control-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

.control-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
  border-bottom: 1px solid #e4e7ed;
}

.control-tabs :deep(.el-tabs__nav-wrap) {
  padding: 0 16px;
}

.collapsed-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
  color: #909399;
}

.indicator-icon {
  font-size: 24px;
  opacity: 0.6;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .control-panel {
    position: relative;
    width: 100%;
    height: auto;
    top: 0;
    box-shadow: none;
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
  }
  
  .control-panel.collapsed {
    width: 100%;
    height: 60px;
  }
  
  .panel-content {
    max-height: 400px;
  }
}

@media (max-width: 768px) {
  .panel-header {
    padding: 12px;
  }
  
  .panel-title {
    font-size: 14px;
  }
  
  .control-tabs :deep(.el-tabs__content) {
    padding: 12px;
  }
}

/* Smooth transitions */
.control-panel * {
  transition: all 0.3s ease;
}

/* Custom scrollbar for content */
.panel-content::-webkit-scrollbar {
  width: 6px;
}

.panel-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.panel-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.panel-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
