import { ref, type Ref, onUnmounted } from 'vue'
import OpenSeadragon from 'openseadragon'
import { useVISoRStore } from '@/stores/visor'

export interface OpenSeadragonOptions {
  specimenId: string
  view: 'sagittal' | 'coronal' | 'horizontal'
  channel?: number
  level?: number
}

export function useOpenSeadragon(containerRef: Ref<HTMLElement | undefined>) {
  const viewer = ref<OpenSeadragon.Viewer | null>(null)
  const coordinates = ref({ x: 0, y: 0, z: 0 })
  const zoom = ref(1)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  const viewerStore = useVISoRStore()

  const createTileSource = (options: OpenSeadragonOptions) => {
    const { specimenId, view, channel = Object.keys(viewerStore.imageInfo?.channels || {})[0] || 0 } = options
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    
    return {
      height: viewerStore.imageInfo?.dimensions[1] || 1, // Minimum default value indicating invalid state
      width: viewerStore.imageInfo?.dimensions[2] || 1,
      tileSize: viewerStore.imageInfo?.tile_size || 512,
      overlap: 0,
      minLevel: 0,
      maxLevel: viewerStore.imageInfo?.resolution_levels?.length 
        ? viewerStore.imageInfo.resolution_levels.length - 1 
        : 0,
      getTileUrl: function(level: number, x: number, y: number) {
        const z = coordinates.value.z
        return `${baseUrl}/api/specimens/${specimenId}/image/${view}/${level}/${z}/${x}/${y}?channel=${channel}`
      }
    }
  }

  const initViewer = async (options: OpenSeadragonOptions) => {
    if (!containerRef.value) return
    
    isLoading.value = true
    error.value = null
    
    try {
      // Destroy existing viewer if it exists
      if (viewer.value) {
        viewer.value.destroy()
      }

      viewer.value = OpenSeadragon({
        element: containerRef.value,
        tileSources: createTileSource(options),
        
        // OpenSeadragon configuration
        prefixUrl: 'https://cdn.jsdelivr.net/npm/openseadragon@4.1.1/build/openseadragon/images/',
        animationTime: 0.3,
        blendTime: 0.1,
        constrainDuringPan: true,
        maxZoomPixelRatio: 4,
        minZoomLevel: 0.1,
        visibilityRatio: 1,
        zoomPerScroll: 1.2,
        
        // Custom styling
        showNavigator: true,
        navigatorPosition: 'BOTTOM_RIGHT',
        showRotationControl: false,
        showHomeControl: false,
        showZoomControl: true,
        showFullPageControl: false,
        
        // Event handling
        gestureSettingsMouse: {
          scrollToZoom: true,
          clickToZoom: true,
          dblClickToZoom: true,
          pinchToZoom: true,
          flickEnabled: true
        }
      })

      // Event listeners
      viewer.value.addHandler('viewport-change', onViewportChange)
      viewer.value.addHandler('canvas-click', onCanvasClick)
      viewer.value.addHandler('tile-loaded', onTileLoaded)
      viewer.value.addHandler('tile-load-failed', onTileLoadFailed)

      isLoading.value = false
    } catch (err) {
      error.value = `Failed to initialize viewer: ${err}`
      isLoading.value = false
    }
  }

  const onViewportChange = () => {
    if (!viewer.value) return
    
    const viewport = viewer.value.viewport
    zoom.value = viewport.getZoom()
    
    // Update coordinates for synchronization
    const center = viewport.getCenter()
    coordinates.value.x = center.x
    coordinates.value.y = center.y
  }

  const onCanvasClick = (event: any) => {
    if (!viewer.value || !viewerStore.imageInfo) return
    
    const webPoint = event.position
    const viewportPoint = viewer.value.viewport.pointFromPixel(webPoint)
    
    // Get image dimensions from store
    const [z, y, x] = viewerStore.imageInfo.dimensions
    const imageCoords = {
      x: Math.floor(viewportPoint.x * x),
      y: Math.floor(viewportPoint.y * y),
      z: coordinates.value.z
    }
    
    // Pick region at the clicked coordinates
    viewerStore.pickRegionAtCoordinate(imageCoords.x, imageCoords.y, imageCoords.z)
  }

  const onTileLoaded = () => {
    // Handle successful tile loading
  }

  const onTileLoadFailed = (event: any) => {
    console.warn('Tile load failed:', event)
  }

  const updateSlice = (newZ: number) => {
    coordinates.value.z = newZ
    if (viewer.value) {
      viewer.value.world.resetItems()
      // Reload tiles for new slice
      viewer.value.open(createTileSource({
        specimenId: viewerStore.currentSpecimen?.id || '',
        view: viewerStore.currentView as any,
        channel: viewerStore.currentChannel
      }))
    }
  }

  const updateChannel = (channel: number) => {
    if (viewer.value) {
      viewer.value.world.resetItems()
      viewer.value.open(createTileSource({
        specimenId: viewerStore.currentSpecimen?.id || '',
        view: viewerStore.currentView as any,
        channel
      }))
    }
  }

  const zoomIn = () => {
    if (viewer.value) {
      viewer.value.viewport.zoomBy(1.5)
    }
  }

  const zoomOut = () => {
    if (viewer.value) {
      viewer.value.viewport.zoomBy(0.67)
    }
  }

  const resetView = () => {
    if (viewer.value) {
      viewer.value.viewport.goHome()
    }
  }

  const goToCoordinate = (x: number, y: number, z: number) => {
    if (!viewer.value || !viewerStore.imageInfo) return
    
    coordinates.value = { x, y, z }
    
    // Convert image coordinates to viewport coordinates
    const [zDim, yDim, xDim] = viewerStore.imageInfo.dimensions
    const viewportPoint = new OpenSeadragon.Point(x / xDim, y / yDim)
    
    viewer.value.viewport.panTo(viewportPoint)
    updateSlice(z)
  }

  onUnmounted(() => {
    if (viewer.value) {
      viewer.value.destroy()
    }
  })

  return {
    viewer,
    coordinates,
    zoom,
    isLoading,
    error,
    initViewer,
    updateSlice,
    updateChannel,
    zoomIn,
    zoomOut,
    resetView,
    goToCoordinate
  }
}
