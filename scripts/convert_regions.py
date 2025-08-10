#!/usr/bin/env python3
"""
Convert region hierarchy from XLSX to JSON format
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import os

def convert_xlsx_to_json(xlsx_path: str, output_path: str) -> None:
    """
    Convert XLSX region hierarchy to structured JSON format
    """
    print(f"Converting {xlsx_path} to {output_path}")
    
    # Check if source file exists
    if not os.path.exists(xlsx_path):
        print(f"Warning: Source file not found: {xlsx_path}")
        print("Creating mock region data instead...")
        create_mock_region_data(output_path)
        return
    
    # Read the Excel file
    try:
        df = pd.read_excel(xlsx_path)
        print(f"Read {len(df)} regions from Excel file")
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        print("Creating mock region data instead...")
        create_mock_region_data(output_path)
        return
    
    # Convert to structured format
    regions = []
    hierarchy = {}
    
    for index, row in df.iterrows():
        # Extract region data
        region = {
            "id": int(row.get('Value', index + 1)),
            "name": str(row.get('Structure', f'Region_{index + 1}')),
            "abbreviation": str(row.get('Abbreviation', '')),
            "level1": str(row.get('Level 1', '')),
            "level2": str(row.get('Level 2', '')),
            "level3": str(row.get('Level 3', '')),
            "level4": str(row.get('Level 4', '')),
            "value": int(row.get('Value', index + 1)),
            "parent_id": None,  # Will be computed based on hierarchy
            "children": []
        }
        regions.append(region)
        
        # Build hierarchy structure
        level1 = region['level1']
        level2 = region['level2']
        level3 = region['level3']
        level4 = region['level4']
        
        if level1 and level1 not in hierarchy:
            hierarchy[level1] = {}
        
        if level2 and level1:
            if level2 not in hierarchy[level1]:
                hierarchy[level1][level2] = {}
            
            if level3:
                if level3 not in hierarchy[level1][level2]:
                    hierarchy[level1][level2][level3] = []
                
                if level4 and level4 not in hierarchy[level1][level2][level3]:
                    hierarchy[level1][level2][level3].append(level4)
    
    # Create the final JSON structure
    output_data = {
        "metadata": {
            "source": xlsx_path,
            "total_regions": len(regions),
            "conversion_date": pd.Timestamp.now().isoformat(),
            "coordinate_system": "right_handed",
            "axes_order": "zyx"
        },
        "regions": regions,
        "hierarchy": hierarchy,
        "region_lookup": {str(r["value"]): r for r in regions}
    }
    
    # Write to JSON file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Successfully converted {len(regions)} regions to {output_path}")

def create_mock_region_data(output_path: str) -> None:
    """
    Create mock region data for development/testing
    """
    print("Creating mock region hierarchy data...")
    
    mock_regions = [
        {
            "id": 1,
            "name": "ventricles",
            "abbreviation": "LV",
            "level1": "ventricles",
            "level2": "ventricles",
            "level3": "ventricles", 
            "level4": "ventricles",
            "value": 1,
            "parent_id": None,
            "children": []
        },
        {
            "id": 2,
            "name": "medulla",
            "abbreviation": "Md",
            "level1": "hindbrain",
            "level2": "myelencephalon",
            "level3": "medulla",
            "level4": "medulla",
            "value": 2,
            "parent_id": None,
            "children": []
        },
        {
            "id": 3,
            "name": "pons",
            "abbreviation": "Pn",
            "level1": "hindbrain",
            "level2": "metencephalon",
            "level3": "pons",
            "level4": "pons",
            "value": 3,
            "parent_id": None,
            "children": []
        },
        {
            "id": 4,
            "name": "cerebellum",
            "abbreviation": "Cb",
            "level1": "hindbrain",
            "level2": "metencephalon",
            "level3": "cerebellum",
            "level4": "cerebellum",
            "value": 4,
            "parent_id": None,
            "children": []
        },
        {
            "id": 5,
            "name": "midbrain",
            "abbreviation": "MB",
            "level1": "midbrain",
            "level2": "midbrain",
            "level3": "midbrain",
            "level4": "midbrain",
            "value": 5,
            "parent_id": None,
            "children": []
        },
        {
            "id": 6,
            "name": "anterior pulvinar",
            "abbreviation": "Apul",
            "level1": "forebrain",
            "level2": "diencephalon",
            "level3": "p2",
            "level4": "thalamus",
            "value": 6,
            "parent_id": None,
            "children": []
        }
    ]
    
    mock_hierarchy = {
        "ventricles": ["ventricles"],
        "hindbrain": {
            "myelencephalon": ["medulla"],
            "metencephalon": ["pons", "cerebellum"]
        },
        "midbrain": ["midbrain"],
        "forebrain": {
            "diencephalon": {
                "p2": ["thalamus"]
            }
        }
    }
    
    output_data = {
        "metadata": {
            "source": "mock_data",
            "total_regions": len(mock_regions),
            "conversion_date": pd.Timestamp.now().isoformat(),
            "coordinate_system": "right_handed",
            "axes_order": "zyx"
        },
        "regions": mock_regions,
        "hierarchy": mock_hierarchy,
        "region_lookup": {str(r["value"]): r for r in mock_regions}
    }
    
    # Write to JSON file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created mock region data: {output_path}")

def main():
    """Main conversion function"""
    project_root = Path(__file__).parent.parent
    
    # Input and output paths
    xlsx_path = project_root / "data" / "regions" / "macaque_brain_regions.xlsx"
    json_path = project_root / "data" / "regions" / "macaque_brain_regions.json"
    
    print("VISoR Platform - Region Hierarchy Conversion")
    print("=" * 50)
    
    convert_xlsx_to_json(str(xlsx_path), str(json_path))
    
    print("\nConversion completed!")
    print(f"Output file: {json_path}")

if __name__ == "__main__":
    main()
