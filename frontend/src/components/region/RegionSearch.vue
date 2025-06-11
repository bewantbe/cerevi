<template>
  <div class="region-search">
    <el-autocomplete
      v-model="searchQuery"
      :fetch-suggestions="querySearchAsync"
      :placeholder="placeholder"
      :trigger-on-focus="false"
      :debounce="300"
      clearable
      @select="handleSelect as any"
      @clear="handleClear"
    >
      <template #prefix>
        <el-icon><Search /></el-icon>
      </template>
      <template #default="{ item }">
        <div class="search-item">
          <div class="item-content">
            <span class="item-name">{{ item.name }}</span>
            <span class="item-abbr">({{ item.abbreviation }})</span>
          </div>
          <div class="item-hierarchy">
            <span class="hierarchy-level">{{ item.level1 }}</span>
            <span v-if="item.level2 !== item.level1" class="hierarchy-separator">→</span>
            <span v-if="item.level2 !== item.level1" class="hierarchy-level">{{ item.level2 }}</span>
            <span v-if="item.level3 !== item.level2" class="hierarchy-separator">→</span>
            <span v-if="item.level3 !== item.level2" class="hierarchy-level">{{ item.level3 }}</span>
          </div>
        </div>
      </template>
    </el-autocomplete>
    
    <div v-if="recentSearches.length > 0" class="recent-searches">
      <div class="recent-header">
        <span>Recent searches</span>
        <el-button text size="small" @click="clearRecent">Clear</el-button>
      </div>
      <div class="recent-items">
        <el-tag
          v-for="recent in recentSearches"
          :key="recent.id"
          size="small"
          closable
          @click="selectRecent(recent)"
          @close="removeRecent(recent.id)"
        >
          {{ recent.name }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElAutocomplete, ElIcon, ElButton, ElTag } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import type { Region } from '@/types'

interface SearchSuggestion {
  id: number
  name: string
  abbreviation: string
  level1: string
  level2: string
  level3: string
  level4: string
  value: string
  parent_id: number | null
  children: Region[]
}

interface Props {
  regions: Region[]
  placeholder?: string
  maxSuggestions?: number
  saveRecent?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Search brain regions...',
  maxSuggestions: 10,
  saveRecent: true
})

const emit = defineEmits<{
  select: [region: Region]
  search: [query: string]
}>()

const searchQuery = ref('')
const recentSearches = ref<Region[]>([])

// Flatten regions for search
const flatRegions = computed(() => {
  const flatten = (regions: Region[]): Region[] => {
    let result: Region[] = []
    for (const region of regions) {
      result.push(region)
      if (region.children && region.children.length > 0) {
        result = result.concat(flatten(region.children))
      }
    }
    return result
  }
  return flatten(props.regions)
})

const querySearchAsync = (queryString: string, callback: (suggestions: SearchSuggestion[]) => void) => {
  if (!queryString) {
    callback([])
    return
  }

  const query = queryString.toLowerCase()
  const suggestions: SearchSuggestion[] = []

  for (const region of flatRegions.value) {
    if (suggestions.length >= props.maxSuggestions) break

    const nameMatch = region.name.toLowerCase().includes(query)
    const abbrMatch = region.abbreviation.toLowerCase().includes(query)
    const level1Match = region.level1.toLowerCase().includes(query)
    const level2Match = region.level2.toLowerCase().includes(query)
    const level3Match = region.level3.toLowerCase().includes(query)
    const level4Match = region.level4.toLowerCase().includes(query)

    if (nameMatch || abbrMatch || level1Match || level2Match || level3Match || level4Match) {
      suggestions.push({
        ...region,
        value: region.name
      })
    }
  }

  // Sort by relevance (exact name match first, then abbreviation, then hierarchy)
  suggestions.sort((a, b) => {
    const aNameExact = a.name.toLowerCase() === query
    const bNameExact = b.name.toLowerCase() === query
    if (aNameExact && !bNameExact) return -1
    if (!aNameExact && bNameExact) return 1

    const aAbbrExact = a.abbreviation.toLowerCase() === query
    const bAbbrExact = b.abbreviation.toLowerCase() === query
    if (aAbbrExact && !bAbbrExact) return -1
    if (!aAbbrExact && bAbbrExact) return 1

    const aNameStart = a.name.toLowerCase().startsWith(query)
    const bNameStart = b.name.toLowerCase().startsWith(query)
    if (aNameStart && !bNameStart) return -1
    if (!aNameStart && bNameStart) return 1

    return a.name.localeCompare(b.name)
  })

  callback(suggestions)
}

const handleSelect = (item: SearchSuggestion) => {
  const region = flatRegions.value.find(r => r.id === item.id)
  if (region) {
    addToRecent(region)
    emit('select', region)
  }
}

const handleClear = () => {
  searchQuery.value = ''
  emit('search', '')
}

const addToRecent = (region: Region) => {
  if (!props.saveRecent) return

  // Remove if already exists
  const index = recentSearches.value.findIndex(r => r.id === region.id)
  if (index !== -1) {
    recentSearches.value.splice(index, 1)
  }

  // Add to beginning
  recentSearches.value.unshift(region)

  // Keep only last 5
  if (recentSearches.value.length > 5) {
    recentSearches.value = recentSearches.value.slice(0, 5)
  }

  // Save to localStorage
  try {
    localStorage.setItem('visor-recent-regions', JSON.stringify(recentSearches.value))
  } catch (e) {
    console.warn('Failed to save recent searches to localStorage:', e)
  }
}

const selectRecent = (region: Region) => {
  searchQuery.value = region.name
  emit('select', region)
}

const removeRecent = (regionId: number) => {
  const index = recentSearches.value.findIndex(r => r.id === regionId)
  if (index !== -1) {
    recentSearches.value.splice(index, 1)
    saveRecentToStorage()
  }
}

const clearRecent = () => {
  recentSearches.value = []
  saveRecentToStorage()
}

const saveRecentToStorage = () => {
  try {
    localStorage.setItem('visor-recent-regions', JSON.stringify(recentSearches.value))
  } catch (e) {
    console.warn('Failed to save recent searches to localStorage:', e)
  }
}

const loadRecentFromStorage = () => {
  try {
    const stored = localStorage.getItem('visor-recent-regions')
    if (stored) {
      recentSearches.value = JSON.parse(stored)
    }
  } catch (e) {
    console.warn('Failed to load recent searches from localStorage:', e)
  }
}

// Watch search query changes
watch(searchQuery, (newQuery) => {
  emit('search', newQuery)
})

// Load recent searches on mount
if (props.saveRecent) {
  loadRecentFromStorage()
}
</script>

<style scoped>
.region-search {
  width: 100%;
}

.search-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
}

.item-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-name {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.item-abbr {
  font-size: 12px;
  color: #909399;
}

.item-hierarchy {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #c0c4cc;
}

.hierarchy-level {
  white-space: nowrap;
}

.hierarchy-separator {
  color: #e4e7ed;
}

.recent-searches {
  margin-top: 12px;
  padding: 12px;
  background-color: #fafafa;
  border-radius: 4px;
  border: 1px solid #f0f0f0;
}

.recent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  color: #909399;
}

.recent-items {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.recent-items .el-tag {
  cursor: pointer;
  transition: background-color 0.2s;
}

.recent-items .el-tag:hover {
  background-color: #e6f7ff;
}

:deep(.el-autocomplete) {
  width: 100%;
}

:deep(.el-autocomplete .el-input__inner) {
  font-size: 14px;
}

:deep(.el-autocomplete-suggestion) {
  max-height: 300px;
}

:deep(.el-autocomplete-suggestion__item) {
  padding: 8px 12px;
  line-height: 1.4;
}
</style>
