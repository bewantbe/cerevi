#!/bin/bash

# VISoR Platform Data Setup Script
# Creates symbolic links to the actual data files

set -e

echo "Setting up VISoR Platform data links..."

# Define source paths
IMAGE_SOURCE="/share/data/VISoR_Reconstruction/SIAT_SIAT/BiGuoqiang/Macaque_Brain/RM009_2/z00000_c1_1.ims"
ATLAS_SOURCE="/share/data/VISoR_Reconstruction/SIAT_SIAT/BiGuoqiang/Macaque_Brain/RM009_2/V1_layers/z00000_c1_mask.ims"
MODEL_SOURCE="/home/xyy/SIAT_CAS/xu/tracing/swc_collect/RM009/mesh/root/1.obj"
REGION_SOURCE="/home/xyy/SIAT_CAS/xu/tracing/swc_collect/RM009/mesh/NIHMS696288-supplement-4.xlsx"

# Define target paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_TARGET="$PROJECT_ROOT/data/specimens/macaque_brain_rm009/image.ims"
ATLAS_TARGET="$PROJECT_ROOT/data/specimens/macaque_brain_rm009/atlas.ims"
MODEL_TARGET="$PROJECT_ROOT/data/models/macaque_brain_rm009/brain_shell.obj"
REGION_TARGET="$PROJECT_ROOT/data/regions/macaque_brain_regions.xlsx"

# Function to create symbolic link safely
create_link() {
    local source=$1
    local target=$2
    local description=$3
    
    echo "Setting up $description..."
    
    # Check if source exists
    if [ ! -f "$source" ]; then
        echo "Warning: Source file not found: $source"
        echo "Skipping $description"
        return 1
    fi
    
    # Remove existing link/file if it exists
    if [ -L "$target" ] || [ -f "$target" ]; then
        echo "Removing existing file/link: $target"
        rm -f "$target"
    fi
    
    # Create the symbolic link
    ln -s "$source" "$target"
    echo "✓ Created link: $target -> $source"
    
    return 0
}

# Create data directories
echo "Creating data directories..."
mkdir -p "$(dirname "$IMAGE_TARGET")"
mkdir -p "$(dirname "$ATLAS_TARGET")"
mkdir -p "$(dirname "$MODEL_TARGET")"
mkdir -p "$(dirname "$REGION_TARGET")"

# Create symbolic links
echo ""
create_link "$IMAGE_SOURCE" "$IMAGE_TARGET" "image data link"
create_link "$ATLAS_SOURCE" "$ATLAS_TARGET" "atlas data link"
create_link "$MODEL_SOURCE" "$MODEL_TARGET" "3D model link"
create_link "$REGION_SOURCE" "$REGION_TARGET" "region hierarchy link"

echo ""
echo "Data setup completed!"
echo ""
echo "Verifying links:"
ls -la "$PROJECT_ROOT/data/specimens/macaque_brain_rm009/"
ls -la "$PROJECT_ROOT/data/models/macaque_brain_rm009/"
ls -la "$PROJECT_ROOT/data/regions/"

echo ""
echo "Next steps:"
echo "1. Run: python scripts/convert_regions.py"
echo "2. Run: docker-compose up -d"
