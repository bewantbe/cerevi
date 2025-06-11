// Viewer state and UI types

import type { ViewType, ChannelType } from './api'

export interface ViewerState {
  currentView: ViewType | 'grid' | '3d'
  position: [number, number, number] // [x, y, z] in image coordinates
  zoom: number
  slice: number
  level: number
}

export interface ViewerSettings {
  synchronizeViews: boolean
  showCrosshair: boolean
  showCoordinates: boolean
  showScale: boolean
  smoothPanning: boolean
  keyboardNavigation: boolean
}

export interface ChannelSettings {
  activeChannels: ChannelType[]
  visibility: Record<ChannelType, boolean>
  brightness: Record<ChannelType, number>
  contrast: Record<ChannelType, number>
  gamma: Record<ChannelType, number>
  blendMode: 'normal' | 'multiply' | 'screen' | 'overlay'
}

export interface AtlasSettings {
  enabled: boolean
  opacity: number
  colorMode: 'region' | 'hierarchy' | 'custom'
  showLabels: boolean
  labelSize: number
}

export interface ViewerLayout {
  showControlPanel: boolean
  controlPanelWidth: number
  activeTab: 'metadata' | 'channels' | 'atlas' | 'regions'
  gridLayout: '2x2' | '1x3' | '3x1'
  maximizedView: ViewType | '3d' | null
}

export interface OpenSeadragonConfig {
  showNavigator: boolean
  showRotationControl: boolean
  showHomeControl: boolean
  showFullPageControl: boolean
  showZoomControl: boolean
  mouseNavEnabled: boolean
  navImages: Record<string, string>
}

export interface ThreeJSConfig {
  enableControls: boolean
  showAxes: boolean
  showGrid: boolean
  backgroundColor: string
  cameraType: 'perspective' | 'orthographic'
  lightIntensity: number
}

export interface CoordinateDisplay {
  format: 'pixel' | 'world' | 'relative'
  precision: number
  showUnits: boolean
}

export interface ViewerError {
  type: 'network' | 'data' | 'rendering' | 'unknown'
  message: string
  details?: string
  timestamp: Date
  recoverable: boolean
}

export interface LoadingState {
  isLoading: boolean
  progress: number
  stage: string
  estimatedTime?: number
}
