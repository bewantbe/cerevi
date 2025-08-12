# Roadmap for Cerevi Development

## Completed Tasks

* Revise README.md. - done
* Finish backend/tests, mostly done.
* add API tests for images - done.
* add API tests for atlas - done.
* improve doc of BACKEND_DEVELOPMENT.md
  - make descriptioin of API more complete - cancelled, leave it to code comments.
  - make the backend_development.md more concise - done
* Check code
  - https://vscode.dev/github/bewantbe/cerevi/blob/main/.env#L10-L15
  - done
* change code
  - ./scripts/start_services.sh
  - make it rebuild when asked, not always rebuild.
  - done. use docker-compose to start the services.
* Fixed image tile API - done
  - Check the returned image is not completely black.
  - tests - done
* rename 'generate' to 'extract' for these functions:
  generate_atlas_tile, generate_image_tile
  - done
* imaris_handler.py: class ImarisHandler, change the programing style to RAAI. Also change related calling code.
  - done
* enable backend py scripts hot-reload in development.
  - done
* make docker read and writes data for mounted path use a predefined UID and GID.
  - done
* ✓ "axes_order": "z_y_x" -> "zyx" (COMPLETED)
* add speed benchmark script that test throughtput of image tile API, may include serial mode and parallel mode.
  - done
* Find the true reason of tile image API performance issue.
  - done
  - It is due to python GIL and hdf5 reading need libz to decompress.
  - add --workers 8 to fix it.
  - future: need to redesign API to have a much better performance.
* restructure the data dir.
  - d

## TODO

* tiles.py: get_image_tile(), get_atlas_tile() has parameter order z,y,x instead of z,x,y now. and API definition changed also. Now we need to fix frontend code accordingly.

* fix frontend openseadragon code.

* Check the API tests
    Too complecated, remove the asserts or tests that are not essential.
    Is `TestSpecimenEndpointsCoverage` a bit redundant?

## possible future tasks

### general
* improve documentation

### frontend
* make it usable
* design UI/UX

### backend
* more test of functionality
* more test of backend
* more performance benchmark

### data
* prepare more data
* add more data

### restructure directory structure

Analysis the backend code and restructure the data directory.

Origin(By data type):

    data/
    ├── specimens/
    │   └── macaque_brain_rm009/
    │       ├── image.ims          # Main multi-resolution brain image data
    │       └── atlas.ims          # Brain region atlas/mask data
    ├── models/
    │   └── macaque_brain_rm009/
    │       └── brain_shell.obj    # 3D brain shell model
    └── regions/
        ├── macaque_brain_regions.json   # Processed region hierarchy (JSON)
        └── macaque_brain_regions.xlsx   # Source region data (Excel)

New (group information from the same source together):

    data/
    ├── macaque_brain_RM009/
    │   ├── image.ims          # Main multi-resolution brain image data
    │   ├── atlas.ims          # Brain region atlas/mask data
    │   └── brain_shell.obj    # 3D brain shell model
    └── macaque_brain_dMRI_atlas_CIVM/
        ├── macaque_brain_regions.json   # Processed region hierarchy (JSON)
        ├── macaque_brain_regions.xlsx   # Source region data (Excel)
        └── copyright
    
    Context of the copyright:
    ```
    Paper: A diffusion tensor MRI atlas of the postmortem rhesus macaque brain

    Highlights
        • We present a high-resolution DTI/MRI atlas of 10 postmortem rhesus macaque brains.
        • The atlas includes 3D segmentations of 241 brain regions, and 42 tracts.
        • We analyze morphometric variation and cortical thickness across the atlas group.

    Cite:
    Calabrese, Evan, Alexandra Badea, Christopher L. Coe, Gabriele R. Lubach, Yundi Shi, Martin A. Styner, and G. Allan Johnson. “A Diffusion Tensor MRI Atlas of the Postmortem Rhesus Macaque Brain.” NeuroImage 117 (August 15, 2015): 408–16. https://doi.org/10.1016/j.neuroimage.2015.05.072.

    Data downloaded from:
    http://www.civm.duhs.duke.edu/rhesusatlas/

    Use of CIVM Data:

        CIVM makes many types of data acquired for published and yet unpublished studies available through our CIVM VoxPort application. Use of VoxPort is free. Registration is required. Register for VoxPort access now. A new browser window or tab will open.

        Data downloaded from this site is for academic use only. If you use this data in a publication please send us a request for copyright permission and appropriate acknowledgements. We ask that you provide contact information, and agree to give credit to the Duke Center for In Vivo Microscopy for any written or oral presentation using data from this site. Licenses can be granted for commercial use. Contact the Center for permission.

        Please use the following acknowledgement: Imaging data provided by the Duke Center for In Vivo Microscopy NIH/NIBIB (P41 EB015897).
    ```


Need to change:
  * code that generates data links
    - e.g. 'scripts/convert_regions.py', './scripts/setup_data_links.sh'
  * code that loads these data, mostly in backend.
  * documentation


* upgrade Python v11 to v13 for speed
* upgrade Node.js v18 to v22 (e.g. v22.18.0 (LTS))
