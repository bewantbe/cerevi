<template>
  <div class="region-tree">
    <div class="tree-header">
      <el-input
        v-model="searchText"
        placeholder="Search regions..."
        size="small"
        clearable
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <div class="tree-actions">
        <el-button-group size="small">
          <el-button @click="expandAll" :disabled="loading">
            <el-icon><Plus /></el-icon>
          </el-button>
          <el-button @click="collapseAll" :disabled="loading">
            <el-icon><Minus /></el-icon>
          </el-button>
        </el-button-group>
      </div>
    </div>

    <div class="tree-content">
      <el-scrollbar height="400px">
        <el-tree
          ref="treeRef"
          :data="filteredRegions"
          :props="treeProps"
          :filter-node-method="filterNode"
          :expand-on-click-node="false"
          :check-on-click-node="true"
          :show-checkbox="selectionMode !== 'single'"
          :check-strictly="checkStrictly"
          node-key="id"
          @node-click="handleNodeClick"
          @check="handleNodeCheck"
        >
          <template #default="{ node, data }">
            <div class="tree-node" :class="{ 'highlighted': data.id === highlightedRegion }">
              <span class="node-label" :title="data.name">
                {{ data.name }}
              </span>
              <span class="node-abbr" :title="data.abbreviation">
                ({{ data.abbreviation }})
              </span>
              <div class="node-actions">
                <el-button
                  v-if="data.id === selectedRegion"
                  size="small"
                  type="primary"
                  circle
                  @click.stop="goToRegion(data)"
                >
                  <el-icon><LocationFilled /></el-icon>
                </el-button>
              </div>
            </div>
          </template>
        </el-tree>
      </el-scrollbar>
    </div>

    <div class="tree-footer">
      <div class="tree-stats">
        <span>{{ filteredCount }} / {{ totalCount }} regions</span>
        <span v-if="selectedRegions.size > 0">
          • {{ selectedRegions.size }} selected
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import {
  ElInput,
  ElButton,
  ElButtonGroup,
  ElTree,
  ElScrollbar,
  ElIcon,
  type TreeInstance
} from 'element-plus'
import {
  Search,
  Plus,
  Minus,
  LocationFilled
} from '@element-plus/icons-vue'
import type { Region, RegionSelection } from '@/types'

interface Props {
  regions: Region[]
  loading?: boolean
  selectedRegion?: number | null
  highlightedRegion?: number | null
  selectedRegions?: Set<number>
  selectionMode?: 'single' | 'multiple' | 'hierarchy'
  checkStrictly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  selectedRegion: null,
  highlightedRegion: null,
  selectedRegions: () => new Set(),
  selectionMode: 'single',
  checkStrictly: false
})

const emit = defineEmits<{
  select: [region: Region]
  check: [regions: Region[]]
  goTo: [region: Region]
}>()

const searchText = ref('')
const treeRef = ref<TreeInstance>()

const treeProps = {
  children: 'children',
  label: 'name',
  disabled: 'disabled'
}

const filteredRegions = computed(() => {
  if (!searchText.value) {
    return props.regions
  }
  return filterRegionsBySearch(props.regions, searchText.value.toLowerCase())
})

const filteredCount = computed(() => {
  return countRegions(filteredRegions.value)
})

const totalCount = computed(() => {
  return countRegions(props.regions)
})

const filterRegionsBySearch = (regions: Region[], search: string): Region[] => {
  return regions.reduce((acc: Region[], region) => {
    const matchesSearch = 
      region.name.toLowerCase().includes(search) ||
      region.abbreviation.toLowerCase().includes(search) ||
      region.level1.toLowerCase().includes(search) ||
      region.level2.toLowerCase().includes(search) ||
      region.level3.toLowerCase().includes(search) ||
      region.level4.toLowerCase().includes(search)

    const filteredChildren = filterRegionsBySearch(region.children || [], search)

    if (matchesSearch || filteredChildren.length > 0) {
      acc.push({
        ...region,
        children: filteredChildren
      })
    }

    return acc
  }, [])
}

const countRegions = (regions: Region[]): number => {
  return regions.reduce((count, region) => {
    return count + 1 + countRegions(region.children || [])
  }, 0)
}

const filterNode = (value: string, data: any) => {
  if (!value) return true
  const searchValue = value.toLowerCase()
  return (
    data.name?.toLowerCase().includes(searchValue) ||
    data.abbreviation?.toLowerCase().includes(searchValue)
  )
}

const handleSearch = () => {
  nextTick(() => {
    treeRef.value?.filter(searchText.value)
  })
}

const handleNodeClick = (data: Region) => {
  emit('select', data)
}

const handleNodeCheck = (data: Region, checkedInfo: any) => {
  const checkedRegions: Region[] = []
  
  // Collect all checked regions
  const collectCheckedRegions = (regions: Region[]) => {
    for (const region of regions) {
      if (checkedInfo.checkedKeys.includes(region.id)) {
        checkedRegions.push(region)
      }
      if (region.children) {
        collectCheckedRegions(region.children)
      }
    }
  }
  
  collectCheckedRegions(props.regions)
  emit('check', checkedRegions)
}

const goToRegion = (region: Region) => {
  emit('goTo', region)
}

const expandAll = () => {
  // Get all node keys recursively
  const getAllKeys = (regions: Region[]): number[] => {
    let keys: number[] = []
    for (const region of regions) {
      keys.push(region.id)
      if (region.children && region.children.length > 0) {
        keys = keys.concat(getAllKeys(region.children))
      }
    }
    return keys
  }
  
  const allKeys = getAllKeys(props.regions)
  // Manually expand each node
  allKeys.forEach(key => {
    const node = treeRef.value?.getNode(key)
    if (node && !node.expanded) {
      node.expand()
    }
  })
}

const collapseAll = () => {
  // Get all node keys recursively
  const getAllKeys = (regions: Region[]): number[] => {
    let keys: number[] = []
    for (const region of regions) {
      keys.push(region.id)
      if (region.children && region.children.length > 0) {
        keys = keys.concat(getAllKeys(region.children))
      }
    }
    return keys
  }
  
  const allKeys = getAllKeys(props.regions)
  // Manually collapse each node (start from children first)
  allKeys.reverse().forEach(key => {
    const node = treeRef.value?.getNode(key)
    if (node && node.expanded) {
      node.collapse()
    }
  })
}

// Watch for external selection changes
watch(() => props.selectedRegions, (newSelection) => {
  if (props.selectionMode !== 'single') {
    const keys = Array.from(newSelection)
    treeRef.value?.setCheckedKeys(keys)
  }
}, { deep: true })
</script>

<style scoped>
.region-tree {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.tree-header {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.tree-header .el-input {
  flex: 1;
}

.tree-content {
  flex: 1;
  min-height: 0;
}

.tree-node {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 2px 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.tree-node.highlighted {
  background-color: #e6f7ff;
  border: 1px solid #91d5ff;
}

.node-label {
  flex: 1;
  font-size: 13px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-abbr {
  font-size: 11px;
  color: #909399;
  margin-left: 8px;
  white-space: nowrap;
}

.node-actions {
  margin-left: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

.tree-footer {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.tree-stats {
  font-size: 12px;
  color: #909399;
  text-align: center;
}

:deep(.el-tree-node__content) {
  padding: 2px 4px;
}

:deep(.el-tree-node__label) {
  font-size: 13px;
}
</style>
