import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import VISoRAPI, { type Specimen, type Region, type ImageInfo, type RegionPickResult } from '@/services/api'

export type ViewType = 'sagittal' | 'coronal' | 'horizontal'

export const useVISoRStore = defineStore('visor', () => {
  // State
  const currentSpecimen = ref<Specimen | null>(null)
  const specimens = ref<Specimen[]>([])
  const imageInfo = ref<ImageInfo | null>(null)
  const regions = ref<Region[]>([])
  const selectedRegion = ref<Region | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Current view state
  const currentView = ref<ViewType>('sagittal')
  const currentSlice = ref<{ sagittal: number; coronal: number; horizontal: number }>({
    sagittal: 0,
    coronal: 0,
    horizontal: 0,
  })
  const currentChannel = ref(0)
  const currentLevel = ref(0)

  // UI state
  const showAtlasOverlay = ref(true)
  const atlasOpacity = ref(0.5)
  const sidebarVisible = ref(true)
  const regionBrowserVisible = ref(true)

  // Computed
  const availableChannels = computed(() => {
    return currentSpecimen.value?.channels || {}
  })

  const maxSlices = computed(() => {
    if (!imageInfo.value) return { sagittal: 0, coronal: 0, horizontal: 0 }
    const [z, y, x] = imageInfo.value.dimensions
    return {
      sagittal: x - 1,  // X slices for sagittal view
      coronal: y - 1,   // Y slices for coronal view
      horizontal: z - 1, // Z slices for horizontal view
    }
  })

  const currentSliceForView = computed(() => {
    return currentSlice.value[currentView.value]
  })

  // Actions
  async function loadSpecimens() {
    loading.value = true
    error.value = null
    try {
      specimens.value = await VISoRAPI.getSpecimens()
    } catch (err) {
      error.value = 'Failed to load specimens'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  async function setCurrentSpecimen(specimenId: string) {
    loading.value = true
    error.value = null
    try {
      const specimen = await VISoRAPI.getSpecimen(specimenId)
      currentSpecimen.value = specimen
      
      // Load image info if available
      if (specimen.has_image) {
        imageInfo.value = await VISoRAPI.getImageInfo(specimenId)
        
        // Initialize slice positions to center
        if (imageInfo.value) {
          const [z, y, x] = imageInfo.value.dimensions
          currentSlice.value = {
            sagittal: Math.floor(x / 2),
            coronal: Math.floor(y / 2),
            horizontal: Math.floor(z / 2),
          }
        }
      }
      
      // Load regions if available
      if (specimen.has_atlas) {
        await loadRegions()
      }
    } catch (err) {
      error.value = 'Failed to load specimen'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  async function loadRegions(options?: { level?: number; search?: string }) {
    if (!currentSpecimen.value) return
    
    loading.value = true
    try {
      const result = await VISoRAPI.getRegions(currentSpecimen.value.id, options)
      regions.value = result.regions
    } catch (err) {
      error.value = 'Failed to load regions'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  async function pickRegionAtCoordinate(x: number, y: number, z: number): Promise<RegionPickResult | null> {
    if (!currentSpecimen.value) return null
    
    try {
      const result = await VISoRAPI.pickRegion(
        currentSpecimen.value.id,
        currentView.value,
        x,
        y,
        z,
        currentLevel.value
      )
      
      if (result.region) {
        selectedRegion.value = result.region
      }
      
      return result
    } catch (err) {
      error.value = 'Failed to pick region'
      console.error(err)
      return null
    }
  }

  function setCurrentView(view: ViewType) {
    currentView.value = view
  }

  function setCurrentSlice(slice: number) {
    currentSlice.value[currentView.value] = Math.max(0, Math.min(slice, maxSlices.value[currentView.value]))
  }

  function setSliceForView(view: ViewType, slice: number) {
    currentSlice.value[view] = Math.max(0, Math.min(slice, maxSlices.value[view]))
  }

  function setCurrentChannel(channel: number) {
    const availableChannelKeys = Object.keys(availableChannels.value).map(Number)
    if (availableChannelKeys.includes(channel)) {
      currentChannel.value = channel
    }
  }

  function setCurrentLevel(level: number) {
    if (imageInfo.value && imageInfo.value.resolution_levels.includes(level)) {
      currentLevel.value = level
    }
  }

  function setSelectedRegion(region: Region | null) {
    selectedRegion.value = region
  }

  function toggleAtlasOverlay() {
    showAtlasOverlay.value = !showAtlasOverlay.value
  }

  function setAtlasOpacity(opacity: number) {
    atlasOpacity.value = Math.max(0, Math.min(1, opacity))
  }

  function toggleSidebar() {
    sidebarVisible.value = !sidebarVisible.value
  }

  function toggleRegionBrowser() {
    regionBrowserVisible.value = !regionBrowserVisible.value
  }

  function clearError() {
    error.value = null
  }

  // Initialize
  function initialize() {
    loadSpecimens()
  }

  return {
    // State
    currentSpecimen,
    specimens,
    imageInfo,
    regions,
    selectedRegion,
    loading,
    error,
    currentView,
    currentSlice,
    currentChannel,
    currentLevel,
    showAtlasOverlay,
    atlasOpacity,
    sidebarVisible,
    regionBrowserVisible,
    
    // Computed
    availableChannels,
    maxSlices,
    currentSliceForView,
    
    // Actions
    loadSpecimens,
    setCurrentSpecimen,
    loadRegions,
    pickRegionAtCoordinate,
    setCurrentView,
    setCurrentSlice,
    setSliceForView,
    setCurrentChannel,
    setCurrentLevel,
    setSelectedRegion,
    toggleAtlasOverlay,
    setAtlasOpacity,
    toggleSidebar,
    toggleRegionBrowser,
    clearError,
    initialize,
  }
})
