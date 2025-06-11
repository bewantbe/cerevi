// API response types and request interfaces

export interface ApiResponse<T = any> {
  data?: T
  error?: string
  message?: string
}

export interface HealthResponse {
  status: string
  version: string
  data_path_exists: boolean
}

export interface TileRequest {
  specimenId: string
  view: ViewType
  level: number
  z: number
  x: number
  y: number
  channel?: number
  tile_size?: number
}

export interface RegionPickRequest {
  view: ViewType
  x: number
  y: number
  z: number
  level: number
}


export type ViewType = 'sagittal' | 'coronal' | 'horizontal'
export type ChannelType = 0 | 1 | 2 | 3

export interface RegionPickResponse {
  region_id: number | null
  region_name: string | null
  coordinates: {
    image: [number, number, number]
    world: [number, number, number]
  }
}

export interface ApiError {
  detail: string
  status_code: number
}
