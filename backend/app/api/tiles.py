"""
API endpoints for image tiles
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import Response
import logging

from ..models.specimen import ViewType
from ..services.tile_service import TileService
from ..config import get_specimen_config

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize tile service
tile_service = TileService()

@router.get("/specimens/{specimen_id}/image/{view}/{level}/{z}/{x}/{y}")
async def get_image_tile(
    specimen_id: str = Path(..., description="Specimen ID"),
    view: ViewType = Path(..., description="View type (sagittal, coronal, horizontal)"),
    level: int = Path(..., ge=0, le=7, description="Resolution level (0-7)"),
    z: int = Path(..., ge=0, description="Slice index"),
    x: int = Path(..., ge=0, description="Tile X coordinate"),
    y: int = Path(..., ge=0, description="Tile Y coordinate"),
    channel: Optional[int] = Query(0, ge=0, le=3, description="Channel (0-3)"),
    tile_size: Optional[int] = Query(None, ge=64, le=2048, description="Tile size")
):
    """Get image tile for specified coordinates and parameters"""
    
    # Verify specimen exists
    if not get_specimen_config(specimen_id):
        raise HTTPException(status_code=404, detail=f"Specimen {specimen_id} not found")
    
    try:
        # Generate tile
        tile_bytes = tile_service.generate_image_tile(
            specimen_id=specimen_id,
            view=view,
            level=level,
            channel=channel,
            z=z,
            x=x,
            y=y,
            tile_size=tile_size
        )
        
        # Return image response
        return Response(
            content=tile_bytes,
            media_type="image/jpeg",
            headers={
                "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                "X-Tile-Info": f"{specimen_id}/{view}/{level}/{z}/{x}/{y}/ch{channel}"
            }
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate image tile: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate tile")

@router.get("/specimens/{specimen_id}/atlas/{view}/{level}/{z}/{x}/{y}")
async def get_atlas_tile(
    specimen_id: str = Path(..., description="Specimen ID"),
    view: ViewType = Path(..., description="View type (sagittal, coronal, horizontal)"),
    level: int = Path(..., ge=0, le=7, description="Resolution level (0-7)"),
    z: int = Path(..., ge=0, description="Slice index"),
    x: int = Path(..., ge=0, description="Tile X coordinate"),
    y: int = Path(..., ge=0, description="Tile Y coordinate"),
    tile_size: Optional[int] = Query(None, ge=64, le=2048, description="Tile size")
):
    """Get atlas mask tile for specified coordinates"""
    
    # Verify specimen exists
    if not get_specimen_config(specimen_id):
        raise HTTPException(status_code=404, detail=f"Specimen {specimen_id} not found")
    
    try:
        # Generate atlas tile
        tile_bytes = tile_service.generate_atlas_tile(
            specimen_id=specimen_id,
            view=view,
            level=level,
            z=z,
            x=x,
            y=y,
            tile_size=tile_size
        )
        
        # Return PNG response (lossless for atlas data)
        return Response(
            content=tile_bytes,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                "X-Atlas-Info": f"{specimen_id}/{view}/{level}/{z}/{x}/{y}"
            }
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate atlas tile: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate atlas tile")

@router.get("/specimens/{specimen_id}/tile-grid/{view}/{level}")
async def get_tile_grid_info(
    specimen_id: str = Path(..., description="Specimen ID"),
    view: ViewType = Path(..., description="View type"),
    level: int = Path(..., ge=0, le=7, description="Resolution level")
):
    """Get tile grid information for a specific view and level"""
    
    # Verify specimen exists
    if not get_specimen_config(specimen_id):
        raise HTTPException(status_code=404, detail=f"Specimen {specimen_id} not found")
    
    try:
        grid_info = tile_service.calculate_tile_grid(specimen_id, view, level)
        return grid_info
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get tile grid info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tile grid information")
