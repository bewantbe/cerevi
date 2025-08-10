#!/usr/bin/env python3
"""
Script to read and save image using backend facilities (TileService)
Equivalent to API call: http://localhost:8000/api/specimens/macaque_brain_rm009/image/coronal/0/z/y/x?channel=0
Note: API coordinate order changed from z/x/y to z/y/x to match standard conventions
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add the backend app to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.tile_service import TileService
from app.models.specimen import ViewType
from app.config import settings
import time

def read_save_ims_backend(specimen_id, view, level, channel, z, y, x, tile_size):
    """Extract and save image tile using backend TileService (matching h5py parameters)"""
    print(f"Fetching image tile using backend TileService...")
    print(f"Parameters: specimen={specimen_id}, view={view}, level={level}, channel={channel}, z={z}, y={y}, x={x}")
    
    try:
        # Initialize tile service
        tile_service = TileService()
        
        # Get raw tile data first to show pixel statistics before conversion
        from app.services.imaris_handler import ImarisHandler
        from app.config import settings
        import numpy as np
        
        # Get the raw tile data directly
        image_path = settings.get_image_path(specimen_id)
        with ImarisHandler(image_path) as handler:
            raw_tile_data = handler.get_tile(view, level, channel, z, y, x, tile_size)
            # Apply final vertical flip (same as TileService does)
            tile_flipped = raw_tile_data[::-1, :]
            
        print(f"\nRaw Tile Pixel Statistics (before JPEG conversion):")
        print(f"  Mean: {np.mean(tile_flipped):.2f}")
        print(f"  Std:  {np.std(tile_flipped):.2f}")
        print(f"  Min:  {np.min(tile_flipped):.2f}")
        print(f"  Max:  {np.max(tile_flipped):.2f}")
        print(f"  Shape: {tile_flipped.shape}")
        print(f"  Dtype: {tile_flipped.dtype}")
        
        # Extract image tile (same as API endpoint but with tile_size parameter)
        start_time = time.time()
        image_bytes = tile_service.extract_image_tile(
            specimen_id=specimen_id,
            view=view,
            level=level,
            channel=channel,
            z=z,
            y=y,
            x=x,
            tile_size=tile_size
        )
        elapsed_time = time.time() - start_time
        print(f"  Tile extraction time: {elapsed_time:.3f} seconds")
        
        # Save to file with same naming convention as h5py
        output_path = Path(__file__).parent / f"image_backend_{specimen_id}_{view}_l{level}_c{channel}_z{z}_y{y}_x{x}.jpg"
        
        with open(output_path, 'wb') as f:
            f.write(image_bytes)
        
        print(f"✓ Image saved successfully: {output_path}")
        print(f"  Image size: {len(image_bytes)} bytes")
        
        # Display image info
        image_info = tile_service.get_image_info(specimen_id)
        print(f"tile_service.get_image_info(specimen_id)")
        print(f"  Image dimensions: {image_info['dimensions']}")
        print(f"  Available channels: {list(image_info['channels'].keys())}")
        print(f"  Resolution levels: {image_info['resolution_levels']}")
        
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        print("  Make sure the image file exists at the expected location.")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1
    
    return 0

def main():
    """Extract and save image tile using backend TileService"""
    
    # Parameters matching the h5py implementation
    params = [
        {
            "specimen_id": "macaque_brain_rm009",
            "view": ViewType.CORONAL,
            "level": 4,
            "z": 256,
            "y": 0,
            "x": 0,
            "channel": 0,
            "tile_size": 512,
        },
        {
            "specimen_id": "macaque_brain_rm009",
            "view": ViewType.SAGITTAL,
            "level": 4,
            "z": 0,
            "y": 0,
            "x": 224,
            "channel": 0,
            "tile_size": 512,
        },
        {
            "specimen_id": "macaque_brain_rm009",
            "view": ViewType.HORIZONTAL,
            "level": 4,
            "z": 0,
            "y": 192,
            "x": 0,
            "channel": 0,
            "tile_size": 512,
        },
        {
            "specimen_id": "macaque_brain_rm009",
            "view": ViewType.CORONAL,
            "level": 0,
            "z": 3200,
            "y": 3200,
            "x": 3200,
            "channel": 0,
            "tile_size": 512,
        },
    ]
    
    # Test the same parameters as h5py
    for pm in params[:-1]:  # Skip the last one for now
        result = read_save_ims_backend(**pm)
        if result != 0:
            return result
        print("\n" + "="*50 + "\n")
    
    return 0

if __name__ == "__main__":
    exit(main())

"""
$ docker compose exec backend dev_script/fetch_image_backend.py 
WARN[0000] /home/xyy/SIAT_CAS/visor_platform/code/cerevi/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion 
Fetching image tile using backend TileService...
Parameters: specimen=macaque_brain_rm009, view=ViewType.CORONAL, level=4, channel=0, z=256, y=0, x=0

Raw Tile Pixel Statistics (before JPEG conversion):
  Mean: 268.06
  Std:  268.57
  Min:  0.00
  Max:  1727.00
  Shape: (384, 448)
  Dtype: uint16
  Tile extraction time: 0.140 seconds
✓ Image saved successfully: /app/dev_script/image_backend_macaque_brain_rm009_ViewType.CORONAL_l4_c0_z256_y0_x0.jpg
  Image size: 17855 bytes
tile_service.get_image_info(specimen_id)
  Image dimensions: (7296, 6016, 7040)
  Available channels: ['0', '1', '2', '3']
  Resolution levels: [0, 1, 2, 3, 4, 5, 6, 7]

==================================================

Fetching image tile using backend TileService...
Parameters: specimen=macaque_brain_rm009, view=ViewType.SAGITTAL, level=4, channel=0, z=0, y=0, x=224

Raw Tile Pixel Statistics (before JPEG conversion):
  Mean: 285.13
  Std:  495.65
  Min:  0.00
  Max:  6026.00
  Shape: (384, 512)
  Dtype: uint16
  Tile extraction time: 0.079 seconds
✓ Image saved successfully: /app/dev_script/image_backend_macaque_brain_rm009_ViewType.SAGITTAL_l4_c0_z0_y0_x224.jpg
  Image size: 15193 bytes
tile_service.get_image_info(specimen_id)
  Image dimensions: (7296, 6016, 7040)
  Available channels: ['0', '1', '2', '3']
  Resolution levels: [0, 1, 2, 3, 4, 5, 6, 7]

==================================================

Fetching image tile using backend TileService...
Parameters: specimen=macaque_brain_rm009, view=ViewType.HORIZONTAL, level=4, channel=0, z=0, y=192, x=0

Raw Tile Pixel Statistics (before JPEG conversion):
  Mean: 341.03
  Std:  436.68
  Min:  0.00
  Max:  6287.00
  Shape: (512, 448)
  Dtype: uint16
  Tile extraction time: 0.090 seconds
✓ Image saved successfully: /app/dev_script/image_backend_macaque_brain_rm009_ViewType.HORIZONTAL_l4_c0_z0_y192_x0.jpg
  Image size: 16839 bytes
tile_service.get_image_info(specimen_id)
  Image dimensions: (7296, 6016, 7040)
  Available channels: ['0', '1', '2', '3']
  Resolution levels: [0, 1, 2, 3, 4, 5, 6, 7]

==================================================
"""