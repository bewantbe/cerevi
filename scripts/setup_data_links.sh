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
IMAGE_TARGET="$PROJECT_ROOT/data/macaque_brain_RM009/image.ims"
ATLAS_TARGET="$PROJECT_ROOT/data/macaque_brain_RM009/atlas.ims"
MODEL_TARGET="$PROJECT_ROOT/data/macaque_brain_RM009/brain_shell.obj"
REGION_TARGET="$PROJECT_ROOT/data/macaque_brain_dMRI_atlas_CIVM/macaque_brain_regions.xlsx"
README_TARGET="$PROJECT_ROOT/data/macaque_brain_RM009/readme"
COPYRIGHT_TARGET="$PROJECT_ROOT/data/macaque_brain_dMRI_atlas_CIVM/copyright"

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

# Function to create text file
create_text_file() {
    local target=$1
    local content=$2
    local description=$3
    
    echo "Creating $description..."
    
    # Remove existing file if it exists
    if [ -f "$target" ]; then
        echo "Removing existing file: $target"
        rm -f "$target"
    fi
    
    # Create the file
    echo "$content" > "$target"
    echo "✓ Created file: $target"
    
    return 0
}

# Create data directories
echo "Creating data directories..."
mkdir -p "$(dirname "$IMAGE_TARGET")"
mkdir -p "$(dirname "$ATLAS_TARGET")"
mkdir -p "$(dirname "$MODEL_TARGET")"
mkdir -p "$(dirname "$REGION_TARGET")"

# Define file contents
README_CONTENT="Macaque Brain RM009 Dataset

This directory contains high-resolution brain imaging data from specimen RM009:

Files:
- image.ims: Multi-resolution brain image data (4 channels: 405nm, 488nm, 561nm, 640nm)
- atlas.ims: Brain region atlas/mask data aligned with image data
- brain_shell.obj: 3D brain shell surface model

Specimen Information:
- Species: Macaca mulatta (Rhesus macaque)
- Specimen ID: RM009
- Imaging Method: VISoR (Volumetric Imaging with Synchronized on-the-fly-scan and Readout)
- Resolution: ~10μm per pixel at level 0
- Coordinate System: Right-handed (z, y, x) order

For more information about VISoR technology, see:
https://academic.oup.com/nsr/article/6/5/982/5475673"

COPYRIGHT_CONTENT="Paper: A diffusion tensor MRI atlas of the postmortem rhesus macaque brain

Highlights
    • We present a high-resolution DTI/MRI atlas of 10 postmortem rhesus macaque brains.
    • The atlas includes 3D segmentations of 241 brain regions, and 42 tracts.
    • We analyze morphometric variation and cortical thickness across the atlas group.

Cite:
Calabrese, Evan, Alexandra Badea, Christopher L. Coe, Gabriele R. Lubach, Yundi Shi, Martin A. Styner, and G. Allan Johnson. \"A Diffusion Tensor MRI Atlas of the Postmortem Rhesus Macaque Brain.\" NeuroImage 117 (August 15, 2015): 408–16. https://doi.org/10.1016/j.neuroimage.2015.05.072.

Data downloaded from:
http://www.civm.duhs.duke.edu/rhesusatlas/

Use of CIVM Data:

    CIVM makes many types of data acquired for published and yet unpublished studies available through our CIVM VoxPort application. Use of VoxPort is free. Registration is required. Register for VoxPort access now. A new browser window or tab will open.

    Data downloaded from this site is for academic use only. If you use this data in a publication please send us a request for copyright permission and appropriate acknowledgements. We ask that you provide contact information, and agree to give credit to the Duke Center for In Vivo Microscopy for any written or oral presentation using data from this site. Licenses can be granted for commercial use. Contact the Center for permission.

    Please use the following acknowledgement: Imaging data provided by the Duke Center for In Vivo Microscopy NIH/NIBIB (P41 EB015897)."

# Create symbolic links
echo ""
create_link "$IMAGE_SOURCE" "$IMAGE_TARGET" "image data link"
create_link "$ATLAS_SOURCE" "$ATLAS_TARGET" "atlas data link"
create_link "$MODEL_SOURCE" "$MODEL_TARGET" "3D model link"
create_link "$REGION_SOURCE" "$REGION_TARGET" "region hierarchy link"

# Create text files
echo ""
create_text_file "$README_TARGET" "$README_CONTENT" "specimen readme file"
create_text_file "$COPYRIGHT_TARGET" "$COPYRIGHT_CONTENT" "atlas copyright file"

echo ""
echo "Data setup completed!"
echo ""
echo "Verifying new data structure:"
echo "RM009 specimen data:"
ls -la "$PROJECT_ROOT/data/macaque_brain_RM009/"
echo ""
echo "CIVM atlas data:"
ls -la "$PROJECT_ROOT/data/macaque_brain_dMRI_atlas_CIVM/"

echo ""
echo "Next steps:"
echo "1. Run: python scripts/convert_regions.py"
echo "2. Run: docker-compose up -d"
