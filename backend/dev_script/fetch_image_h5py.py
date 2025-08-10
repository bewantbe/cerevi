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
    print(f"\n##### Fetching image tile using h5py directly #####")
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
        print(f"Pixel Statistics (raw pixel value):")
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

        img_jpg = Image.open(io.BytesIO(image_bytes))
        print(f"Pixel Statistics (after normalization and decode):")
        print(f"  Mean: {np.mean(np.array(img_jpg)):.2f}")
        print(f"  Std:  {np.std(np.array(img_jpg)):.2f}")
        print(f"  Min:  {np.min(np.array(img_jpg)):.2f}")
        print(f"  Max:  {np.max(np.array(img_jpg)):.2f}")
        
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

    for pm in params:
        read_save_ims(**pm)

    return 0

if __name__ == "__main__":
    exit(main())

"""
$ docker-compose exec backend python dev_script/fetch_image_h5py.py

##### Fetching image tile using h5py directly #####
Parameters: specimen=macaque_brain_rm009, view=coronal, level=4, channel=0, z=256, y=0, x=0
Image file path: /app/data/specimens/macaque_brain_rm009/image.ims
Dataset path: DataSet/ResolutionLevel 4/TimePoint 0/Channel 0/Data
Dataset shape: (512, 384, 448) (z, y, x)
Dataset dtype: uint16
Tile shape: (384, 448)
WARNING: dimension mismatch, tile_size = 512.
Tile generation time: 0.153 seconds
Pixel Statistics (raw pixel value):
  Mean: 268.06
  Std:  268.57
  Min:  0.00
  Max:  1727.00
Image saved successfully: /app/dev_script/image_h5py_macaque_brain_rm009_coronal_l4_c0_z256_y0_x0.jpg
Image size: 17855 bytes
Pixel Statistics (after normalization and decode):
  Mean: 39.27
  Std:  39.47
  Min:  0.00
  Max:  255.00

##### Fetching image tile using h5py directly #####
Parameters: specimen=macaque_brain_rm009, view=sagittal, level=4, channel=0, z=0, y=0, x=224
Image file path: /app/data/specimens/macaque_brain_rm009/image.ims
Dataset path: DataSet/ResolutionLevel 4/TimePoint 0/Channel 0/Data
Dataset shape: (512, 384, 448) (z, y, x)
Dataset dtype: uint16
Tile shape: (384, 512)
WARNING: dimension mismatch, tile_size = 512.
Tile generation time: 0.077 seconds
Pixel Statistics (raw pixel value):
  Mean: 285.13
  Std:  495.65
  Min:  0.00
  Max:  6026.00
Image saved successfully: /app/dev_script/image_h5py_macaque_brain_rm009_sagittal_l4_c0_z0_y0_x224.jpg
Image size: 15193 bytes
Pixel Statistics (after normalization and decode):
  Mean: 11.79
  Std:  20.88
  Min:  0.00
  Max:  255.00

##### Fetching image tile using h5py directly #####
Parameters: specimen=macaque_brain_rm009, view=horizontal, level=4, channel=0, z=0, y=192, x=0
Image file path: /app/data/specimens/macaque_brain_rm009/image.ims
Dataset path: DataSet/ResolutionLevel 4/TimePoint 0/Channel 0/Data
Dataset shape: (512, 384, 448) (z, y, x)
Dataset dtype: uint16
Tile shape: (512, 448)
WARNING: dimension mismatch, tile_size = 512.
Tile generation time: 0.095 seconds
Pixel Statistics (raw pixel value):
  Mean: 341.03
  Std:  436.68
  Min:  0.00
  Max:  6287.00
Image saved successfully: /app/dev_script/image_h5py_macaque_brain_rm009_horizontal_l4_c0_z0_y192_x0.jpg
Image size: 16839 bytes
Pixel Statistics (after normalization and decode):
  Mean: 13.52
  Std:  17.57
  Min:  0.00
  Max:  255.00

##### Fetching image tile using h5py directly #####
Parameters: specimen=macaque_brain_rm009, view=coronal, level=0, channel=0, z=3200, y=3200, x=3200
Image file path: /app/data/specimens/macaque_brain_rm009/image.ims
Dataset path: DataSet/ResolutionLevel 0/TimePoint 0/Channel 0/Data
Dataset shape: (7296, 6016, 7040) (z, y, x)
Dataset dtype: uint16
Tile shape: (512, 512)
Tile generation time: 0.339 seconds
Pixel Statistics (raw pixel value):
"""