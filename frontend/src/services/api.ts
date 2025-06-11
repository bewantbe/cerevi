import axios from 'axios'

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface Specimen {
  id: string
  name: string
  species: string
  description: string
  has_image: boolean
  has_atlas: boolean
  has_model: boolean
  channels: Record<string, string>
  resolution_um: number
  coordinate_system: string
  axes_order: string
}

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
  children: number[]
  color?: string
}

export interface ImageInfo {
  specimen_id: string
  dimensions: [number, number, number]
  channels: Record<string, string>
  resolution_levels: number[]
  tile_size: number
  pixel_size_um: [number, number, number]
  data_type: string
  file_size: number
}

export interface TileGridInfo {
  view: string
  level: number
  tile_size: number
  tiles_x: number
  tiles_y: number
  image_shape: [number, number, number]
  total_tiles: number
}

export interface RegionPickResult {
  specimen_id: string
  coordinate: { x: number; y: number; z: number }
  region: Region | null
  region_value: number
  confidence: number
}

export interface RegionResponse {
  regions: Region[]
  total_count: number
  filtered_count: number
}

// API methods
export class VISoRAPI {
  // Specimens
  static async getSpecimens(): Promise<Specimen[]> {
    const response = await api.get('/api/specimens')
    return response.data
  }

  static async getSpecimen(specimenId: string): Promise<Specimen> {
    const response = await api.get(`/api/specimens/${specimenId}`)
    return response.data
  }

  // Image metadata
  static async getImageInfo(specimenId: string): Promise<ImageInfo> {
    const response = await api.get(`/api/specimens/${specimenId}/image-info`)
    return response.data
  }

  static async getTileGridInfo(
    specimenId: string,
    view: string,
    level: number
  ): Promise<TileGridInfo> {
    const response = await api.get(
      `/api/specimens/${specimenId}/tile-grid/${view}/${level}`
    )
    return response.data
  }

  // Tiles
  static getImageTileUrl(
    specimenId: string,
    view: string,
    level: number,
    z: number,
    x: number,
    y: number,
    channel: number = 0
  ): string {
    return `${API_BASE_URL}/api/specimens/${specimenId}/image/${view}/${level}/${z}/${x}/${y}?channel=${channel}`
  }

  static getAtlasTileUrl(
    specimenId: string,
    view: string,
    level: number,
    z: number,
    x: number,
    y: number
  ): string {
    return `${API_BASE_URL}/api/specimens/${specimenId}/atlas/${view}/${level}/${z}/${x}/${y}`
  }

  // Regions
  static async getRegions(
    specimenId: string,
    options?: {
      level?: number
      search?: string
      maxResults?: number
    }
  ): Promise<RegionResponse> {
    const params = new URLSearchParams()
    if (options?.level) params.append('level', options.level.toString())
    if (options?.search) params.append('search', options.search)
    if (options?.maxResults) params.append('max_results', options.maxResults.toString())

    const response = await api.get(`/api/specimens/${specimenId}/regions?${params}`)
    return response.data
  }

  static async getRegion(specimenId: string, regionId: number): Promise<Region> {
    const response = await api.get(`/api/specimens/${specimenId}/regions/${regionId}`)
    return response.data
  }

  static async pickRegion(
    specimenId: string,
    view: string,
    x: number,
    y: number,
    z: number,
    level: number = 0
  ): Promise<RegionPickResult> {
    const response = await api.post(`/api/specimens/${specimenId}/pick-region`, {
      specimen_id: specimenId,
      view,
      x,
      y,
      z,
      level,
    })
    return response.data
  }

  static async searchRegions(
    specimenId: string,
    query: string,
    maxResults: number = 50
  ): Promise<{ query: string; results: Region[]; total_matches: number }> {
    const response = await api.get(
      `/api/specimens/${specimenId}/regions/search?q=${encodeURIComponent(query)}&max_results=${maxResults}`
    )
    return response.data
  }

  // Health check
  static async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await api.get('/health')
    return response.data
  }
}

// Error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default VISoRAPI
