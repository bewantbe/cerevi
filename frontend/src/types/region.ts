// Brain region and atlas types

export interface Region {
  id: number
  name: string
  abbreviation: string
  level1: string
  level2: string
  level3: string
  level4: string
  value: number
  parent_id: number | null
  children: Region[]
  color?: string
  visible?: boolean
  selected?: boolean
}

export interface RegionHierarchy {
  regions: Region[]
  hierarchy: Record<string, any>
  total_count: number
  max_depth: number
}

export interface RegionFilter {
  search: string
  level: number | null
  parent_id: number | null
  show_empty: boolean
}

export interface RegionSelection {
  selectedRegions: Set<number>
  highlightedRegion: number | null
  hoveredRegion: number | null
  selectionMode: 'single' | 'multiple' | 'hierarchy'
}

export interface RegionStyle {
  fillColor: string
  strokeColor: string
  strokeWidth: number
  fillOpacity: number
  strokeOpacity: number
}

export interface RegionPickResult {
  region: Region | null
  coordinates: {
    image: [number, number, number]
    world: [number, number, number]
    view: [number, number]
  }
  view: 'sagittal' | 'coronal' | 'horizontal'
  level: number
}

export interface AtlasOverlay {
  enabled: boolean
  opacity: number
  colorScheme: 'default' | 'rainbow' | 'heat' | 'custom'
  showBorders: boolean
  borderWidth: number
  labelMode: 'none' | 'hover' | 'selected' | 'all'
}

export interface RegionStatistics {
  region_id: number
  volume_voxels: number
  volume_mm3: number
  centroid: [number, number, number]
  bounding_box: {
    min: [number, number, number]
    max: [number, number, number]
  }
  intensity_stats?: {
    mean: number
    std: number
    min: number
    max: number
    channel: number
  }[]
}

export interface RegionTree {
  root: Region
  flatList: Region[]
  levelMap: Map<number, Region[]>
  parentMap: Map<number, Region>
  childrenMap: Map<number, Region[]>
}
