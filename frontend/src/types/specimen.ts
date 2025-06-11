// Specimen and metadata types

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

export interface SpecimenMetadata {
  specimen: Specimen
  image_info?: ImageInfo
  atlas_info?: AtlasInfo
  model_info?: ModelInfo
  processing_info?: ProcessingInfo
}

export interface ImageInfo {
  dimensions: [number, number, number] // [z, y, x]
  resolution_levels: number
  channels: number
  data_type: string
  file_size_bytes: number
  pixel_size_um: [number, number, number]
  voxel_count: number
}

export interface AtlasInfo {
  dimensions: [number, number, number]
  resolution_levels: number
  region_count: number
  file_size_bytes: number
}

export interface ModelInfo {
  format: string
  vertices: number
  faces: number
  file_size_bytes: number
}

export interface ProcessingInfo {
  created_at: string
  processing_time_hours: number
  software_version: string
  parameters: Record<string, any>
}

export interface ChannelInfo {
  id: number
  name: string
  wavelength: string
  color: string
  enabled: boolean
  brightness: number
  contrast: number
  gamma: number
}
