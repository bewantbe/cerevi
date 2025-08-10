#!/usr/bin/env python3
"""
Script to read and save image using h5py directly (no backend dependencies)
Equivalent to API call: http://localhost:8000/api/specimens/macaque_brain_rm009/image/coronal/0/0/0/0
"""

import h5py
import numpy as np
from PIL import Image
import io
from datetime import datetime
from pathlib import Path
import os
import time

def array_to_image_bytes(array, format='JPEG'):
    """Convert numpy array to image bytes (same logic as backend)"""
    
    # Normalize array to 0-255 range
    if array.dtype != np.uint8:
        # Handle different data types
        if array.dtype in [np.uint16, np.uint32]:
            # For uint16/32, scale down to uint8
            array_max = np.max(array)
            if array_max > 0:
                array = (array.astype(np.float32) / array_max * 255).astype(np.uint8)
            else:
                array = array.astype(np.uint8)
        else:
            # For float types, assume 0-1 range
            array = (np.clip(array, 0, 1) * 255).astype(np.uint8)
    
    # Create PIL Image (grayscale)
    if len(array.shape) == 2:
        image = Image.fromarray(array, mode='L')
    else:
        raise ValueError("Only 2D arrays are supported for tile generation")
    
    # Convert to bytes
    buffer = io.BytesIO()
    
    if format == 'JPEG':
        # High quality JPEG for image data
        image.save(buffer, format='JPEG', quality=85, optimize=True)
    elif format == 'PNG':
        # Lossless PNG
        image.save(buffer, format='PNG', optimize=True)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    return buffer.getvalue()

def read_save_ims(specimen_id, view, level, channel, z, y, x, tile_size):
    print(f"Fetching image tile using h5py directly...")
    print(f"Parameters: specimen={specimen_id}, view={view}, level={level}, channel={channel}, z={z}, y={y}, x={x}")
    
    # Construct file path based on backend config logic
    data_path = Path(os.getenv("DATA_PATH", "data"))
    image_path = data_path / "specimens" / specimen_id / "image.ims"
    
    print(f"Image file path: {image_path}")
    
    if not image_path.exists():
        print(f"Error: Image file not found at {image_path}")
        return 1
    
    # Open HDF5 file
    with h5py.File(image_path, 'r') as h5_file:
        start_time = time.time()
        
        # Construct dataset path
        dataset_path = f'DataSet/ResolutionLevel {level}/TimePoint 0/Channel {channel}/Data'
        print(f"Dataset path: {dataset_path}")
        
        if dataset_path not in h5_file:
            print(f"Error: Dataset not found at {dataset_path}")
            print(f"Available datasets:")
            def print_structure(name, obj):
                print(f"  {name}")
            h5_file.visititems(print_structure)
            return 1
        
        dataset = h5_file[dataset_path]
        
        # Ensure we have a dataset (not a group)
        if not isinstance(dataset, h5py.Dataset):
            print(f"Error: {dataset_path} is not a dataset")
            return 1
        
        data_shape = dataset.shape  # (z, y, x)
        print(f"Dataset shape: {data_shape} (z, y, x)")
        print(f"Dataset dtype: {dataset.dtype}")
        
        pivot_zyx = (z, y, z)
        for i in range(3):
            if pivot_zyx[i] < 0 or pivot_zyx[i] >= data_shape[i]:
                print(f"Error: Slice index {pivot_zyx[i]} out of bounds for dimension {i} with size {data_shape[i]}")
                return 1

        # Extract slice based on view type
        # zero-padding should be also in this step
        #             horizontal  vertical
        # coronal:    -x          -y
        # sagittal:    z          -y
        # horizontal: -x          -z
        if view == "coronal":
            rg_horizontal = slice(x, x + tile_size)  # -x
            rg_vertical   = slice(y, y + tile_size)  # -y
            tile = dataset[z, rg_vertical, rg_horizontal][::-1, ::-1]
        elif view == "sagittal":
            rg_horizontal = slice(z, z + tile_size)  #  z
            rg_vertical   = slice(y, y + tile_size)  # -y
            tile = dataset[rg_horizontal, rg_vertical, x][:, ::-1].T
        elif view == "horizontal":
            rg_horizontal = slice(x, x + tile_size)  # -x
            rg_vertical   = slice(z, z + tile_size)  # -z
            tile = dataset[rg_vertical, y, rg_horizontal][::-1, ::-1]
        else:
            print(f"Error: Unknown view type: {view}")
            return 1
        
        print(f"Tile shape: {tile.shape}")
        if tile.shape != (tile_size, tile_size):
            print(f"WARNING: dimension mismatch, tile_size = {tile_size}.")
        
        elapsed_time = time.time() - start_time
        print(f"Tile generation time: {elapsed_time:.3f} seconds")
        
        # Calculate and display pixel statistics
        print(f"\nPixel Statistics:")
        print(f"  Mean: {np.mean(tile):.2f}")
        print(f"  Std:  {np.std(tile):.2f}")
        print(f"  Min:  {np.min(tile):.2f}")
        print(f"  Max:  {np.max(tile):.2f}")

        # extra flip for conventional vertical axis direction when saving to file
        tile_f = tile[::-1, :]
        # save image
        image_bytes = array_to_image_bytes(tile_f, format='JPEG')  
        output_path = Path(__file__).parent / f"image_h5py_{specimen_id}_{view}_l{level}_c{channel}_z{z}_y{y}_x{x}.jpg"
        with open(output_path, 'wb') as f:
            f.write(image_bytes)
        print(f"Image saved successfully: {output_path}")
        print(f"Image size: {len(image_bytes)} bytes")
        
def main():
    """Generate and save image tile using h5py directly"""
    
    # Parameters matching the API endpoint

    params = [
        {
            "specimen_id": "macaque_brain_rm009",
            "view": "coronal",
            "level": 4,
            "z": 256,
            "y": 0,
            "x": 0,
            "channel": 0,
            "tile_size": 512,
        },
        {
            "specimen_id": "macaque_brain_rm009",
            "view": "sagittal",
            "level": 4,
            "z": 0,
            "y": 0,
            "x": 224,
            "channel": 0,
            "tile_size": 512,
        },
        {
            "specimen_id": "macaque_brain_rm009",
            "view": "horizontal",
            "level": 4,
            "z": 0,
            "y": 192,
            "x": 0,
            "channel": 0,
            "tile_size": 512,
        },
        {
            "specimen_id": "macaque_brain_rm009",
            "view": "coronal",
            "level": 0,
            "z": 3200,
            "y": 3200,
            "x": 3200,
            "channel": 0,
            "tile_size": 512,
        },
    ]
    
    #read_save_ims(**params[3])

    for pm in params[:-1]:
        read_save_ims(**pm)

    return 0

if __name__ == "__main__":
    exit(main())
