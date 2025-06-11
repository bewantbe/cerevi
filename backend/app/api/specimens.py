"""
API endpoints for specimens
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from ..models.specimen import SpecimenMetadata
from ..config import get_specimen_config, get_all_specimens

router = APIRouter()

@router.get("/specimens", response_model=List[SpecimenMetadata])
async def list_specimens():
    """Get list of all available specimens"""
    try:
        specimens = get_all_specimens()
        return [SpecimenMetadata(**specimen) for specimen in specimens]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get specimens: {str(e)}")

@router.get("/specimens/{specimen_id}", response_model=SpecimenMetadata)
async def get_specimen(specimen_id: str):
    """Get details for a specific specimen"""
    specimen_config = get_specimen_config(specimen_id)
    
    if not specimen_config:
        raise HTTPException(status_code=404, detail=f"Specimen {specimen_id} not found")
    
    try:
        return SpecimenMetadata(**specimen_config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get specimen: {str(e)}")

@router.get("/specimens/{specimen_id}/config")
async def get_specimen_config_endpoint(specimen_id: str):
    """Get configuration for a specific specimen"""
    specimen_config = get_specimen_config(specimen_id)
    
    if not specimen_config:
        raise HTTPException(status_code=404, detail=f"Specimen {specimen_id} not found")
    
    return specimen_config
