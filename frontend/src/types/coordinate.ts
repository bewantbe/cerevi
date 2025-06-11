// Coordinate system and transformation types

import type { ViewType } from './api'

export interface Point3D {
  x: number
  y: number
  z: number
}

export interface Point2D {
  x: number
  y: number
}

export interface BoundingBox3D {
  min: Point3D
  max: Point3D
}

export interface BoundingBox2D {
  min: Point2D
  max: Point2D
}

export interface CoordinateSystem {
  name: string
  handedness: 'left' | 'right'
  axes_order: string
  origin: Point3D
  units: string
  scale: [number, number, number]
}

export interface ViewTransform {
  view: ViewType
  slice_axis: 'x' | 'y' | 'z'
  display_axes: [string, string]
  array_mapping: [number, number]
  flip_x: boolean
  flip_y: boolean
  rotation: number
}

export interface CoordinateTransform {
  from_system: string
  to_system: string
  translation: Point3D
  rotation: number[]
  scale: Point3D
  matrix: number[][]
}

export interface ViewportState {
  center: Point2D
  zoom: number
  rotation: number
  bounds: BoundingBox2D
  pixel_size: Point2D
}

export interface SliceInfo {
  view: ViewType
  slice_index: number
  slice_position: number
  slice_thickness: number
  total_slices: number
  spacing: number
}

export interface PixelInfo {
  image_coordinates: Point3D
  world_coordinates: Point3D
  view_coordinates: Point2D
  pixel_value: number | number[]
  region_id: number | null
  zoom_level: number
}

export interface NavigationState {
  position: Point3D
  target: Point3D
  zoom: number
  rotation: Point3D
  view_matrix: number[][]
  projection_matrix: number[][]
}

export interface CrosshairState {
  enabled: boolean
  position: Point3D
  color: string
  thickness: number
  style: 'solid' | 'dashed' | 'dotted'
  show_labels: boolean
}

export type CoordinateFormat = 'pixel' | 'micron' | 'millimeter' | 'relative' | 'slice'

export interface CoordinateDisplay {
  format: CoordinateFormat
  precision: number
  show_units: boolean
  separator: string
}
