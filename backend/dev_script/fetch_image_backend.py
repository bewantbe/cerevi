#!/usr/bin/env python3
"""
Script to read and save image using backend facilities (TileService)
Equivalent to API call: http://localhost:8000/api/specimens/macaque_brain_rm009/image/coronal/0/0/0/0
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

def main():
    """Generate and save image tile using backend TileService"""
    
    # Parameters matching the API endpoint
    specimen_id = "macaque_brain_rm009"
    view = ViewType.CORONAL
    level = 0
    z = 3200  # slice index
    x = 3200  # tile x coordinate
    y = 3200  # tile y coordinate
    channel = 0  # default channel
    
    print(f"Fetching image tile using backend TileService...")
    print(f"Parameters: specimen={specimen_id}, view={view}, level={level}, z={z}, x={x}, y={y}, channel={channel}")
    
    try:
        # Initialize tile service
        tile_service = TileService()
        
        # Generate image tile (same as API endpoint)
        start_time = time.time()
        image_bytes = tile_service.generate_image_tile(
            specimen_id=specimen_id,
            view=view,
            level=level,
            channel=channel,
            z=z,
            x=x,
            y=y
        )
        elapsed_time = time.time() - start_time
        print(f"  Tile generation time: {elapsed_time:.3f} seconds")
        
        # Save to file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(__file__).parent / f"image_backend_{timestamp}.jpg"
        
        with open(output_path, 'wb') as f:
            f.write(image_bytes)
        
        print(f"✓ Image saved successfully: {output_path}")
        print(f"  Image size: {len(image_bytes)} bytes")
        
        # Calculate and display pixel statistics
        # Read the saved image back to analyze pixel values
        from PIL import Image
        import numpy as np
        
        saved_image = Image.open(output_path)
        image_array = np.array(saved_image)
        
        print(f"\nPixel Statistics:")
        print(f"  Mean: {np.mean(image_array):.2f}")
        print(f"  Std:  {np.std(image_array):.2f}")
        print(f"  Min:  {np.min(image_array):.2f}")
        print(f"  Max:  {np.max(image_array):.2f}")
        
        # Display image info
        image_info = tile_service.get_image_info(specimen_id)
        print(f"tile_service.get_image_info(specimen_id)")
        print(f"  Image dimensions: {image_info['dimensions']}")
        print(f"  Available channels: {list(image_info['channels'].keys())}")
        print(f"  Resolution levels: {image_info['resolution_levels']}")
        
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        print("  Make sure the image file exists at the expected location.")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
