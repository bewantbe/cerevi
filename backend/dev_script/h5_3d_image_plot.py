#show image plane

# Usage example:
# python dev_script/h5_3d_image_plot.py --img-path "/media/xyy/Extreme SSD/data/macaque_brain_rm009/atlas.ims" \
# --level 3 --channel 0 --zyx 100,100,100 --pixel-normalize-mode index --interactive

import sys
import time
from pathlib import Path
import argparse
import pprint

import h5py
import numpy as np
_a = lambda a: np.array(a)
import matplotlib as mpl
import matplotlib.pyplot as plt

debug_level = 5

tic = lambda: time.clock_gettime(time.CLOCK_MONOTONIC)
_t00_ = tic()
toc = lambda: time.clock_gettime(time.CLOCK_MONOTONIC) - _t00_

# copy from utils.py
def dbg_print(level, *p, **keys):
    """
    Used for printing error and debugging information.
    Controlled by global (module) debug_level.
    Higher debug_level will show more information.
        debug_level == 0: show nothing.
        debug_level == 1: show only error.
        debug_level == 2: show warning.
        debug_level == 3: show hint.
        debug_level == 4: show message.
        debug_level == 5: most verbose.
    """
    if level > debug_level:
        return
    level_str = {1:'Error  ', 2:'Warning', 3:'Hint   ', 4:'Message', 5:'Verbose'}
    print('%7.3fs'%(toc()), level_str[level] + ':', *p, **keys)

# modified from data_loader.py
#@functools.cache
def open_ims_meta(ims_path):
    ims = h5py.File(ims_path, 'r')
    # convert metadata in IMS to python dict
    metadata = {}
    if 'DataSetInfo' in ims:
        img_info = ims['DataSetInfo']
        for it in img_info.keys():
            metadata[it] = \
                {k:''.join([c.decode('utf-8') for c in v])
                    for k, v in img_info[it].attrs.items()}

    dbg_print(4, '  Done loading meta data')
    return ims, metadata

class Indexer:
    def __init__(self, img_h5):
        self.img_h5 = img_h5

    @property
    def shape(self):
        im = self.img_h5['DataSet']
        n_level     = len(im)
        im_r = im.get('ResolutionLevel 0', {})
        n_timepoint = len(im_r)
        im_t = im_r.get('TimePoint 0', {})
        n_channel   = len(im_t)
        return n_level, n_timepoint, n_channel

    def __getitem__(self, idx):
        level, time_point, channel = idx
        img_arr = self.img_h5['DataSet'] \
                    ['ResolutionLevel %d'%(level)] \
                    ['TimePoint %d'%(time_point)] \
                    ['Channel %d'%(channel)]['Data']
        return img_arr


def f_contrast(im, i_min, i_max, fn = None):
    # fn map [0, 1] to [0, 1]
    if fn is None:
        fn = lambda x: x
    return fn(np.clip((np.float32(im)-i_min)/(i_max-i_min), 0, 1))

def normalize_image_pixels(img_sliver_z, img_sliver_y, img_sliver_x,
                           normalize_mode):
    if normalize_mode == 'auto_intensity':
        # auto contrast (avoid reading whole 3D image)
        img_3quadrant = [img_sliver_z, img_sliver_y, img_sliver_x]
        img_3flat = np.concatenate(list(map(lambda x:np.ravel(x), img_3quadrant)))
        print('n_pixel =', len(img_3flat))
        val_0 = 100
        q99 = np.quantile(img_3flat, 0.999)
        dbg_print(4, f'pixel bounds = {val_0}, {q99}')
        img_sliver_z = f_contrast(img_sliver_z, val_0, q99, np.sqrt)
        img_sliver_y = f_contrast(img_sliver_y, val_0, q99, np.sqrt)
        img_sliver_x = f_contrast(img_sliver_x, val_0, q99, np.sqrt)
    elif normalize_mode == 'index':
        # do nothing
        pass
    elif ',' in normalize_mode:
        val_0, q99 = map(int, normalize_mode.split(','))
        dbg_print(4, f'pixel bounds = {val_0}, {q99}')
        img_sliver_x = f_contrast(img_sliver_x, val_0, q99).T
        img_sliver_y = f_contrast(img_sliver_y, val_0, q99).T
        img_sliver_z = f_contrast(img_sliver_z, val_0, q99).T
    else:
        raise ValueError(f"Unknown pixel_scaling_mode {pixel_scaling_mode}")
    return img_sliver_z, img_sliver_y, img_sliver_x

def ThreeViewOf3DImage(im3, pivot_rel, thickness):
    im3_shape = im3.shape
    dbg_print(4, f'3D img shape = {im3_shape}, thickness = {thickness}')

    # pick slices for 3 views
    pivot_zyx = np.int64(np.clip(np.floor(_a(im3_shape) * _a(pivot_rel)), 0, _a(im3_shape)-1))

    if thickness <= 1:
        img_sliver_z = im3[pivot_zyx[0],:,:]
        img_sliver_y = im3[:,pivot_zyx[1],:]
        img_sliver_x = im3[:,:,pivot_zyx[2]]
    else:
        rgn = [None]*3
        for j in range(3):
            rgn[j] = slice(*np.clip(np.int32(
                pivot_zyx[2-j] + np.array([-1,1])*thickness/2 + 1/2
            ), 0, im3_shape[2-j]))
        img_sliver_z = im3[rgn[2],:,:].max(axis=0)
        img_sliver_y = im3[:,rgn[1],:].max(axis=1)
        img_sliver_x = im3[:,:,rgn[0]].max(axis=2)

    dbg_print(4, 'Done reading')

    return img_sliver_z, img_sliver_y, img_sliver_x

class Plot3ViewSeparate:
    def __init__(self, im3, pixel_normalize_mode):
        self.fig1, self.ax1 = plt.subplots()
        self.ax1.axis('equal')
        self.ax1.set_ylabel('z')
        self.ax1.set_xlabel('y')
        self.fig2, self.ax2 = plt.subplots()
        self.ax2.axis('equal')
        self.ax2.set_ylabel('z')
        self.ax2.set_xlabel('x')
        self.fig3, self.ax3 = plt.subplots()
        self.ax3.axis('equal')
        self.ax3.set_ylabel('y')
        self.ax3.set_xlabel('x')
        self.im3 = im3
        self._pivot_rel_ = np.array([0.5, 0.5, 0.5])
        self.pixel_normalize_mode = pixel_normalize_mode
    
    def getq99(self, img_3quadrant):
        # auto contrast (avoid reading whole 3D image)
        #img_3quadrant = [img_sliver_z, img_sliver_y, img_sliver_x]
        img_3flat = np.concatenate(list(map(lambda x:np.ravel(x), img_3quadrant)))
        print(len(img_3flat))
        q99 = np.quantile(img_3flat, 0.99)
        dbg_print(4, 'q99 =', q99)
        return q99
    
    def plot(self, pivot_rel, need_update = (1,1,1)):
        im3 = self.im3
        im3_shape = self.im3.shape
        dbg_print(4, '3D img size =', im3_shape)

        # pick slices for 3 views
        dbg_print(4, 'start reading image at pivot_rel', pivot_rel)
        pivot_zyx = np.int64(np.clip(np.floor(_a(im3_shape) * _a(pivot_rel)), 0, _a(im3_shape)-1))
        img_sliver_z = im3[pivot_zyx[0],:,:]
        img_sliver_y = im3[:,pivot_zyx[1],:]
        img_sliver_x = im3[:,:,pivot_zyx[2]]
        dbg_print(4, 'Done reading')

        img_sliver_z, img_sliver_y, img_sliver_x = \
            normalize_image_pixels(img_sliver_z, img_sliver_y, img_sliver_x,
                                   self.pixel_normalize_mode)

        if need_update[2]:
            self.ax1.imshow(img_sliver_x, cmap='gray', origin='lower')
            self.ax1.set_title(f'sliver_x = {pivot_zyx[2]}', fontsize=14)
            if need_update[2]>1:
                self.fig1.canvas.draw()
        if need_update[1]:
            self.ax2.imshow(img_sliver_y, cmap='gray', origin='lower')
            self.ax2.set_title(f'sliver_y = {pivot_zyx[1]}', fontsize=14)
            if need_update[1]>1:
                self.fig2.canvas.draw()
        if need_update[0]:
            self.ax3.imshow(img_sliver_z, cmap='gray', origin='lower')
            self.ax3.set_title(f'sliver_z = {pivot_zyx[0]}', fontsize=14)
            if need_update[0]>1:
                self.fig3.canvas.draw()
        self._pivot_rel_ = _a(pivot_rel)
        dbg_print(4, 'Done plot')
    
    def on_call(self):
        # Define the function that will be called on mouse click
        im3_shape = self.im3.shape
        def onclickany(clicked_view):
            def onclick(event):
                xy = [event.xdata, event.ydata]
                dbg_print(4, 'clicked_view =', clicked_view, ' figure x,y =', xy, ' shape =', im3_shape)
                if (xy[0] is None) or (xy[1] is None):
                    return
                # put x, y according to nonzeros of update_view
                pivot_rel = self._pivot_rel_
                if clicked_view == 1:
                    pivot_rel[0] = xy[1] / im3_shape[0]
                    pivot_rel[1] = xy[0] / im3_shape[1]
                    update_view = (2,2,0)
                if clicked_view == 2:
                    pivot_rel[0] = xy[1] / im3_shape[0]
                    pivot_rel[2] = xy[0] / im3_shape[2]
                    update_view = (2,0,2)
                if clicked_view == 3:
                    pivot_rel[1] = xy[1] / im3_shape[1]
                    pivot_rel[2] = xy[0] / im3_shape[2]
                    update_view = (0,2,2)
                dbg_print(4, 'pivot_rel =', pivot_rel)
                self.plot(pivot_rel, update_view)
                self._pivot_rel_ = pivot_rel
            return onclick

        # Connect the mouse click event to the onclick function
        self.cid1 = self.fig1.canvas. \
            mpl_connect('button_press_event', onclickany(1))
        self.cid2 = self.fig2.canvas. \
            mpl_connect('button_press_event', onclickany(2))
        self.cid3 = self.fig3.canvas. \
            mpl_connect('button_press_event', onclickany(3))

    def show(self):
        plt.show()

def showall(im3, pivot_rel, normalize_mode, thickness):
    img_sliver_z, img_sliver_y, img_sliver_x = \
        ThreeViewOf3DImage(im3, pivot_rel, thickness)
    
    img_sliver_z, img_sliver_y, img_sliver_x = \
        normalize_image_pixels(img_sliver_z, img_sliver_y, img_sliver_x,
                               normalize_mode)

    im_shape = im3.shape
    pivot_zyx = np.int64(np.clip(np.floor(_a(im_shape) * _a(pivot_rel)), 0, _a(im_shape)-1))

    fig, ax = plt.subplots()
    ax.axis('equal')  # image show in equal axis scale
    ax.imshow(img_sliver_x, cmap='gray', origin='lower')
    ax.set_title(f'sliver_x = {pivot_zyx[2]}', fontsize=14)
    ax.set_ylabel('z')
    ax.set_xlabel('y')

    fig, ax = plt.subplots()
    ax.axis('equal')  # image show in equal axis scale
    ax.imshow(img_sliver_y, cmap='gray', origin='lower')
    ax.set_title(f'sliver_y = {pivot_zyx[1]}', fontsize=14)
    ax.set_ylabel('z')
    ax.set_xlabel('x')

    fig, ax = plt.subplots()
    ax.axis('equal')  # image show in equal axis scale
    ax.imshow(img_sliver_z, cmap='gray', origin='lower')
    ax.set_title(f'sliver_z = {pivot_zyx[0]}', fontsize=14)
    ax.set_ylabel('y')
    ax.set_xlabel('x')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--img-path", type=Path, help="Path to data directory, ends with ims, h5 or zarr")
    parser.add_argument("--level", type=int, help="resolution level")
    parser.add_argument("--channel", type=int, help="data channel")
    parser.add_argument("--zyx", type=str, help="coordinate for Z,Y,X")
    parser.add_argument("--thickness", type=int, default=1, help="thickness for MIP")
    parser.add_argument("--interactive", action="store_true", help="interactive show or not.")
    parser.add_argument("--pixel-normalize-mode", type=str, help="pixel_scaling_mode, [auto_intensity, index, '100,2000']")
    args = parser.parse_args()

    img_path = args.img_path
    im_slice = (args.level, 0, args.channel)
    if img_path.suffix == '.h5' or img_path.suffix == '.ims':
        img_h5, metadata = open_ims_meta(img_path)
        img_h5i = Indexer(img_h5)
        im3 = img_h5i[im_slice]
    elif img_path.suffix == '.zarr':
        import zarr
        img3d = zarr.open(img_path)
        im3 = img3d[f'{im_slice[0]}/0/{im_slice[2]}']
    else:
        print('Error: unknown image format')
        raise ValueError
    
    zyx = tuple(map(int, args.zyx.split(',')))
    im_shape = im3.shape
    pivot_rel = (zyx[0]/im_shape[0],
                 zyx[1]/im_shape[1],
                 zyx[2]/im_shape[2])
    dbg_print(4, 'start reading image at\n    level,time,channel', im_slice, ' pivot_rel', pivot_rel)

    if args.interactive:
        print('interactive mode')
        view3angles = Plot3ViewSeparate(im3, args.pixel_normalize_mode)
        view3angles.plot(pivot_rel)
        view3angles.on_call()
        view3angles.show()
    else:
        print('show once mode')
        showall(im3, pivot_rel, args.pixel_normalize_mode, args.thickness)
        plt.show()

