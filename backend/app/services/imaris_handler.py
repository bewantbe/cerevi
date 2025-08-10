"""
Service for handling Imaris (.ims) files
"""

import h5py
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import logging
from ..models.specimen import ViewType, COORDINATE_TRANSFORMS
from ..config import settings

logger = logging.getLogger(__name__)

class ImarisHandler:
    """Handler for Imaris (.ims) HDF5 files"""
    
    def __init__(self, file_path: Union[str, Path]):
        """Initialize with path to .ims file"""
        self.file_path = Path(file_path)
        self._file = None
        self._metadata = None
        
    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        
    def open(self):
        """Open the HDF5 file"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Imaris file not found: {self.file_path}")
        
        try:
            self._file = h5py.File(self.file_path, 'r')
            logger.info(f"Opened Imaris file: {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to open Imaris file {self.file_path}: {e}")
            raise
            
    def close(self):
        """Close the HDF5 file"""
        if self._file:
            self._file.close()
            self._file = None
            
    @property
    def is_open(self) -> bool:
        """Check if file is open"""
        return self._file is not None
        
    def get_resolution_levels(self) -> List[int]:
        """Get available resolution levels"""
        if not self.is_open:
            raise RuntimeError("File not open")
            
        levels = []
        dataset_group = self._file.get('DataSet')
        if dataset_group:
            for key in dataset_group.keys():
                if key.startswith('ResolutionLevel'):
                    level_num = int(key.split()[-1])
                    levels.append(level_num)
        
        return sorted(levels)
    
    def get_channels(self) -> List[int]:
        """Get available channels"""
        if not self.is_open:
            raise RuntimeError("File not open")
            
        channels = []
        # Check first resolution level for available channels
        levels = self.get_resolution_levels()
        if levels:
            level_group = self._file[f'DataSet/ResolutionLevel {levels[0]}/TimePoint 0']
            for key in level_group.keys():
                if key.startswith('Channel'):
                    channel_num = int(key.split()[-1])
                    channels.append(channel_num)
        
        return sorted(channels)
    
    def get_data_shape(self, level: int, channel: int = 0) -> Tuple[int, int, int]:
        """Get shape of data array for specific level and channel"""
        if not self.is_open:
            raise RuntimeError("File not open")
            
        try:
            dataset_path = f'DataSet/ResolutionLevel {level}/TimePoint 0/Channel {channel}/Data'
            dataset = self._file[dataset_path]
            return dataset.shape  # (z, y, x)
        except KeyError:
            raise ValueError(f"Data not found for level {level}, channel {channel}")
    
    def get_tile(self, view: ViewType, level: int, channel: int,
                 z: int, y: int, x: int, tile_size: int = 512) -> np.ndarray:
        """Extract tile from 3D data using direct pixel coordinates
        
        Args:
            view: View type (coronal, sagittal, horizontal)
            level: Resolution level
            channel: Channel index
            z: Z coordinate (pixel position)
            y: Y coordinate (pixel position)
            x: X coordinate (pixel position)
            tile_size: Size of extracted tile
            
        Returns:
            2D numpy array containing the extracted tile
            
        Note: Coordinates (z,y,x) specify the origin (top-left corner) of the tile.
        """
        if not self.is_open:
            raise RuntimeError("File not open")
            
        dataset_path = f'DataSet/ResolutionLevel {level}/TimePoint 0/Channel {channel}/Data'
        dataset = self._file[dataset_path]
        
        data_shape = dataset.shape  # (z, y, x)
        
        # Validate coordinates
        pivot_zyx = (z, y, x)
        for i in range(3):
            if pivot_zyx[i] < 0 or pivot_zyx[i] >= data_shape[i]:
                raise ValueError(f"Coordinate {pivot_zyx[i]} out of bounds for dimension {i} with size {data_shape[i]}")

        # Extract slice based on view type with same logic as h5py implementation
        if view == ViewType.CORONAL:
            rg_horizontal = slice(x, x + tile_size)    # -x direction
            rg_vertical = slice(y, y + tile_size)      # -y direction
            tile = dataset[z, rg_vertical, rg_horizontal][::-1, ::-1]
        elif view == ViewType.SAGITTAL:
            rg_horizontal = slice(z, z + tile_size)    #  z direction
            rg_vertical = slice(y, y + tile_size)      # -y direction
            tile = dataset[rg_horizontal, rg_vertical, x][:, ::-1].T
        elif view == ViewType.HORIZONTAL:
            rg_horizontal = slice(x, x + tile_size)    # -x direction
            rg_vertical = slice(z, z + tile_size)      # -z direction
            tile = dataset[rg_vertical, y, rg_horizontal][::-1, ::-1]
        else:
            raise ValueError(f"Unknown view type: {view}")
        
        # We may pad to full tile_size here
        return tile
    
    def get_metadata(self) -> Dict:
        """Extract metadata from the file"""
        if not self.is_open:
            raise RuntimeError("File not open")
            
        if self._metadata is None:
            metadata = {
                "file_path": str(self.file_path),
                "file_size": self.file_path.stat().st_size,
                "resolution_levels": self.get_resolution_levels(),
                "channels": self.get_channels(),
                "shapes": {},
                "data_type": None,
            }
            
            # Get shapes for each resolution level
            levels = metadata["resolution_levels"]
            channels = metadata["channels"]
            
            if levels and channels:
                for level in levels:
                    try:
                        shape = self.get_data_shape(level, channels[0])
                        metadata["shapes"][level] = shape
                        
                        # Get data type from first level
                        if metadata["data_type"] is None:
                            dataset_path = f'DataSet/ResolutionLevel {level}/TimePoint 0/Channel {channels[0]}/Data'
                            dataset = self._file[dataset_path]
                            metadata["data_type"] = str(dataset.dtype)
                            
                    except Exception as e:
                        logger.warning(f"Could not get shape for level {level}: {e}")
            
            self._metadata = metadata
            
        return self._metadata
    
    def get_histogram(self, level: int, channel: int) -> Optional[np.ndarray]:
        """Get histogram data for a specific level and channel"""
        if not self.is_open:
            raise RuntimeError("File not open")
            
        try:
            hist_path = f'DataSet/ResolutionLevel {level}/TimePoint 0/Channel {channel}/Histogram'
            histogram = self._file[hist_path]
            return np.array(histogram)
        except KeyError:
            logger.warning(f"No histogram found for level {level}, channel {channel}")
            return None
    
    def get_pixel_value_at_coordinate(self, level: int, channel: int, 
                                    x: int, y: int, z: int) -> Union[int, float]:
        """Get pixel value at specific 3D coordinate"""
        if not self.is_open:
            raise RuntimeError("File not open")
            
        try:
            dataset_path = f'DataSet/ResolutionLevel {level}/TimePoint 0/Channel {channel}/Data'
            dataset = self._file[dataset_path]
            
            # Check bounds
            shape = dataset.shape  # (z, y, x)
            if not (0 <= z < shape[0] and 0 <= y < shape[1] and 0 <= x < shape[2]):
                raise ValueError(f"Coordinates ({x}, {y}, {z}) out of bounds for shape {shape}")
            
            return dataset[z, y, x]
            
        except KeyError:
            raise ValueError(f"Data not found for level {level}, channel {channel}")

    def calculate_tile_grid_size(self, view: ViewType, level: int, 
                                tile_size: int = 512) -> Tuple[int, int]:
        """Calculate number of tiles needed in each dimension"""
        if not self.is_open:
            raise RuntimeError("File not open")
            
        # Get shape for any channel (they should be the same)
        channels = self.get_channels()
        if not channels:
            raise ValueError("No channels found")
            
        shape = self.get_data_shape(level, channels[0])  # (z, y, x)
        
        # Get the 2D slice dimensions based on view
        if view == ViewType.SAGITTAL:
            height, width = shape[0], shape[1]  # z, y
        elif view == ViewType.CORONAL:
            height, width = shape[0], shape[2]  # z, x
        elif view == ViewType.HORIZONTAL:
            height, width = shape[1], shape[2]  # y, x
        else:
            raise ValueError(f"Unknown view type: {view}")
        
        # Calculate number of tiles
        tiles_x = (width + tile_size - 1) // tile_size
        tiles_y = (height + tile_size - 1) // tile_size
        
        return tiles_x, tiles_y
