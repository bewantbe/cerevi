import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import VISoRAPI from '@/services/api'
import type { 
  Specimen, 
  Region, 
  ImageInfo, 
  RegionPickResult, 
  ViewerState,
  ChannelSettings,
  AtlasSettings,
  ViewerLayout
} from '@/types'
import type { ViewType, ChannelType } from '@/types/api'

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
  const zoomLevel = ref(1)
  const position = ref<[number, number, number]>([0, 0, 0])

  // UI state
  const showAtlasOverlay = ref(true)
  const atlasOpacity = ref(0.5)
  const sidebarVisible = ref(true)
  const regionBrowserVisible = ref(true)
  const maximizedView = ref<ViewType | '3d' | null>(null)
  const synchronizeViews = ref(true)
  const showCrosshair = ref(true)

  // Channel settings
  const channelSettings = ref<ChannelSettings>({
    activeChannels: [0],
    visibility: { 0: true, 1: true, 2: true, 3: true },
    brightness: { 0: 50, 1: 50, 2: 50, 3: 50 },
    contrast: { 0: 50, 1: 50, 2: 50, 3: 50 },
    gamma: { 0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0 },
    blendMode: 'normal'
  })

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

  const maxLevel = computed(() => {
    return imageInfo.value?.resolution_levels || 0
  })

  const viewerState = computed((): ViewerState => ({
    currentView: maximizedView.value || 'grid',
    position: position.value,
    zoom: zoomLevel.value,
    slice: currentSliceForView.value,
    level: currentLevel.value
  }))

  const currentSliceForView = computed(() => {
    return currentSlice.value[currentView.value as keyof typeof currentSlice.value]
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
        imageInfo.value = await VISoRAPI.getImageInfo(specimenId) as any
        
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
      regions.value = result.regions as any
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
        selectedRegion.value = result.region as any
      }
      
      return result as any
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
    const view = currentView.value as keyof typeof currentSlice.value
    currentSlice.value[view] = Math.max(0, Math.min(slice, maxSlices.value[view]))
  }

  function setSliceForView(view: ViewType, slice: number) {
    currentSlice.value[view as keyof typeof currentSlice.value] = Math.max(0, Math.min(slice, maxSlices.value[view as keyof typeof maxSlices.value]))
  }

  function setCurrentChannel(channel: number) {
    const availableChannelKeys = Object.keys(availableChannels.value).map(Number)
    if (availableChannelKeys.includes(channel)) {
      currentChannel.value = channel
    }
  }

  function setCurrentLevel(level: number) {
    if (imageInfo.value && level >= 0 && level < imageInfo.value.resolution_levels) {
      currentLevel.value = level
    }
  }

  function setZoomLevel(zoom: number) {
    zoomLevel.value = Math.max(0.1, Math.min(100, zoom))
  }

  function setPosition(newPosition: [number, number, number]) {
    position.value = [...newPosition]
    
    // Update slice positions if synchronizeViews is enabled
    if (synchronizeViews.value) {
      const [z, y, x] = newPosition
      currentSlice.value = {
        sagittal: Math.round(x),
        coronal: Math.round(y),
        horizontal: Math.round(z)
      }
    }
  }

  function maximizeView(view: ViewType | '3d' | null) {
    maximizedView.value = view
  }

  function toggleViewSync() {
    synchronizeViews.value = !synchronizeViews.value
  }

  function toggleCrosshair() {
    showCrosshair.value = !showCrosshair.value
  }

  function updateChannelSettings(channel: ChannelType, settings: Partial<{
    visibility: boolean
    brightness: number
    contrast: number
    gamma: number
  }>) {
    if (settings.visibility !== undefined) {
      channelSettings.value.visibility[channel as keyof typeof channelSettings.value.visibility] = settings.visibility
    }
    if (settings.brightness !== undefined) {
      channelSettings.value.brightness[channel as keyof typeof channelSettings.value.brightness] = settings.brightness
    }
    if (settings.contrast !== undefined) {
      channelSettings.value.contrast[channel as keyof typeof channelSettings.value.contrast] = settings.contrast
    }
    if (settings.gamma !== undefined) {
      channelSettings.value.gamma[channel as keyof typeof channelSettings.value.gamma] = settings.gamma
    }
  }

  function setChannelBlendMode(mode: 'normal' | 'multiply' | 'screen' | 'overlay') {
    channelSettings.value.blendMode = mode
  }

  function resetChannelSettings() {
    channelSettings.value = {
      activeChannels: [0],
      visibility: { 0: true, 1: true, 2: true, 3: true },
      brightness: { 0: 50, 1: 50, 2: 50, 3: 50 },
      contrast: { 0: 50, 1: 50, 2: 50, 3: 50 },
      gamma: { 0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0 },
      blendMode: 'normal'
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
    zoomLevel,
    position,
    showAtlasOverlay,
    atlasOpacity,
    sidebarVisible,
    regionBrowserVisible,
    maximizedView,
    synchronizeViews,
    showCrosshair,
    channelSettings,
    
    // Computed
    availableChannels,
    maxSlices,
    maxLevel,
    currentSliceForView,
    viewerState,
    
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
    setZoomLevel,
    setPosition,
    setSelectedRegion,
    maximizeView,
    toggleViewSync,
    toggleCrosshair,
    toggleAtlasOverlay,
    setAtlasOpacity,
    toggleSidebar,
    toggleRegionBrowser,
    updateChannelSettings,
    setChannelBlendMode,
    resetChannelSettings,
    clearError,
    initialize,
  }
})
