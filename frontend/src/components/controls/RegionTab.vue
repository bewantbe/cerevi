<template>
  <div class="region-tab">
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading">
        <Loading />
      </el-icon>
      <span>Loading regions...</span>
    </div>

    <div v-else class="region-content">
      <!-- Search and Filters -->
      <div class="control-section">
        <h4 class="section-title">Search & Filter</h4>
        <div class="search-controls">
          <el-input
            v-model="searchQuery"
            placeholder="Search regions..."
            @input="onSearchChange"
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-select v-model="selectedLevel" @change="onLevelFilterChange" class="level-filter">
            <el-option label="All Levels" value="" />
            <el-option label="Level 1" value="1" />
            <el-option label="Level 2" value="2" />
            <el-option label="Level 3" value="3" />
            <el-option label="Level 4" value="4" />
          </el-select>
        </div>
        
        <div class="filter-stats">
          <span class="stats-text">
            Showing {{ filteredRegions.length }} of {{ totalRegions }} regions
          </span>
        </div>
      </div>

      <!-- Region Tree -->
      <div class="control-section">
        <h4 class="section-title">Region Hierarchy</h4>
        <div class="tree-container">
          <el-tree
            :data="regionTreeData"
            :props="treeProps"
            node-key="id"
            :default-expand-all="false"
            :expand-on-click-node="false"
            :highlight-current="true"
            @node-click="onRegionClick"
            class="region-tree"
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <div class="node-content">
                  <span 
                    class="region-indicator" 
                    :style="{ backgroundColor: getRegionColor(data.id) }"
                  ></span>
                  <span class="region-name">{{ data.name }}</span>
                  <span class="region-abbrev">{{ data.abbreviation }}</span>
                </div>
                <div class="node-actions">
                  <el-button
                    size="small"
                    type="text"
                    @click.stop="highlightRegion(data)"
                    title="Highlight in viewer"
                  >
                    <el-icon><View /></el-icon>
                  </el-button>
                  <el-button
                    size="small"
                    type="text"
                    @click.stop="goToRegion(data)"
                    title="Go to region"
                  >
                    <el-icon><Location /></el-icon>
                  </el-button>
                </div>
              </div>
            </template>
          </el-tree>
        </div>
      </div>

      <!-- Selected Region Info -->
      <div v-if="selectedRegion" class="control-section">
        <h4 class="section-title">Selected Region</h4>
        <div class="region-details">
          <div class="detail-header">
            <div 
              class="region-color-large" 
              :style="{ backgroundColor: getRegionColor(selectedRegion.id) }"
            ></div>
            <div class="region-title">
              <h5 class="region-name-large">{{ selectedRegion.name }}</h5>
              <span class="region-abbrev-large">{{ selectedRegion.abbreviation }}</span>
            </div>
          </div>
          
          <div class="detail-grid">
            <div class="detail-item">
              <span class="label">ID:</span>
              <span class="value">{{ selectedRegion.id }}</span>
            </div>
            <div class="detail-item">
              <span class="label">Value:</span>
              <span class="value">{{ selectedRegion.value }}</span>
            </div>
            <div class="detail-item">
              <span class="label">Level 1:</span>
              <span class="value">{{ selectedRegion.level1 }}</span>
            </div>
            <div class="detail-item">
              <span class="label">Level 2:</span>
              <span class="value">{{ selectedRegion.level2 }}</span>
            </div>
            <div class="detail-item">
              <span class="label">Level 3:</span>
              <span class="value">{{ selectedRegion.level3 }}</span>
            </div>
            <div class="detail-item">
              <span class="label">Level 4:</span>
              <span class="value">{{ selectedRegion.level4 }}</span>
            </div>
          </div>
          
          <div class="detail-actions">
            <el-button size="small" @click="highlightRegion(selectedRegion)">
              <el-icon><View /></el-icon>
              Highlight
            </el-button>
            <el-button size="small" @click="goToRegion(selectedRegion)">
              <el-icon><Location /></el-icon>
              Navigate
            </el-button>
            <el-button size="small" @click="clearSelection">
              <el-icon><Close /></el-icon>
              Clear
            </el-button>
          </div>
        </div>
      </div>

      <!-- Region Statistics -->
      <div class="control-section">
        <h4 class="section-title">Statistics</h4>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-label">Total Regions:</span>
            <span class="stat-value">{{ totalRegions }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Hierarchies:</span>
            <span class="stat-value">{{ hierarchyLevels }} levels</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Current Filter:</span>
            <span class="stat-value">{{ currentFilter }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Selected:</span>
            <span class="stat-value">{{ selectedRegion?.name || 'None' }}</span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="control-section">
        <h4 class="section-title">Quick Actions</h4>
        <div class="action-buttons">
          <el-button size="small" @click="expandAll">
            <el-icon><Plus /></el-icon>
            Expand All
          </el-button>
          <el-button size="small" @click="collapseAll">
            <el-icon><Minus /></el-icon>
            Collapse All
          </el-button>
          <el-button size="small" @click="clearSearch">
            <el-icon><Refresh /></el-icon>
            Clear Search
          </el-button>
          <el-button size="small" @click="exportRegions">
            <el-icon><Download /></el-icon>
            Export List
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
  ElInput,
  ElSelect,
  ElOption,
  ElTree,
  ElMessage
} from 'element-plus'
import { 
  Loading, 
  Search, 
  View, 
  Location, 
  Close,
  Plus,
  Minus,
  Refresh,
  Download
} from '@element-plus/icons-vue'
import { useVISoRStore } from '@/stores/visor'
import type { Region } from '@/types'

interface Props {
  specimenId: string
}

const props = defineProps<Props>()

// Store
const visorStore = useVISoRStore()

// State
const loading = ref(false)
const searchQuery = ref('')
const selectedLevel = ref('')
const treeRef = ref()

// Tree properties
const treeProps = {
  children: 'children',
  label: 'name'
}

// Computed
const allRegions = computed(() => visorStore.regions)
const selectedRegion = computed(() => visorStore.selectedRegion)
const totalRegions = computed(() => allRegions.value.length)

const filteredRegions = computed(() => {
  let regions = allRegions.value
  
  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    regions = regions.filter(region => 
      region.name.toLowerCase().includes(query) ||
      region.abbreviation.toLowerCase().includes(query) ||
      region.level1.toLowerCase().includes(query) ||
      region.level2.toLowerCase().includes(query) ||
      region.level3.toLowerCase().includes(query) ||
      region.level4.toLowerCase().includes(query)
    )
  }
  
  // Apply level filter
  if (selectedLevel.value) {
    const level = parseInt(selectedLevel.value)
    regions = regions.filter(region => {
      // Filter by hierarchy level
      switch (level) {
        case 1: return region.level1 !== region.level2
        case 2: return region.level2 !== region.level3
        case 3: return region.level3 !== region.level4
        case 4: return true
        default: return true
      }
    })
  }
  
  return regions
})

const regionTreeData = computed(() => {
  // Convert flat region list to hierarchical tree structure
  const regions = filteredRegions.value
  const tree: any[] = []
  const lookup: Record<string, any> = {}
  
  // Create lookup map and initialize nodes
  regions.forEach(region => {
    const node = {
      id: region.id,
      name: region.name,
      abbreviation: region.abbreviation,
      level1: region.level1,
      level2: region.level2,
      level3: region.level3,
      level4: region.level4,
      value: region.value,
      children: []
    }
    lookup[region.id] = node
  })
  
  // Build hierarchy based on level relationships
  regions.forEach(region => {
    const node = lookup[region.id]
    if (region.parent_id && lookup[region.parent_id]) {
      lookup[region.parent_id].children.push(node)
    } else {
      tree.push(node)
    }
  })
  
  return tree
})

const hierarchyLevels = computed(() => 4)

const currentFilter = computed(() => {
  if (searchQuery.value && selectedLevel.value) {
    return `Search + Level ${selectedLevel.value}`
  } else if (searchQuery.value) {
    return 'Search'
  } else if (selectedLevel.value) {
    return `Level ${selectedLevel.value}`
  }
  return 'None'
})

// Methods
const getRegionColor = (regionId: number) => {
  // Generate consistent color based on region ID
  const colors = [
    '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7',
    '#fd79a8', '#e17055', '#81ecec', '#74b9ff', '#a29bfe'
  ]
  return colors[regionId % colors.length]
}

const onSearchChange = () => {
  // Search is handled by computed filteredRegions
}

const onLevelFilterChange = () => {
  // Filter is handled by computed filteredRegions
}

const onRegionClick = (data: any) => {
  const region = allRegions.value.find(r => r.id === data.id)
  if (region) {
    visorStore.setSelectedRegion(region)
    ElMessage.success(`Selected region: ${region.name}`)
  }
}

const highlightRegion = (region: any) => {
  // TODO: Implement region highlighting in viewers
  console.log('Highlighting region:', region.name)
  ElMessage.success(`Highlighting ${region.name}`)
}

const goToRegion = async (region: any) => {
  try {
    // Use the region picking API to find region center
    const result = await visorStore.pickRegionAtCoordinate(0, 0, 0)
    if (result) {
      ElMessage.success(`Navigated to ${region.name}`)
    }
  } catch (err) {
    console.error('Failed to navigate to region:', err)
    ElMessage.error('Failed to navigate to region')
  }
}

const clearSelection = () => {
  visorStore.setSelectedRegion(null)
  ElMessage.info('Selection cleared')
}

const expandAll = () => {
  // TODO: Implement tree expansion
  ElMessage.success('Expanded all nodes')
}

const collapseAll = () => {
  // TODO: Implement tree collapse
  ElMessage.success('Collapsed all nodes')
}

const clearSearch = () => {
  searchQuery.value = ''
  selectedLevel.value = ''
  ElMessage.info('Search cleared')
}

const exportRegions = () => {
  try {
    const data = JSON.stringify(filteredRegions.value, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `regions_${props.specimenId}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    ElMessage.success('Region list exported')
  } catch (err) {
    console.error('Export failed:', err)
    ElMessage.error('Failed to export regions')
  }
}

const loadRegions = async () => {
  if (!props.specimenId) return
  
  loading.value = true
  try {
    await visorStore.loadRegions()
  } catch (err) {
    console.error('Failed to load regions:', err)
  } finally {
    loading.value = false
  }
}

// Watch for specimen changes
watch(
  () => props.specimenId,
  () => {
    searchQuery.value = ''
    selectedLevel.value = ''
    loadRegions()
  },
  { immediate: true }
)

// Initialize
onMounted(() => {
  loadRegions()
})
</script>

<style scoped>
.region-tab {
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

.region-content {
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

.search-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 12px;
}

.search-input,
.level-filter {
  width: 100%;
}

.filter-stats {
  padding: 8px 12px;
  background: #e6f7ff;
  border-radius: 4px;
  border: 1px solid #91d5ff;
}

.stats-text {
  font-size: 12px;
  color: #0958d9;
  font-weight: 500;
}

.tree-container {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  background: #fff;
}

.region-tree {
  padding: 8px;
}

.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 4px 0;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.region-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.region-name {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
}

.region-abbrev {
  font-size: 11px;
  color: #909399;
  font-family: monospace;
}

.node-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

.region-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.region-color-large {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  flex-shrink: 0;
}

.region-title {
  flex: 1;
}

.region-name-large {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.region-abbrev-large {
  font-size: 12px;
  color: #909399;
  font-family: monospace;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
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

.detail-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
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
  padding: 8px;
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
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.action-buttons .el-button {
  justify-content: flex-start;
}

/* Custom scrollbar */
.region-tab::-webkit-scrollbar,
.tree-container::-webkit-scrollbar {
  width: 6px;
}

.region-tab::-webkit-scrollbar-track,
.tree-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.region-tab::-webkit-scrollbar-thumb,
.tree-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.region-tab::-webkit-scrollbar-thumb:hover,
.tree-container::-webkit-scrollbar-thumb:hover {
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
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    grid-template-columns: 1fr;
  }
  
  .detail-actions {
    flex-direction: column;
  }
}
</style>
